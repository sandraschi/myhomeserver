"""
MCP Client with stdio communication for arbitrary MCP servers.
Implements the Model Context Protocol over JSON-RPC via standard input/output.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

import httpx

logger = logging.getLogger(__name__)


@dataclass
class MCPTool:
    """Represents an MCP tool."""
    name: str
    description: str
    input_schema: Dict[str, Any]


@dataclass
class MCPResource:
    """Represents an MCP resource."""
    uri: str
    name: str
    description: str
    mime_type: str


@dataclass
class MCPPrompt:
    """Represents an MCP prompt."""
    name: str
    description: str
    arguments: List[Dict[str, Any]]


class MCPClientError(Exception):
    """Base exception for MCP client errors."""
    pass


class MCPProtocolError(MCPClientError):
    """Error in MCP protocol communication."""
    pass


class MCPClient:
    """
    MCP Client that communicates with MCP servers via stdio JSON-RPC.

    This implements the full MCP protocol including:
    - initialize: Server initialization and capability negotiation
    - tools/list: List available tools
    - tools/call: Execute tools
    - resources/list: List available resources
    - resources/read: Read resource contents
    - prompts/list: List available prompts
    - prompts/get: Get prompt contents
    """

    def __init__(self, server_command: List[str], server_name: str = "unknown",
                 working_directory: Optional[str] = None, environment: Optional[Dict[str, str]] = None):
        self.server_command = server_command
        self.server_name = server_name
        self.working_directory = working_directory
        self.environment = environment or {}
        self.process: Optional[asyncio.subprocess.Process] = None
        self.initialized = False
        self.server_info: Optional[Dict[str, Any]] = None
        self.available_tools: List[MCPTool] = []
        self.available_resources: List[MCPResource] = []
        self.available_prompts: List[MCPPrompt] = []

        # JSON-RPC state
        self.next_id = 1
        self.pending_requests: Dict[int, asyncio.Future] = {}

        # Reader/writer for stdio communication
        self.reader: Optional[asyncio.StreamReader] = None
        self.writer: Optional[asyncio.StreamWriter] = None
        self.stdout_reader: Optional[asyncio.Task] = None

    async def start_server(self) -> None:
        """Start the MCP server process."""
        try:
            # Use working directory if specified
            cwd = self.working_directory or os.getcwd()

            logger.info(f"Starting MCP server: {' '.join(self.server_command)}")
            logger.info(f"MCP server working directory: {cwd}")

            # Set PYTHONPATH to include src directory
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent.parent / "src")

            # Add the server's own src directory to PYTHONPATH if working directory is set
            if self.working_directory:
                # Add the MCP server root directory (for bin scripts that need it)
                env["PYTHONPATH"] = f"{self.working_directory}:{env['PYTHONPATH']}"

                # Also add the src subdirectory if it exists
                server_src = Path(self.working_directory) / "src"
                if server_src.exists():
                    # Prepend the server src directory to PYTHONPATH for higher priority
                    env["PYTHONPATH"] = f"{str(server_src)}:{env['PYTHONPATH']}"

            # Add server-specific environment variables
            env.update(self.environment)

            logger.info(f"MCP server PYTHONPATH: {env.get('PYTHONPATH', 'NOT SET')}")

            logger.info(f"Creating subprocess with command: {self.server_command}")
            logger.info(f"Working directory: {cwd}")
            logger.info(f"Environment PYTHONPATH: {env.get('PYTHONPATH', 'NOT SET')}")

            try:
                # For MCP servers, we need stdin/stdout pipes for stdio communication
                # But for testing, we might not need stdin
                stdin_pipe = asyncio.subprocess.PIPE if "stdio" in str(self.server_command) or "mcp" in str(self.server_command) else None

                self.process = await asyncio.create_subprocess_exec(
                    *self.server_command,
                    stdin=stdin_pipe,
                    stdout=asyncio.subprocess.PIPE,
                    stderr=asyncio.subprocess.PIPE,
                    env=env,
                    cwd=cwd
                )
                logger.info(f"Subprocess created successfully with PID: {self.process.pid}")
            except Exception as e:
                logger.error(f"Failed to create subprocess: {e}")
                raise

            # Set up stdio communication
            if not self.process.stdout:
                raise MCPClientError("Failed to get stdout from MCP server process")

            # Start background task to read responses from stdout
            self.stdout_reader = asyncio.create_task(self._read_stdout_lines())

            # Start background error reader if stderr available
            if self.process.stderr:
                asyncio.create_task(self._read_stderr())

            # Monitor process exit code
            asyncio.create_task(self._monitor_process())

            logger.info(f"MCP server {self.server_name} started successfully")

        except Exception as e:
            logger.error(f"Failed to start MCP server {self.server_name}: {e}")
            raise MCPClientError(f"Failed to start server: {e}")

    async def stop_server(self) -> None:
        """Stop the MCP server process."""
        # Cancel stdout reader task
        if self.stdout_reader and not self.stdout_reader.done():
            self.stdout_reader.cancel()
            try:
                await self.stdout_reader
            except asyncio.CancelledError:
                pass

        if self.process:
            try:
                self.process.terminate()
                await asyncio.wait_for(self.process.wait(), timeout=5.0)
                logger.info(f"MCP server {self.server_name} stopped")
            except asyncio.TimeoutError:
                logger.warning(f"Force killing MCP server {self.server_name}")
                self.process.kill()
                await self.process.wait()
            except Exception as e:
                logger.error(f"Error stopping MCP server {self.server_name}: {e}")

        self.process = None
        self.initialized = False

    async def initialize(self) -> Dict[str, Any]:
        """Initialize the MCP server and negotiate capabilities."""
        try:
            logger.info(f"Starting MCP handshake with {self.server_name}")

            # Send initialize request
            logger.info(f"Sending initialize request to {self.server_name}")
            result = await self._send_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "myhomeserver-mcp-client",
                    "version": "1.0.0"
                }
            })

            self.server_info = result
            self.initialized = True
            logger.info(f"MCP server {self.server_name} initialized successfully")

            # Cache available capabilities
            logger.info(f"Caching capabilities for {self.server_name}")
            await self._cache_capabilities()
            logger.info(f"MCP handshake complete for {self.server_name}: tools={len(self.available_tools)}, resources={len(self.available_resources)}, prompts={len(self.available_prompts)}")

            return result

        except Exception as e:
            logger.error(f"Failed MCP handshake with {self.server_name}: {e}")
            raise MCPClientError(f"Initialization failed: {e}")

    async def _cache_capabilities(self) -> None:
        """Cache server capabilities after initialization."""
        try:
            # Cache tools
            logger.debug(f"Querying tools from {self.server_name}")
            tools_result = await self._send_request("tools/list", {})
            self.available_tools = [
                MCPTool(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    input_schema=tool.get("inputSchema", {})
                )
                for tool in tools_result.get("tools", [])
            ]
            logger.debug(f"Cached {len(self.available_tools)} tools from {self.server_name}")

            # Cache resources
            logger.debug(f"Querying resources from {self.server_name}")
            resources_result = await self._send_request("resources/list", {})
            self.available_resources = [
                MCPResource(
                    uri=resource["uri"],
                    name=resource.get("name", ""),
                    description=resource.get("description", ""),
                    mime_type=resource.get("mimeType", "")
                )
                for resource in resources_result.get("resources", [])
            ]
            logger.debug(f"Cached {len(self.available_resources)} resources from {self.server_name}")

            # Cache prompts
            logger.debug(f"Querying prompts from {self.server_name}")
            prompts_result = await self._send_request("prompts/list", {})
            self.available_prompts = [
                MCPPrompt(
                    name=prompt["name"],
                    description=prompt.get("description", ""),
                    arguments=prompt.get("arguments", [])
                )
                for prompt in prompts_result.get("prompts", [])
            ]
            logger.debug(f"Cached {len(self.available_prompts)} prompts from {self.server_name}")

        except Exception as e:
            logger.warning(f"Failed to cache capabilities for {self.server_name}: {e}")

    async def list_tools(self) -> List[MCPTool]:
        """List available tools."""
        if not self.initialized:
            await self.initialize()
        return self.available_tools

    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """Call a tool by name."""
        if not self.initialized:
            await self.initialize()

        logger.info(f"Calling tool {tool_name} on {self.server_name}")

        result = await self._send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments
        })

        return result

    async def list_resources(self) -> List[MCPResource]:
        """List available resources."""
        if not self.initialized:
            await self.initialize()
        return self.available_resources

    async def read_resource(self, uri: str) -> str:
        """Read a resource by URI."""
        if not self.initialized:
            await self.initialize()

        result = await self._send_request("resources/read", {"uri": uri})
        return result.get("contents", [{}])[0].get("text", "")

    async def list_prompts(self) -> List[MCPPrompt]:
        """List available prompts."""
        if not self.initialized:
            await self.initialize()
        return self.available_prompts

    async def get_prompt(self, prompt_name: str, arguments: Dict[str, Any] = None) -> str:
        """Get a prompt by name."""
        if not self.initialized:
            await self.initialize()

        params = {"name": prompt_name}
        if arguments:
            params["arguments"] = arguments

        result = await self._send_request("prompts/get", params)
        return result.get("description", "")

    async def _send_request(self, method: str, params: Dict[str, Any]) -> Any:
        """Send a JSON-RPC request and wait for response."""
        if not self.process or not self.process.stdin:
            raise MCPProtocolError("MCP server not connected")

        request_id = self.next_id
        self.next_id += 1

        request = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }

        # Create future for response
        future = asyncio.Future()
        self.pending_requests[request_id] = future

        # Send request to stdin
        request_json = json.dumps(request) + "\n"
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()

        logger.debug(f"Sent MCP request: {method} (id: {request_id})")

        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            # Clean up pending request
            del self.pending_requests[request_id]
            raise MCPProtocolError(f"Request timeout for method {method}")

    async def _read_stdout_lines(self) -> None:
        """Background task to read JSON-RPC responses from stdout."""
        if not self.process or not self.process.stdout:
            return

        try:
            while True:
                # Read line from stdout
                line = await self.process.stdout.readline()
                if not line:
                    break

                line_str = line.decode().strip()
                if not line_str:
                    continue

                try:
                    response = json.loads(line_str)
                    await self._handle_response(response)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {self.server_name}: {line_str}")

        except Exception as e:
            logger.error(f"Error reading stdout from {self.server_name}: {e}")

    async def _handle_response(self, response: Dict[str, Any]) -> None:
        """Handle a JSON-RPC response."""
        if "id" in response and response["id"] in self.pending_requests:
            future = self.pending_requests.pop(response["id"])

            if "result" in response:
                future.set_result(response["result"])
            elif "error" in response:
                error = response["error"]
                future.set_exception(MCPProtocolError(f"MCP error: {error.get('message', 'Unknown error')}"))
            else:
                future.set_exception(MCPProtocolError("Invalid response format"))

    async def _monitor_process(self) -> None:
        """Monitor MCP server process and report exit code."""
        if not self.process:
            return

        try:
            return_code = await self.process.wait()
            logger.error(f"MCP server {self.server_name} exited with code: {return_code}")
            print(f"MCP server {self.server_name} exited with code: {return_code}")
        except Exception as e:
            logger.error(f"Error monitoring MCP server {self.server_name}: {e}")
            print(f"Error monitoring MCP server {self.server_name}: {e}")

    async def _read_stderr(self) -> None:
        """Background task to read stderr for debugging."""
        if not self.process or not self.process.stderr:
            return

        try:
            while True:
                line = await self.process.stderr.readline()
                if not line:
                    break

                line_str = line.decode().strip()
                if line_str:
                    logger.error(f"MCP server {self.server_name} stderr: {line_str}")
                    # Also print to stdout for immediate visibility
                    print(f"MCP server {self.server_name} stderr: {line_str}")

        except Exception as e:
            logger.error(f"Error reading stderr from {self.server_name}: {e}")
            print(f"Error reading stderr from {self.server_name}: {e}")

    async def __aenter__(self):
        """Async context manager entry."""
        await self.start_server()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.stop_server()


class MCPClientManager:
    """
    Manager for multiple MCP clients with connection pooling and health monitoring.
    """

    def __init__(self):
        self.clients: Dict[str, MCPClient] = {}
        self.server_configs: Dict[str, Dict[str, Any]] = {}

    def register_server(self, name: str, command: List[str], **config) -> None:
        """Register an MCP server configuration."""
        self.server_configs[name] = {
            "command": command,
            **config
        }

    async def get_client(self, server_name: str) -> MCPClient:
        """Get or create an MCP client for a server."""
        if server_name not in self.clients:
            if server_name not in self.server_configs:
                raise MCPClientError(f"Unknown MCP server: {server_name}")

            config = self.server_configs[server_name]
            auto_start = config.get("auto_start", True)

            # Don't start servers that are not configured to auto-start
            if not auto_start:
                raise MCPClientError(f"MCP server {server_name} is not configured to auto-start")

            client = MCPClient(
                config["command"],
                server_name,
                working_directory=config.get("working_directory"),
                environment=config.get("environment", {})
            )
            await client.start_server()
            await client.initialize()
            self.clients[server_name] = client

        return self.clients[server_name]

    async def close_all(self) -> None:
        """Close all MCP client connections."""
        for client in self.clients.values():
            await client.stop_server()
        self.clients.clear()

    async def health_check(self, server_name: str) -> bool:
        """Check if an MCP server is healthy."""
        try:
            # Only check health for servers that are already running
            config = self.server_configs.get(server_name, {})
            auto_start = config.get("auto_start", True)

            # If server is not configured to auto-start and not already running, consider it "not healthy" (not started)
            if not auto_start and server_name not in self.clients:
                return False

            # If server is running, check if it's actually healthy
            if server_name in self.clients:
                client = self.clients[server_name]
                if client.initialized:
                    # Simple health check - try to list tools
                    await client.list_tools()
                    return True
                else:
                    return False

            # Auto-start servers that are configured to auto-start
            try:
                client = await self.get_client(server_name)
                # Simple health check - try to list tools
                await client.list_tools()
                return True
            except Exception:
                return False

            return False
        except Exception:
            return False

    async def list_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all registered servers with their status."""
        result = {}
        for name, config in self.server_configs.items():
            try:
                auto_start = config.get("auto_start", True)
                client = self.clients.get(name)

                # For servers that are running, check their health
                if client and client.initialized:
                    try:
                        # Simple health check - try to list tools
                        await client.list_tools()
                        healthy = True
                    except:
                        healthy = False
                elif auto_start:
                    # For servers configured to auto-start but not running, try to start them
                    try:
                        client = await self.get_client(name)
                        healthy = True
                    except:
                        healthy = False
                else:
                    # For servers not configured to auto-start
                    healthy = False

                result[name] = {
                    "healthy": healthy,
                    "command": config["command"],
                    "tools_count": len(client.available_tools) if client and client.initialized else 0,
                    "resources_count": len(client.available_resources) if client and client.initialized else 0,
                    "prompts_count": len(client.available_prompts) if client and client.initialized else 0,
                    "status": "running" if client and client.initialized else ("not_started" if not auto_start else "starting_failed")
                }
            except Exception as e:
                result[name] = {
                    "healthy": False,
                    "command": config["command"],
                    "error": str(e),
                    "status": "error"
                }

        return result


# Global client manager instance
mcp_manager = MCPClientManager()