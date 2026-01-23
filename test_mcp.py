#!/usr/bin/env python3
"""
Test script to run MCP servers manually and debug issues.
"""

import asyncio
import os
import sys
from pathlib import Path

async def test_tapo_server():
    """Test the Tapo Camera MCP server."""
    try:
        # Set up PYTHONPATH
        tapo_path = Path("D:/Dev/repos/tapo-camera-mcp")
        myhome_path = Path("D:/Dev/repos/myhomeserver")

        sys.path.insert(0, str(tapo_path / "src"))
        sys.path.insert(0, str(tapo_path))
        sys.path.insert(0, str(myhome_path / "src"))

        print("Testing Tapo Camera MCP server import...")
        from tapo_camera_mcp.core.server import TapoCameraServer
        print("✓ Import successful")

        print("Creating server instance...")
        server = await TapoCameraServer.get_instance()
        print("✓ Server instance created")

        print("Starting server in stdio mode...")
        await server.run(stdio=True, direct=True)
        print("✓ Server started successfully")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_tapo_server())