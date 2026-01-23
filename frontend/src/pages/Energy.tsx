import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Zap, Power, Settings, TrendingUp, DollarSign } from 'lucide-react';

export const Energy: React.FC = () => {
  // Mock energy device data
  const devices = [
    { id: '1', name: 'Living Room Lamp', type: 'Light', power: 0, isOn: false, location: 'Living Room' },
    { id: '2', name: 'Kitchen Coffee Maker', type: 'Appliance', power: 1250, isOn: true, location: 'Kitchen' },
    { id: '3', name: 'Office Computer', type: 'Computer', power: 85, isOn: true, location: 'Office' },
    { id: '4', name: 'Bedroom Fan', type: 'Fan', power: 0, isOn: false, location: 'Bedroom' },
    { id: '5', name: 'Garage Door Opener', type: 'Motor', power: 0, isOn: false, location: 'Garage' },
    { id: '6', name: 'TV & Sound System', type: 'Entertainment', power: 245, isOn: true, location: 'Living Room' },
  ];

  const energyStats = {
    todayUsage: 12.5,
    monthUsage: 387.2,
    costToday: 3.25,
    costMonth: 98.50,
    averageDaily: 12.9,
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Energy</h1>
          <p className="text-muted-foreground mt-2">
            Monitor energy usage and control smart devices
          </p>
        </div>
        <Button>
          <Settings className="w-4 h-4 mr-2" />
          Energy Settings
        </Button>
      </div>

      {/* Energy Statistics */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today Usage</CardTitle>
            <Zap className="h-4 w-4 text-yellow-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{energyStats.todayUsage} kWh</div>
            <p className="text-xs text-muted-foreground">
              +2.1 kWh from yesterday
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Usage</CardTitle>
            <TrendingUp className="h-4 w-4 text-blue-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{energyStats.monthUsage} kWh</div>
            <p className="text-xs text-muted-foreground">
              Avg: {energyStats.averageDaily} kWh/day
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Today's Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${energyStats.costToday}</div>
            <p className="text-xs text-muted-foreground">
              At $0.26/kWh
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Monthly Cost</CardTitle>
            <DollarSign className="h-4 w-4 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">${energyStats.costMonth}</div>
            <p className="text-xs text-muted-foreground">
              Est. savings: $12.50
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Device Grid */}
      <Card>
        <CardHeader>
          <CardTitle>Smart Devices</CardTitle>
          <CardDescription>
            Control and monitor energy usage of connected devices
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {devices.map((device) => (
              <div key={device.id} className="border rounded-lg p-4">
                <div className="flex justify-between items-start mb-3">
                  <div>
                    <h3 className="font-medium">{device.name}</h3>
                    <p className="text-sm text-muted-foreground">{device.location}</p>
                  </div>
                  <Badge variant="outline">{device.type}</Badge>
                </div>

                <div className="flex items-center justify-between mb-3">
                  <div className="flex items-center space-x-2">
                    <Power className={`w-4 h-4 ${device.isOn ? 'text-green-500' : 'text-gray-400'}`} />
                    <span className={`text-sm font-medium ${device.isOn ? 'text-green-600' : 'text-gray-500'}`}>
                      {device.isOn ? 'On' : 'Off'}
                    </span>
                  </div>
                  <div className="text-right">
                    <div className="text-lg font-bold">{device.power}W</div>
                    <div className="text-xs text-muted-foreground">Current</div>
                  </div>
                </div>

                <Button
                  size="sm"
                  variant={device.isOn ? "destructive" : "default"}
                  className="w-full"
                >
                  {device.isOn ? 'Turn Off' : 'Turn On'}
                </Button>

                <div className="mt-2 text-xs text-muted-foreground">
                  Today: {device.isOn ? `${(device.power * 0.024).toFixed(2)} kWh` : '0.00 kWh'}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Energy Chart Placeholder */}
      <Card>
        <CardHeader>
          <CardTitle>Energy Usage Trends</CardTitle>
          <CardDescription>
            Daily energy consumption over the past week
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-64 bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              <TrendingUp className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">Energy usage chart</p>
              <p className="text-xs text-muted-foreground">Chart integration coming soon</p>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Energy Saving Tips */}
      <Card>
        <CardHeader>
          <CardTitle>Energy Saving Suggestions</CardTitle>
          <CardDescription>
            AI-powered recommendations to reduce energy costs
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-3 bg-green-50 dark:bg-green-950 rounded-lg">
              <div className="w-2 h-2 bg-green-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-green-800 dark:text-green-200">Turn off unused devices</p>
                <p className="text-sm text-green-700 dark:text-green-300">
                  Kitchen coffee maker has been running for 4 hours. Consider turning it off when not in use.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-3 bg-blue-50 dark:bg-blue-950 rounded-lg">
              <div className="w-2 h-2 bg-blue-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-blue-800 dark:text-blue-200">Optimize lighting schedule</p>
                <p className="text-sm text-blue-700 dark:text-blue-300">
                  Set bedroom lights to turn off automatically at 11 PM to save 0.5 kWh daily.
                </p>
              </div>
            </div>

            <div className="flex items-start space-x-3 p-3 bg-yellow-50 dark:bg-yellow-950 rounded-lg">
              <div className="w-2 h-2 bg-yellow-500 rounded-full mt-2"></div>
              <div>
                <p className="font-medium text-yellow-800 dark:text-yellow-200">Peak usage alert</p>
                <p className="text-sm text-yellow-700 dark:text-yellow-300">
                  High energy usage detected between 6-8 PM. Consider shifting some usage to off-peak hours.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};