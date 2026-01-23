import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Shield, Camera, Bell, AlertTriangle, CheckCircle, Clock, User } from 'lucide-react';

export const Security: React.FC = () => {
  // Mock security data
  const securityEvents = [
    {
      id: '1',
      timestamp: new Date(Date.now() - 1000 * 60 * 15), // 15 minutes ago
      type: 'motion' as const,
      deviceName: 'Front Door Camera',
      location: 'Entryway',
      description: 'Motion detected at front door',
      severity: 'medium' as const,
      acknowledged: false,
    },
    {
      id: '2',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 2), // 2 hours ago
      type: 'doorbell' as const,
      deviceName: 'Ring Doorbell',
      location: 'Front Door',
      description: 'Someone rang the doorbell',
      severity: 'low' as const,
      acknowledged: true,
    },
    {
      id: '3',
      timestamp: new Date(Date.now() - 1000 * 60 * 60 * 4), // 4 hours ago
      type: 'alarm' as const,
      deviceName: 'Smoke Detector',
      location: 'Kitchen',
      description: 'Smoke alarm triggered',
      severity: 'high' as const,
      acknowledged: true,
    },
  ];

  const securityDevices = [
    { id: '1', name: 'Front Door Camera', type: 'camera', status: 'online', battery: 85 },
    { id: '2', name: 'Backyard Camera', type: 'camera', status: 'online', battery: 92 },
    { id: '3', name: 'Ring Doorbell', type: 'doorbell', status: 'online', battery: 78 },
    { id: '4', name: 'Living Room Sensor', type: 'motion', status: 'online', battery: 65 },
    { id: '5', name: 'Kitchen Smoke Detector', type: 'smoke', status: 'online', battery: 90 },
    { id: '6', name: 'Garage Door Sensor', type: 'contact', status: 'offline', battery: 45 },
  ];

  const formatTime = (date: Date) => {
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffMins = Math.floor(diffMs / (1000 * 60));
    const diffHours = Math.floor(diffMins / 60);
    const diffDays = Math.floor(diffHours / 24);

    if (diffMins < 60) {
      return `${diffMins} min ago`;
    } else if (diffHours < 24) {
      return `${diffHours} hours ago`;
    } else {
      return `${diffDays} days ago`;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
      case 'critical':
        return 'text-red-600 bg-red-100 dark:bg-red-950';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 dark:bg-yellow-950';
      case 'low':
        return 'text-green-600 bg-green-100 dark:bg-green-950';
      default:
        return 'text-gray-600 bg-gray-100 dark:bg-gray-950';
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Security</h1>
          <p className="text-muted-foreground mt-2">
            Monitor security events and control access systems
          </p>
        </div>
        <div className="flex space-x-2">
          <Button variant="outline">
            <Bell className="w-4 h-4 mr-2" />
            Test Alarms
          </Button>
          <Button>
            <Shield className="w-4 h-4 mr-2" />
            Arm System
          </Button>
        </div>
      </div>

      {/* Security Status */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">System Status</CardTitle>
            <Shield className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">Armed</div>
            <p className="text-xs text-muted-foreground">
              Away mode active
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Active Cameras</CardTitle>
            <Camera className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">3/3</div>
            <p className="text-xs text-muted-foreground">
              All cameras online
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Events</CardTitle>
            <AlertTriangle className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">12</div>
            <p className="text-xs text-muted-foreground">
              +3 from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Unacknowledged</CardTitle>
            <Bell className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">1</div>
            <p className="text-xs text-muted-foreground">
              Requires attention
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Security Events Timeline */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Security Events</CardTitle>
          <CardDescription>
            Timeline of security events and alerts from all devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {securityEvents.map((event) => (
              <div key={event.id} className="flex items-start space-x-4 p-4 border rounded-lg">
                <div className={`p-2 rounded-full ${getSeverityColor(event.severity)}`}>
                  {event.type === 'motion' && <Camera className="w-4 h-4" />}
                  {event.type === 'doorbell' && <Bell className="w-4 h-4" />}
                  {event.type === 'alarm' && <AlertTriangle className="w-4 h-4" />}
                </div>

                <div className="flex-1">
                  <div className="flex items-center justify-between mb-1">
                    <h3 className="font-medium">{event.description}</h3>
                    <div className="flex items-center space-x-2">
                      <Badge variant={
                        event.severity === 'high' ? 'destructive' :
                        event.severity === 'medium' ? 'default' :
                        'secondary'
                      }>
                        {event.severity}
                      </Badge>
                      {!event.acknowledged && (
                        <Badge variant="outline" className="text-red-600">
                          New
                        </Badge>
                      )}
                    </div>
                  </div>

                  <div className="flex items-center space-x-4 text-sm text-muted-foreground mb-2">
                    <span className="flex items-center">
                      <User className="w-3 h-3 mr-1" />
                      {event.deviceName}
                    </span>
                    <span className="flex items-center">
                      <Clock className="w-3 h-3 mr-1" />
                      {formatTime(event.timestamp)}
                    </span>
                    <span>{event.location}</span>
                  </div>

                  <div className="flex space-x-2">
                    {!event.acknowledged && (
                      <Button size="sm" variant="outline">
                        <CheckCircle className="w-3 h-3 mr-1" />
                        Acknowledge
                      </Button>
                    )}
                    <Button size="sm" variant="outline">
                      View Details
                    </Button>
                    {event.type === 'doorbell' && (
                      <Button size="sm" variant="outline">
                        View Recording
                      </Button>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Security Devices */}
      <Card>
        <CardHeader>
          <CardTitle>Security Devices</CardTitle>
          <CardDescription>
            Status and battery levels of all security devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {securityDevices.map((device) => (
              <div key={device.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-medium">{device.name}</h3>
                    <p className="text-sm text-muted-foreground capitalize">{device.type}</p>
                  </div>
                  <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                    device.status === 'online'
                      ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                      : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                  }`}>
                    {device.status}
                  </div>
                </div>

                <div className="space-y-2">
                  <div className="flex justify-between text-sm">
                    <span>Battery</span>
                    <span className={device.battery < 50 ? 'text-red-600' : 'text-green-600'}>
                      {device.battery}%
                    </span>
                  </div>
                  <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
                    <div
                      className={`h-2 rounded-full ${
                        device.battery < 50 ? 'bg-red-500' :
                        device.battery < 75 ? 'bg-yellow-500' : 'bg-green-500'
                      }`}
                      style={{ width: `${device.battery}%` }}
                    />
                  </div>
                </div>

                <div className="mt-3 flex space-x-2">
                  <Button size="sm" variant="outline" className="flex-1">
                    Test
                  </Button>
                  <Button size="sm" variant="outline" className="flex-1">
                    Settings
                  </Button>
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
          <CardDescription>
            Common security operations and emergency controls
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Button className="h-16 flex flex-col items-center justify-center">
              <Shield className="w-6 h-6 mb-1" />
              <span>Arm System</span>
            </Button>
            <Button variant="outline" className="h-16 flex flex-col items-center justify-center">
              <Bell className="w-6 h-6 mb-1" />
              <span>Disarm System</span>
            </Button>
            <Button variant="destructive" className="h-16 flex flex-col items-center justify-center">
              <AlertTriangle className="w-6 h-6 mb-1" />
              <span>Panic Button</span>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};