#!/usr/bin/env python3
"""
MyHomeServer Dashboard Demo
Shows what the dashboard looks like when MCP servers are connected
"""

import asyncio
import httpx
import json
from datetime import datetime

async def demo_dashboard():
    """Demo dashboard data aggregation"""
    print("🏠 MyHomeServer Dashboard Demo")
    print("=" * 50)

    # Simulate MCP server responses
    mock_responses = {
        "cameras": {
            "cameras": [
                {"id": "cam1", "name": "Front Door", "status": "online", "location": "Entryway"},
                {"id": "cam2", "name": "Backyard", "status": "online", "location": "Garden"},
                {"id": "cam3", "name": "Garage", "status": "online", "location": "Garage"}
            ]
        },
        "energy": {
            "devices": [
                {"id": "plug1", "name": "Coffee Maker", "power": 0, "isOn": False},
                {"id": "plug2", "name": "TV", "power": 85, "isOn": True},
                {"id": "plug3", "name": "Computer", "power": 120, "isOn": True}
            ],
            "usage": {
                "today": 8.5,
                "month": 245.3,
                "cost": 2.15
            }
        },
        "security": {
            "events": [
                {"id": "1", "type": "motion", "description": "Motion detected - Front Door", "timestamp": "2024-01-20T10:30:00Z"},
                {"id": "2", "type": "doorbell", "description": "Doorbell rang", "timestamp": "2024-01-20T09:15:00Z"},
                {"id": "3", "type": "motion", "description": "Motion detected - Backyard", "timestamp": "2024-01-20T08:45:00Z"}
            ]
        },
        "weather": {
            "current": {
                "temperature": 22,
                "humidity": 65,
                "conditions": "Partly Cloudy",
                "windSpeed": 8
            }
        }
    }

    # Calculate dashboard data
    cameras = mock_responses["cameras"]["cameras"]
    energy_devices = mock_responses["energy"]["devices"]
    security_events = mock_responses["security"]["events"]

    total_devices = len(cameras) + len(energy_devices)
    online_devices = total_devices  # Assume all online for demo
    recent_events = security_events[:5]

    print("📊 Dashboard Overview:")
    print(f"  Total Devices: {total_devices}")
    print(f"  Online: {online_devices}")
    print(f"  Recent Events: {len(recent_events)}")
    print()

    print("📹 Cameras:")
    for camera in cameras:
        print(f"  ✅ {camera['name']} ({camera['location']})")
    print()

    print("⚡ Energy Devices:")
    for device in energy_devices:
        status = "🔌" if device["isOn"] else "🔌❌"
        power = f"{device['power']}W" if device["power"] > 0 else "Off"
        print(f"  {status} {device['name']}: {power}")
    print()

    print("🌤️ Current Weather:")
    weather = mock_responses["weather"]["current"]
    print(f"  🌡️  {weather['temperature']}°C")
    print(f"  💧 {weather['humidity']}% Humidity")
    print(f"  🌤️  {weather['conditions']}")
    print(f"  💨 {weather['windSpeed']} mph wind")
    print()

    print("🚨 Recent Security Events:")
    for event in recent_events:
        emoji = "🚪" if event["type"] == "motion" else "🔔" if event["type"] == "doorbell" else "🚨"
        print(f"  {emoji} {event['description']}")
    print()

    print("💰 Energy Usage:")
    usage = mock_responses["energy"]["usage"]
    print(f"  Today: {usage['today']} kWh (${usage['cost']})")
    print(f"  Month: {usage['month']} kWh")
    print()

    print("✅ Demo Complete!")
    print("This is what MyHomeServer shows when MCP servers are connected.")
    print()
    print("To see the real dashboard:")
    print("1. Start MCP servers: cd ../tapo-camera-mcp && python -m tapo_camera_mcp.server")
    print("2. Start MyHomeServer: cd myhomeserver/frontend && npm run dev:full")
    print("3. Open: http://localhost:5173")
    print("4. API Docs: http://localhost:11111/docs")

if __name__ == "__main__":
    asyncio.run(demo_dashboard())