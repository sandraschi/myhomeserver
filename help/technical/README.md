# Technical Documentation

This section contains detailed technical documentation for MyHomeServer's architecture, APIs, and implementation details.

## 📚 Available Documentation

### Core Architecture
- **[MCP Client Implementation](../docs/MCP_CLIENT_TECHNICAL.md)** - Complete MCP stdio client architecture
- **[API Reference](api.md)** - REST API endpoints and specifications
- **[Database Schema](database/)** - Data models and relationships

### MCP Protocol Details
- **[Protocol Implementation](../docs/MCP_CLIENT_TECHNICAL.md#json-rpc-protocol)** - JSON-RPC communication details
- **[Auto-Discovery System](../docs/MCP_CLIENT_TECHNICAL.md#auto-discovery-system)** - Server discovery mechanisms
- **[Process Management](../docs/MCP_CLIENT_TECHNICAL.md#process-management)** - Subprocess lifecycle handling

### Integration Guides
- **[HTTP Bridge API](../docs/MCP_CLIENT_TECHNICAL.md#http-api-bridge)** - RESTful MCP server interaction
- **[React Integration](../docs/MCP_CLIENT_TECHNICAL.md#react-frontend-integration)** - Frontend MCP client usage
- **[Error Handling](../docs/MCP_CLIENT_TECHNICAL.md#error-handling)** - Comprehensive error management

## 🔧 MCP Client Architecture

### Overview

MyHomeServer implements a complete MCP (Model Context Protocol) client that bridges HTTP REST APIs to MCP servers using stdio JSON-RPC communication.

### Key Components

#### MCPClient Class
```python
class MCPClient:
    """Complete MCP client with stdio communication."""

    async def initialize(self) -> Dict[str, Any]:
        """Initialize MCP server and cache capabilities."""
        # 1. Send initialize request
        # 2. Call tools/list, resources/list, prompts/list
        # 3. Cache server capabilities

    async def call_tool(self, tool_name: str, arguments: Dict) -> Any:
        """Execute tool on MCP server via JSON-RPC."""

    async def list_tools(self) -> List[MCPTool]:
        """Get cached list of available tools."""
```

#### Protocol Flow
```
Client                  Server
  │                       │
  │── initialize ────────▶│  (negotiate capabilities)
  │◀── serverInfo ────────│
  │                       │
  │── tools/list ────────▶│  (discover tools)
  │◀── toolList ──────────│
  │                       │
  │── tools/call ────────▶│  (execute tool)
  │◀── toolResult ────────│
```

### HTTP API Bridge

The MCP client is exposed via RESTful HTTP endpoints:

```http
# Server management
GET  /api/v1/mcp/servers
POST /api/v1/mcp/servers/{name}/initialize

# Tool operations
GET  /api/v1/mcp/servers/{name}/tools
POST /api/v1/mcp/tools/call

# Resource operations
GET  /api/v1/mcp/servers/{name}/resources
POST /api/v1/mcp/resources/read
```

### Auto-Discovery System

MyHomeServer automatically discovers MCP servers in the workspace:

```python
# Scans for patterns like:
# - src/*/mcp/server.py
# - src/*/server.py
# - main.py, server.py, app.py

# Categorizes by functionality:
categories = {
    "camera": ["camera", "video"],
    "energy": ["energy", "power"],
    "ai": ["ai", "llm", "gpt"],
    # ... etc
}
```

## 🚀 Quick Technical Reference

### Starting MCP Server Communication

```python
from app.mcp.client import mcp_manager

# Get client for server
client = await mcp_manager.get_client("tapo-camera-mcp")

# Initialize (calls tools/list, resources/list, prompts/list)
await client.initialize()

# Call a tool
result = await client.call_tool("list_cameras", {})

# List available tools
tools = await client.list_tools()
```

### HTTP API Usage

```bash
# List all servers
curl http://localhost:11111/api/v1/mcp/servers

# Call a tool
curl -X POST http://localhost:11111/api/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "server": "tapo-camera-mcp",
    "tool": "list_cameras",
    "arguments": {}
  }'
```

### Debugging MCP Issues

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check server health
healthy = await mcp_manager.health_check("server-name")

# Force reinitialize
await mcp_manager.get_client("server-name", force_reinit=True)
```

## Device Testing and Validation

### Physical Device Integration Testing

MyHomeServer includes comprehensive testing for physical smart home devices:

```bash
# Run complete device integration tests
cd ../../../tests
python test_devices.py
```

**Test Coverage:**
- **Cameras**: 2 Tapo cameras + 1 Ring camera (streaming, PTZ, motion detection, doorbell)
- **USB Cameras**: 2 USB webcams (OpenCV integration)
- **Smart Plugs**: 3 Tapo plugs (power monitoring, remote control)
- **Lighting**: 1 Tapo lightstrip + Philips Hue bridge (RGB control, effects)
- **Smart Home**: Nest thermostat + Nest Protect (Home Assistant integration)
- **Weather**: Netatmo weather station (environmental monitoring)
- **Security**: Ring doorbell/camera system (motion detection, alerts)

### MCP Server Validation

```python
# Test individual MCP server connectivity
from app.mcp.client import mcp_manager

# Test Tapo MCP server
client = await mcp_manager.get_client("tapo-camera-mcp")
tools = await client.list_tools()
cameras = await client.call_tool("list_cameras", {})

# Test Netatmo MCP server
weather_client = await mcp_manager.get_client("netatmo-weather-mcp")
weather_data = await weather_client.call_tool("get_current_weather", {})
```

## 📖 Further Reading

- **[Complete MCP Client Technical Documentation](../docs/MCP_CLIENT_TECHNICAL.md)**
- **[Device Testing Implementation](../../tests/test_devices.py)**
- **[MCP Protocol Specification](https://modelcontextprotocol.io/specification)**
- **[JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)**

---

**For detailed implementation details, see the [MCP Client Technical Documentation](../docs/MCP_CLIENT_TECHNICAL.md).**