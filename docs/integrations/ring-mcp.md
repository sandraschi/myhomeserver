# Ring MCP Integration

## 🔔 Overview

The Ring MCP server provides comprehensive security and access control integration for Ring doorbells and cameras. It enables live video streaming, motion detection, doorbell control, and security event management within MyHomeServer.

**Repository**: `d:\Dev\repos\ring-mcp`
**Primary Use**: Security monitoring and access control in MyHomeServer

## 🔧 Features

### Doorbell & Camera Control
- **Live Video Streaming**: Real-time doorbell and security camera feeds
- **Two-Way Audio**: Speak to visitors through doorbell speakers
- **Motion Detection**: AI-powered motion alerts and event recording
- **Doorbell History**: Complete call log with answered/missed events
- **Snapshot Capture**: Take photos remotely

### Security Management
- **Event Timeline**: Chronological security event log
- **Device Status Monitoring**: Battery levels, connectivity, signal strength
- **Geofencing**: Location-based security settings
- **Emergency Controls**: Panic buttons and emergency contact alerts

### Integration Capabilities
- **Push Notifications**: Real-time alerts for doorbell rings and motion
- **Video Storage**: Access to Ring's cloud storage
- **Device Groups**: Organize multiple Ring devices
- **Shared Access**: Family member access controls

## 🏗️ Architecture Integration

### MyHomeServer Usage

```typescript
// frontend/src/services/securityService.ts
import { apiClient } from './apiClient';

export const securityService = {
  async getDevices() {
    return apiClient.get('/api/security/devices');
  },

  async getEvents(limit: number = 50) {
    return apiClient.get(`/api/security/events?limit=${limit}`);
  },

  async getLiveStream(deviceId: string) {
    return apiClient.get(`/api/security/${deviceId}/stream`);
  },

  async answerCall(deviceId: string) {
    return apiClient.post(`/api/security/${deviceId}/answer`);
  },

  async speakToVisitor(deviceId: string, message: string) {
    return apiClient.post(`/api/security/${deviceId}/speak`, { message });
  }
};
```

### Backend Proxy Implementation

```python
# backend/api/routes/security.py
from fastapi import APIRouter, HTTPException
from ..services.mcp_client import RingMcpClient

router = APIRouter()
ring_client = RingMcpClient("http://localhost:7782")  # Ring MCP server URL

@router.get("/security/devices")
async def get_security_devices():
    """Get all Ring security devices"""
    try:
        devices = await ring_client.get_devices()
        return {"devices": devices}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ring MCP unavailable: {e}")

@router.get("/security/events")
async def get_security_events(limit: int = 50):
    """Get security events timeline"""
    try:
        events = await ring_client.get_events(limit=limit)
        return {"events": events}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Events unavailable: {e}")

@router.get("/security/{device_id}/stream")
async def get_live_stream(device_id: str):
    """Get live stream URL for device"""
    try:
        stream_url = await ring_client.get_stream_url(device_id)
        return {"stream_url": stream_url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=f"Device {device_id} not found")

@router.post("/security/{device_id}/speak")
async def speak_to_visitor(device_id: str, message: str):
    """Send audio message through doorbell"""
    try:
        result = await ring_client.speak(device_id, message)
        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Speak command failed: {e}")
```

## 🔗 API Endpoints

### Device Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/security/devices` | List all Ring devices |
| GET | `/api/security/devices/{id}` | Get device details |
| GET | `/api/security/devices/{id}/health` | Device health status |

### Event Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/security/events` | Get security events |
| GET | `/api/security/events/{id}` | Get specific event |
| DELETE | `/api/security/events/{id}` | Delete event |

### Live Features

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/security/{id}/stream` | Get live stream URL |
| POST | `/api/security/{id}/answer` | Answer doorbell call |
| POST | `/api/security/{id}/speak` | Send audio message |
| POST | `/api/security/{id}/snapshot` | Take snapshot |

## ⚙️ Configuration

### MyHomeServer Backend Configuration

```yaml
# config.yaml
mcp_servers:
  ring:
    url: "http://localhost:7782"
    timeout: 45  # Longer timeout for video operations
    retry_attempts: 2
    health_check_interval: 300  # Less frequent for battery devices

