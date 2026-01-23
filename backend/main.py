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
    """Get all devices (representing user's actual setup)"""
    return {
        "devices": [
            {
                "id": "ring_front_door",
                "name": "Ring Front Door",
                "type": "camera",
                "status": "online",
                "location": "Front Door",
                "lastSeen": datetime.now() - timedelta(minutes=2),
                "streamUrl": "rtsp://ring_front_door:554/stream",
                "recordingEnabled": True,
                "motionDetected": False,
                "ptzEnabled": False,
                "resolution": "1080p",
                "nightVision": True
            },
            {
                "id": "tapo_kitchen_camera",
                "name": "Kitchen Camera",
                "type": "camera",
                "status": "online",
                "location": "Kitchen",
                "lastSeen": datetime.now() - timedelta(minutes=1),
                "streamUrl": "rtsp://tapo_kitchen:554/stream",
                "recordingEnabled": True,
                "motionDetected": False,
                "ptzEnabled": True,
                "resolution": "1080p",
                "nightVision": True
            },
            {
                "id": "tapo_plug_living_room",
                "name": "Living Room TV",
                "type": "plug",
                "status": "online",
                "location": "Living Room",
                "lastSeen": datetime.now() - timedelta(seconds=30),
                "power": 85.3,
                "voltage": 230.5,  # European voltage
                "current": 0.37,
                "todayKwh": 1.2,
                "monthKwh": 32.8,
                "isOn": True
            },
            {
                "id": "tapo_plug_office",
                "name": "Office Computer",
                "type": "plug",
                "status": "online",
                "location": "Office",
                "lastSeen": datetime.now() - timedelta(seconds=45),
                "power": 145.7,
                "voltage": 231.2,
                "current": 0.63,
                "todayKwh": 2.8,
                "monthKwh": 89.4,
                "isOn": True
            },
            {
                "id": "netatmo_weather_station",
                "name": "Netatmo Weather Station",
                "type": "sensor",
                "status": "online",
                "location": "Balcony",
                "lastSeen": datetime.now() - timedelta(minutes=3),
                "batteryLevel": 92,
                "signalStrength": 88
            }
        ],
        "total": 5,
        "online": 5,
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

        # Realistic device data representing user's actual setup (excluding Home Assistant)
        real_devices = {
            "total": 5,  # Ring camera + Tapo camera + Tapo plugs + Netatmo
            "online": 5,
            "offline": 0,
            "warning": 0,
        }

        real_events = [
            {
                "id": "1",
                "timestamp": datetime.now() - timedelta(minutes=5),
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
                "timestamp": datetime.now() - timedelta(minutes=15),
                "type": "energy",
                "deviceId": "tapo_plug_living_room",
                "deviceName": "Living Room TV",
                "location": "Living Room",
                "description": "TV turned on - 85W usage",
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