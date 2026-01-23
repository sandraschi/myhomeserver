"""
MyHomeServer API - Unified smart home automation via MCP servers.
"""

from datetime import datetime
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import MCP components
from app.mcp.registry import initialize_mcp_registry, mcp_registry
from app.api.mcp import router as mcp_router

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

# API endpoints - returns data from MCP servers only
@app.get("/api/v1/dashboard")
async def get_dashboard():
    """Get dashboard data from MCP servers only"""
    try:
        # Get data from MCP servers
        devices = await get_devices_from_mcp()
        weather = await get_weather_from_mcp()
        events = await get_events_from_mcp()

        return {
            "devices": devices,
            "weather": weather,
            "recent_events": events,
            "system_status": {
                "mcp_servers_total": len(mcp_registry.servers),
                "mcp_servers_healthy": await get_healthy_mcp_count(),
                "backend_status": "online"
            }
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {e}")
        return {
            "devices": {"total": 0, "online": 0, "offline": 0, "warning": 0},
            "weather": None,
            "recent_events": [],
            "system_status": {
                "mcp_servers_total": len(mcp_registry.servers),
                "mcp_servers_healthy": 0,
                "backend_status": "error"
            }
        }


@app.get("/api/v1/devices")
async def get_devices():
    """Get all devices from MCP servers only"""
    try:
        devices = await get_devices_from_mcp()
        return {"devices": devices}
    except Exception as e:
        logger.error(f"Error getting devices: {e}")
        return {"devices": []}


# Helper functions to get data from MCP servers
async def get_devices_from_mcp():
    """Get devices from connected MCP servers"""
    devices = []
    try:
        # Get devices from Tapo MCP server
        try:
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")
            tapo_devices = await tapo_client.list_devices()
            devices.extend(tapo_devices)
        except Exception as e:
            logger.warning(f"Failed to get devices from tapo-camera-mcp: {e}")

        # Get devices from Ring MCP server
        try:
            ring_client = await mcp_manager.get_client("ring-mcp")
            ring_devices = await ring_client.list_devices()
            devices.extend(ring_devices)
        except Exception as e:
            logger.warning(f"Failed to get devices from ring-mcp: {e}")

        # Get devices from Home Assistant MCP server
        try:
            ha_client = await mcp_manager.get_client("home-assistant-mcp")
            ha_devices = await ha_client.list_devices()
            devices.extend(ha_devices)
        except Exception as e:
            logger.warning(f"Failed to get devices from home-assistant-mcp: {e}")

    except Exception as e:
        logger.error(f"Error getting devices from MCP servers: {e}")

    return devices

async def get_weather_from_mcp():
    """Get weather data from MCP servers"""
    try:
        # Try Netatmo MCP server first
        try:
            netatmo_client = await mcp_manager.get_client("netatmo-weather-mcp")
            weather_data = await netatmo_client.get_weather()
            return weather_data
        except Exception as e:
            logger.warning(f"Failed to get weather from netatmo-weather-mcp: {e}")

        # Fallback to other weather sources
        return None
    except Exception as e:
        logger.error(f"Error getting weather from MCP servers: {e}")
        return None

async def get_events_from_mcp():
    """Get recent events from MCP servers"""
    events = []
    try:
        # Get events from Tapo MCP server
        try:
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")
            tapo_events = await tapo_client.get_recent_events()
            events.extend(tapo_events)
        except Exception as e:
            logger.warning(f"Failed to get events from tapo-camera-mcp: {e}")

        # Get events from Ring MCP server
        try:
            ring_client = await mcp_manager.get_client("ring-mcp")
            ring_events = await ring_client.get_recent_events()
            events.extend(ring_events)
        except Exception as e:
            logger.warning(f"Failed to get events from ring-mcp: {e}")

    except Exception as e:
        logger.error(f"Error getting events from MCP servers: {e}")

    # Sort events by timestamp (most recent first)
    events.sort(key=lambda x: x.get("timestamp", datetime.min), reverse=True)
    return events[:10]  # Return only the 10 most recent events

async def get_healthy_mcp_count():
    """Count healthy MCP servers"""
    healthy_count = 0
    try:
        for server_name in mcp_registry.servers.keys():
            try:
                client = await mcp_manager.get_client(server_name)
                # Simple health check - if we can get client, consider it healthy
                healthy_count += 1
            except Exception:
                pass
    except Exception as e:
        logger.error(f"Error counting healthy MCP servers: {e}")

    return healthy_count


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


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=10500)