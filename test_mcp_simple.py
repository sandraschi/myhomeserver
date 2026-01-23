#!/usr/bin/env python3
"""
Simple MCP Test - Direct server execution
"""

import asyncio
import subprocess
import json
import sys
from pathlib import Path

async def test_mcp_direct():
    """Test MCP server by running it directly and sending initialize"""

    tapo_path = Path("D:/Dev/repos/tapo-camera-mcp")

    # Start the server
    print("Starting MCP server...")
    proc = await asyncio.create_subprocess_exec(
        sys.executable, "-m", "tapo_camera_mcp.cli_v2",
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            "PYTHONPATH": f"{tapo_path}/src:{tapo_path}",
            **dict(os.environ)
        },
        cwd=str(tapo_path)
    )

    print(f"Server started with PID: {proc.pid}")

    # Wait a bit for server to initialize
    await asyncio.sleep(2)

    # Send initialize request
    init_msg = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-03-26",
            "capabilities": {
                "roots": {
                    "listChanged": True
                },
                "sampling": {}
            },
            "clientInfo": {
                "name": "test-client",
                "version": "1.0.0"
            }
        }
    }

    print("Sending initialize request...")
    request_json = json.dumps(init_msg) + "\n"
    proc.stdin.write(request_json.encode())
    await proc.stdin.drain()

    print("Waiting for response...")

    try:
        # Read response
        response_data = await asyncio.wait_for(proc.stdout.readline(), timeout=5.0)
        response_str = response_data.decode().strip()
        print(f"Received: {response_str}")

        try:
            response = json.loads(response_str)
            print("✅ Valid JSON-RPC response!")
            print(f"Response: {response}")
            return True
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON: {e}")
            return False

    except asyncio.TimeoutError:
        print("❌ Timeout - no response")

        # Check stderr
        try:
            stderr_data = await proc.stderr.read()
            stderr_str = stderr_data.decode()
            if stderr_str.strip():
                print(f"Server stderr: {stderr_str}")
        except:
            pass

        return False

    finally:
        proc.terminate()
        try:
            await asyncio.wait_for(proc.wait(), timeout=2.0)
        except:
            proc.kill()

if __name__ == "__main__":
    import os
    result = asyncio.run(test_mcp_direct())
    print(f"Test result: {'PASS' if result else 'FAIL'}")
    sys.exit(0 if result else 1)