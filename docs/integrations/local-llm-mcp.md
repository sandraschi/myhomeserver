# Local LLM MCP Integration

## 🤖 Overview

The Local LLM MCP server provides privacy-preserving AI capabilities for MyHomeServer. It enables intelligent automation suggestions, natural language processing, predictive insights, and smart home optimization without relying on external cloud services.

**Repository**: `d:\Dev\repos\local-llm-mcp`
**Primary Use**: AI-powered insights and automation in MyHomeServer

## 🔧 Features

### Intelligent Automation
- **Smart Suggestions**: AI-generated automation rules based on usage patterns
- **Natural Language Commands**: Voice-to-action processing for device control
- **Predictive Actions**: Anticipate user needs based on time/location/context
- **Energy Optimization**: AI-powered efficiency recommendations

### Home Intelligence
- **Usage Pattern Analysis**: Learn and predict household behavior
- **Anomaly Detection**: Identify unusual patterns or security concerns
- **Contextual Insights**: Understand relationships between devices and users
- **Personalized Recommendations**: Tailored suggestions based on preferences

### Privacy-First Design
- **Local Processing**: All AI inference happens on local hardware
- **No Data Sharing**: User data never leaves the home network
- **Offline Operation**: Functions without internet connectivity
- **Data Minimization**: Only process necessary data for functionality

## 🏗️ Architecture Integration

### MyHomeServer Usage

```typescript
// frontend/src/services/aiService.ts
import { apiClient } from './apiClient';

export const aiService = {
  async getInsights() {
    return apiClient.get('/api/ai/insights');
  },

  async getSuggestions() {
    return apiClient.get('/api/ai/suggestions');
  },

  async processCommand(command: string) {
    return apiClient.post('/api/ai/command', { command });
  },

  async createAutomation(description: string) {
    return apiClient.post('/api/ai/automation', { description });
  },

  async analyzeEnergy() {
    return apiClient.get('/api/ai/energy-analysis');
  }
};
```

### Backend Proxy Implementation

```python
# backend/api/routes/ai.py
from fastapi import APIRouter, HTTPException
from ..services.mcp_client import LocalLlmMcpClient

router = APIRouter()
llm_client = LocalLlmMcpClient("http://localhost:7786")  # Local LLM MCP server URL

@router.get("/ai/insights")
async def get_insights():
    """Get AI-powered home insights"""
    try:
        insights = await llm_client.get_insights()
        return {"insights": insights}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"AI service unavailable: {e}")

@router.get("/ai/suggestions")
async def get_suggestions():
    """Get automation suggestions"""
    try:
        suggestions = await llm_client.get_suggestions()
        return {"suggestions": suggestions}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Suggestions unavailable: {e}")

@router.post("/ai/command")
async def process_command(command: dict):
    """Process natural language command"""
    try:
        result = await llm_client.process_command(command["text"])
        return {"result": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Command processing failed: {e}")

@router.post("/ai/automation")
async def create_automation(description: dict):
    """Create AI-generated automation"""
    try:
        automation = await llm_client.create_automation(description["text"])
        return {"automation": automation}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Automation creation failed: {e}")
```

## 🔗 API Endpoints

### Insights & Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/insights` | Get home intelligence insights |
| GET | `/api/ai/patterns` | Analyze usage patterns |
| GET | `/api/ai/anomalies` | Detect unusual activity |
| GET | `/api/ai/predictions` | Get predictive insights |

### Automation & Suggestions

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/suggestions` | Get automation suggestions |
| POST | `/api/ai/automation` | Create AI automation rule |
| GET | `/api/ai/automations` | List AI-created automations |
| DELETE | `/api/ai/automations/{id}` | Remove automation |

### Natural Language Processing

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/ai/command` | Process voice/text command |
| POST | `/api/ai/chat` | Interactive AI conversation |
| GET | `/api/ai/intents` | Get recognized intents |
| POST | `/api/ai/train` | Train on custom commands |

### Energy & Optimization

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/ai/energy-analysis` | Analyze energy usage patterns |
| GET | `/api/ai/optimization` | Get optimization recommendations |
| POST | `/api/ai/schedule` | Create optimal schedules |
| GET | `/api/ai/savings` | Calculate potential savings |

## ⚙️ Configuration

### MyHomeServer Backend Configuration

```yaml
# config.yaml
mcp_servers:
  local_llm:
    url: "http://localhost:7786"
    timeout: 120  # Longer timeout for AI processing
    retry_attempts: 2
    health_check_interval: 300  # Less frequent for resource-intensive service

