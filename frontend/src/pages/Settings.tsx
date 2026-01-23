import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Input } from '../components/ui/input';
import { Badge } from '../components/ui/badge';
import { Settings as SettingsIcon, Server, Shield, Bell, Database } from 'lucide-react';

export const Settings: React.FC = () => {
  // Mock MCP server status
  const mcpServers = [
    { name: 'Tapo Camera', url: 'http://localhost:7778', status: 'connected', version: '1.2.0' },
    { name: 'Netatmo', url: 'http://localhost:7781', status: 'connected', version: '1.1.5' },
    { name: 'Ring', url: 'http://localhost:7782', status: 'error', version: null },
    { name: 'Home Assistant', url: 'http://localhost:7783', status: 'connected', version: '2.0.1' },
    { name: 'Local LLM', url: 'http://localhost:7784', status: 'connecting', version: null },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">Settings</h1>
        <p className="text-muted-foreground mt-2">
          Configure MyHomeServer and manage MCP server connections
        </p>
      </div>

      {/* MCP Server Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Server className="w-5 h-5 mr-2" />
            MCP Server Configuration
          </CardTitle>
          <CardDescription>
            Manage connections to Model Context Protocol servers
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {mcpServers.map((server) => (
              <div key={server.name} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center space-x-3">
                  <div className={`w-3 h-3 rounded-full ${
                    server.status === 'connected' ? 'bg-green-500' :
                    server.status === 'connecting' ? 'bg-yellow-500' :
                    'bg-red-500'
                  }`} />
                  <div>
                    <h3 className="font-medium">{server.name}</h3>
                    <p className="text-sm text-muted-foreground">{server.url}</p>
                    {server.version && (
                      <p className="text-xs text-muted-foreground">v{server.version}</p>
                    )}
                  </div>
                </div>

                <div className="flex items-center space-x-2">
                  <Badge variant={
                    server.status === 'connected' ? 'default' :
                    server.status === 'connecting' ? 'secondary' :
                    'destructive'
                  }>
                    {server.status}
                  </Badge>
                  <Button size="sm" variant="outline">
                    Configure
                  </Button>
                  <Button size="sm" variant="outline">
                    Test
                  </Button>
                </div>
              </div>
            ))}
          </div>

          <div className="mt-6 pt-6 border-t">
            <Button>
              <Server className="w-4 h-4 mr-2" />
              Add MCP Server
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Configuration */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <SettingsIcon className="w-5 h-5 mr-2" />
            System Configuration
          </CardTitle>
          <CardDescription>
            General system settings and preferences
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <label className="block text-sm font-medium mb-2">API Base URL</label>
              <Input defaultValue="http://localhost:8000" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Refresh Interval (seconds)</label>
              <Input type="number" defaultValue="30" />
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Log Level</label>
              <select className="w-full px-3 py-2 border border-input rounded-md bg-background">
                <option>INFO</option>
                <option>DEBUG</option>
                <option>WARNING</option>
                <option>ERROR</option>
              </select>
            </div>
            <div>
              <label className="block text-sm font-medium mb-2">Timezone</label>
              <select className="w-full px-3 py-2 border border-input rounded-md bg-background">
                <option>America/New_York</option>
                <option>America/Los_Angeles</option>
                <option>Europe/London</option>
                <option>Asia/Tokyo</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end">
            <Button>Save Settings</Button>
          </div>
        </CardContent>
      </Card>

      {/* Security Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Shield className="w-5 h-5 mr-2" />
            Security & Privacy
          </CardTitle>
          <CardDescription>
            Configure security settings and data privacy options
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Enable HTTPS</h3>
                <p className="text-sm text-muted-foreground">Use secure connections for all API calls</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Data Encryption</h3>
                <p className="text-sm text-muted-foreground">Encrypt sensitive data at rest</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Anonymous Analytics</h3>
                <p className="text-sm text-muted-foreground">Help improve MyHomeServer with usage statistics</p>
              </div>
              <input type="checkbox" className="rounded" />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium mb-2">API Key</label>
            <div className="flex space-x-2">
              <Input type="password" defaultValue="••••••••••••••••" />
              <Button variant="outline">Regenerate</Button>
            </div>
          </div>

          <div className="flex justify-end">
            <Button>Save Security Settings</Button>
          </div>
        </CardContent>
      </Card>

      {/* Notifications */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Bell className="w-5 h-5 mr-2" />
            Notifications
          </CardTitle>
          <CardDescription>
            Configure notification preferences and alert settings
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Security Alerts</h3>
                <p className="text-sm text-muted-foreground">Get notified of security events</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Energy Alerts</h3>
                <p className="text-sm text-muted-foreground">Notifications for unusual energy usage</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">System Updates</h3>
                <p className="text-sm text-muted-foreground">Updates about system status and maintenance</p>
              </div>
              <input type="checkbox" className="rounded" />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <h3 className="font-medium">Weather Alerts</h3>
                <p className="text-sm text-muted-foreground">Severe weather notifications</p>
              </div>
              <input type="checkbox" defaultChecked className="rounded" />
            </div>
          </div>

          <div className="flex justify-end">
            <Button>Save Notification Settings</Button>
          </div>
        </CardContent>
      </Card>

      {/* System Information */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center">
            <Database className="w-5 h-5 mr-2" />
            System Information
          </CardTitle>
          <CardDescription>
            Current system status and version information
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="font-medium mb-2">MyHomeServer</h3>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>Version: 1.0.0</div>
                <div>Build: 2024.01.20</div>
                <div>Environment: Development</div>
              </div>
            </div>

            <div>
              <h3 className="font-medium mb-2">System Resources</h3>
              <div className="text-sm text-muted-foreground space-y-1">
                <div>CPU Usage: 15%</div>
                <div>Memory: 256MB / 1GB</div>
                <div>Storage: 2.1GB free</div>
              </div>
            </div>
          </div>

          <div className="mt-6 pt-6 border-t flex justify-between">
            <Button variant="outline">
              Export Settings
            </Button>
            <Button variant="outline">
              System Logs
            </Button>
            <Button variant="destructive">
              Reset to Defaults
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};