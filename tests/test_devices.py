#!/usr/bin/env python3
"""
Device Integration Tests for MyHomeServer MCP Client.
Tests connectivity and functionality with physical devices.
"""

import asyncio
import pytest
import logging
from typing import Dict, Any
from pathlib import Path

from backend.app.mcp.client import mcp_manager, MCPClient
from backend.app.mcp.registry import mcp_registry

logger = logging.getLogger(__name__)


class DeviceTestSuite:
    """Comprehensive device testing suite."""

    def __init__(self):
        self.test_results = {}
        self.devices = {
            "tapo_cameras": [
                {"name": "front_door", "expected_type": "tapo_camera"},
                {"name": "backyard", "expected_type": "tapo_camera"}
            ],
            "ring_cameras": [
                {"name": "doorbell_camera", "expected_type": "ring_camera"}
            ],
            "usb_cameras": [
                {"name": "webcam_1", "expected_type": "usb_camera"},
                {"name": "webcam_2", "expected_type": "usb_camera"}
            ],
            "tapo_plugs": [
                {"name": "coffee_maker", "expected_type": "smart_plug"},
                {"name": "tv", "expected_type": "smart_plug"},
                {"name": "computer", "expected_type": "smart_plug"}
            ],
            "tapo_lightstrip": [
                {"name": "desk_lightstrip", "expected_type": "lightstrip"}
            ],
            "hue_bridge": [
                {"name": "living_room_lights", "expected_type": "hue_bridge"}
            ],
            "nest_devices": [
                {"name": "thermostat", "expected_type": "nest_thermostat"},
                {"name": "smoke_detector", "expected_type": "nest_protect"}
            ],
            "netatmo_weatherstation": [
                {"name": "outdoor_weather", "expected_type": "weather_station"}
            ]
        }

    async def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive device tests."""
        logger.info("Starting comprehensive device testing...")

        results = {
            "summary": {},
            "device_tests": {},
            "mcp_server_tests": {},
            "integration_tests": {}
        }

        try:
            # Test MCP server connectivity
            results["mcp_server_tests"] = await self.test_mcp_servers()

            # Test individual devices
            results["device_tests"] = await self.test_devices()

            # Test device integration
            results["integration_tests"] = await self.test_device_integration()

            # Generate summary
            results["summary"] = self.generate_summary(results)

        except Exception as e:
            logger.error(f"Device testing failed: {e}")
            results["error"] = str(e)

        return results

    async def test_mcp_servers(self) -> Dict[str, Any]:
        """Test MCP server connectivity and health."""
        logger.info("Testing MCP server connectivity...")

        results = {}

        # Test Tapo Camera MCP
        try:
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")
            health = await mcp_manager.health_check("tapo-camera-mcp")
            tools = await tapo_client.list_tools()
            resources = await tapo_client.list_resources()

            results["tapo_camera_mcp"] = {
                "healthy": health,
                "tools_count": len(tools),
                "resources_count": len(resources),
                "tools": [t.name for t in tools],
                "status": "connected" if health else "unhealthy"
            }
        except Exception as e:
            results["tapo_camera_mcp"] = {"error": str(e), "status": "failed"}

        # Test Netatmo MCP
        try:
            netatmo_client = await mcp_manager.get_client("netatmo-weather-mcp")
            health = await mcp_manager.health_check("netatmo-weather-mcp")
            tools = await netatmo_client.list_tools()

            results["netatmo_weather_mcp"] = {
                "healthy": health,
                "tools_count": len(tools),
                "tools": [t.name for t in tools],
                "status": "connected" if health else "unhealthy"
            }
        except Exception as e:
            results["netatmo_weather_mcp"] = {"error": str(e), "status": "failed"}

        # Test Ring MCP server
        try:
            ring_client = await mcp_manager.get_client("ring-mcp")
            health = await mcp_manager.health_check("ring-mcp")
            tools = await ring_client.list_tools()

            results["ring_mcp"] = {
                "healthy": health,
                "tools_count": len(tools),
                "tools": [t.name for t in tools],
                "status": "connected" if health else "unhealthy"
            }
        except Exception as e:
            results["ring_mcp"] = {"error": str(e), "status": "failed"}

        # Test Home Assistant MCP server (Nest devices)
        try:
            ha_client = await mcp_manager.get_client("home-assistant-mcp")
            health = await mcp_manager.health_check("home-assistant-mcp")
            tools = await ha_client.list_tools()

            results["home_assistant_mcp"] = {
                "healthy": health,
                "tools_count": len(tools),
                "tools": [t.name for t in tools],
                "status": "connected" if health else "unhealthy"
            }
        except Exception as e:
            results["home_assistant_mcp"] = {"error": str(e), "status": "failed"}

        # Test other MCP servers
        for server_name in ["local-llm-mcp"]:
            try:
                health = await mcp_manager.health_check(server_name)
                results[server_name] = {
                    "healthy": health,
                    "status": "connected" if health else "unhealthy"
                }
            except Exception as e:
                results[server_name] = {"error": str(e), "status": "failed"}

        return results

    async def test_devices(self) -> Dict[str, Any]:
        """Test individual device connectivity and functionality."""
        logger.info("Testing individual devices...")

        results = {}

        # Test Tapo Cameras
        try:
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")

            # Try to list cameras
            camera_result = await tapo_client.call_tool("list_cameras", {})
            camera_list = camera_result.get("cameras", [])

            results["tapo_cameras"] = {
                "count": len(camera_list),
                "cameras": camera_list,
                "expected": len(self.devices["tapo_cameras"]),
                "status": "success" if len(camera_list) >= 2 else "partial"
            }

            # Test individual camera access
            for camera in camera_list[:2]:  # Test first 2 cameras
                camera_id = camera.get("id")
                try:
                    # Try to get camera stream (if available)
                    stream_result = await tapo_client.call_tool("get_camera_stream", {"camera_id": camera_id})
                    camera["stream_test"] = "success" if stream_result.get("stream_url") else "failed"
                except Exception as e:
                    camera["stream_test"] = f"error: {str(e)}"

        except Exception as e:
            results["tapo_cameras"] = {"error": str(e), "status": "failed"}

        # Test Ring Cameras
        try:
            ring_client = await mcp_manager.get_client("ring-mcp")

            # Try to list Ring devices (cameras, doorbells)
            ring_result = await ring_client.call_tool("list_devices", {})
            ring_devices = ring_result.get("devices", [])

            # Filter for cameras
            ring_cameras = [d for d in ring_devices if d.get("type") in ["doorbell", "camera"]]

            results["ring_cameras"] = {
                "count": len(ring_cameras),
                "cameras": ring_cameras,
                "expected": len(self.devices["ring_cameras"]),
                "status": "success" if len(ring_cameras) >= 1 else "not_found"
            }

            # Test individual Ring camera access
            for camera in ring_cameras[:1]:  # Test first camera
                camera_id = camera.get("id")
                try:
                    # Try to get camera live view or recent events
                    events_result = await ring_client.call_tool("get_recent_events", {"device_id": camera_id})
                    camera["events_test"] = "success" if events_result.get("events") is not None else "failed"
                except Exception as e:
                    camera["events_test"] = f"error: {str(e)}"

        except Exception as e:
            results["ring_cameras"] = {"error": str(e), "status": "failed"}

        # Test USB Cameras (these would need different MCP server)
        results["usb_cameras"] = {
            "status": "not_implemented",
            "note": "USB cameras require separate MCP server implementation",
            "expected": len(self.devices["usb_cameras"])
        }

        # Test Tapo Plugs
        try:
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")

            # Try to list energy devices
            energy_result = await tapo_client.call_tool("list_energy_devices", {})
            plug_list = energy_result.get("devices", [])

            results["tapo_plugs"] = {
                "count": len(plug_list),
                "plugs": plug_list,
                "expected": len(self.devices["tapo_plugs"]),
                "status": "success" if len(plug_list) >= 3 else "partial"
            }

            # Test individual plug control
            for plug in plug_list[:3]:  # Test first 3 plugs
                plug_id = plug.get("id")
                try:
                    # Try to get current status
                    status_result = await tapo_client.call_tool("get_device_status", {"device_id": plug_id})
                    plug["status_test"] = "success" if status_result.get("power") is not None else "failed"
                except Exception as e:
                    plug["status_test"] = f"error: {str(e)}"

        except Exception as e:
            results["tapo_plugs"] = {"error": str(e), "status": "failed"}

        # Test Tapo Lightstrip
        try:
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")

            # Lightstrip might be under energy devices or separate
            lightstrip_result = await tapo_client.call_tool("list_light_devices", {})
            light_devices = lightstrip_result.get("devices", [])

            results["tapo_lightstrip"] = {
                "count": len(light_devices),
                "lights": light_devices,
                "expected": len(self.devices["tapo_lightstrip"]),
                "status": "success" if len(light_devices) >= 1 else "not_found"
            }

        except Exception as e:
            results["tapo_lightstrip"] = {"error": str(e), "status": "failed"}

        # Test Hue Bridge (would need separate MCP server)
        results["hue_bridge"] = {
            "status": "not_implemented",
            "note": "Hue bridge requires separate MCP server implementation",
            "expected": len(self.devices["hue_bridge"])
        }

        # Test Netatmo Weather Station
        try:
            netatmo_client = await mcp_manager.get_client("netatmo-weather-mcp")

            # Try to get weather data
            weather_result = await netatmo_client.call_tool("get_current_weather", {})
            weather_data = weather_result.get("weather", {})

            results["netatmo_weatherstation"] = {
                "temperature": weather_data.get("temperature"),
                "humidity": weather_data.get("humidity"),
                "pressure": weather_data.get("pressure"),
                "status": "success" if weather_data.get("temperature") is not None else "no_data"
            }

        except Exception as e:
            results["netatmo_weatherstation"] = {"error": str(e), "status": "failed"}

        # Test Nest Devices (via Home Assistant MCP)
        try:
            ha_client = await mcp_manager.get_client("home-assistant-mcp")

            # Try to list all Home Assistant entities (includes Nest devices)
            entities_result = await ha_client.call_tool("list_entities", {})
            all_entities = entities_result.get("entities", [])

            # Filter for Nest devices
            nest_entities = [e for e in all_entities if "nest" in e.get("entity_id", "").lower()]

            results["nest_devices"] = {
                "count": len(nest_entities),
                "entities": nest_entities,
                "expected": len(self.devices["nest_devices"]),
                "status": "success" if len(nest_entities) >= 1 else "not_found"
            }

            # Test individual Nest device access
            for entity in nest_entities[:2]:  # Test first 2 entities
                entity_id = entity.get("entity_id")
                try:
                    # Try to get entity state
                    state_result = await ha_client.call_tool("get_entity_state", {"entity_id": entity_id})
                    entity["state_test"] = "success" if state_result.get("state") is not None else "failed"
                except Exception as e:
                    entity["state_test"] = f"error: {str(e)}"

        except Exception as e:
            results["nest_devices"] = {"error": str(e), "status": "failed"}

        return results

    async def test_device_integration(self) -> Dict[str, Any]:
        """Test device integration and cross-device functionality."""
        logger.info("Testing device integration...")

        results = {}

        try:
            # Test camera + energy correlation
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")

            # Get camera and energy data simultaneously
            cameras_task = tapo_client.call_tool("list_cameras", {})
            energy_task = tapo_client.call_tool("list_energy_devices", {})

            camera_result, energy_result = await asyncio.gather(cameras_task, energy_task)

            results["camera_energy_integration"] = {
                "cameras_found": len(camera_result.get("cameras", [])),
                "energy_devices_found": len(energy_result.get("devices", [])),
                "status": "success" if len(camera_result.get("cameras", [])) > 0 and len(energy_result.get("devices", [])) > 0 else "partial"
            }

        except Exception as e:
            results["camera_energy_integration"] = {"error": str(e), "status": "failed"}

        # Test weather + energy correlation (if available)
        try:
            netatmo_client = await mcp_manager.get_client("netatmo-weather-mcp")
            tapo_client = await mcp_manager.get_client("tapo-camera-mcp")

            weather_task = netatmo_client.call_tool("get_current_weather", {})
            energy_task = tapo_client.call_tool("get_energy_usage", {"period": "today"})

            weather_result, energy_result = await asyncio.gather(weather_task, energy_task)

            results["weather_energy_integration"] = {
                "weather_data": bool(weather_result.get("weather")),
                "energy_data": bool(energy_result.get("usage")),
                "status": "success" if weather_result.get("weather") and energy_result.get("usage") else "partial"
            }

        except Exception as e:
            results["weather_energy_integration"] = {"error": str(e), "status": "failed"}

        return results

    def generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        """Generate test summary."""
        summary = {
            "total_devices_tested": 0,
            "devices_working": 0,
            "devices_partial": 0,
            "devices_failed": 0,
            "mcp_servers_connected": 0,
            "mcp_servers_failed": 0
        }

        # Count MCP server status
        for server_result in results.get("mcp_server_tests", {}).values():
            if server_result.get("status") == "connected":
                summary["mcp_servers_connected"] += 1
            elif server_result.get("status") in ["failed", "unhealthy"]:
                summary["mcp_servers_failed"] += 1

        # Count device status
        device_category_count = 0
        for device_category, device_result in results.get("device_tests", {}).items():
            device_category_count += 1
            status = device_result.get("status", "unknown")

            if status == "success":
                summary["devices_working"] += 1
            elif status == "partial":
                summary["devices_partial"] += 1
            else:
                summary["devices_failed"] += 1

        summary["total_devices_tested"] = device_category_count

        return summary


async def run_device_tests():
    """Run the complete device test suite."""
    test_suite = DeviceTestSuite()
    results = await test_suite.run_all_tests()

    # Print summary
    print("\n" + "="*60)
    print("DEVICE TESTING SUMMARY")
    print("="*60)

    summary = results["summary"]
    print(f"Total Devices Tested: {summary['total_devices_tested']}")
    print(f"Devices Working: {summary['devices_working']}")
    print(f"Devices Partial: {summary['devices_partial']}")
    print(f"Devices Failed: {summary['devices_failed']}")
    print(f"MCP Servers Connected: {summary['mcp_servers_connected']}")
    print(f"MCP Servers Failed: {summary['mcp_servers_failed']}")

    # Print detailed results
    print("\nMCP SERVER STATUS:")
    for server_name, server_data in results["mcp_server_tests"].items():
        status = server_data.get("status", "unknown")
        healthy = "[OK]" if server_data.get("healthy", False) else "[ERROR]"
        print(f"  {server_name}: {status} {healthy}")

    print("\nDEVICE STATUS:")
    for device_name, device_data in results["device_tests"].items():
        status = device_data.get("status", "unknown")
        status_icon = {"success": "[OK]", "partial": "[PARTIAL]", "failed": "[ERROR]", "not_implemented": "[NOT_IMPLEMENTED]", "not_found": "[NOT_FOUND]"}
        icon = status_icon.get(status, "[?]")
        count = device_data.get("count", 0)
        expected = device_data.get("expected", "?")
        print(f"  {device_name}: {status} {icon} ({count}/{expected})")

    print("\nINTEGRATION STATUS:")
    integration_results = results.get("integration_tests", {})
    for integration_name, integration_data in integration_results.items():
        status = integration_data.get("status", "unknown")
        status_icon = {"success": "[OK]", "partial": "[PARTIAL]", "failed": "[ERROR]"}
        icon = status_icon.get(status, "[?]")
        print(f"  {integration_name}: {status} {icon}")

    return results


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Run tests
    asyncio.run(run_device_tests())