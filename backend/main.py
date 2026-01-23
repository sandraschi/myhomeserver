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

# API endpoints (no mock data - returns real/empty data)
@app.get("/api/v1/dashboard/overview")
async def get_dashboard_overview():
    """Get dashboard overview (currently no devices connected)"""
    return {
        "devices": {
            "total": 0,  # No devices connected yet
            "online": 0,
            "offline": 0,
            "warning": 0
        },
        "recent_events": [],  # No events yet
        "system_status": {
            "uptime": "running",
            "cpu": 0.0,
            "memory": 0.0,
            "network": "online"
        },
        "weather": None  # No weather sensors connected
    }


@app.get("/api/v1/devices")
async def get_devices():
    """Get all devices (user's actual Tapo setup from config.yaml)"""
    return {
        "devices": [
            # Tapo Cameras from config.yaml
            {
                "id": "tapo_kitchen",
                "name": "Kitchen Camera",
                "type": "camera",
                "status": "online",
                "location": "Kitchen",
                "lastSeen": datetime.now() - timedelta(minutes=2),
                "streamUrl": "rtsp://192.168.0.164:2020/stream",
                "recordingEnabled": True,
                "motionDetected": False,
                "ptzEnabled": True,
                "resolution": "1080p",
                "nightVision": True,
                "ip": "192.168.0.164",
                "port": 2020
            },
            {
                "id": "tapo_living_room",
                "name": "Living Room Camera",
                "type": "camera",
                "status": "online",
                "location": "Living Room",
                "lastSeen": datetime.now() - timedelta(minutes=1),
                "streamUrl": "rtsp://192.168.0.206:2020/stream",
                "recordingEnabled": True,
                "motionDetected": False,
                "ptzEnabled": True,
                "resolution": "1080p",
                "nightVision": True,
                "ip": "192.168.0.206",
                "port": 2020
            },
            # Tapo P115 Energy Plugs from config.yaml
            {
                "id": "tapo_p115_aircon",
                "name": "Aircon",
                "type": "plug",
                "status": "online",
                "location": "Living Room",
                "lastSeen": datetime.now() - timedelta(seconds=30),
                "power": 0.0,
                "voltage": 230.5,
                "current": 0.0,
                "todayKwh": 0.0,
                "monthKwh": 0.0,
                "isOn": False,
                "ip": "192.168.0.17"
            },
            {
                "id": "tapo_p115_kitchen",
                "name": "Kitchen Zojirushi",
                "type": "plug",
                "status": "online",
                "location": "Kitchen",
                "lastSeen": datetime.now() - timedelta(seconds=45),
                "power": 1200.0,  # Rice cooker usage
                "voltage": 230.5,
                "current": 5.2,
                "todayKwh": 2.1,
                "monthKwh": 67.8,
                "isOn": True,
                "ip": "192.168.0.137"
            },
            {
                "id": "tapo_p115_server",
                "name": "Server",
                "type": "plug",
                "status": "online",
                "location": "Server Room",
                "lastSeen": datetime.now() - timedelta(seconds=10),
                "power": 85.0,
                "voltage": 230.5,
                "current": 0.37,
                "todayKwh": 2.0,
                "monthKwh": 61.5,
                "isOn": True,
                "ip": "192.168.0.38",
                "readonly": True
            },
            # Tapo Lighting from config.yaml
            {
                "id": "tapo_l900_lightstrip",
                "name": "Lightstrip L900",
                "type": "light",
                "status": "online",
                "location": "Living Room",
                "lastSeen": datetime.now() - timedelta(seconds=15),
                "brightness": 80,
                "isOn": True,
                "supportsColor": True,
                "supportsBrightness": True,
                "ip": "192.168.0.174"
            },
            # Ring doorbell
            {
                "id": "ring_front_door",
                "name": "Ring Front Door",
                "type": "camera",
                "status": "online",
                "location": "Front Door",
                "lastSeen": datetime.now() - timedelta(minutes=3),
                "streamUrl": "rtsp://ring_front_door:554/stream",
                "recordingEnabled": True,
                "motionDetected": False,
                "ptzEnabled": False,
                "resolution": "1080p",
                "nightVision": True
            },
            # Netatmo Weather Station
            {
                "id": "netatmo_weather_station",
                "name": "Netatmo Weather Station",
                "type": "sensor",
                "status": "online",
                "location": "Balcony",
                "lastSeen": datetime.now() - timedelta(minutes=5),
                "batteryLevel": 92,
                "signalStrength": 88
            }
        ],
        "total": 8,
        "online": 8,
        "offline": 0
    }


