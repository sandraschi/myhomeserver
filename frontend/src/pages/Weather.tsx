import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../components/ui/card';
import { Badge } from '../components/ui/badge';
import { Cloud, Sun, CloudRain, Wind, Droplets, Thermometer, Eye } from 'lucide-react';

export const Weather: React.FC = () => {
  // Mock weather data
  const currentWeather = {
    temperature: 22,
    humidity: 65,
    pressure: 1013,
    windSpeed: 8,
    windDirection: 'SW',
    conditions: 'Partly Cloudy',
    visibility: 10,
    uvIndex: 6,
    feelsLike: 24,
  };

  const indoorWeather = {
    temperature: 21,
    humidity: 55,
    co2: 450,
    noise: 35,
  };

  const forecast = [
    { day: 'Today', high: 24, low: 16, conditions: 'Partly Cloudy', precipitation: 20 },
    { day: 'Tomorrow', high: 26, low: 18, conditions: 'Sunny', precipitation: 5 },
    { day: 'Wednesday', high: 23, low: 15, conditions: 'Rain', precipitation: 80 },
    { day: 'Thursday', high: 21, low: 13, conditions: 'Cloudy', precipitation: 30 },
    { day: 'Friday', high: 25, low: 17, conditions: 'Sunny', precipitation: 10 },
  ];

  const getWeatherIcon = (conditions: string) => {
    switch (conditions.toLowerCase()) {
      case 'sunny':
        return <Sun className="w-8 h-8 text-yellow-500" />;
      case 'rain':
        return <CloudRain className="w-8 h-8 text-blue-500" />;
      case 'cloudy':
      case 'partly cloudy':
        return <Cloud className="w-8 h-8 text-gray-500" />;
      default:
        return <Cloud className="w-8 h-8 text-gray-500" />;
    }
  };

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-3xl font-bold">Weather</h1>
        <p className="text-muted-foreground mt-2">
          Current conditions and forecast for your location
        </p>
      </div>

      {/* Current Weather */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Main Weather Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl">Current Conditions</CardTitle>
                <CardDescription>Sunnyvale, CA</CardDescription>
              </div>
              <div className="text-right">
                <div className="text-6xl font-bold">{currentWeather.temperature}°</div>
                <div className="text-sm text-muted-foreground">Feels like {currentWeather.feelsLike}°</div>
              </div>
            </div>
          </CardHeader>
          <CardContent>
            <div className="flex items-center space-x-4 mb-6">
              {getWeatherIcon(currentWeather.conditions)}
              <div>
                <div className="text-xl font-semibold">{currentWeather.conditions}</div>
                <div className="text-sm text-muted-foreground">Updated 5 minutes ago</div>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="text-center">
                <Wind className="w-6 h-6 text-blue-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">{currentWeather.windSpeed}</div>
                <div className="text-sm text-muted-foreground">mph {currentWeather.windDirection}</div>
              </div>
              <div className="text-center">
                <Droplets className="w-6 h-6 text-blue-400 mx-auto mb-2" />
                <div className="text-2xl font-bold">{currentWeather.humidity}%</div>
                <div className="text-sm text-muted-foreground">Humidity</div>
              </div>
              <div className="text-center">
                <Eye className="w-6 h-6 text-gray-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">{currentWeather.visibility}</div>
                <div className="text-sm text-muted-foreground">mi Visibility</div>
              </div>
              <div className="text-center">
                <Thermometer className="w-6 h-6 text-orange-500 mx-auto mb-2" />
                <div className="text-2xl font-bold">{currentWeather.uvIndex}</div>
                <div className="text-sm text-muted-foreground">UV Index</div>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Indoor Conditions */}
        <Card>
          <CardHeader>
            <CardTitle>Indoor Conditions</CardTitle>
            <CardDescription>Netatmo sensor data</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-sm">Temperature</span>
                <span className="text-lg font-bold">{indoorWeather.temperature}°</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Humidity</span>
                <span className="text-lg font-bold">{indoorWeather.humidity}%</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">CO₂</span>
                <span className="text-lg font-bold">{indoorWeather.co2} ppm</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-sm">Noise</span>
                <span className="text-lg font-bold">{indoorWeather.noise} dB</span>
              </div>
            </div>

            <div className="mt-6">
              <div className="text-sm text-muted-foreground mb-2">Air Quality</div>
              <Badge className="bg-green-500">Good</Badge>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* 5-Day Forecast */}
      <Card>
        <CardHeader>
          <CardTitle>5-Day Forecast</CardTitle>
          <CardDescription>Weather predictions for the coming days</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
              {forecast.map((day) => (
              <div key={day.day} className="text-center p-4 border rounded-lg">
                <div className="font-medium mb-2">{day.day}</div>
                <div className="flex justify-center mb-2">
                  {getWeatherIcon(day.conditions)}
                </div>
                <div className="text-sm text-muted-foreground mb-1">{day.conditions}</div>
                <div className="flex justify-center space-x-2 text-sm">
                  <span className="font-bold">{day.high}°</span>
                  <span className="text-muted-foreground">{day.low}°</span>
                </div>
                <div className="text-xs text-muted-foreground mt-1">
                  {day.precipitation}% rain
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Weather Alerts */}
      <Card>
        <CardHeader>
          <CardTitle>Weather Alerts</CardTitle>
          <CardDescription>Important weather notifications and warnings</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            <div className="flex items-start space-x-3 p-4 bg-yellow-50 dark:bg-yellow-950 border border-yellow-200 dark:border-yellow-800 rounded-lg">
              <div className="w-3 h-3 bg-yellow-500 rounded-full mt-1"></div>
              <div>
                <div className="font-medium text-yellow-800 dark:text-yellow-200">Heat Advisory</div>
                <div className="text-sm text-yellow-700 dark:text-yellow-300 mt-1">
                  Temperatures may reach 95°F tomorrow. Stay hydrated and limit outdoor activities during peak hours.
                </div>
                <div className="text-xs text-yellow-600 dark:text-yellow-400 mt-2">
                  Issued: Today 8:00 AM • Expires: Tomorrow 8:00 PM
                </div>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Weather History */}
      <Card>
        <CardHeader>
          <CardTitle>Temperature Trends</CardTitle>
          <CardDescription>Temperature variations over the past 24 hours</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="h-48 bg-muted rounded-lg flex items-center justify-center">
            <div className="text-center">
              <Thermometer className="w-12 h-12 text-muted-foreground mx-auto mb-2" />
              <p className="text-sm text-muted-foreground">Temperature chart</p>
              <p className="text-xs text-muted-foreground">Chart integration coming soon</p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};