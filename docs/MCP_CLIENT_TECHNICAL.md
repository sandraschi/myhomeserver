# MyHomeServer MCP Client - Technical Implementation

## Overview

MyHomeServer implements a complete **Model Context Protocol (MCP) client** that communicates with MCP servers via **stdio JSON-RPC**. This document provides technical details about the MCP client architecture, protocol implementation, and integration patterns.

## Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │────│   MCP Client    │────│   MCP Servers   │
│   HTTP API      │    │   Bridge        │    │   (stdio)       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │                       │
         ▼                       ▼                       ▼
   HTTP Endpoints         JSON-RPC Protocol       Stdio Processes
   /api/v1/mcp/*          tools/list, call        python -m server
```

### Key Classes

#### `MCPClient`
The core MCP client that manages stdio communication with individual MCP servers.

```python
class MCPClient:
    def __init__(self, server_command: List[str], server_name: str)
    async def start_server(self) -> None
    async def stop_server(self) -> None
    async def initialize(self) -> Dict[str, Any]
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any
    async def list_tools(self) -> List[MCPTool]
    async def read_resource(self, uri: str) -> str
    async def list_resources(self) -> List[MCPResource]
```

#### `MCPClientManager`
Manages multiple MCP client connections with pooling and health monitoring.

```python
class MCPClientManager:
    def register_server(self, name: str, command: List[str], **config)
    async def get_client(self, server_name: str) -> MCPClient
    async def health_check(self, server_name: str) -> bool
    async def list_all_servers(self) -> Dict[str, Dict[str, Any]]
```

#### `MCPServerRegistry`
Handles auto-discovery and configuration of MCP servers in the workspace.

```python
class MCPServerRegistry:
    async def load_config(self) -> None
    async def _auto_discover_servers(self) -> None
    def register_server(self, config: MCPServerConfig) -> None
    async def initialize_all_auto_start(self) -> None
```

## MCP Protocol Implementation

### Connection Establishment

1. **Process Launch**: MCP server started as subprocess with stdin/stdout pipes
2. **Stream Setup**: Direct asyncio StreamReader/StreamWriter for JSON-RPC communication
3. **Background Tasks**: Concurrent readers for responses and stderr logging

```python
# Start MCP server process with async subprocess
self.process = await asyncio.create_subprocess_exec(
    *self.server_command,
    stdin=asyncio.subprocess.PIPE,
    stdout=asyncio.subprocess.PIPE,
    stderr=asyncio.subprocess.PIPE,
    env=env,
    cwd=working_directory
)

# Start background tasks for stdout/stderr reading
self._stdout_task = asyncio.create_task(self._read_stdout_lines())
self._stderr_task = asyncio.create_task(self._read_stderr())
```

**Key Implementation Details:**
- Uses `asyncio.create_subprocess_exec` for proper async subprocess handling
- Direct access to `process.stdin` (StreamWriter) and `process.stdout` (StreamReader)
- Background tasks read lines concurrently without blocking main event loop
- Proper encoding handling with UTF-8 and error replacement

### JSON-RPC Protocol

#### Request/Response Format
```json
// Request
{
  "jsonrpc": "2.0",
  "id": 1,
  "method": "tools/list",
  "params": {}
}

// Response
{
  "jsonrpc": "2.0",
  "id": 1,
  "result": {
    "tools": [
      {
        "name": "list_cameras",
        "description": "List available cameras",
        "inputSchema": {
          "type": "object",
          "properties": {}
        }
      }
    ]
  }
}
```

#### Message Flow
```
Client                  Server
  │                       │
  │── initialize ────────▶│
  │◀── serverInfo ────────│
  │                       │
  │── notifications/ ────▶│
  │   initialized         │
  │                       │
  │── tools/list ────────▶│
  │◀── toolList ──────────│
  │                       │
  │── resources/list ────▶│
  │◀── resourceList ──────│
  │                       │
  │── prompts/list ──────▶│
  │◀── promptList ────────│
  │                       │
  │── tools/call ────────▶│
  │◀── toolResult ────────│
  │                       │
```

**Protocol Version**: `2025-11-25` (latest MCP specification)
**Capabilities**: `{"roots": {"listChanged": true}, "sampling": {}}`

### Protocol Methods Implemented

#### Core Protocol
- `initialize` - Server capability negotiation with protocol version `2025-11-25`
  - Sends client capabilities: `roots.listChanged`, `sampling`
  - Receives server capabilities and server info
  - Caches server capabilities for future operations
- `notifications/initialized` - Sent after successful initialize response
- `shutdown` - Graceful server termination

#### Tools API
- `tools/list` - Discover available tools
  - Returns list of all available tools with schemas
  - Cached after initialization for performance
- `tools/call` - Execute tools with parameters
  - Validates tool exists before calling
  - Returns tool execution results

#### Resources API
- `resources/list` - Discover available resources
  - Returns list of available resource URIs
- `resources/read` - Read resource content
  - Fetches resource data by URI

#### Prompts API
- `prompts/list` - Discover available prompts
  - Returns list of available prompt templates
- `prompts/get` - Retrieve prompt content
  - Gets prompt with arguments filled in

## Auto-Discovery System

### Discovery Patterns

The registry scans the workspace for MCP server patterns:

```python
server_patterns = [
    ("src/*/mcp/server.py", "python", ["-m", "{module}.mcp.server"]),
    ("src/*/server.py", "python", ["-m", "{module}.server"]),
    ("main.py", "python", ["main.py"]),
    ("server.py", "python", ["server.py"]),
    ("app.py", "python", ["app.py"]),
]
```

### Server Categorization

Auto-discovered servers are categorized by functionality:

```python
categories = {
    "camera": ["camera", "video", "surveillance"],
    "energy": ["energy", "power", "electric", "smartplug"],
    "weather": ["weather", "netatmo", "climate"],
    "security": ["security", "ring", "alarm"],
    "home": ["home", "assistant", "hub", "nest"],
    "ai": ["ai", "llm", "gpt", "claude", "language"],
    "media": ["media", "plex", "jellyfin", "emby"],
    "network": ["network", "tailscale", "vpn"],
}
```

### Configuration Persistence

Server configurations are saved to `mcp_servers.json`:

```json
{
  "tapo-camera-mcp": {
    "name": "tapo-camera-mcp",
    "command": ["python", "-m", "tapo_camera_mcp.server"],
    "description": "Tapo camera and smart device control",
    "category": "camera",
    "working_directory": "d:\\Dev\\repos\\tapo-camera-mcp"
  }
}
```

## HTTP API Bridge

### REST Endpoints

#### Server Management
```http
GET  /api/v1/mcp/servers
POST /api/v1/mcp/servers/{name}/initialize
POST /api/v1/mcp/servers/{name}/shutdown
GET  /api/v1/mcp/health
```

#### Tool Operations
```http
GET  /api/v1/mcp/servers/{name}/tools
POST /api/v1/mcp/tools/call
Content-Type: application/json

