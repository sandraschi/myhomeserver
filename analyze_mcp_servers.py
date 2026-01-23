#!/usr/bin/env python3
"""
Analyze MCP servers discovered by MyHomeServer
"""

import json
import requests
from collections import Counter

def analyze_mcp_servers():
    """Analyze the MCP servers discovered by MyHomeServer"""

    # Get MCP servers data
    try:
        response = requests.get('http://localhost:10500/api/v1/mcp/servers', timeout=10)
        servers = response.json()
    except Exception as e:
        print(f"Failed to get MCP servers data: {e}")
        return

    print("TARGET MyHomeServer MCP Server Analysis")
    print("=" * 50)
    print(f"DATA Total MCP servers discovered: {len(servers)}")
    print()

    # Get categories
    categories = {server_data['category'] for server_data in servers.values()}
    print(f"LABELS Categories found: {sorted(categories)}")
    print()

    # Count servers by category
    category_counts = Counter(server_data['category'] for server_data in servers.values())
    print("CHART Server breakdown by category:")
    for category, count in sorted(category_counts.items()):
        print(f"   {category}: {count} servers")
    print()

    # Show key smart home servers
    smart_home_servers = {
        name: data for name, data in servers.items()
        if name in ['tapo-camera-mcp', 'ring-mcp', 'home-assistant-mcp', 'netatmo-weather-mcp']
    }

    if smart_home_servers:
        print("HOME Your Smart Home MCP Servers:")
        for name, data in smart_home_servers.items():
            status = "[READY]" if data.get('healthy', False) else "[NOT_RUNNING]"
            category = data.get('category', 'unknown')
            tools = data.get('tools_count', 0)
            resources = data.get('resources_count', 0)
            print(f"   * {name} ({category}): {status} - {tools} tools, {resources} resources")
        print()

    # Show some interesting servers
    interesting_servers = [
        ('blender-mcp', '3D modeling'),
        ('gimp-mcp', 'Image editing'),
        ('plex-mcp', 'Media server'),
        ('docker-mcp', 'Container management'),
        ('vrchat-mcp', 'VR social'),
        ('unity3d-mcp', 'Game development'),
        ('osc-mcp', 'Audio/MIDI'),
        ('email-mcp', 'Email processing'),
        ('reaper-mcp', 'Audio production'),
        ('calibre-mcp', 'E-book management')
    ]

    print("ROCKET Interesting MCP Servers Discovered:")
    for server_name, description in interesting_servers:
        if server_name in servers:
            data = servers[server_name]
            category = data.get('category', 'unknown')
            tools = data.get('tools_count', 0)
            print(f"   * {server_name} ({category}): {description} - {tools} tools")

if __name__ == "__main__":
    analyze_mcp_servers()