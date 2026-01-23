#!/usr/bin/env python3
"""
Manual MCP debugging - run server and send messages manually
"""

import subprocess
import json
import time
import sys
from pathlib import Path

def main():
    tapo_path = Path("D:/Dev/repos/tapo-camera-mcp")

    print("Starting MCP server manually...")
    proc = subprocess.Popen(
        [sys.executable, "-m", "tapo_camera_mcp.cli_v2"],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        env={
            "PYTHONPATH": f"{tapo_path}/src:{tapo_path}",
            **dict(os.environ)
        },
        cwd=str(tapo_path),
        text=True,  # Use text mode
        bufsize=0  # Unbuffered
    )

    print(f"Server started with PID: {proc.pid}")

    # Wait a bit for server to initialize
    time.sleep(3)

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

    request_json = json.dumps(init_msg) + "\n"
    print(f"Sending: {request_json.strip()}")

    try:
        # Send request
        proc.stdin.write(request_json)
        proc.stdin.flush()
        print("Request sent, waiting for response...")

        # Read response
        response = proc.stdout.readline()
        if response:
            print(f"Received: {response.strip()}")
            try:
                parsed = json.loads(response.strip())
                print(f"Parsed response: {parsed}")
            except json.JSONDecodeError as e:
                print(f"Invalid JSON: {e}")
        else:
            print("No response received")

        # Check stderr
        stderr_output = proc.stderr.read()
        if stderr_output:
            print(f"Stderr: {stderr_output}")

    except Exception as e:
        print(f"Error: {e}")

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except:
            proc.kill()

if __name__ == "__main__":
    main()