{
  "server": "tapo-camera-mcp",
  "tool": "list_cameras",
  "arguments": {}
}
```

#### Resource Operations
```http
GET  /api/v1/mcp/servers/{name}/resources
POST /api/v1/mcp/resources/read
Content-Type: application/json

{
  "server": "plex-mcp",
  "uri": "plex://libraries"
}
```

#### Prompt Operations
```http
GET  /api/v1/mcp/servers/{name}/prompts
POST /api/v1/mcp/prompts/get
Content-Type: application/json

{
  "server": "ai-assistant-mcp",
  "prompt": "code_review",
  "arguments": {"language": "python"}
}
```

### Error Handling

#### MCP Protocol Errors
```python
class MCPClientError(Exception):
    """Base exception for MCP client errors."""

class MCPProtocolError(MCPClientError):
    """Error in MCP protocol communication."""
```

#### HTTP Error Responses
```json
{
  "detail": "MCP client error: Connection timeout"
}
```

## Process Management

### Lifecycle Management

1. **Server Start**:
   - Launch subprocess with `asyncio.create_subprocess_exec`
   - Setup stdin/stdout/stderr pipes
   - Start background tasks for stdout/stderr reading
   - Log process PID for monitoring

2. **Initialization**:
   - Send `initialize` request with protocol version `2025-11-25`
   - Wait for initialize response (10s timeout)
   - Cache server capabilities and server info
   - Send `notifications/initialized` notification
   - Discover tools, resources, and prompts
   - Mark as initialized and ready

3. **Operation**:
   - Route tool/resource/prompt calls via JSON-RPC
   - Handle responses asynchronously via pending request futures
   - Parse JSON-RPC responses line-by-line from stdout
   - Handle errors gracefully with proper error messages

4. **Shutdown**:
   - Cancel background reading tasks
   - Send termination signal to process
   - Wait for process to exit gracefully
   - Close streams and pipes
   - Cleanup all resources

### Health Monitoring

```python
async def health_check(self, server_name: str) -> bool:
    """Check if an MCP server is healthy."""
    try:
        client = await self.get_client(server_name)
        # Simple health check - try to list tools
        await client.list_tools()
        return True
    except Exception:
        return False
```

## Integration Patterns

### React Frontend Integration

```typescript
// Using React Query for MCP API calls
const { data: servers } = useQuery({
  queryKey: ['mcp-servers'],
  queryFn: () => api.get('/api/v1/mcp/servers'),
  refetchInterval: 30000,
});

