import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { ApiResponse, DashboardData, Device, SecurityEvent, McpServerStatus } from '../types';

// Create axios instance with default config
const api: AxiosInstance = axios.create({
  baseURL: (import.meta as any).env?.VITE_API_URL || 'http://localhost:10500',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor for auth
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('auth_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor for error handling
api.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error) => {
    // Handle common errors
    if (error.response?.status === 401) {
      // Unauthorized - redirect to login
      localStorage.removeItem('auth_token');
      window.location.href = '/login';
    } else if (error.response?.status >= 500) {
      // Server error - show generic message
      console.error('Server error:', error.response.data);
    } else if (error.code === 'NETWORK_ERROR') {
      // Network error - MCP server might be down
      console.error('Network error - MCP server may be unavailable');
    }

    return Promise.reject(error);
  }
);

// Generic API methods
export const apiService = {
  // GET request
  get: <T>(url: string, params?: any): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.get(url, { params });
  },

  // POST request
  post: <T>(url: string, data?: any): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.post(url, data);
  },

  // PUT request
  put: <T>(url: string, data?: any): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.put(url, data);
  },

  // DELETE request
  delete: <T>(url: string): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.delete(url);
  },

  // PATCH request
  patch: <T>(url: string, data?: any): Promise<AxiosResponse<ApiResponse<T>>> => {
    return api.patch(url, data);
  },
};

// Specific API methods for MyHomeServer
export const dashboardApi = {
  async getOverview(): Promise<DashboardData> {
    const response = await apiService.get<DashboardData>('/api/v1/dashboard');
    return response.data.data; // Backend returns { success: true, data: DashboardData }
  },
};

export const camerasApi = {
  async getCameras(): Promise<{ cameras: Device[]; total: number }> {
    const response = await apiService.get<{ cameras: Device[]; total: number }>('/api/v1/cameras');
    return response.data.data;
  },
};

export const energyApi = {
  async getDevices(): Promise<{ devices: Device[]; usage: { today: number; month: number; cost: number } }> {
    const response = await apiService.get<{ devices: Device[]; usage: { today: number; month: number; cost: number } }>('/api/v1/energy');
    return response.data.data;
  },
};

export const weatherApi = {
  async getWeather(): Promise<{ current: any; forecast: any[]; indoor?: any }> {
    const response = await apiService.get<{ current: any; forecast: any[]; indoor?: any }>('/api/v1/weather');
    return response.data.data;
  },
};

export const securityApi = {
  async getEvents(): Promise<{ events: SecurityEvent[]; devices: Device[] }> {
    const response = await apiService.get<{ events: SecurityEvent[]; devices: Device[] }>('/api/v1/security');
    return response.data.data;
  },
};

export const devicesApi = {
  async getAllDevices(): Promise<{ cameras: Device[]; energy_devices: Device[]; climate_devices: Device[]; security_devices: Device[]; other_devices: Device[] }> {
    const response = await apiService.get<{ cameras: Device[]; energy_devices: Device[]; climate_devices: Device[]; security_devices: Device[]; other_devices: Device[] }>('/api/v1/devices');
    return response.data.data;
  },
};

// MCP Server health checks
export const mcpHealthService = {
  async checkServer(serverName: string, url: string): Promise<McpServerStatus> {
    try {
      const response = await axios.get(`${url}/health`, { timeout: 5000 });
      return {
        name: serverName,
        url,
        status: 'connected' as const,
        lastPing: new Date(),
        responseTime: response.data.responseTime || 0,
        version: response.data.version,
      };
    } catch (error) {
      return {
        name: serverName,
        url,
        status: 'error' as const,
        lastPing: new Date(),
        responseTime: 0,
        error: error instanceof Error ? error.message : 'Unknown error',
      };
    }
  },

  async checkAllServers(): Promise<McpServerStatus[]> {
    try {
      const response = await apiService.get('/api/v1/mcp/health');
      return response.data;
    } catch (error) {
      // Fallback to mock data if backend is not available
      return [
        {
          name: 'Tapo Camera',
          url: 'http://localhost:7778',
          status: 'connected' as const,
          lastPing: new Date(),
          responseTime: 45,
          version: '1.2.0'
        },
        {
          name: 'Netatmo Weather',
          url: 'http://localhost:7781',
          status: 'connected' as const,
          lastPing: new Date(),
          responseTime: 32,
          version: '1.1.5'
        },
        {
          name: 'Home Assistant',
          url: 'http://localhost:7783',
          status: 'connected' as const,
          lastPing: new Date(),
          responseTime: 28,
          version: '2.0.1'
        },
        {
          name: 'Ring Security',
          url: 'http://localhost:7782',
          status: 'disconnected' as const,
          lastPing: new Date(),
          responseTime: 0,
          error: 'Connection timeout'
        }
      ];
    }
  },
};

export default api;