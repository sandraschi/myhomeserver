import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Camera, Play, Square, RotateCcw } from 'lucide-react';

export const Cameras: React.FC = () => {
  // Mock camera data
  const cameras = [
    { id: '1', name: 'Front Door', status: 'online', location: 'Entryway', recording: true },
    { id: '2', name: 'Backyard', status: 'online', location: 'Garden', recording: false },
    { id: '3', name: 'Living Room', status: 'offline', location: 'Living Room', recording: false },
    { id: '4', name: 'Garage', status: 'online', location: 'Garage', recording: true },
  ];

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-3xl font-bold">Cameras</h1>
          <p className="text-muted-foreground mt-2">
            Monitor and control your security cameras
          </p>
        </div>
        <Button>
          <Camera className="w-4 h-4 mr-2" />
          Add Camera
        </Button>
      </div>

      {/* Camera Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {cameras.map((camera) => (
          <Card key={camera.id}>
            <CardHeader>
              <div className="flex justify-between items-start">
                <div>
                  <CardTitle className="text-lg">{camera.name}</CardTitle>
                  <CardDescription>{camera.location}</CardDescription>
                </div>
                <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                  camera.status === 'online'
                    ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
                    : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
                }`}>
                  {camera.status}
                </div>
              </div>
            </CardHeader>
            <CardContent>
              {/* Camera Preview Placeholder */}
              <div className="aspect-video bg-muted rounded-lg mb-4 flex items-center justify-center">
                <div className="text-center">
                  <Camera className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
                  <p className="text-sm text-muted-foreground">Camera Feed</p>
                  <p className="text-xs text-muted-foreground">Live stream not available</p>
                </div>
              </div>

              {/* Camera Controls */}
              <div className="flex space-x-2">
                <Button size="sm" variant="outline" className="flex-1">
                  <Play className="w-4 h-4 mr-1" />
                  Live
                </Button>
                <Button size="sm" variant="outline" className="flex-1">
                  <Square className="w-4 h-4 mr-1" />
                  {camera.recording ? 'Stop' : 'Record'}
                </Button>
                <Button size="sm" variant="outline">
                  <RotateCcw className="w-4 h-4" />
                </Button>
              </div>

              {/* Camera Info */}
              <div className="mt-4 text-sm text-muted-foreground">
                <div className="flex justify-between">
                  <span>Recording:</span>
                  <span className={camera.recording ? 'text-green-600' : 'text-red-600'}>
                    {camera.recording ? 'Active' : 'Inactive'}
                  </span>
                </div>
                <div className="flex justify-between mt-1">
                  <span>Last Motion:</span>
                  <span>2 hours ago</span>
                </div>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>

      {/* Recording History */}
      <Card>
        <CardHeader>
          <CardTitle>Recent Recordings</CardTitle>
          <CardDescription>
            Latest motion-triggered recordings from all cameras
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-16 h-12 bg-muted rounded flex items-center justify-center">
                  <Play className="w-6 h-6 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-medium">Front Door - Motion Detected</p>
                  <p className="text-sm text-muted-foreground">2 hours ago • 15 seconds</p>
                </div>
              </div>
              <Button size="sm" variant="outline">
                View
              </Button>
            </div>

            <div className="flex items-center justify-between p-3 border rounded-lg">
              <div className="flex items-center space-x-3">
                <div className="w-16 h-12 bg-muted rounded flex items-center justify-center">
                  <Play className="w-6 h-6 text-muted-foreground" />
                </div>
                <div>
                  <p className="font-medium">Backyard - Motion Detected</p>
                  <p className="text-sm text-muted-foreground">5 hours ago • 8 seconds</p>
                </div>
              </div>
              <Button size="sm" variant="outline">
                View
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};