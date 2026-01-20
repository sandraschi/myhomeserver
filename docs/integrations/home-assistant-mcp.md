# Home Assistant MCP Integration

## 🏠 Overview

The Home Assistant MCP server provides comprehensive smart home integration with Nest devices and other Home Assistant entities. It enables centralized control of thermostats, security cameras, sensors, and automation routines within MyHomeServer.

**Repository**: `d:\Dev\repos\home-assistant-mcp`
**Primary Use**: Smart home hub and Nest device integration in MyHomeServer

## 🔧 Features

### Climate Control
- **Thermostat Management**: Temperature control and scheduling
- **HVAC Monitoring**: Real-time energy usage and efficiency
- **Zone Control**: Multi-zone temperature management
- **Weather Integration**: Outdoor temperature compensation

### Security Integration
- **Nest Cam Control**: Live video streaming and recording
- **Motion Detection**: AI-powered security alerts
- **Occupancy Sensing**: Presence detection and automation
- **Smart Locks**: Access control and monitoring

### Device Automation
- **Scene Control**: Pre-configured lighting and comfort scenes
- **Routine Management**: Time-based and trigger-based automations
- **Device Groups**: Organized control of multiple devices
- **Energy Optimization**: Smart scheduling based on usage patterns

## 🏗️ Architecture Integration

### MyHomeServer Usage

```typescript
// frontend/src/services/smartHomeService.ts
import { apiClient } from './apiClient';

export const smartHomeService = {
  async getDevices() {
    return apiClient.get('/api/hass/devices');
  },

  async getClimateStatus() {
    return apiClient.get('/api/hass/climate');
  },

  async setTemperature(deviceId: string, temperature: number) {
    return apiClient.post(`/api/hass/climate/${deviceId}`, {
      temperature,
      mode: 'heat'
    });
  },

  async controlScene(sceneId: string, action: 'activate' | 'deactivate') {
    return apiClient.post(`/api/hass/scene/${sceneId}`, { action });
  },

  async getSecurityStatus() {
    return apiClient.get('/api/hass/security');
  }
};
```

### Backend Proxy Implementation

```python
# backend/api/routes/hass.py
from fastapi import APIRouter, HTTPException
from ..services.mcp_client import HassMcpClient

router = APIRouter()
hass_client = HassMcpClient("http://localhost:7784")  # Home Assistant MCP server URL

@router.get("/hass/devices")
async def get_hass_devices():
    """Get all Home Assistant devices"""
    try:
        devices = await hass_client.get_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Home Assistant MCP unavailable: {e}")

@router.get("/hass/climate")
async def get_climate_status():
    """Get climate control status"""
    try:
        climate_data = await hass_client.get_climate_devices()
        return {"climate": climate_data}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Climate data unavailable: {e}")

@router.post("/hass/climate/{device_id}")
async def set_climate(device_id: str, settings: dict):
    """Control climate device"""
    try:
        result = await hass_client.set_climate(device_id, settings)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Climate control failed: {e}")

@router.post("/hass/scene/{scene_id}")
async def control_scene(scene_id: str, action: str):
    """Control Home Assistant scene"""
    try:
        result = await hass_client.control_scene(scene_id, action)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Scene control failed: {e}")
```

## 🔗 API Endpoints

### Device Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hass/devices` | List all HA devices |
| GET | `/api/hass/devices/{id}` | Get device details |
| POST | `/api/hass/devices/{id}` | Control device |
| GET | `/api/hass/devices/{id}/history` | Device state history |

### Climate Control

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hass/climate` | Get climate devices |
| GET | `/api/hass/climate/{id}` | Get thermostat status |
| POST | `/api/hass/climate/{id}` | Set temperature/mode |
| GET | `/api/hass/climate/{id}/schedule` | Get temperature schedule |

### Scenes & Automation

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hass/scenes` | List available scenes |
| POST | `/api/hass/scenes/{id}` | Activate/deactivate scene |
| GET | `/api/hass/automations` | List automation rules |
| POST | `/api/hass/automations/{id}` | Control automation |

### Security & Sensors

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/hass/security` | Security system status |
| GET | `/api/hass/cameras` | Security cameras |
| GET | `/api/hass/sensors` | Sensor readings |
| POST | `/api/hass/security/alarm` | Control alarm system |

## ⚙️ Configuration

### MyHomeServer Backend Configuration

```yaml
# config.yaml
mcp_servers:
  home_assistant:
    url: "http://localhost:7784"
    timeout: 30
    retry_attempts: 3
    health_check_interval: 60

