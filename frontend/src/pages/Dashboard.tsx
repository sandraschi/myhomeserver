import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Camera, Zap, Cloud, Shield, Home, Activity, AlertCircle } from 'lucide-react';
import { dashboardApi } from '../services/api';

export const Dashboard: React.FC = () => {
  // Fetch dashboard data from API
  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['dashboard'],
    queryFn: () => dashboardApi.getOverview(),
    refetchInterval: 30000, // Refresh every 30 seconds
  });

  // Fallback data if API is not available
  const deviceStats = dashboardData?.devices || {
    total: 0,
    online: 0,
    offline: 0,
    warning: 0,
  };

  const recentEvents = dashboardData?.recentEvents || [];
  const weather = dashboardData?.weather;

  if (isLoading) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Loading your smart home overview...
          </p>
        </div>
        <div className="flex items-center justify-center h-64">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground mt-2">
            Overview of your smart home system and recent activity
          </p>
        </div>
        <Card className="border-red-500/50 bg-red-50 dark:bg-red-950/20">
          <CardContent className="pt-6">
            <div className="flex items-center space-x-2 text-red-600 dark:text-red-400">
              <AlertCircle className="w-5 h-5" />
              <span className="font-medium">Connection Error</span>
            </div>
            <p className="text-sm text-red-600 dark:text-red-400 mt-2">
              Unable to connect to MyHomeServer backend. Please ensure the backend is running on port 10500.
            </p>
            <div className="mt-4 text-xs text-muted-foreground">
              Error: {error instanceof Error ? error.message : 'Unknown error'}
            </div>
          </CardContent>
        </Card>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">Dashboard</h1>
        <p className="text-muted-foreground mt-2">
          Overview of your smart home system and recent activity
        </p>
      </div>

      {/* Device Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Devices</CardTitle>
            <Home className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{deviceStats.total}</div>
            <p className="text-xs text-muted-foreground">
              Connected smart devices
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Online</CardTitle>
            <Activity className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">{deviceStats.online}</div>
            <p className="text-xs text-muted-foreground">
              Devices responding
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Offline</CardTitle>
            <Activity className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">{deviceStats.offline}</div>
            <p className="text-xs text-muted-foreground">
              Devices not responding
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Warnings</CardTitle>
            <Activity className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-yellow-600">{deviceStats.warning}</div>
            <p className="text-xs text-muted-foreground">
              Devices with issues
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="cursor-pointer hover:bg-accent transition-colors">
          <CardContent className="flex items-center p-6">
            <Camera className="h-8 w-8 text-blue-500 mr-4" />
            <div>
              <h3 className="font-semibold">Cameras</h3>
              <p className="text-sm text-muted-foreground">View live feeds</p>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:bg-accent transition-colors">
          <CardContent className="flex items-center p-6">
            <Zap className="h-8 w-8 text-yellow-500 mr-4" />
            <div>
              <h3 className="font-semibold">Energy</h3>
              <p className="text-sm text-muted-foreground">Monitor usage</p>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:bg-accent transition-colors">
          <CardContent className="flex items-center p-6">
            <Cloud className="h-8 w-8 text-blue-400 mr-4" />
            <div>
              <h3 className="font-semibold">Weather</h3>
              <p className="text-sm text-muted-foreground">Current conditions</p>
            </div>
          </CardContent>
        </Card>

        <Card className="cursor-pointer hover:bg-accent transition-colors">
          <CardContent className="flex items-center p-6">
            <Shield className="h-8 w-8 text-red-500 mr-4" />
            <div>
              <h3 className="font-semibold">Security</h3>
              <p className="text-sm text-muted-foreground">Monitor alerts</p>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Recent Events */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Events</CardTitle>
          <CardDescription>
            Latest activity from your smart home devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {recentEvents.map((event) => (
              <div key={(event as any).id} className="flex items-center justify-between p-3 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    event.severity === 'low' ? 'bg-green-500' :
                    event.severity === 'medium' ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`} />
                  <div>
                    <p className="font-medium">{event.deviceName}</p>
                    <p className="text-sm text-muted-foreground capitalize">{event.type} detected</p>
                  </div>
                </div>
                <div className="text-right">
                  <p className="text-sm text-muted-foreground">{event.timestamp.toLocaleTimeString()}</p>
                  <Badge variant={
                    event.severity === 'low' ? 'secondary' :
                    event.severity === 'medium' ? 'default' :
                    'destructive'
                  } className="text-xs">
                    {event.severity}
                  </Badge>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Weather Widget */}
      {weather && (
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center">
              <Cloud className="w-5 h-5 mr-2" />
              Current Weather
            </CardTitle>
            <CardDescription>
              Local weather conditions
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4">
              <div className="text-4xl font-bold">
                {weather.temperature || '--'}°C
              </div>
              <div>
                <div className="text-lg font-medium">
                  {weather.conditions || 'No data'}
                </div>
                <div className="text-sm text-muted-foreground">
                  Humidity: {weather.humidity || '--'}%
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* System Status */}
      <Card>
        <CardHeader>
          <CardTitle>System Status</CardTitle>
          <CardDescription>
            Health overview of MyHomeServer and connected MCP servers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="font-medium">Backend API</span>
              <Badge className="bg-green-500">Online</Badge>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="font-medium">MCP Servers</span>
              <Badge variant="secondary">0/7 Online</Badge>
            </div>
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <span className="font-medium">Database</span>
              <Badge className="bg-green-500">Connected</Badge>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};