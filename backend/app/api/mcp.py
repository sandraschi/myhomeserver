"""
MCP API Endpoints - Bridge HTTP to MCP stdio interface.
Provides RESTful endpoints for interacting with arbitrary MCP servers.
"""

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

from ..mcp.client import mcp_manager, MCPClientError
from ..mcp.registry import mcp_registry

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models for API requests/responses
class ToolCallRequest(BaseModel):
    """Request model for tool calls."""
    server: str = Field(..., description="MCP server name")
    tool: str = Field(..., description="Tool name to call")
    arguments: Dict[str, Any] = Field(default_factory=dict, description="Tool arguments")


class ResourceReadRequest(BaseModel):
    """Request model for resource reads."""
    server: str = Field(..., description="MCP server name")
    uri: str = Field(..., description="Resource URI to read")


class PromptGetRequest(BaseModel):
    """Request model for prompt retrieval."""
    server: str = Field(..., description="MCP server name")
    prompt: str = Field(..., description="Prompt name to get")
    arguments: Optional[Dict[str, Any]] = Field(None, description="Prompt arguments")


class ServerInfo(BaseModel):
    """Server information response model."""
    name: str
    category: str
    description: str
    healthy: bool
    tools_count: int
    resources_count: int
    prompts_count: int
    command: List[str]


class ToolInfo(BaseModel):
    """Tool information response model."""
    name: str
    description: str
    input_schema: Dict[str, Any]


class ResourceInfo(BaseModel):
    """Resource information response model."""
    uri: str
    name: str
    description: str
    mime_type: str


class PromptInfo(BaseModel):
    """Prompt information response model."""
    name: str
    description: str
    arguments: List[Dict[str, Any]]


@router.get("/servers", response_model=Dict[str, ServerInfo])
async def list_servers():
    """List all registered MCP servers with their status."""
    try:
        # Get all registered servers from the registry
        all_servers = mcp_registry.list_servers()

        result = {}
        for config in all_servers:
            # Check if we have a client for this server (basic health check)
            try:
                healthy = await mcp_manager.health_check(config.name)
                # Get client info if available
                client = mcp_manager.clients.get(config.name)
                tools_count = len(client.available_tools) if client else 0
                resources_count = len(client.available_resources) if client else 0
                prompts_count = len(client.available_prompts) if client else 0
            except Exception:
                healthy = False
                tools_count = 0
                resources_count = 0
                prompts_count = 0

            result[config.name] = ServerInfo(
                name=config.name,
                category=config.category,
                description=config.description,
                healthy=healthy,
                tools_count=tools_count,
                resources_count=resources_count,
                prompts_count=prompts_count,
                command=config.command,
            )

        return result

    except Exception as e:
        logger.error(f"Failed to list MCP servers: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list servers: {str(e)}")


@router.get("/servers/{server_name}/tools", response_model=List[ToolInfo])
async def list_server_tools(server_name: str):
    """List all tools available on a specific MCP server."""
    try:
        client = await mcp_manager.get_client(server_name)
        tools = await client.list_tools()

        return [
            ToolInfo(
                name=tool.name,
                description=tool.description,
                input_schema=tool.input_schema,
            )
            for tool in tools
        ]

    except MCPClientError as e:
        logger.error(f"MCP client error for server {server_name}: {e}")
        raise HTTPException(status_code=400, detail=f"MCP client error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to list tools for server {server_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list tools: {str(e)}")


@router.post("/tools/call")
async def call_tool(request: ToolCallRequest):
    """Call a tool on an MCP server."""
    try:
        client = await mcp_manager.get_client(request.server)
        result = await client.call_tool(request.tool, request.arguments)

        return {
            "success": True,
            "server": request.server,
            "tool": request.tool,
            "result": result,
        }

    except MCPClientError as e:
        logger.error(f"MCP client error calling tool {request.tool} on {request.server}: {e}")
        raise HTTPException(status_code=400, detail=f"MCP client error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to call tool {request.tool} on {request.server}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to call tool: {str(e)}")


