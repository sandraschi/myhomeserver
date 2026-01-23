# MyHomeServer Help System

Welcome to the MyHomeServer help system. This comprehensive guide covers all aspects of using and understanding MyHomeServer.

## 📚 Documentation Structure

- **[User Guide](user/)** - Getting started, basic usage, and tutorials
- **[Technical Documentation](technical/)** - Architecture, APIs, and technical details
- **[Troubleshooting](troubleshooting/)** - Common issues and solutions
- **[Integration Guides](integrations/)** - MCP server integrations

## 🚀 Quick Start

If you're new to MyHomeServer, start here:

1. **[Installation Guide](user/installation.md)** - Set up MyHomeServer
2. **[First Dashboard](user/first-dashboard.md)** - Create your first smart home dashboard
3. **[MCP Server Setup](user/mcp-setup.md)** - Connect your first MCP server

## 🔧 Technical Section

### MCP Client Architecture

MyHomeServer includes a sophisticated MCP (Model Context Protocol) client that enables communication with any MCP-compatible server via stdio JSON-RPC.

#### 📖 [MCP Client Technical Implementation](../docs/MCP_CLIENT_TECHNICAL.md)

**Key Topics Covered:**
- **Protocol Implementation** - Complete MCP stdio JSON-RPC protocol
- **Auto-Discovery System** - Automatic MCP server detection and registration
- **HTTP Bridge API** - RESTful API for MCP server interaction
- **Process Management** - Robust MCP server lifecycle management
- **Performance Optimization** - Connection pooling and async operations

#### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │────│   MCP Client    │────│   MCP Servers   │
│   HTTP API      │    │   Bridge        │    │   (stdio)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

#### Protocol Flow

1. **Discovery**: Auto-discovery finds 50+ MCP servers in workspace
2. **Initialization**: `initialize` → negotiate protocol capabilities
3. **Capability Caching**: `tools/list`, `resources/list`, `prompts/list`
4. **Tool Execution**: `tools/call` for server interactions
5. **Resource Access**: `resources/read` for data retrieval

### API Reference

#### Server Management
```http
GET  /api/v1/mcp/servers                    # List discovered servers
POST /api/v1/mcp/servers/{name}/initialize   # Start MCP server
POST /api/v1/mcp/servers/{name}/shutdown     # Stop MCP server
GET  /api/v1/mcp/health                      # System health check
```

#### Tool Operations
```http
GET  /api/v1/mcp/servers/{name}/tools         # List server tools
POST /api/v1/mcp/tools/call                   # Execute tool
```

#### Resource Operations
```http
GET  /api/v1/mcp/servers/{name}/resources     # List server resources
POST /api/v1/mcp/resources/read               # Read resource
```

### Troubleshooting MCP Issues

#### Connection Problems
- **Timeout Errors**: Check if MCP server is running on correct port
- **Protocol Errors**: Verify MCP server implements protocol correctly
- **Process Issues**: Use `taskkill /f /im python.exe` to clean up zombies

#### Auto-Discovery Issues
- **Missing Servers**: Run auto-discovery manually
- **Wrong Categories**: Check server naming conventions
- **Path Issues**: Verify `PYTHONPATH` includes `src` directories

#### Performance Issues
- **Slow Responses**: Check server health and resource usage
- **Memory Leaks**: Monitor subprocess cleanup
- **Connection Pooling**: Verify client reuse

## 🔍 Common Tasks

### Adding New MCP Servers

1. **Manual Registration**:
   ```python
   from app.mcp.registry import mcp_registry
   mcp_registry.register_server(MCPServerConfig(
       name="my-server",
       command=["python", "-m", "my_server.mcp"],
       category="custom"
   ))
   ```

2. **Auto-Discovery**: Place server in workspace with proper structure

3. **Configuration**: Update `mcp_servers.json` for persistence

### Debugging MCP Communication

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test server connection
from app.mcp.client import mcp_manager
client = await mcp_manager.get_client("server-name")
result = await client.call_tool("test_tool", {})
```

### Monitoring System Health

```bash
# Check MCP system status
curl http://localhost:11111/api/v1/mcp/health

# List active servers
curl http://localhost:11111/api/v1/mcp/servers

# Test tool execution
curl -X POST http://localhost:11111/api/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"server": "tapo-camera-mcp", "tool": "list_cameras"}'
```

## 📋 Support

### Getting Help

1. **Check Documentation**: Search this help system first
2. **Log Analysis**: Review backend logs for error details
3. **Health Checks**: Use built-in health endpoints for diagnostics
4. **Community**: Check MCP ecosystem documentation

### Issue Reporting

When reporting issues, include:
- MCP server name and version
- Full error traceback
- System configuration
- Steps to reproduce

---

**For detailed technical information, see [MCP Client Technical Implementation](../docs/MCP_CLIENT_TECHNICAL.md).**