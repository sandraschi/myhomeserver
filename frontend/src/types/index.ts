// Core types for MyHomeServer

export interface Device {
  id: string;
  name: string;
  type: 'camera' | 'light' | 'plug' | 'sensor' | 'thermostat' | 'lock';
  status: 'online' | 'offline' | 'error' | 'unknown';
  location: string;
  lastSeen: Date;
  batteryLevel?: number;
  signalStrength?: number;
}

export interface Camera extends Device {
  type: 'camera';
  streamUrl?: string;
  recordingEnabled: boolean;
  motionDetected: boolean;
  ptzEnabled: boolean;
  resolution?: string;
  nightVision: boolean;
}

export interface Light extends Device {
  type: 'light';
  brightness: number;
  color?: {
    hue: number;
    saturation: number;
    brightness: number;
  };
  isOn: boolean;
  supportsColor: boolean;
  supportsBrightness: boolean;
}

export interface EnergyDevice extends Device {
  type: 'plug';
  power: number; // Current power in watts
  voltage: number;
  current: number;
  todayKwh: number;
  monthKwh: number;
  isOn: boolean;
}

export interface WeatherData {
  timestamp: Date;
  temperature: number;
  humidity: number;
  pressure: number;
  windSpeed: number;
  windDirection: number;
  conditions: string;
  forecast: WeatherForecast[];
  indoor?: {
    temperature: number;
    humidity: number;
    co2: number;
    noise: number;
  };
}

export interface WeatherForecast {
  date: Date;
  temperature: {
    min: number;
    max: number;
  };
  conditions: string;
  precipitation: number;
  windSpeed: number;
}

export interface SecurityEvent {
  id: string;
  timestamp: Date;
  type: 'motion' | 'doorbell' | 'alarm' | 'system';
  deviceId: string;
  deviceName: string;
  location: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  acknowledged: boolean;
  mediaUrl?: string;
}

export interface ClimateDevice extends Device {
  type: 'thermostat';
  currentTemperature: number;
  targetTemperature: number;
  humidity?: number;
  mode: 'off' | 'heat' | 'cool' | 'auto';
  hvacAction?: 'idle' | 'heating' | 'cooling';
  fanMode?: string;
}

// API Response types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  timestamp: Date;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  hasNext: boolean;
  hasPrev: boolean;
}

// MCP Server status
export interface McpServerStatus {
  name: string;
  url: string;
  status: 'connected' | 'disconnected' | 'error';
  lastPing: Date;
  responseTime: number;
  version?: string;
  error?: string;
}

// LLM Configuration
export interface LlmProvider {
  id: string;
  name: string;
  type: 'local' | 'cloud';
  model: string;
  baseUrl?: string;
  apiKey?: string;
  temperature: number;
  maxTokens: number;
  enabled: boolean;
}

export interface LlmConfig {
  providers: LlmProvider[];
  defaultProvider: string;
}

// UI State types
export interface UiState {
  sidebarOpen: boolean;
  theme: 'dark'; // Only dark theme
  currentPage: string;
}

export interface ModalState {
  logger: boolean;
  help: boolean;
  settings: boolean;
}

// Navigation
export interface NavItem {
  id: string;
  label: string;
  icon: string;
  path: string;
  badge?: number;
}

// Dashboard data
export interface DashboardData {
  devices: {
    total: number;
    online: number;
    offline: number;
    warning: number;
  };
  recentEvents: SecurityEvent[];
  systemStatus: {
    uptime: string;
    cpu: number;
    memory: number;
    network: 'online' | 'offline';
  };
  weather?: WeatherData;
}