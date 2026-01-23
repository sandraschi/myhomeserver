#!/usr/bin/env python3
"""
MCP Client Test Runner
Runs tests for MCP client functionality and device integration.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

async def test_mcp_client():
    """Test basic MCP client functionality."""
    print("Testing MCP Client...")

    try:
        from app.mcp.registry import initialize_mcp_registry, mcp_registry
        from app.mcp.client import mcp_manager

        # Initialize MCP registry
        await initialize_mcp_registry()

        print(f"Found {len(mcp_registry.servers)} MCP servers")

        # Test basic MCP manager functionality
        servers = await mcp_manager.list_all_servers()
        print(f"MCP manager found {len(servers)} servers")

        # Try to connect to first available server
        for server_name in servers.keys():
            try:
                print(f"Testing connection to {server_name}...")
                client = await mcp_manager.get_client(server_name)
                tools = await client.list_tools()
                print(f"  ✓ {server_name}: {len(tools)} tools available")
                break
            except Exception as e:
                print(f"  ✗ {server_name}: {str(e)}")

        print("[OK] MCP Client test completed")

    except Exception as e:
        print(f"[ERROR] MCP Client test failed: {e}")
        return False

    return True

async def test_api_endpoints():
    """Test MCP API endpoints."""
    print("\nTesting MCP API endpoints...")

    try:
        import httpx

        base_url = "http://localhost:11111"

        # Test servers endpoint
        response = await httpx.AsyncClient().get(f"{base_url}/api/v1/mcp/servers", timeout=10.0)
        if response.status_code == 200:
            servers = response.json()
            print(f"[OK] Found {len(servers)} servers via API")
        else:
            print(f"[ERROR] API test failed: {response.status_code}")
            return False

        # Test health endpoint
        response = await httpx.AsyncClient().get(f"{base_url}/api/v1/mcp/health", timeout=10.0)
        if response.status_code == 200:
            health = response.json()
            print(f"[OK] Health check: {health.get('status', 'unknown')}")
        else:
            print(f"[ERROR] Health check failed: {response.status_code}")

        print("[OK] MCP API test completed")

    except Exception as e:
        print(f"[ERROR] MCP API test failed: {e}")
        return False

    return True

async def main():
    """Run all MCP tests."""
    print("MyHomeServer MCP Client Tests")
    print("=" * 40)

    # Test MCP client
    client_test = await test_mcp_client()

    # Test API endpoints (requires backend running)
    try:
        api_test = await test_api_endpoints()
    except Exception:
        print("\n[WARNING] API tests skipped (backend not running)")
        print("   Start backend with: cd backend && python start.py")
        api_test = None

    print("\n" + "=" * 40)
    print("Test Results:")

    if client_test:
        print("[OK] MCP Client: PASSED")
    else:
        print("[ERROR] MCP Client: FAILED")

    if api_test is True:
        print("[OK] MCP API: PASSED")
    elif api_test is False:
        print("[ERROR] MCP API: FAILED")
    else:
        print("[WARNING] MCP API: SKIPPED")

    success = client_test and (api_test is not False)
    print(f"\nOverall: {'PASSED' if success else 'FAILED'}")

    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)