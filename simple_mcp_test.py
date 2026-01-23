#!/usr/bin/env python3
"""
Simple MCP Test - Send initialize and see if we get a response
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path

async def test_mcp_stdio():
    """Test basic MCP stdio communication"""

    # Start the MCP server
    tapo_path = Path("D:/Dev/repos/tapo-camera-mcp")
    env = {
        "PYTHONPATH": f"{tapo_path}/src:{tapo_path}:D:/Dev/repos/myhomeserver/src",
        **dict(os.environ)
    }

    print("Starting MCP server...")
    process = await asyncio.create_subprocess_exec(
        "python", "-m", "tapo_camera_mcp.cli_v2",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env=env,
        cwd=str(tapo_path)
    )

    print(f"MCP server started with PID: {process.pid}")

    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
                "resources": {},
                "prompts": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    print("Sending initialize request...")
    request_json = json.dumps(init_request) + "\n"
    process.stdin.write(request_json.encode())
    await process.stdin.drain()

    print("Waiting for response...")

    # Read response
    try:
        response_data = await asyncio.wait_for(process.stdout.readline(), timeout=10.0)
        response_str = response_data.decode().strip()
        print(f"Received response: {response_str}")

        try:
            response = json.loads(response_str)
            print("✅ Valid JSON response received!")
            print(f"Response: {response}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON response: {e}")
            return False

    except asyncio.TimeoutError:
        print("❌ Timeout waiting for response")

        # Check stderr
        stderr_data = await process.stderr.read()
        stderr_str = stderr_data.decode()
        if stderr_str:
            print(f"Stderr: {stderr_str}")

        return False

    finally:
        process.terminate()
        try:
            await asyncio.wait_for(process.wait(), timeout=5.0)
        except:
            process.kill()

if __name__ == "__main__":
    import os
    result = asyncio.run(test_mcp_stdio())
    print(f"Test {'PASSED' if result else 'FAILED'}")
    sys.exit(0 if result else 1)