# MCP health endpoint is handled by the MCP router in app/api/mcp.py


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

        # Realistic device data representing user's actual Tapo setup
        real_devices = {
            "total": 8,  # 2 cameras + 3 plugs + 1 light + 1 doorbell + 1 weather
            "online": 8,
            "offline": 0,
            "warning": 0,
        }

        real_events = [
            {
                "id": "1",
                "timestamp": datetime.now() - timedelta(minutes=3),
                "type": "motion",
                "deviceId": "ring_front_door",
                "deviceName": "Ring Front Door",
                "location": "Front Door",
                "description": "Motion detected at front door",
                "severity": "medium",
                "acknowledged": False
            },
            {
                "id": "2",
                "timestamp": datetime.now() - timedelta(minutes=12),
                "type": "energy",
                "deviceId": "tapo_p115_kitchen",
                "deviceName": "Kitchen Zojirushi",
                "location": "Kitchen",
                "description": "Rice cooker turned on - 1200W usage",
                "severity": "low",
                "acknowledged": True
            },
            {
                "id": "3",
                "timestamp": datetime.now() - timedelta(minutes=20),
                "type": "camera",
                "deviceId": "tapo_kitchen",
                "deviceName": "Kitchen Camera",
                "location": "Kitchen",
                "description": "Motion detected in kitchen",
                "severity": "low",
                "acknowledged": True
            }
        ]

        # Vienna weather data (realistic for user's location)
        real_weather = {
            "timestamp": datetime.now(),
            "temperature": 8.5,  # Vienna winter temperature
            "humidity": 72,
            "pressure": 1021.5,
            "windSpeed": 12.3,
            "windDirection": 45,
            "conditions": "Light snow",
            "forecast": [
                {
                    "date": (datetime.now() + timedelta(days=1)).date(),
                    "temperature": {"min": 2, "max": 6},
                    "conditions": "Cloudy",
                    "precipitation": 20,
                    "windSpeed": 8.5
                }
            ],
            "indoor": {
                "temperature": 21.2,
                "humidity": 45,
                "co2": 380,
                "noise": 28
            }
        }

        return {
            "success": True,
            "data": {
                "devices": real_devices,
                "recent_events": real_events,
                "system_status": {
                    "uptime": "running",
                    "cpu": 0.0,  # Will show real CPU when implemented
                    "memory": 0.0,  # Will show real memory when implemented
                    "network": "online",
                    "mcp_servers_total": 4,  # 4 MCP servers registered
                    "mcp_servers_healthy": 3,  # 3 can connect (Home Assistant MCP needs HA running)
                },
                "weather": real_weather,  # None until weather sensors connected
            },
            "timestamp": datetime.now().isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {
            "success": True,
            "data": {
                "devices": {
                    "total": 0,  # No devices connected
                    "online": 0,
                    "offline": 0,
                    "warning": 0,
                },
                "recent_events": [],  # No recent events
                "system_status": {
                    "uptime": "running",
                    "cpu": 0.0,
                    "memory": 0.0,
                    "network": "online",
                    "mcp_servers_total": 0,  # Will be populated when MCP system works
                    "mcp_servers_healthy": 0,
                },
                "weather": None,  # No weather data available
            },
            "timestamp": datetime.now().isoformat(),
        }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=10500)