ai:
  local_llm:
    model: "llama-2-7b-chat"  # or "mistral-7b", "phi-2", etc.
    context_window: 4096
    temperature: 0.7
    max_tokens: 512

    # Privacy and data settings
    data_retention_days: 90
    anonymize_pii: true
    local_only: true  # Never send data externally

    # Feature toggles
    natural_language: true
    predictive_automation: true
    energy_optimization: true
    anomaly_detection: true
    personalized_insights: true

  # Training and customization
  training:
    enabled: true
    custom_intents:
      - "turn on living room lights"
      - "set thermostat to comfortable"
      - "show me energy usage"
      - "is anyone home?"

    house_rules:
      - "Always turn off lights when no motion for 30 minutes"
      - "Keep temperature between 20-24°C during occupied hours"
      - "Notify when energy usage exceeds daily average by 50%"

  # Performance settings
  performance:
    cache_embeddings: true
    batch_processing: true
    gpu_acceleration: true  # If available
    memory_limit_gb: 4
```

### Local LLM MCP Server Requirements

Ensure the Local LLM MCP server is running with:

```bash
# In d:\Dev\repos\local-llm-mcp
python -m local_llm_mcp.server --host 0.0.0.0 --port 7786 --model llama-2-7b-chat
```

## 🔄 Data Flow

```
MyHomeServer Frontend
        │
        ▼
FastAPI Backend (MyHomeServer)
        │
        ▼ (HTTP/JSON)
Local LLM MCP Server
        │
        ▼ (Local Inference)
AI Models (Llama, Mistral, etc.)
        ├── Usage Pattern Analysis
        ├── Natural Language Processing
        ├── Predictive Modeling
        ├── Automation Generation
        └── Anomaly Detection
```

## 📊 Data Models

### AI Insight Object
```typescript
interface AiInsight {
  id: string;
  type: 'pattern' | 'anomaly' | 'prediction' | 'recommendation';
  title: string;
  description: string;
  confidence: number;  // 0-1
  severity?: 'low' | 'medium' | 'high' | 'critical';

  data: {
    affectedDevices?: string[];
    timeRange?: {
      start: Date;
      end: Date;
    };
    metrics?: Record<string, number>;
    recommendations?: string[];
  };

  timestamp: Date;
  expiresAt?: Date;  // When insight becomes stale
}
```

### Automation Suggestion Object
```typescript
interface AutomationSuggestion {
  id: string;
  title: string;
  description: string;
  confidence: number;

  trigger: {
    type: 'time' | 'device' | 'sensor' | 'presence';
    condition: string;
    schedule?: string;
  };

  actions: Array<{
    deviceId: string;
    action: string;
    parameters?: Record<string, any>;
  }>;

  potentialSavings?: {
    energy?: number;  // kWh saved per month
    time?: number;    // minutes saved per week
    cost?: number;    // dollars saved per month
  };

  metadata: {
    basedOnHistory: boolean;
    dataPoints: number;
    timeRange: {
      start: Date;
      end: Date;
    };
  };
}
```

### Natural Language Command Object
```typescript
interface NlpCommand {
  id: string;
  rawText: string;
  timestamp: Date;

  intent: {
    name: string;           // "turn_on_lights", "set_temperature", etc.
    confidence: number;
    entities: Array<{
      type: string;         // "device", "location", "value"
      value: string;
      confidence: number;
    }>;
  };

  actions: Array<{
    type: 'device_control' | 'scene_activation' | 'automation' | 'query';
    target: string;         // Device ID, scene ID, etc.
    action: string;         // "turn_on", "set_temperature", etc.
    parameters?: Record<string, any>;
  }>;

