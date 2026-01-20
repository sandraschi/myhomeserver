// Shared TypeScript types for MyHomeServer

export interface Device {
  id: string;
  name: string;
  type: string;
  status: 'online' | 'offline' | 'error';
  location: string;
  lastSeen: Date;
}

export interface Camera extends Device {
  streamUrl: string;
  recordingEnabled: boolean;
  motionDetected: boolean;
  ptzEnabled: boolean;
}

export interface EnergyDevice extends Device {
  power: number;
  voltage: number;
  current: number;
  todayKwh: number;
  monthKwh: number;
  isOn: boolean;
}

export interface WeatherData {
  temperature: number;
  humidity: number;
  pressure: number;
  windSpeed: number;
  windDirection: number;
  conditions: string;
  forecast: WeatherForecast[];
}

export interface WeatherForecast {
  date: Date;
  temperature: number;
  conditions: string;
  precipitation: number;
}

export interface SecurityEvent {
  id: string;
  timestamp: Date;
  type: 'motion' | 'doorbell' | 'alarm' | 'system';
  location: string;
  description: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
}

export interface ClimateDevice extends Device {
  temperature: number;
  targetTemperature: number;
  humidity: number;
  mode: 'off' | 'heat' | 'cool' | 'auto';
  fanMode: 'auto' | 'low' | 'medium' | 'high';
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
}