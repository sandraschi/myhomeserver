# MyHomeServer Changelog

All notable changes to MyHomeServer will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [2.0.0] - 2026-01-21

### Added
- **Complete MCP Client Implementation**: Full stdio MCP client with HTTP bridge
  - JSON-RPC protocol over stdio communication
  - Process management for MCP server lifecycle
  - Connection pooling and health monitoring
  - Support for arbitrary MCP servers in the ecosystem
- **Auto-Discovery System**: Automatically discovers 50+ MCP servers in workspace
  - Scans repository structure for MCP server patterns
  - Categorizes servers (camera, energy, security, AI, etc.)
  - Dynamic server registration and configuration
- **MCP Bridge API**: Comprehensive HTTP API for MCP server interaction
  - Server management (initialize, shutdown, health checks)
  - Tool operations (list, call) across all MCP servers
  - Resource operations (list, read) for MCP server resources
  - Prompt operations (list, get) for MCP server prompts
- **Enhanced Architecture**: Major architectural improvements
  - Proper separation of concerns with MCP client layer
  - Async/await patterns for non-blocking operations
  - Comprehensive error handling and recovery
  - Type-safe implementations with Pydantic models

### Changed
- **Backend Architecture**: Complete rewrite with MCP client capabilities
  - FastAPI now includes full MCP client instead of just proxy
  - Added MCP client manager and registry components
  - Enhanced startup initialization with MCP system bootstrap
- **Port Configuration**: Updated to comply with MCP standards (port 11111)
  - Moved from port 8000 to 11111 for standards compliance
  - Updated all configuration files and documentation
- **Project Structure**: Reorganized for MCP client architecture
  - Added `app/mcp/` directory for MCP client components
  - Separated API endpoints into dedicated modules
  - Enhanced configuration management

### Technical Improvements
- **MCP Protocol Support**: Full implementation of MCP protocol
  - `initialize`: Server capability negotiation
  - `tools/list` and `tools/call`: Tool discovery and execution
  - `resources/list` and `resources/read`: Resource access
  - `prompts/list` and `prompts/get`: Prompt management
- **Process Management**: Robust MCP server process lifecycle
  - Automatic server startup on-demand
  - Proper cleanup and resource management
  - Health monitoring and reconnection logic
- **Error Handling**: Comprehensive error recovery
  - MCP protocol error handling
  - Network timeout and reconnection logic
  - Graceful degradation when servers unavailable
- **Performance**: Optimized for multiple MCP server connections
  - Connection pooling prevents resource exhaustion
  - Async operations prevent blocking
  - Efficient caching of server capabilities

## [1.0.0] - 2026-01-20

### Added
- **Initial Release**: Basic home automation dashboard
- **React Frontend**: Modern UI with Tailwind CSS dark theme
- **FastAPI Backend**: RESTful API for device management
- **Basic MCP Integration**: HTTP-based proxy for MCP servers
- **Device Dashboard**: Overview of connected smart devices
- **Responsive Design**: Mobile-friendly interface

### Features
- Device status monitoring
- Basic energy analytics
- Weather integration
- Security event display
- Dark theme UI
- Real-time updates

### Infrastructure
- Docker support
- Development scripts
- Basic testing framework
- API documentation with FastAPI