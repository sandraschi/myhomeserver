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

    def __init__(self, server_command: List[str], server_name: str = "unknown"):
        self.server_command = server_command
        self.server_name = server_name
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

    async def start_server(self) -> None:
        """Start the MCP server process."""
        try:
            logger.info(f"Starting MCP server: {' '.join(self.server_command)}")

            # Set PYTHONPATH to include src directory
            env = os.environ.copy()
            env["PYTHONPATH"] = str(Path(__file__).parent.parent.parent.parent / "src")

            self.process = await asyncio.create_subprocess_exec(
                *self.server_command,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env
            )

            # Set up stdio streams
            self.reader = asyncio.StreamReader()
            reader_protocol = asyncio.StreamReaderProtocol(self.reader)
            transport, _ = await asyncio.get_event_loop().connect_read_pipe(
                lambda: reader_protocol, self.process.stdout
            )

            # Start background reader task
            asyncio.create_task(self._read_responses())

            # Start background error reader
            asyncio.create_task(self._read_stderr())

            logger.info(f"MCP server {self.server_name} started successfully")

        except Exception as e:
            logger.error(f"Failed to start MCP server {self.server_name}: {e}")
            raise MCPClientError(f"Failed to start server: {e}")

    async def stop_server(self) -> None:
        """Stop the MCP server process."""
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
            logger.info(f"Initializing MCP server {self.server_name}")

            # Send initialize request
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

            # Cache available capabilities
            await self._cache_capabilities()

            logger.info(f"MCP server {self.server_name} initialized: {result.get('serverInfo', {})}")
            return result

        except Exception as e:
            logger.error(f"Failed to initialize MCP server {self.server_name}: {e}")
            raise MCPClientError(f"Initialization failed: {e}")

    async def _cache_capabilities(self) -> None:
        """Cache server capabilities after initialization."""
        try:
            # Cache tools
            tools_result = await self._send_request("tools/list", {})
            self.available_tools = [
                MCPTool(
                    name=tool["name"],
                    description=tool.get("description", ""),
                    input_schema=tool.get("inputSchema", {})
                )
                for tool in tools_result.get("tools", [])
            ]

            # Cache resources
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

            # Cache prompts
            prompts_result = await self._send_request("prompts/list", {})
            self.available_prompts = [
                MCPPrompt(
                    name=prompt["name"],
                    description=prompt.get("description", ""),
                    arguments=prompt.get("arguments", [])
                )
                for prompt in prompts_result.get("prompts", [])
            ]

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
        if not self.process or not self.writer:
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

        # Send request
        request_json = json.dumps(request) + "\n"
        self.writer.write(request_json.encode())
        await self.writer.drain()

        logger.debug(f"Sent MCP request: {method} (id: {request_id})")

        # Wait for response with timeout
        try:
            response = await asyncio.wait_for(future, timeout=30.0)
            return response
        except asyncio.TimeoutError:
            # Clean up pending request
            del self.pending_requests[request_id]
            raise MCPProtocolError(f"Request timeout for method {method}")

    async def _read_responses(self) -> None:
        """Background task to read JSON-RPC responses."""
        if not self.reader:
            return

        try:
            while True:
                line = await self.reader.readline()
                if not line:
                    break

                try:
                    response = json.loads(line.decode().strip())
                    await self._handle_response(response)
                except json.JSONDecodeError:
                    logger.warning(f"Invalid JSON from {self.server_name}: {line.decode().strip()}")

        except Exception as e:
            logger.error(f"Error reading from {self.server_name}: {e}")

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

    async def _read_stderr(self) -> None:
        """Background task to read stderr for debugging."""
        if not self.process or not self.process.stderr:
            return

        try:
            while True:
                line = await self.process.stderr.readline()
                if not line:
                    break

                logger.debug(f"{self.server_name} stderr: {line.decode().strip()}")

        except Exception as e:
            logger.error(f"Error reading stderr from {self.server_name}: {e}")

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

            client = MCPClient(config["command"], server_name)
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
            # Only check health for servers that are already running or configured to auto-start
            config = self.server_configs.get(server_name, {})
            auto_start = config.get("auto_start", True)

            # If server is not configured to auto-start and not already running, consider it "not healthy" (not started)
            if not auto_start and server_name not in self.clients:
                return False

            client = await self.get_client(server_name)
            # Simple health check - try to list tools
            await client.list_tools()
            return True
        except Exception:
            return False

    async def list_all_servers(self) -> Dict[str, Dict[str, Any]]:
        """List all registered servers with their status."""
        result = {}
        for name, config in self.server_configs.items():
            try:
                auto_start = config.get("auto_start", True)
                healthy = await self.health_check(name)
                client = self.clients.get(name)

                # For servers not configured to auto-start, show status without trying to start them
                if not auto_start and not healthy:
                    result[name] = {
                        "healthy": False,
                        "command": config["command"],
                        "tools_count": 0,
                        "resources_count": 0,
                        "prompts_count": 0,
                        "status": "not_started"
                    }
                else:
                    result[name] = {
                        "healthy": healthy,
                        "command": config["command"],
                        "tools_count": len(client.available_tools) if client else 0,
                        "resources_count": len(client.available_resources) if client else 0,
                        "prompts_count": len(client.available_prompts) if client else 0,
                    }
            except Exception as e:
                result[name] = {
                    "healthy": False,
                    "command": config["command"],
                    "error": str(e)
                }

        return result


# Global client manager instance
mcp_manager = MCPClientManager()