  response: {
    success: boolean;
    message: string;
    executedActions?: string[];
    errors?: string[];
  };
}
```

## 🧠 AI Capabilities

### Pattern Recognition
- **Daily Routines**: Learn wake-up, meal, and sleep patterns
- **Device Usage**: Identify frequently used device combinations
- **Energy Patterns**: Detect high/low usage periods and causes
- **Presence Detection**: Learn when home is occupied vs empty

### Predictive Automation
- **Morning Routine**: Turn on lights, start coffee maker, adjust thermostat
- **Evening Wind-down**: Dim lights, prepare bedroom temperature
- **Away Mode**: Activate security, reduce heating/cooling
- **Guest Mode**: Adjust lighting and temperature for visitors

### Natural Language Processing
- **Device Control**: "Turn on the living room lights"
- **Scene Activation**: "Set the mood for movie night"
- **Queries**: "How much energy did we use today?"
- **Complex Commands**: "If I'm home and it's after sunset, turn on the porch light"

### Anomaly Detection
- **Security**: Unusual motion patterns, unexpected device activations
- **Energy**: Spikes in usage, devices left on when away
- **Environmental**: Extreme temperature/humidity changes
- **System**: Device failures, connectivity issues

## 🛡️ Privacy & Security

### Data Protection
- **Local Processing**: All AI inference happens on-device
- **No Cloud Dependencies**: Functions without internet connectivity
- **Data Encryption**: Sensitive data encrypted at rest and in transit
- **Access Controls**: Strict permissions for AI-generated actions

### Privacy-First Design
- **Minimal Data Collection**: Only collect necessary usage data
- **Data Retention Limits**: Automatically purge old data
- **User Consent**: Clear opt-in for AI features
- **Audit Logging**: Track AI decisions and actions

### Security Measures
- **Input Validation**: Sanitize all natural language inputs
- **Rate Limiting**: Prevent AI service abuse
- **Error Boundaries**: Contain AI failures to prevent system compromise
- **Fallback Modes**: Graceful degradation when AI unavailable

## 📈 Performance Considerations

### Resource Management

1. **Model Optimization**: Use quantized models for faster inference
2. **Batch Processing**: Group similar requests for efficiency
3. **Caching Strategy**: Cache embeddings and common responses
4. **GPU Acceleration**: Utilize available GPU resources when possible

### Performance Benchmarks

- **Simple Commands**: <500ms (turn on light, set temperature)
- **Complex Analysis**: <3s (pattern recognition, energy analysis)
- **Automation Generation**: <5s (create new automation rule)
- **Batch Processing**: <2s for up to 10 concurrent requests

### Scalability Features

- **Model Switching**: Automatically switch to smaller models under load
- **Request Prioritization**: Critical commands (security) get priority
- **Background Processing**: Non-critical analysis runs in background
- **Resource Monitoring**: Adjust processing based on available resources

## 🔧 Troubleshooting

### Common Issues

1. **"AI service not responding"**
   - Check if LLM model is properly loaded
   - Verify sufficient RAM/GPU memory
   - Check server logs for model loading errors

2. **"Commands not understood"**
   - Train model on additional command examples
   - Check intent recognition confidence thresholds
   - Verify natural language processing pipeline

3. **"Slow response times"**
   - Consider using smaller/faster model
   - Check for resource contention (CPU/GPU usage)
   - Enable caching for frequent requests

4. **"Inaccurate predictions"**
   - Ensure sufficient historical data for training
   - Check data quality and preprocessing
   - Adjust model parameters (temperature, context window)

### Debug Commands

```bash
# Test MCP server health
curl http://localhost:7786/health

# Test basic AI query
curl -X POST http://localhost:7786/api/query \
  -H "Content-Type: application/json" \
  -d '{"text": "turn on living room lights"}'

# Get AI insights
curl http://localhost:7786/api/insights

# Check model status
curl http://localhost:7786/api/model/status
```

## 🚀 Future Enhancements

### Advanced AI Features
- **Multi-Modal Processing**: Combine text, voice, and visual inputs
- **Federated Learning**: Learn from multiple home setups (privacy-preserving)
- **Emotion Recognition**: Adjust automation based on user mood
- **Predictive Maintenance**: Anticipate device failures before they occur

### Integration Opportunities
- **Voice Assistants**: Enhanced natural language processing
- **Computer Vision**: Visual scene understanding and automation
- **IoT Sensors**: Advanced environmental monitoring and response
- **Energy Management**: AI-optimized energy usage and cost reduction

## 📚 Related Documentation

- [Efficient MCP Usage Guide](../efficient-mcp-usage.md)
- [MyHomeServer PRD](../../PRD.md)
- [Local LLM MCP README](../../../../local-llm-mcp/README.md)

This integration brings intelligent, privacy-preserving AI capabilities to MyHomeServer, enabling smart automation, natural interaction, and predictive insights while keeping all processing local and secure.