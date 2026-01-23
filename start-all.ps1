# MyHomeServer - Start All Services
# This script starts the MCP servers and MyHomeServer frontend/backend

Write-Host "Starting MyHomeServer Ecosystem" -ForegroundColor Green
Write-Host "==============================="
Write-Host ""

# Check if we're in the right directory
if (!(Test-Path "backend\main.py")) {
    Write-Host "Error: Please run this script from the myhomeserver directory" -ForegroundColor Red
    exit 1
}

# Function to check if port is available
function Test-PortAvailable {
    param([int]$Port)
    $result = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
    return !$result.TcpTestSucceeded
}

# Check MCP server ports
$mcpPorts = @(7778, 7779, 7780, 7781, 7782, 7783, 7784)
$mcpServers = @(
    @{Name="Tapo Camera MCP"; Port=7778; Path="../tapo-camera-mcp"},
    @{Name="Tapo Energy MCP"; Port=7779; Path="../tapo-camera-mcp"},  # Same repo, different service
    @{Name="Tapo Lighting MCP"; Port=7780; Path="../tapo-camera-mcp"}, # Same repo, different service
    @{Name="Netatmo MCP"; Port=7781; Path="../netatmo-mcp"},
    @{Name="Ring MCP"; Port=7782; Path="../ring-mcp"},
    @{Name="Home Assistant MCP"; Port=7783; Path="../home-assistant-mcp"},
    @{Name="Local LLM MCP"; Port=7784; Path="../local-llm-mcp"}
)

# MyHomeServer ports
$myHomePorts = @(10500, 5173)
$myHomeServers = @(
    @{Name="MyHomeServer Backend"; Port=10500; Service="backend"},
    @{Name="MyHomeServer Frontend"; Port=5173; Service="frontend"}
)

Write-Host "Checking MCP Server Status..." -ForegroundColor Yellow
foreach ($server in $mcpServers) {
    $available = Test-PortAvailable $server.Port
    if ($available) {
        Write-Host "  [NOT RUNNING] $($server.Name) (port $($server.Port))" -ForegroundColor Red
    } else {
        Write-Host "  [RUNNING] $($server.Name) (port $($server.Port))" -ForegroundColor Green
    }
}
Write-Host ""

# Check MyHomeServer ports
Write-Host ""
Write-Host "Checking MyHomeServer Status..." -ForegroundColor Yellow
foreach ($server in $myHomeServers) {
    $available = Test-PortAvailable $server.Port
    if ($available) {
        Write-Host "[NOT RUNNING] $($server.Name) (port $($server.Port))" -ForegroundColor Red
    } else {
        Write-Host "[RUNNING] $($server.Name) (port $($server.Port))" -ForegroundColor Green
    }
}
Write-Host ""

# Ask user what to do
Write-Host "Choose an action:" -ForegroundColor Cyan
Write-Host "1. Start MyHomeServer Backend only"
Write-Host "2. Start MyHomeServer Frontend only"
Write-Host "3. Start both MyHomeServer services"
Write-Host "4. Show MCP server startup commands"
Write-Host "5. Check system status"
Write-Host ""

$choice = Read-Host "Enter your choice (1-5)"

switch ($choice) {
    "1" {
        Write-Host "Starting MyHomeServer Backend..." -ForegroundColor Green
        Write-Host "API will be available at: http://localhost:10500" -ForegroundColor Cyan
        Write-Host "API Documentation at: http://localhost:10500/docs" -ForegroundColor Cyan
        Write-Host "Health check at: http://localhost:10500/health" -ForegroundColor Cyan
        Write-Host ""
        Set-Location backend
        python start.py
    }
    "2" {
        Write-Host "Starting MyHomeServer Frontend..." -ForegroundColor Green
        Set-Location frontend
        npm run dev
    }
    "3" {
        Write-Host "Starting both MyHomeServer services..." -ForegroundColor Green
        Write-Host ""
        Write-Host "This will start the backend and frontend concurrently." -ForegroundColor Yellow
        Write-Host "You can access MyHomeServer at: http://localhost:5173" -ForegroundColor Cyan
        Write-Host ""
        Write-Host "Press Ctrl+C to stop both services" -ForegroundColor Yellow
        Write-Host ""

        Set-Location frontend
        npm run dev:full
    }
    "4" {
        Write-Host "MCP Server Startup Commands:" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "# Tapo Camera MCP (includes Camera, Energy, Lighting services)" -ForegroundColor Cyan
        Write-Host "cd ../tapo-camera-mcp" -ForegroundColor White
        Write-Host "python -m tapo_camera_mcp.server" -ForegroundColor White
        Write-Host ""
        Write-Host "# Individual MCP servers (if available)" -ForegroundColor Cyan
        Write-Host "cd ../netatmo-mcp && python -m netatmo_mcp.server" -ForegroundColor White
        Write-Host "cd ../ring-mcp && python -m ring_mcp.server" -ForegroundColor White
        Write-Host "cd ../home-assistant-mcp && python -m home_assistant_mcp.server" -ForegroundColor White
        Write-Host "cd ../local-llm-mcp && python -m local_llm_mcp.server" -ForegroundColor White
    }
    "5" {
        Write-Host "System Status Check Complete" -ForegroundColor Green
        Write-Host ""
        Write-Host "Summary:" -ForegroundColor Cyan
        Write-Host "- Backend API: http://localhost:10500" -ForegroundColor White
        Write-Host "- API Docs: http://localhost:10500/docs" -ForegroundColor White
        Write-Host "- Frontend: http://localhost:5173" -ForegroundColor White
        Write-Host "- Health Check: http://localhost:10500/health" -ForegroundColor White
        Write-Host ""
        Write-Host "MCP Server Ports:" -ForegroundColor Yellow
        Write-Host "- Tapo Camera MCP: http://localhost:7778" -ForegroundColor White
        Write-Host "- Netatmo Weather MCP: http://localhost:7781" -ForegroundColor White
        Write-Host "- Ring Security MCP: http://localhost:7782" -ForegroundColor White
        Write-Host "- Home Assistant MCP: http://localhost:7783" -ForegroundColor White
        Write-Host "- Local LLM MCP: http://localhost:7784" -ForegroundColor White
    }
    default {
        Write-Host "Invalid choice. Please run the script again." -ForegroundColor Red
    }
}

Write-Host ""
Write-Host "👋 MyHomeServer startup script completed" -ForegroundColor Green