@router.get("/servers/{server_name}/resources", response_model=List[ResourceInfo])
async def list_server_resources(server_name: str):
    """List all resources available on a specific MCP server."""
    try:
        client = await mcp_manager.get_client(server_name)
        resources = await client.list_resources()

        return [
            ResourceInfo(
                uri=resource.uri,
                name=resource.name,
                description=resource.description,
                mime_type=resource.mime_type,
            )
            for resource in resources
        ]

    except MCPClientError as e:
        logger.error(f"MCP client error for server {server_name}: {e}")
        raise HTTPException(status_code=400, detail=f"MCP client error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to list resources for server {server_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list resources: {str(e)}")


@router.post("/resources/read")
async def read_resource(request: ResourceReadRequest):
    """Read a resource from an MCP server."""
    try:
        client = await mcp_manager.get_client(request.server)
        content = await client.read_resource(request.uri)

        return {
            "success": True,
            "server": request.server,
            "uri": request.uri,
            "content": content,
        }

    except MCPClientError as e:
        logger.error(f"MCP client error reading resource {request.uri} from {request.server}: {e}")
        raise HTTPException(status_code=400, detail=f"MCP client error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to read resource {request.uri} from {request.server}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to read resource: {str(e)}")


@router.get("/servers/{server_name}/prompts", response_model=List[PromptInfo])
async def list_server_prompts(server_name: str):
    """List all prompts available on a specific MCP server."""
    try:
        client = await mcp_manager.get_client(server_name)
        prompts = await client.list_prompts()

        return [
            PromptInfo(
                name=prompt.name,
                description=prompt.description,
                arguments=prompt.arguments,
            )
            for prompt in prompts
        ]

    except MCPClientError as e:
        logger.error(f"MCP client error for server {server_name}: {e}")
        raise HTTPException(status_code=400, detail=f"MCP client error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to list prompts for server {server_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list prompts: {str(e)}")


@router.post("/prompts/get")
async def get_prompt(request: PromptGetRequest):
    """Get a prompt from an MCP server."""
    try:
        client = await mcp_manager.get_client(request.server)
        content = await client.get_prompt(request.prompt, request.arguments)

        return {
            "success": True,
            "server": request.server,
            "prompt": request.prompt,
            "content": content,
        }

    except MCPClientError as e:
        logger.error(f"MCP client error getting prompt {request.prompt} from {request.server}: {e}")
        raise HTTPException(status_code=400, detail=f"MCP client error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to get prompt {request.prompt} from {request.server}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get prompt: {str(e)}")


@router.post("/servers/{server_name}/initialize")
async def initialize_server(server_name: str):
    """Initialize or reinitialize an MCP server connection."""
    try:
        # Close existing connection if any
        if server_name in mcp_manager.clients:
            await mcp_manager.clients[server_name].stop_server()
            del mcp_manager.clients[server_name]

        # Create new connection
        client = await mcp_manager.get_client(server_name)

        return {
            "success": True,
            "server": server_name,
            "server_info": client.server_info,
            "tools_count": len(client.available_tools),
            "resources_count": len(client.available_resources),
            "prompts_count": len(client.available_prompts),
        }

    except MCPClientError as e:
        logger.error(f"MCP client error initializing server {server_name}: {e}")
        raise HTTPException(status_code=400, detail=f"MCP client error: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to initialize server {server_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize server: {str(e)}")


@router.post("/servers/{server_name}/shutdown")
async def shutdown_server(server_name: str):
    """Shutdown an MCP server connection."""
    try:
        if server_name in mcp_manager.clients:
            await mcp_manager.clients[server_name].stop_server()
            del mcp_manager.clients[server_name]

        return {
            "success": True,
            "server": server_name,
            "message": "Server shutdown successfully",
        }

    except Exception as e:
        logger.error(f"Failed to shutdown server {server_name}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to shutdown server: {str(e)}")


@router.get("/health")
async def mcp_health_check():
    """Check the health of the MCP system."""
    try:
        # Get all servers status
        servers_status = await mcp_manager.list_all_servers()

        # Only return real registered servers (no mock data)

        healthy_servers = sum(1 for status in servers_status.values() if status.get("healthy", False))
        total_servers = len(servers_status)

        return {
            "status": "healthy" if healthy_servers > 0 else "degraded",
            "total_servers": total_servers,
            "healthy_servers": healthy_servers,
            "servers": servers_status,
        }

    except Exception as e:
        logger.error(f"MCP health check failed: {e}")
        return {
            "status": "error",
            "error": str(e),
        }