home_assistant:
  url: "http://homeassistant.local:8123"
  access_token: "your_long_lived_access_token"
  verify_ssl: true

  # Device mappings and preferences
  devices:
    nest_thermostat:
      entity_id: "climate.nest_thermostat"
      friendly_name: "Living Room Thermostat"
      location: "Living Room"
      preferred_unit: "celsius"

    nest_camera_living:
      entity_id: "camera.nest_living_room"
      friendly_name: "Living Room Camera"
      location: "Living Room"
      recording_enabled: true

    nest_protect_hallway:
      entity_id: "binary_sensor.nest_protect_hallway"
      friendly_name: "Hallway Smoke Detector"
      location: "Hallway"
      alert_on_smoke: true
      alert_on_co: true

  # Scene configurations
  scenes:
    morning_routine:
      scene_id: "scene.morning_routine"
      friendly_name: "Good Morning"
      description: "Open blinds, start coffee, adjust temperature"

    away_mode:
      scene_id: "scene.away_mode"
      friendly_name: "Away Mode"
      description: "Security on, temperature down, lights off"

  # Automation preferences
  automations:
    enabled: true
    auto_create_scenes: true
    energy_optimization: true
    security_integration: true
```

### Home Assistant MCP Server Requirements

Ensure the Home Assistant MCP server is running with:

```bash
# In d:\Dev\repos\home-assistant-mcp
python -m hass_mcp.server --host 0.0.0.0 --port 7784
```

## 🔄 Data Flow

```
MyHomeServer Frontend
        │
        ▼
FastAPI Backend (MyHomeServer)
        │
        ▼ (HTTP/JSON)
Home Assistant MCP Server
        │
        ▼ (WebSocket/REST)
Home Assistant Core
        ├── Nest Thermostat
        ├── Nest Cameras
        ├── Smart Lights
        ├── Sensors
        ├── Automations
        └── Scenes
```

## 📊 Data Models

### Home Assistant Device Object
```typescript
interface HassDevice {
  id: string;
  entityId: string;
  name: string;
  type: 'climate' | 'camera' | 'light' | 'switch' | 'sensor' | 'scene';
  domain: string;  // 'climate', 'camera', 'light', etc.
  location: string;
  status: 'on' | 'off' | 'unavailable' | 'unknown';

  attributes: {
    // Climate-specific
    temperature?: number;
    targetTemperature?: number;
    humidity?: number;
    hvacMode?: 'off' | 'heat' | 'cool' | 'auto';
    presetMode?: string;

    // Camera-specific
    streamUrl?: string;
    recordingEnabled?: boolean;

    // Sensor-specific
    unitOfMeasurement?: string;
    deviceClass?: string;
    stateClass?: string;

    // Light-specific
    brightness?: number;
    colorTemp?: number;
    rgbColor?: [number, number, number];
  };

  lastUpdated: Date;
  lastChanged: Date;
}
```

### Climate Device Object
```typescript
interface ClimateDevice extends HassDevice {
  type: 'climate';

  climateAttributes: {
    currentTemperature: number;
    targetTemperature: number;
    targetTemperatureHigh?: number;
    targetTemperatureLow?: number;
    maxTemp: number;
    minTemp: number;
    temperatureStep: number;

    currentHumidity?: number;
    targetHumidity?: number;

    hvacMode: 'off' | 'heat' | 'cool' | 'heat_cool' | 'auto' | 'dry' | 'fan_only';
    hvacAction?: 'off' | 'heating' | 'cooling' | 'drying' | 'fan' | 'preheating';

    presetMode?: string;
    presetModes?: string[];

    fanMode?: string;
    fanModes?: string[];

    swingMode?: string;
    swingModes?: string[];
  };

  capabilities: {
    targetTemperature: boolean;
    targetTemperatureRange: boolean;
    targetHumidity: boolean;
    fanMode: boolean;
    presetMode: boolean;
    swingMode: boolean;
  };
}
```

### Scene Object
```typescript
interface HassScene {
  id: string;
  entityId: string;
  name: string;
  description?: string;
  status: 'on' | 'off';

  metadata: {
    createdBy: string;
    lastActivated?: Date;
    activationCount: number;
    devices: string[];  // Entity IDs affected by this scene
  };

