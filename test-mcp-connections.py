#!/usr/bin/env python3
"""
Test MCP Server Connections for MyHomeServer
This script tests connectivity to all MCP servers that MyHomeServer integrates with.
"""

import asyncio
import httpx
import json
from datetime import datetime

# MCP Server configuration
MCP_SERVERS = {
    "tapo-camera": "http://localhost:7778",
    "tapo-energy": "http://localhost:7779",
    "tapo-lighting": "http://localhost:7780",
    "netatmo": "http://localhost:7781",
    "ring": "http://localhost:7782",
    "home-assistant": "http://localhost:7783",
    "local-llm": "http://localhost:7784",
}

async def test_mcp_server(server_name: str, server_url: str) -> dict:
    """Test connection to a single MCP server"""
    print(f"[TEST] Testing {server_name} at {server_url}...")

    start_time = datetime.now()

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            # Test health endpoint
            response = await client.get(f"{server_url}/health")
            response_time = (datetime.now() - start_time).total_seconds() * 1000

            if response.status_code == 200:
                try:
                    health_data = response.json()
                    return {
                        "name": server_name,
                        "url": server_url,
                        "status": "[OK] Connected",
                        "response_time": f"{response_time:.1f}ms",
                        "version": health_data.get("version", "unknown"),
                        "details": health_data,
                    }
                except:
                    return {
                        "name": server_name,
                        "url": server_url,
                        "status": "[OK] Connected",
                        "response_time": f"{response_time:.1f}ms",
                        "version": "unknown",
                        "details": "Health endpoint responded",
                    }
            else:
                return {
                    "name": server_name,
                    "url": server_url,
                    "status": f"[ERROR] HTTP {response.status_code}",
                    "response_time": f"{response_time:.1f}ms",
                    "version": None,
                    "details": f"HTTP {response.status_code} error",
                }

    except httpx.TimeoutException:
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return {
            "name": server_name,
            "url": server_url,
            "status": "[TIMEOUT] Timeout",
            "response_time": f"{response_time:.1f}ms",
            "version": None,
            "details": "Connection timeout after 5 seconds",
        }

    except Exception as e:
        response_time = (datetime.now() - start_time).total_seconds() * 1000
        return {
            "name": server_name,
            "url": server_url,
            "status": "[ERROR] Error",
            "response_time": f"{response_time:.1f}ms",
            "version": None,
            "details": str(e),
        }

async def test_myhome_server():
    """Test connection to MyHomeServer backend"""
    print("[TEST] Testing MyHomeServer backend...")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get("http://localhost:11111/health")
            if response.status_code == 200:
                health_data = response.json()
                print("  [OK] MyHomeServer Backend: Connected")
                print(f"    Version: {health_data.get('version', 'unknown')}")
                return True
            else:
                print(f"  [ERROR] MyHomeServer Backend: HTTP {response.status_code}")
                return False
    except Exception as e:
        print(f"  [ERROR] MyHomeServer Backend: {e}")
        return False

async def main():
    """Main test function"""
    print("MyHomeServer MCP Connection Test")
    print("=" * 50)

    # Test MyHomeServer backend first
    backend_ok = await test_myhome_server()
    print()

    # Test MCP servers
    print("Testing MCP Server Connections...")
    print()

    tasks = [test_mcp_server(name, url) for name, url in MCP_SERVERS.items()]
    results = await asyncio.gather(*tasks)

    # Display results
    connected_count = 0
    for result in results:
        status = result["status"]
        if "[OK]" in status:
            connected_count += 1
        print(f"  {result['name']:<15} {result['status']:<15} {result['response_time']:<8} {result.get('version', 'N/A')}")
        if "[ERROR]" in result["status"] or "[TIMEOUT]" in result["status"]:
            print(f"    Details: {result['details']}")

    print()
    print("=" * 50)
    print("Summary:")
    print(f"  MCP Servers: {connected_count}/{len(MCP_SERVERS)} connected")
    print(f"  MyHomeServer: {'[OK] Connected' if backend_ok else '[ERROR] Not connected'}")

    if connected_count == 0:
        print()
        print("To start MCP servers:")
        print("  cd ../tapo-camera-mcp && python -m tapo_camera_mcp.server")
        print("  cd ../ring-mcp && python -m ring_mcp.server")
        print("  cd ../home-assistant-mcp && python -m home_assistant_mcp.server")
        print("  # ... start other MCP servers as needed")

    if not backend_ok:
        print()
        print("To start MyHomeServer backend:")
        print("  cd backend && python start.py")

    print()
    print("Access MyHomeServer at: http://localhost:5173")
    print("API Documentation: http://localhost:11114/docs")

if __name__ == "__main__":
    asyncio.run(main())