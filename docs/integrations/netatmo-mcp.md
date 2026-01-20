# Netatmo MCP Integration

## 🌤️ Overview

The Netatmo MCP server provides comprehensive weather monitoring and indoor air quality data. It integrates with Netatmo weather stations, indoor modules, and outdoor sensors to deliver detailed environmental data for smart home automation and user awareness.

**Repository**: `d:\Dev\repos\netatmo-mcp`
**Primary Use**: Weather data and environmental monitoring in MyHomeServer

## 🔧 Features

### Weather Monitoring
- **Outdoor Weather Station**: Temperature, humidity, wind speed/direction, rain measurement
- **Indoor Air Quality**: CO2 levels, humidity, temperature, noise levels
- **Historical Data**: Long-term weather trends and patterns
- **Weather Alerts**: Integration with local weather warning systems
- **Forecast Integration**: Combine Netatmo data with external weather APIs

### Environmental Intelligence
- **Air Quality Index**: Real-time AQI calculations
- **Comfort Indicators**: Dew point, feels-like temperature
- **Health Recommendations**: Based on air quality and weather conditions
- **Trend Analysis**: Historical comparisons and anomaly detection

## 🏗️ Architecture Integration

### MyHomeServer Usage

```typescript
// frontend/src/services/weatherService.ts
import { apiClient } from './apiClient';

export const weatherService = {
  async getCurrentWeather() {
    return apiClient.get('/api/weather/current');
  },

  async getIndoorSensors() {
    return apiClient.get('/api/weather/indoor');
  },

  async getWeatherHistory(hours: number = 24) {
    return apiClient.get(`/api/weather/history?hours=${hours}`);
  },

  async getForecast() {
    return apiClient.get('/api/weather/forecast');
  }
};
```

### Backend Proxy Implementation

```python
# backend/api/routes/weather.py
from fastapi import APIRouter, HTTPException
from ..services.mcp_client import NetatmoMcpClient

router = APIRouter()
netatmo_client = NetatmoMcpClient("http://localhost:7780")  # Netatmo MCP server URL

@router.get("/weather/current")
async def get_current_weather():
    """Get current weather from Netatmo MCP"""
    try:
        weather_data = await netatmo_client.get_current_weather()
        return weather_data
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Netatmo MCP unavailable: {e}")

@router.get("/weather/indoor")
async def get_indoor_sensors():
    """Get indoor sensor data"""
    try:
        indoor_data = await netatmo_client.get_indoor_sensors()
        return {"sensors": indoor_data}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Indoor sensors unavailable: {e}")

@router.get("/weather/history")
async def get_weather_history(hours: int = 24):
    """Get historical weather data"""
    try:
        history = await netatmo_client.get_history(hours=hours)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"History data unavailable: {e}")
```

## 🔗 API Endpoints

### Weather Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/weather/current` | Current weather conditions |
| GET | `/api/weather/forecast` | Weather forecast (external API) |
| GET | `/api/weather/indoor` | Indoor sensor readings |
| GET | `/api/weather/history` | Historical weather data |
| GET | `/api/weather/alerts` | Weather alerts and warnings |

### Data Types

- **Temperature**: °C with min/max tracking
- **Humidity**: Percentage with comfort levels
- **Pressure**: hPa with trend analysis
- **CO2**: ppm with health impact indicators
- **Noise**: dB with disturbance levels
- **Wind**: Speed (km/h) and direction (°)
- **Rain**: Daily accumulation (mm)

## ⚙️ Configuration

### MyHomeServer Backend Configuration

```yaml
# config.yaml
mcp_servers:
  netatmo:
    url: "http://localhost:7780"
    timeout: 30
    retry_attempts: 3
    health_check_interval: 120  # Weather data less critical

weather:
  netatmo:
    client_id: "your_netatmo_client_id"
    client_secret: "your_netatmo_client_secret"
    username: "your_netatmo_email"
    password: "your_netatmo_password"
    device_id: "your_station_id"

  external_api:
    openweather:
      api_key: "your_openweather_api_key"
      units: "metric"
      lang: "en"

  alerts:
    enabled: true
    rain_threshold: 10.0  # mm/day
    wind_threshold: 50.0  # km/h
    temperature_extremes:
      min: -5
      max: 35
```

### Netatmo MCP Server Requirements

Ensure the Netatmo MCP server is running with:

```bash
# In d:\Dev\repos\netatmo-mcp
python -m netatmo_mcp.server --host 0.0.0.0 --port 7780
```

## 🔄 Data Flow

```
MyHomeServer Frontend
        │
        ▼
FastAPI Backend (MyHomeServer)
        │
        ▼ (HTTP/JSON)
Netatmo MCP Server
        │
        ▼ (Netatmo API)
Netatmo Weather Station
        ├── Outdoor Module
        ├── Indoor Module
        ├── Rain Gauge
        └── Wind Sensor
```

## 📊 Data Models

### Weather Data Object
```typescript
interface WeatherData {
  timestamp: Date;
  outdoor: {
    temperature: number;      // °C
    humidity: number;         // %
    pressure: number;         // hPa
    windStrength: number;     // km/h
    windAngle: number;        // degrees
    gustStrength: number;     // km/h
    rain: number;            // mm (daily accumulation)
  };
  indoor: IndoorSensor[];
  station: {
    wifiStatus: 'good' | 'average' | 'bad';
    batteryLevel: number;     // %
    lastUpdate: Date;
  };
}
```

