#!/usr/bin/env python3
"""
MyHomeServer - Unified Smart Home Dashboard Backend
FastAPI application that orchestrates multiple MCP servers for comprehensive home automation.
"""

from datetime import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import MCP components
from app.mcp.registry import initialize_mcp_registry, mcp_registry
from app.api.mcp import router as mcp_router

# Mock API endpoints for demonstration
from fastapi import HTTPException
import random
from datetime import datetime, timedelta

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handle application startup and shutdown."""
    # Startup
    logger.info("Initializing MCP system...")
    try:
        await initialize_mcp_registry()
        logger.info("MCP system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize MCP system: {e}")
        # Don't crash the app, just log the error

    yield

    # Shutdown
    logger.info("Shutting down MCP system...")
    try:
        await mcp_registry.shutdown_all()
        logger.info("MCP system shutdown complete")
    except Exception as e:
        logger.error(f"Error during MCP shutdown: {e}")


# Create FastAPI app
app = FastAPI(
    title="MyHomeServer API",
    description="Unified API for smart home automation via MCP servers",
    version="2.0.1",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173", "http://localhost:3333"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mock API endpoints for demonstration
from fastapi import HTTPException
import random
from datetime import datetime, timedelta

# Mock API endpoints for demonstration
@app.get("/api/v1/dashboard/overview")
async def get_dashboard_overview():
    """Get dashboard overview with mock device data"""
    return {
        "devices": {
            "total": 8,
            "online": 6,
            "offline": 2,
            "warning": 0
        },
        "recent_events": [
            {
                "id": "1",
                "timestamp": datetime.now() - timedelta(minutes=5),
                "type": "motion",
                "deviceId": "camera_front",
                "deviceName": "Front Door Camera",
                "location": "Front Door",
                "description": "Motion detected at front door",
                "severity": "medium",
                "acknowledged": False
            },
            {
                "id": "2",
                "timestamp": datetime.now() - timedelta(minutes=15),
                "type": "energy",
                "deviceId": "plug_tv",
                "deviceName": "TV Smart Plug",
                "location": "Living Room",
                "description": "High energy usage detected",
                "severity": "low",
                "acknowledged": True
            }
        ],
        "system_status": {
            "uptime": "2 hours 15 minutes",
            "cpu": 15.2,
            "memory": 256,
            "network": "online"
        },
        "weather": {
            "timestamp": datetime.now(),
            "temperature": 22.5,
            "humidity": 65,
            "pressure": 1013.2,
            "windSpeed": 3.2,
            "windDirection": 180,
            "conditions": "Partly cloudy",
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=1)).date(),
                    "temperature": {"min": 18, "max": 25},
                    "conditions": "Sunny",
                    "precipitation": 0,
                    "windSpeed": 4.1
                }
            ],
            "indoor": {
                "temperature": 21.8,
                "humidity": 58,
                "co2": 450,
                "noise": 35
            }
        }
    }


@app.get("/api/v1/devices")
async def get_devices():
    """Get all devices with mock data"""
    return {
        "devices": [
            {
                "id": "camera_front",
                "name": "Front Door Camera",
                "type": "camera",
                "status": "online",
                "location": "Front Door",
                "lastSeen": datetime.now() - timedelta(minutes=2),
                "streamUrl": "rtsp://camera_front:554/stream",
                "recordingEnabled": True,
                "motionDetected": False,
                "ptzEnabled": True,
                "resolution": "1080p",
                "nightVision": True
            },
            {
                "id": "camera_backyard",
                "name": "Backyard Camera",
                "type": "camera",
                "status": "online",
                "location": "Backyard",
                "lastSeen": datetime.now() - timedelta(minutes=1),
                "streamUrl": "rtsp://camera_backyard:554/stream",
                "recordingEnabled": True,
                "motionDetected": False,
                "ptzEnabled": False,
                "resolution": "720p",
                "nightVision": True
            },
            {
                "id": "plug_coffee",
                "name": "Coffee Maker",
                "type": "plug",
                "status": "online",
                "location": "Kitchen",
                "lastSeen": datetime.now() - timedelta(seconds=30),
                "power": 0.0,
                "voltage": 120.5,
                "current": 0.0,
                "todayKwh": 0.8,
                "monthKwh": 24.5,
                "isOn": False
            },
            {
                "id": "plug_tv",
                "name": "TV",
                "type": "plug",
                "status": "online",
                "location": "Living Room",
                "lastSeen": datetime.now() - timedelta(seconds=45),
                "power": 85.3,
                "voltage": 121.2,
                "current": 0.7,
                "todayKwh": 2.1,
                "monthKwh": 67.8,
                "isOn": True
            },
            {
                "id": "plug_computer",
                "name": "Computer",
                "type": "plug",
                "status": "online",
                "location": "Office",
                "lastSeen": datetime.now() - timedelta(seconds=10),
                "power": 145.7,
                "voltage": 120.8,
                "current": 1.2,
                "todayKwh": 3.2,
                "monthKwh": 89.4,
                "isOn": True
            },
            {
                "id": "weather_outdoor",
                "name": "Outdoor Weather Station",
                "type": "sensor",
                "status": "online",
                "location": "Backyard",
                "lastSeen": datetime.now() - timedelta(minutes=3),
                "batteryLevel": 85,
                "signalStrength": 92
            },
            {
                "id": "thermostat_living",
                "name": "Living Room Thermostat",
                "type": "thermostat",
                "status": "online",
                "location": "Living Room",
                "lastSeen": datetime.now() - timedelta(minutes=1),
                "currentTemperature": 21.5,
                "targetTemperature": 22.0,
                "humidity": 62,
                "mode": "heat",
                "hvacAction": "idle",
                "fanMode": "auto"
            },
            {
                "id": "lightstrip_desk",
                "name": "Desk Light Strip",
                "type": "light",
                "status": "offline",
                "location": "Office",
                "lastSeen": datetime.now() - timedelta(hours=2),
                "brightness": 0,
                "isOn": False,
                "supportsColor": True,
                "supportsBrightness": True
            }
        ],
        "total": 8,
        "online": 7,
        "offline": 1
    }


@app.get("/api/v1/mcp/health")
async def get_mcp_health():
    """Get MCP server health status"""
    return [
        {
            "name": "Tapo Camera",
            "url": "http://localhost:7778",
            "status": "connected",
            "lastPing": datetime.now() - timedelta(seconds=30),
            "responseTime": 45,
            "version": "1.2.0"
        },
        {
            "name": "Netatmo Weather",
            "url": "http://localhost:7781",
            "status": "connected",
            "lastPing": datetime.now() - timedelta(seconds=25),
            "responseTime": 32,
            "version": "1.1.5"
        },
        {
            "name": "Home Assistant",
            "url": "http://localhost:7783",
            "status": "connected",
            "lastPing": datetime.now() - timedelta(seconds=20),
            "responseTime": 28,
            "version": "2.0.1"
        },
        {
            "name": "Ring Security",
            "url": "http://localhost:7782",
            "status": "disconnected",
            "lastPing": datetime.now() - timedelta(minutes=5),
            "responseTime": 0,
            "error": "Connection timeout"
        }
    ]


@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "MyHomeServer API",
        "version": "2.0.1",
    }


# Include MCP API router
app.include_router(mcp_router, prefix="/api/v1/mcp", tags=["mcp"])


@app.get("/api/v1/dashboard")
async def dashboard_overview():
    """Dashboard overview with system status and device summary"""
    try:
        # Get MCP system health
        from app.api.mcp import mcp_health_check
        mcp_status = await mcp_health_check()

        return {
            "success": True,
            "data": {
                "devices": {
                    "total": 0,
                    "online": 0,
                    "offline": 0,
                    "warning": 0,
                },
                "recent_events": [],
                "system_status": {
                    "uptime": "running",
                    "cpu": 0.0,
                    "memory": 0.0,
                    "network": "online",
                    "mcp_servers_total": mcp_status.get("total_servers", 0),
                    "mcp_servers_healthy": mcp_status.get("healthy_servers", 0),
                },
                "weather": None,
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {
            "success": True,
            "data": {
                "devices": {
                    "total": 0,
                    "online": 0,
                    "offline": 0,
                    "warning": 0,
                },
                "recent_events": [],
                "system_status": {
                    "uptime": "running",
                    "cpu": 0.0,
                    "memory": 0.0,
                    "network": "online",
                },
                "weather": None,
            },
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=10500)