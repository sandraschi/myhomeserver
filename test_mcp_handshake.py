#!/usr/bin/env python3
"""
Test MCP Handshake Completion
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent / "backend"))

from backend.app.mcp.client import MCPClient

async def test_mcp_handshake():
    """Test if MCP handshake completes"""
    print("Testing MCP handshake completion...")

    # Test with Tapo camera MCP
    tapo_path = Path("D:/Dev/repos/tapo-camera-mcp")

    client = MCPClient(
        server_name="tapo-camera-mcp",
        server_command=["python", "-m", "tapo_camera_mcp.cli_v2"],
        working_directory=str(tapo_path)
    )

    try:
        print("Starting MCP server...")
        await client.start_server()

        print("Waiting for handshake to complete...")
        await asyncio.sleep(5)  # Wait for handshake

        if client.initialized:
            print("✅ MCP handshake completed successfully!")
            print(f"Server info: {client.server_info}")
            print(f"Available tools: {len(client.available_tools)}")
            print(f"Available resources: {len(client.available_resources)}")
            print(f"Available prompts: {len(client.available_prompts)}")
            return True
        else:
            print("❌ MCP handshake did not complete")
            return False

    except Exception as e:
        print(f"❌ MCP handshake failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        await client.stop_server()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    result = asyncio.run(test_mcp_handshake())
    sys.exit(0 if result else 1)