security:
  ring:
    email: "your_ring_email@example.com"
    password: "your_ring_password"
    token_file: "ring_token.cache"
    two_factor_auth: true

    devices:
      front_door:
        device_id: "front_door_bell"
        location: "Front Door"
        type: "doorbell"
      backyard:
        device_id: "backyard_camera"
        location: "Backyard"
        type: "camera"

    notifications:
      enabled: true
      pushover_token: "your_pushover_token"  # Optional
      email_alerts: true
      motion_zones: true

    recording:
      auto_save: true
      retention_days: 30
      cloud_backup: true
```

### Ring MCP Server Requirements

**Auto-Start Configuration**: The Ring MCP server is automatically started by MyHomeServer backend via stdio subprocess. No manual server startup required.

**Manual Testing** (if needed):
```bash
# In d:\Dev\repos\ring-mcp
python -m ring_mcp
```

**MCP Client Integration**: MyHomeServer automatically:
- Discovers Ring MCP server in workspace
- Starts server as subprocess with stdio pipes
- Completes MCP handshake (initialize → initialized notification)
- Discovers 18 available tools
- Caches server capabilities for performance

## 🔄 Data Flow

```
MyHomeServer Frontend
        │
        ▼
FastAPI Backend (MyHomeServer)
        │
        ▼ (stdio JSON-RPC)
Ring MCP Server (subprocess)
        │
        ▼ (Ring API)
Ring Devices & Services
        ├── Doorbell Pro
        ├── Video Doorbell
        ├── Stick Up Cam
        ├── Floodlight Cam
        └── Security System
```

**Status**: ✅ **FULLY OPERATIONAL** (2026-01-23)
- MCP handshake complete
- 18 tools discovered and available
- Server auto-starts on backend initialization
- Full stdio JSON-RPC communication working

## 📊 Data Models

### Security Device Object
```typescript
interface SecurityDevice {
  id: string;
  name: string;
  type: 'doorbell' | 'camera' | 'stickup_cam' | 'floodlight';
  model: string;
  location: string;
  status: 'online' | 'offline' | 'error';

  capabilities: {
    liveView: boolean;
    twoWayAudio: boolean;
    motionDetection: boolean;
    nightVision: boolean;
    siren: boolean;
  };

  battery?: {
    level: number;      // 0-100%
    charging: boolean;
    health: 'good' | 'fair' | 'poor';
  };

  wifi?: {
    signalStrength: number;  // -100 to 0 dBm
    networkName: string;
  };

  lastActivity: Date;
  firmwareVersion: string;
}
```

### Security Event Object
```typescript
interface SecurityEvent {
  id: string;
  deviceId: string;
  deviceName: string;
  timestamp: Date;
  eventType: 'motion' | 'doorbell' | 'ring_cancelled' | 'knock' | 'package';

  details: {
    confidence?: number;      // Motion detection confidence
    duration?: number;        // Event duration in seconds
    zones?: string[];         // Motion detection zones triggered
    answered?: boolean;       // Was doorbell answered?
    recordingUrl?: string;    // URL to recorded video
  };

  thumbnailUrl?: string;      // Event thumbnail image
  videoUrl?: string;          // Full video recording URL
  audioUrl?: string;          // Audio recording URL

  severity: 'low' | 'medium' | 'high' | 'critical';
  acknowledged: boolean;
  acknowledgedBy?: string;
  acknowledgedAt?: Date;
}
```

### Live Stream Object
```typescript
interface LiveStream {
  deviceId: string;
  streamUrl: string;          // RTSP or HLS stream URL
  streamType: 'rtsp' | 'hls' | 'webrtc';
  quality: 'low' | 'medium' | 'high';
  audioEnabled: boolean;
  nightVisionEnabled: boolean;

  session: {
    sessionId: string;
    expiresAt: Date;
    maxDuration: number;      // seconds
  };

