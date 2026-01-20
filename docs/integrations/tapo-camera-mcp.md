# Tapo Camera MCP Integration

## 🎥 Overview

The Tapo Camera MCP server provides comprehensive camera management and smart energy monitoring capabilities. It integrates with TP-Link Tapo cameras and smart plugs, offering real-time video streaming, PTZ controls, motion detection, and energy analytics.

**Repository**: `d:\Dev\repos\tapo-camera-mcp`
**Primary Use**: Cameras and Energy monitoring in MyHomeServer

## 🔧 Features

### Camera Management
- **Live Video Streaming**: Real-time camera feeds with adaptive quality
- **PTZ Controls**: Pan, tilt, zoom functionality for supported cameras
- **Motion Detection**: AI-powered motion alerts and event recording
- **Recording Management**: View, download, and manage recorded footage
- **Multi-Camera Support**: Handle multiple cameras simultaneously

### Energy Monitoring
- **Smart Plug Control**: On/off control of TP-Link smart plugs
- **Real-time Energy Data**: Live power consumption monitoring
- **Historical Analytics**: Energy usage trends and cost calculations
- **Device Scheduling**: Automated power scheduling and routines
- **Multi-Device Support**: Manage multiple energy devices

## 🏗️ Architecture Integration

### MyHomeServer Usage

```typescript
// frontend/src/services/cameraService.ts
import { apiClient } from './apiClient';

export const cameraService = {
  async getCameras() {
    return apiClient.get('/api/cameras');
  },

  async getCameraStream(cameraId: string) {
    return apiClient.get(`/api/cameras/${cameraId}/stream`);
  },

  async controlPTZ(cameraId: string, command: PTZCommand) {
    return apiClient.post(`/api/cameras/${cameraId}/ptz`, command);
  }
};

// frontend/src/services/energyService.ts
export const energyService = {
  async getDevices() {
    return apiClient.get('/api/energy/devices');
  },

  async getUsage() {
    return apiClient.get('/api/energy/usage');
  },

  async controlDevice(deviceId: string, action: 'on' | 'off') {
    return apiClient.post(`/api/energy/${deviceId}/control`, { action });
  }
};
```

### Backend Proxy Implementation

```python
# backend/api/routes/camera.py
from fastapi import APIRouter, HTTPException
from ..services.mcp_client import TapoMcpClient

router = APIRouter()
tapo_client = TapoMcpClient("http://localhost:7778")  # Tapo MCP server URL

@router.get("/cameras")
async def get_cameras():
    """Get all cameras from Tapo MCP"""
    try:
        cameras = await tapo_client.get_cameras()
        return {"cameras": cameras}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Tapo MCP unavailable: {e}")

@router.get("/cameras/{camera_id}/stream")
async def get_camera_stream(camera_id: str):
    """Get camera stream URL"""
    try:
        stream_url = await tapo_client.get_stream_url(camera_id)
        return {"stream_url": stream_url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Camera {camera_id} not found")

@router.post("/cameras/{camera_id}/ptz")
async def control_ptz(camera_id: str, command: dict):
    """Control camera PTZ"""
    try:
        result = await tapo_client.ptz_control(camera_id, command)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"PTZ control failed: {e}")
```

## 🔗 API Endpoints

### Camera Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/cameras` | List all cameras |
| GET | `/api/cameras/{id}` | Get camera details |
| GET | `/api/cameras/{id}/stream` | Get stream URL |
| POST | `/api/cameras/{id}/ptz` | Control PTZ movement |
| GET | `/api/cameras/{id}/recordings` | Get recordings |
| POST | `/api/cameras/{id}/snapshot` | Take snapshot |

### Energy Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/energy/devices` | List energy devices |
| GET | `/api/energy/usage` | Current energy usage |
| POST | `/api/energy/{id}/control` | Control device power |
| GET | `/api/energy/history` | Historical usage data |
| GET | `/api/energy/costs` | Energy cost calculations |

## ⚙️ Configuration

### MyHomeServer Backend Configuration

```yaml
# config.yaml
mcp_servers:
  tapo_camera:
    url: "http://localhost:7778"
    timeout: 30
    retry_attempts: 3
    health_check_interval: 60

cameras:
  living_room:
    type: onvif
    params:
      host: "192.168.0.100"
      username: "your_username"
      password: "your_password"
  kitchen:
    type: tapo
    params:
      device_id: "kitchen_camera"
      cloud_password: "your_cloud_password"

energy:
  devices:
    aircon:
      host: "192.168.0.101"
      device_id: "aircon_plug"
    kitchen:
      host: "192.168.0.102"
      device_id: "kitchen_plug"
```

