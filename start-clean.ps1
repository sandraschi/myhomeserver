# MyHomeServer - Clean Startup Script
# Kills existing processes and starts services with fixed ports

param(
    [switch]$NoKill,
    [switch]$BackendOnly,
    [switch]$FrontendOnly
)

Write-Host "MyHomeServer Clean Startup" -ForegroundColor Green
Write-Host "==========================" -ForegroundColor Green
Write-Host ""

# Function to kill process on specific port
function Stop-ProcessOnPort {
    param([int]$Port)

    try {
        # Find process using the port
        $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue | Where-Object { $_.State -eq 'Listen' }
        if ($connections) {
            foreach ($conn in $connections) {
                $process = Get-Process -Id $conn.OwningProcess -ErrorAction SilentlyContinue
                if ($process) {
                    Write-Host "Stopping process $($process.Name) (PID: $($process.Id)) on port $Port" -ForegroundColor Yellow
                    Stop-Process -Id $process.Id -Force -ErrorAction SilentlyContinue
                    Start-Sleep -Seconds 2
                }
            }
        }
    } catch {
        Write-Host "Warning: Could not check port $Port - $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Function to wait for port to be available
function Wait-PortAvailable {
    param([int]$Port, [int]$TimeoutSeconds = 30)

    $startTime = Get-Date
    while (((Get-Date) - $startTime).TotalSeconds -lt $TimeoutSeconds) {
        try {
            $test = Test-NetConnection -ComputerName localhost -Port $Port -WarningAction SilentlyContinue
            if ($test.TcpTestSucceeded) {
                return $false  # Port is still in use
            } else {
                return $true   # Port is available
            }
        } catch {
            return $true  # Port is available (connection failed)
        }
        Start-Sleep -Milliseconds 500
    }
    return $false  # Timeout
}

# Check if we're in the right directory
if (!(Test-Path "backend\main.py")) {
    Write-Host "Error: Please run this script from the myhomeserver directory" -ForegroundColor Red
    exit 1
}

# Kill existing processes if requested
if (-not $NoKill) {
    Write-Host "Cleaning up existing processes..." -ForegroundColor Yellow

    # Kill backend on port 10500
    if (-not $FrontendOnly) {
        Stop-ProcessOnPort -Port 10500
    }

    # Kill frontend on port 5173
    if (-not $BackendOnly) {
        Stop-ProcessOnPort -Port 5173
    }

    # Also kill any node processes that might be running
    Get-Process -Name "node" -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.CommandLine -like "*myhomeserver*" -or $_.CommandLine -like "*5173*") {
            Write-Host "Stopping Node.js process (PID: $($_.Id))" -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }

    # Kill any python processes running our backend
    Get-Process -Name "python" -ErrorAction SilentlyContinue | ForEach-Object {
        if ($_.CommandLine -like "*main.py*" -or $_.CommandLine -like "*uvicorn*10500*") {
            Write-Host "Stopping Python process (PID: $($_.Id))" -ForegroundColor Yellow
            Stop-Process -Id $_.Id -Force -ErrorAction SilentlyContinue
        }
    }

    Write-Host "Process cleanup complete" -ForegroundColor Green
    Write-Host ""
}

# Start services
$jobs = @()

# Start backend
if (-not $FrontendOnly) {
    Write-Host "Starting MyHomeServer Backend on port 10500..." -ForegroundColor Green
    Write-Host "API Documentation: http://localhost:10500/docs" -ForegroundColor Cyan
    Write-Host "Health Check: http://localhost:10500/health" -ForegroundColor Cyan
    Write-Host ""

    # Wait for port to be available
    if (-not $NoKill) {
        $portAvailable = Wait-PortAvailable -Port 10500 -TimeoutSeconds 10
        if (-not $portAvailable) {
            Write-Host "Warning: Port 10500 still in use, starting anyway..." -ForegroundColor Yellow
        }
    }

    $backendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD\backend
        & python start.py
    }
    $jobs += $backendJob

    # Give backend time to start
    Start-Sleep -Seconds 3
}

# Start frontend
if (-not $BackendOnly) {
    Write-Host "Starting MyHomeServer Frontend on port 5173..." -ForegroundColor Green
    Write-Host "Dashboard: http://localhost:5173" -ForegroundColor Cyan
    Write-Host ""

    # Wait for port to be available
    if (-not $NoKill) {
        $portAvailable = Wait-PortAvailable -Port 5173 -TimeoutSeconds 10
        if (-not $portAvailable) {
            Write-Host "Warning: Port 5173 still in use, starting anyway..." -ForegroundColor Yellow
        }
    }

    $frontendJob = Start-Job -ScriptBlock {
        Set-Location $using:PWD\frontend
        & npm run dev
    }
    $jobs += $frontendJob
}

Write-Host ""
Write-Host "Services starting..." -ForegroundColor Green
Write-Host "Press Ctrl+C to stop all services" -ForegroundColor Yellow
Write-Host ""

# Wait for jobs to complete
try {
    $jobs | Wait-Job | Out-Null
} catch {
    Write-Host ""
    Write-Host "Stopping services..." -ForegroundColor Yellow
    $jobs | Stop-Job -ErrorAction SilentlyContinue
    $jobs | Remove-Job -ErrorAction SilentlyContinue
}

Write-Host "MyHomeServer startup script completed" -ForegroundColor Green