  capabilities: {
    ptz: boolean;
    zoom: boolean;
    audio: boolean;
    speaker: boolean;
  };
}
```

## 🛡️ Error Handling

### Common Error Scenarios

1. **Ring API Authentication Issues**
   - **Detection**: 401/403 responses, token expiration
   - **Handling**: Automatic token refresh, re-authentication prompts
   - **User Impact**: Temporary service interruption with clear messaging

2. **Device Offline/Connectivity Issues**
   - **Detection**: Connection timeouts, battery depletion
   - **Handling**: Graceful degradation, last known status display
   - **User Impact**: Clear offline indicators with reconnection status

3. **Video Stream Failures**
   - **Detection**: Stream connection failures, codec issues
   - **Handling**: Fallback to lower quality, alternative stream sources
   - **User Impact**: Automatic quality adjustment or offline message

4. **Rate Limiting**
   - **Detection**: HTTP 429 responses
   - **Handling**: Exponential backoff, request queuing
   - **User Impact**: Slight delays during high usage periods

### Circuit Breaker Implementation

```python
# backend/services/security_circuit_breaker.py
from ..services.circuit_breaker import CircuitBreaker

security_circuit_breaker = CircuitBreaker(
    server_name="ring",
    failure_threshold=3,  # Lower threshold for security-critical service
    timeout=180  # 3 minutes - quicker recovery for security
)

@security_circuit_breaker
async def get_live_stream(device_id: str):
    """Get live stream with circuit breaker protection"""
    return await ring_client.get_stream(device_id)
```

## 📈 Performance Considerations

### Streaming Optimization

1. **Adaptive Bitrate**: Automatically adjust quality based on connection
2. **Stream Pooling**: Reuse stream connections for multiple viewers
3. **Caching Strategy**: Cache device status and recent events
4. **Lazy Loading**: Load video streams only when requested

### Battery Device Considerations

- **Reduced Polling**: Poll battery devices less frequently
- **Wake-on-Demand**: Only activate devices when needed
- **Batch Updates**: Group status checks to minimize wake-ups

### Expected Performance

- **Device List Load**: <300ms
- **Event History**: <500ms for recent events
- **Live Stream Start**: <2s (network dependent)
- **Audio Commands**: <500ms
- **Status Updates**: <200ms

## 🔧 Troubleshooting

### Common Issues

1. **"Ring authentication failed"**
   - Verify email/password in config
   - Check if 2FA is enabled (requires manual token entry)
   - Ensure Ring account has API access permissions

2. **"Device not responding"**
   - Check device battery level and charging status
   - Verify WiFi connectivity and signal strength
   - Ensure device is properly paired to Ring account

3. **"Video stream not loading"**
   - Check internet connection speed and stability
   - Verify firewall settings allow streaming ports
   - Try different quality settings or browsers

4. **"Motion events not appearing"**
   - Check motion sensitivity settings in Ring app
   - Verify device has proper line-of-sight
   - Check if motion zones are configured correctly

### Debug Commands

```bash
# Test MCP server health
curl http://localhost:7782/health

# List Ring devices
curl http://localhost:7782/api/devices

# Get recent events
curl "http://localhost:7782/api/events?limit=10"

# Test authentication
curl -X POST http://localhost:7782/api/auth/verify \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test"}'
```

## 🚨 Security Considerations

### Data Protection
- **End-to-End Encryption**: All video/audio streams encrypted
- **Token Security**: Secure storage and automatic rotation
- **Access Logging**: Comprehensive audit trails
- **Privacy Controls**: User-controlled data retention

### Network Security
- **HTTPS Only**: All communications encrypted
- **IP Whitelisting**: Restrict API access to trusted networks
- **Rate Limiting**: Prevent abuse and DoS attacks
- **Session Management**: Secure session handling and timeouts

## 🚀 Future Enhancements

### Planned Features
- **Advanced Motion Detection**: AI-powered person/vehicle recognition
- **Smart Alerts**: Contextual notifications based on time/location
- **Package Detection**: Automated package delivery alerts
- **Integration with Smart Locks**: Coordinated access control
- **Professional Monitoring**: Integration with security services

### Advanced Analytics
- **Behavioral Patterns**: Learning normal activity patterns
- **Predictive Alerts**: Anticipating security issues
- **Visitor Analytics**: Tracking frequent visitors
- **Energy Impact**: Security device power consumption analysis

## 📚 Related Documentation

- [Efficient MCP Usage Guide](../efficient-mcp-usage.md)
- [MyHomeServer PRD](../../PRD.md)
- [Ring MCP README](../../../../ring-mcp/README.md)

This integration provides comprehensive security monitoring for MyHomeServer, leveraging Ring's robust security ecosystem for reliable home protection and access control.