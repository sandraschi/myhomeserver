#!/usr/bin/env python3
"""Simplified version of main.py to isolate the issue"""

import asyncio
from datetime import datetime
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Create FastAPI app
app = FastAPI(
    title="MyHomeServer API",
    description="Unified API for smart home automation via MCP servers",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health_check():
    """Basic health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "service": "MyHomeServer API",
        "version": "1.0.0",
    }

@app.get("/api/v1/dashboard")
async def dashboard_overview():
    """Dashboard overview"""
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
    uvicorn.run(app, host="0.0.0.0", port=11112)