### Tapo MCP Server Requirements

Ensure the Tapo MCP server is running with:

```bash
# In d:\Dev\repos\tapo-camera-mcp
python -m tapo_camera_mcp.server --host 0.0.0.0 --port 7778
```

## 🔄 Data Flow

```
MyHomeServer Frontend
        │
        ▼
FastAPI Backend (MyHomeServer)
        │
        ▼ (HTTP/JSON)
Tapo Camera MCP Server
        │
        ▼ (Tapo API)
TP-Link Tapo Devices
        ├── Cameras
        └── Smart Plugs
```

## 📊 Data Models

### Camera Object
```typescript
interface Camera {
  id: string;
  name: string;
  type: 'tapo' | 'onvif';
  status: 'online' | 'offline' | 'error';
  capabilities: {
    ptz: boolean;
    audio: boolean;
    nightVision: boolean;
    motionDetection: boolean;
  };
  streamUrl?: string;
  lastSeen: Date;
  location: string;
}
```

### Energy Device Object
```typescript
interface EnergyDevice {
  id: string;
  name: string;
  type: 'smart_plug' | 'smart_strip';
  status: 'online' | 'offline';
  power: number;        // Current power in watts
  voltage: number;      // Current voltage
  current: number;      // Current in amps
  todayKwh: number;     // Today's energy usage
  monthKwh: number;     // Monthly energy usage
  isOn: boolean;        // Power state
  location: string;
}
```

## 🛡️ Error Handling

### Common Error Scenarios

1. **MCP Server Unavailable**
   - **Detection**: Health check failures
   - **Handling**: Graceful fallback to cached data
   - **User Impact**: Shows last known status with warning

2. **Camera Offline**
   - **Detection**: Connection timeout or API errors
   - **Handling**: Mark as offline, show last snapshot
   - **User Impact**: Clear offline indicator, retry option

3. **Energy Device Unresponsive**
   - **Detection**: Failed control commands
   - **Handling**: Retry with exponential backoff
   - **User Impact**: Temporary unresponsiveness message

### Circuit Breaker Implementation

```python
# Automatic failure handling
circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    timeout=300  # 5 minutes
)

@circuit_breaker
async def get_camera_feed(camera_id: str):
    return await tapo_client.get_stream(camera_id)
```

## 📈 Performance Considerations

### Optimization Strategies

1. **Stream Caching**: Cache stream URLs for 5-10 minutes
2. **Thumbnail Generation**: Pre-generate camera thumbnails
3. **Batch Requests**: Group multiple device status requests
4. **Connection Pooling**: Reuse HTTP connections to MCP server

### Expected Performance

- **Camera List Load**: <500ms
- **Stream URL Retrieval**: <200ms (cached), <2s (fresh)
- **PTZ Control Response**: <300ms
- **Energy Data Updates**: <100ms (real-time)

## 🔧 Troubleshooting

### Common Issues

1. **"Camera not found" errors**
   - Check camera configuration in config.yaml
   - Verify camera is powered on and connected
   - Ensure correct IP address and credentials

2. **Stream loading failures**
   - Check network connectivity to camera
   - Verify camera supports streaming format
   - Check firewall settings for streaming ports

3. **Energy device control failures**
   - Verify device is connected to WiFi
   - Check Tapo app connectivity
   - Ensure device firmware is up to date

### Debug Commands

```bash
# Test MCP server connectivity
curl http://localhost:7778/health

# Test camera discovery
curl http://localhost:7778/api/cameras

# Check energy device status
curl http://localhost:7778/api/energy/devices
```

## 🚀 Future Enhancements

### Planned Features
- **AI-powered motion detection**: Advanced person/vehicle recognition
- **Automated recording rules**: Smart recording based on AI analysis
- **Energy optimization**: AI-powered usage optimization suggestions
- **Multi-camera synchronization**: Coordinated PTZ movements
- **Advanced analytics**: Usage patterns and predictive maintenance

### Integration Opportunities
- **Home Assistant**: Direct integration with HA entities
- **Google Home/Assistant**: Voice control integration
- **IFTTT/Webhooks**: Custom automation triggers
- **Storage integration**: Cloud backup and archiving

## 📚 Related Documentation

- [Efficient MCP Usage Guide](../efficient-mcp-usage.md)
- [MyHomeServer PRD](../../PRD.md)
- [Tapo Camera MCP README](../../../../tapo-camera-mcp/README.md)

This integration provides the foundation for camera and energy management in MyHomeServer, leveraging the robust Tapo Camera MCP server for reliable device control and monitoring.