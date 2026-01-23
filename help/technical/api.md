# MCP API Reference

This document provides detailed API reference for the MCP (Model Context Protocol) HTTP bridge endpoints.

## Base URL
```
http://localhost:11111/api/v1/mcp
```

## Authentication
Currently no authentication required for local development. In production, consider adding API key authentication.

## Response Format
All responses follow this structure:
```json
{
  "success": true,
  "data": { ... },
  "error": null,
  "timestamp": "2026-01-21T19:15:26.010736"
}
```

## Error Responses
```json
{
  "success": false,
  "error": "Error message",
  "timestamp": "2026-01-21T19:15:26.010736"
}
```

---

## Server Management

### List All Servers
Get information about all registered MCP servers.

**Endpoint:** `GET /servers`

**Response:**
```json
{
  "tapo-camera-mcp": {
    "name": "tapo-camera-mcp",
    "category": "camera",
    "description": "Tapo camera and smart device control",
    "healthy": true,
    "tools_count": 5,
    "resources_count": 2,
    "prompts_count": 1,
    "command": ["python", "-m", "tapo_camera_mcp.server"]
  }
}
```

### Initialize Server
Start and initialize an MCP server connection.

**Endpoint:** `POST /servers/{server_name}/initialize`

**Response:**
```json
{
  "success": true,
  "server": "tapo-camera-mcp",
  "server_info": {
    "protocolVersion": "2024-11-05",
    "serverInfo": {
      "name": "tapo-camera-mcp",
      "version": "1.0.0"
    }
  },
  "tools_count": 5,
  "resources_count": 2,
  "prompts_count": 1
}
```

### Shutdown Server
Stop an MCP server connection.

**Endpoint:** `POST /servers/{server_name}/shutdown`

**Response:**
```json
{
  "success": true,
  "server": "tapo-camera-mcp",
  "message": "Server shutdown successfully"
}
```

---

## Tool Operations

### List Server Tools
Get all tools available on a specific MCP server.

**Endpoint:** `GET /servers/{server_name}/tools`

**Response:**
```json
[
  {
    "name": "list_cameras",
    "description": "List all available cameras",
    "input_schema": {
      "type": "object",
      "properties": {
        "filter": {
          "type": "string",
          "description": "Optional filter for camera names"
        }
      }
    }
  }
]
```

### Call Tool
Execute a tool on an MCP server.

**Endpoint:** `POST /tools/call`

**Request Body:**
```json
{
  "server": "tapo-camera-mcp",
  "tool": "list_cameras",
  "arguments": {
    "filter": "front"
  }
}
```

**Response:**
```json
{
  "success": true,
  "server": "tapo-camera-mcp",
  "tool": "list_cameras",
  "result": [
    {
      "id": "cam1",
      "name": "Front Door Camera",
      "status": "online",
      "location": "Entryway"
    }
  ]
}
```

---

## Resource Operations

### List Server Resources
Get all resources available on a specific MCP server.

**Endpoint:** `GET /servers/{server_name}/resources`

**Response:**
```json
[
  {
    "uri": "camera://config",
    "name": "Camera Configuration",
    "description": "Current camera settings",
    "mime_type": "application/json"
  }
]
```

### Read Resource
Read the content of an MCP server resource.

**Endpoint:** `POST /resources/read`

**Request Body:**
```json
{
  "server": "tapo-camera-mcp",
  "uri": "camera://config"
}
```

**Response:**
```json
{
  "success": true,
  "server": "tapo-camera-mcp",
  "uri": "camera://config",
  "content": "{\"motion_detection\": true, \"night_mode\": false}"
}
```

---

## Prompt Operations

### List Server Prompts
Get all prompts available on a specific MCP server.

**Endpoint:** `GET /servers/{server_name}/prompts`

**Response:**
```json
[
  {
    "name": "camera_report",
    "description": "Generate camera activity report",
    "arguments": [
      {
        "name": "days",
        "description": "Number of days to include",
        "required": false
      }
    ]
  }
]
```

### Get Prompt
Retrieve a prompt from an MCP server.

**Endpoint:** `POST /prompts/get`

**Request Body:**
```json
{
  "server": "ai-assistant-mcp",
  "prompt": "camera_report",
  "arguments": {
    "days": 7
  }
}
```

**Response:**
```json
{
  "success": true,
  "server": "ai-assistant-mcp",
  "prompt": "camera_report",
  "content": "Generate a comprehensive report of camera activity for the last 7 days..."
}
```

---

## Health Monitoring

### System Health Check
Check the overall health of the MCP system.

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "total_servers": 58,
  "healthy_servers": 45,
  "servers": {
    "tapo-camera-mcp": {
      "healthy": true,
      "tools_count": 5,
      "resources_count": 2,
      "prompts_count": 1
    }
  }
}
```

---

## Error Codes

### MCP Protocol Errors
- `400` - Invalid request parameters
- `404` - Server or tool not found
- `408` - Request timeout
- `500` - Internal server error
- `502` - MCP server communication error
- `503` - MCP server unavailable

### Common Error Responses
```json
{
  "success": false,
  "error": "MCP client error: Connection timeout",
  "timestamp": "2026-01-21T19:15:26.010736"
}
```

---

## Rate Limiting
Currently no rate limiting implemented. Consider adding for production use.

## Versioning
API version is included in the URL path (`/api/v1/mcp`). Future versions will use `/api/v2/mcp`, etc.

---

**For implementation details, see [MCP Client Technical Documentation](../docs/MCP_CLIENT_TECHNICAL.md).**