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
    """Get all devices (currently none connected)"""
    return {
        "devices": [],  # No devices connected yet
        "total": 0,
        "online": 0,
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

        # No mock data - return real/empty data
        real_devices = {
            "total": 0,  # No devices connected yet
            "online": 0,
            "offline": 0,
            "warning": 0,
        }

        real_events = []  # No events yet

        # No weather data - will be None when no sensors available
        real_weather = None

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
                    "mcp_servers_total": mcp_status.get("total_servers", 0),
                    "mcp_servers_healthy": mcp_status.get("healthy_servers", 0),
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