const callTool = useMutation({
  mutationFn: (params: ToolCallRequest) =>
    api.post('/api/v1/mcp/tools/call', params),
});
```

### Error Boundaries

```typescript
// React error boundary for MCP errors
class MCPErrorBoundary extends Component {
  render() {
    if (this.state.hasError) {
      return (
        <div className="error">
          MCP Server Communication Error
          <button onClick={() => window.location.reload()}>
            Retry Connection
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

## Performance Considerations

### Connection Pooling
- Clients are cached and reused
- Prevents resource exhaustion
- Health checks prevent stale connections

### Async Operations
- All MCP calls are async/await
- Non-blocking I/O operations
- Concurrent request handling

### Resource Management
- Proper subprocess cleanup
- Stream closure on errors
- Memory-efficient caching

## Testing Strategy

### Device Integration Tests
MyHomeServer includes comprehensive device testing for physical smart home devices:

```python
# tests/test_devices.py - Complete device integration testing
from tests.test_devices import DeviceTestSuite

async def test_all_devices():
    """Test all physical devices in the smart home setup."""
    test_suite = DeviceTestSuite()
    results = await test_suite.run_all_tests()

    # Tests 2 Tapo cameras, 2 USB cameras, 3 Tapo plugs,
    # 1 Tapo lightstrip, 1 Hue bridge, 1 Netatmo weatherstation

    assert results["summary"]["devices_working"] >= 6  # At least 6 devices working
    assert results["summary"]["mcp_servers_connected"] >= 2  # At least 2 MCP servers
```

**Supported Device Testing:**
- **Cameras**: 2 Tapo cameras + 1 Ring camera (live streaming, PTZ, motion detection, doorbell)
- **USB Cameras**: 2 USB webcams (OpenCV integration)
- **Smart Plugs**: 3 Tapo plugs (power monitoring, remote control)
- **Lightstrip**: 1 Tapo lightstrip (RGB control, effects)
- **Hue Bridge**: Philips Hue integration (lighting control)
- **Nest Devices**: Thermostat + Protect (via Home Assistant MCP)
- **Weather Station**: Netatmo weather station (environmental monitoring)
- **Security**: Ring doorbell/camera system (motion detection, alerts)

### Unit Tests
```python
@pytest.mark.asyncio
async def test_mcp_client_initialization():
    client = MCPClient(["python", "-m", "test_server"], "test")
    await client.start_server()
    await client.initialize()
    assert client.initialized
    assert len(client.available_tools) > 0
```

### Integration Tests
```python
@pytest.mark.asyncio
async def test_mcp_bridge_api(client):
    response = await client.get("/api/v1/mcp/servers")
    assert response.status_code == 200
    servers = response.json()
    assert len(servers) > 0
```

### Mock MCP Servers
```python
# Mock server for testing
async def mock_mcp_server():
    while True:
        line = await asyncio.get_event_loop().run_in_executor(
            None, sys.stdin.readline
        )
        if not line:
            break

        request = json.loads(line)
        if request["method"] == "initialize":
            response = {
                "jsonrpc": "2.0",
                "id": request["id"],
                "result": {
                    "protocolVersion": "2024-11-05",
                    "serverInfo": {"name": "mock-server"}
                }
            }
        # Handle other methods...

        print(json.dumps(response))
        sys.stdout.flush()
```

## Troubleshooting

### Common Issues

#### Connection Timeouts
```python
# Increase timeout in client
response = await asyncio.wait_for(future, timeout=60.0)
```

#### Protocol Errors
```python
# Check server logs
tail -f /path/to/mcp/server/logs
```

#### Process Cleanup
```python
# Force kill zombie processes
import psutil
for proc in psutil.process_iter(['pid', 'name']):
    if 'mcp' in proc.info['name']:
        proc.kill()
```

### Debug Logging

Enable detailed logging:
```python
logging.basicConfig(
    level=logging.DEBUG,
    format='%(name)s - %(levelname)s - %(message)s'
)
```

### Health Check Commands

```bash
# Check MCP system health
curl http://localhost:11111/api/v1/mcp/health

# List all servers
curl http://localhost:11111/api/v1/mcp/servers

# Test tool call
curl -X POST http://localhost:11111/api/v1/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{"server": "test-server", "tool": "test_tool"}'
```

## Future Enhancements

### Planned Features
- **WebSocket Support**: Real-time MCP communication
- **Load Balancing**: Distribute calls across server instances
- **Caching Layer**: Redis-based response caching
- **Metrics Collection**: Prometheus integration
- **Configuration UI**: Web interface for server management

### Protocol Extensions
- **Streaming Responses**: Handle large result sets
- **Binary Data**: Support for file uploads/downloads
- **Authentication**: OAuth2 integration
- **Rate Limiting**: Prevent server overload

## References

- [MCP Protocol Specification](https://modelcontextprotocol.io/specification)
- [JSON-RPC 2.0 Specification](https://www.jsonrpc.org/specification)
- [Asyncio Documentation](https://docs.python.org/3/library/asyncio.html)

---

**This MCP client implementation provides a robust bridge between HTTP REST APIs and the stdio-based MCP protocol, enabling seamless integration with any MCP-compatible server.**