  attributes: {
    // Scene-specific attributes
    friendlyName: string;
    icon?: string;
    area?: string;
  };
}
```

## 🛡️ Error Handling

### Common Error Scenarios

1. **Home Assistant Unreachable**
   - **Detection**: Connection timeouts, DNS failures
   - **Handling**: Circuit breaker, cached data fallback
   - **User Impact**: Shows last known state with offline indicator

2. **Device State Sync Issues**
   - **Detection**: State desynchronization between HA and MCP
   - **Handling**: Periodic state reconciliation, conflict resolution
   - **User Impact**: Manual refresh option, conflict notifications

3. **Authentication Failures**
   - **Detection**: 401/403 responses, token expiration
   - **Handling**: Token refresh, re-authentication workflow
   - **User Impact**: Clear error messages with recovery steps

4. **Scene/Automation Conflicts**
   - **Detection**: Multiple automations triggering simultaneously
   - **Handling**: Priority-based execution, conflict logging
   - **User Impact**: Status indicators for automation conflicts

### State Synchronization

```python
# backend/services/state_sync.py
class HassStateSync:
    def __init__(self, hass_client: HassMcpClient):
        self.client = hass_client
        self.last_sync = {}
        self.sync_interval = 30  # seconds

    async def sync_device_states(self):
        """Synchronize device states between HA and MyHomeServer"""
        try:
            # Get current states from Home Assistant
            ha_states = await self.client.get_all_states()

            # Compare with cached states
            changes = self._detect_changes(ha_states)

            if changes:
                # Update cache and notify subscribers
                await self._update_cache(changes)
                await self._notify_subscribers(changes)

        except Exception as e:
            logger.error(f"State sync failed: {e}")
            # Continue with cached data

    def _detect_changes(self, new_states: dict) -> list:
        """Detect state changes"""
        changes = []
        for entity_id, new_state in new_states.items():
            old_state = self.last_sync.get(entity_id)
            if old_state != new_state:
                changes.append({
                    'entity_id': entity_id,
                    'old_state': old_state,
                    'new_state': new_state,
                    'timestamp': datetime.now()
                })
        return changes
```

## 📈 Performance Considerations

### Optimization Strategies

1. **WebSocket Subscriptions**: Real-time updates for critical devices
2. **Selective Polling**: Different polling intervals based on device type
3. **State Caching**: Cache device states with TTL-based invalidation
4. **Batch Operations**: Group multiple device commands into single requests

### Device-Specific Optimizations

- **Climate Devices**: Poll every 30 seconds, WebSocket for temperature changes
- **Cameras**: Lazy loading of streams, cache snapshot thumbnails
- **Lights/Switches**: Immediate response, optimistic UI updates
- **Sensors**: Poll every 5 minutes, aggregate readings

### Expected Performance

- **Device List Load**: <500ms
- **State Updates**: <200ms for local changes, <2s for HA round-trip
- **Scene Activation**: <300ms
- **Bulk Operations**: <1s for up to 10 devices
- **Historical Data**: <1s for 24h, <3s for 7 days

## 🔧 Troubleshooting

### Common Issues

1. **"Home Assistant connection failed"**
   - Verify HA URL and access token in config
   - Check HA server connectivity and SSL certificates
   - Ensure long-lived access token is valid

2. **"Device not responding"**
   - Check device connectivity in HA dashboard
   - Verify device is not excluded from MCP integration
   - Check HA logs for device-specific errors

3. **"Scene activation failed"**
   - Verify scene exists and is properly configured in HA
   - Check for conflicting automations
   - Review HA automation logs

4. **"State synchronization issues"**
   - Clear MCP cache and force resync
   - Check HA WebSocket connection stability
   - Verify entity IDs are consistent

### Debug Commands

```bash
# Test MCP server health
curl http://localhost:7784/health

# List HA devices
curl http://localhost:7784/api/devices

# Test climate control
curl http://localhost:7784/api/climate

# Check scene activation
curl -X POST http://localhost:7784/api/scenes/scene.morning_routine \
  -H "Content-Type: application/json" \
  -d '{"action": "activate"}'
```

## 🚀 Future Enhancements

### Planned Features
- **Advanced Automation Builder**: Visual automation creation
- **Energy Analytics**: Detailed consumption analysis and optimization
- **Predictive Maintenance**: AI-powered device health monitoring
- **Multi-Home Support**: Manage multiple HA instances
- **Voice Integration**: Natural language device control

### Integration Opportunities
- **Google Home/Assistant**: Enhanced voice control
- **Apple HomeKit**: iOS device integration
- **Matter Protocol**: Direct device connectivity
- **Thread/Zigbee**: Mesh network management
- **Solar Integration**: Energy production monitoring

## 📚 Related Documentation

- [Efficient MCP Usage Guide](../efficient-mcp-usage.md)
- [MyHomeServer PRD](../../PRD.md)
- [Home Assistant MCP README](../../../../home-assistant-mcp/README.md)

This integration transforms MyHomeServer into a comprehensive smart home control center, leveraging Home Assistant's robust automation platform for seamless device management and intelligent home control.