### Indoor Sensor Object
```typescript
interface IndoorSensor {
  id: string;
  name: string;
  location: string;
  temperature: number;        // °C
  humidity: number;           // %
  co2: number;               // ppm
  noise: number;             // dB
  batteryLevel: number;      // %
  reachable: boolean;
  lastUpdate: Date;

  // Calculated fields
  airQuality: 'excellent' | 'good' | 'average' | 'poor' | 'bad';
  comfort: 'comfortable' | 'dry' | 'humid';
  healthRisk: 'low' | 'medium' | 'high';
}
```

### Weather Forecast Object
```typescript
interface WeatherForecast {
  date: Date;
  temperature: {
    min: number;
    max: number;
    morning: number;
    day: number;
    evening: number;
    night: number;
  };
  weather: {
    main: string;           // "Clear", "Clouds", "Rain", etc.
    description: string;    // "clear sky", "few clouds", etc.
    icon: string;          // Icon code for UI
  };
  precipitation: {
    probability: number;    // 0-100%
    amount: number;         // mm
  };
  wind: {
    speed: number;          // km/h
    direction: number;      // degrees
  };
  humidity: number;         // %
}
```

## 🛡️ Error Handling

### Common Error Scenarios

1. **Netatmo API Rate Limiting**
   - **Detection**: HTTP 429 responses
   - **Handling**: Exponential backoff, cache usage
   - **User Impact**: Slightly stale data during limits

2. **Sensor Offline**
   - **Detection**: Missing data points, old timestamps
   - **Handling**: Show last known values with warning
   - **User Impact**: Clear offline indicators

3. **Network Connectivity Issues**
   - **Detection**: Connection timeouts, DNS failures
   - **Handling**: Retry with fallback to cached data
   - **User Impact**: Graceful degradation

### Weather Data Validation

```python
# backend/services/weather_validator.py
class WeatherDataValidator:
    def validate_temperature(self, temp: float) -> bool:
        """Validate temperature readings"""
        return -50 <= temp <= 60  # Reasonable temperature range

    def validate_humidity(self, humidity: float) -> bool:
        """Validate humidity readings"""
        return 0 <= humidity <= 100

    def validate_pressure(self, pressure: float) -> bool:
        """Validate pressure readings"""
        return 900 <= pressure <= 1100  # hPa range

    def validate_co2(self, co2: float) -> bool:
        """Validate CO2 readings"""
        return 300 <= co2 <= 5000  # ppm range (300 = outdoor, 5000 = dangerous)
```

## 📈 Performance Considerations

### Data Optimization

1. **Smart Polling**: Different intervals for different data types
   - Weather data: Every 5 minutes
   - Indoor sensors: Every 10 minutes
   - Historical data: On-demand

2. **Data Aggregation**: Pre-compute daily/weekly summaries
3. **Compression**: Compress historical data for storage
4. **Caching Strategy**: Cache weather data for 10-30 minutes

### Expected Performance

- **Current Weather**: <200ms (cached), <3s (fresh)
- **Indoor Sensors**: <300ms
- **Historical Data**: <500ms for 24h, <2s for 7 days
- **Forecast Data**: <1s (external API dependent)

## 🔧 Troubleshooting

### Common Issues

1. **"Netatmo API authentication failed"**
   - Check client credentials in config
   - Verify Netatmo account has correct permissions
   - Ensure app is registered in Netatmo developer portal

2. **"Sensor data not updating"**
   - Check sensor battery levels
   - Verify WiFi connectivity
   - Ensure sensors are properly paired to base station

3. **"Weather data unavailable"**
   - Check internet connectivity
   - Verify Netatmo service status
   - Check for API rate limiting

### Debug Commands

```bash
# Test MCP server health
curl http://localhost:7780/health

# Test weather data retrieval
curl http://localhost:7780/api/weather/current

# Check indoor sensors
curl http://localhost:7780/api/weather/indoor

# Test authentication
curl -H "Authorization: Bearer YOUR_TOKEN" http://localhost:7780/api/auth/status
```

## 🌡️ Air Quality Intelligence

### CO2 Level Classification
- **Excellent**: <800 ppm (Good ventilation)
- **Good**: 800-1000 ppm (Normal indoor)
- **Average**: 1000-1400 ppm (Needs ventilation)
- **Poor**: 1400-2000 ppm (Poor air quality)
- **Bad**: >2000 ppm (Immediate ventilation needed)

### Humidity Comfort Zones
- **Dry**: <30% (Uncomfortable, static electricity)
- **Comfortable**: 30-60% (Ideal range)
- **Humid**: >60% (Mold risk, discomfort)

### Noise Level Assessment
- **Quiet**: <30 dB (Peaceful environment)
- **Normal**: 30-50 dB (Typical indoor)
- **Loud**: 50-70 dB (Disturbing)
- **Very Loud**: >70 dB (Uncomfortable)

## 🚀 Future Enhancements

### Planned Features
- **Pollen Count Integration**: Local pollen data and allergies
- **UV Index Monitoring**: Sun protection recommendations
- **Air Quality Forecasting**: Predict air quality changes
- **Smart Ventilation**: Automated window/screen control
- **Health Correlations**: Link weather to health metrics

### Advanced Analytics
- **Weather Pattern Recognition**: AI-powered weather prediction
- **Energy Correlation**: Weather impact on energy usage
- **Health Insights**: Weather effects on well-being
- **Agricultural Data**: Weather impact on gardens/plants

## 📚 Related Documentation

- [Efficient MCP Usage Guide](../efficient-mcp-usage.md)
- [MyHomeServer PRD](../../PRD.md)
- [Netatmo MCP README](../../../../netatmo-mcp/README.md)

This integration provides comprehensive environmental monitoring for MyHomeServer, combining Netatmo's precise sensor data with intelligent analysis for optimal home comfort and health.