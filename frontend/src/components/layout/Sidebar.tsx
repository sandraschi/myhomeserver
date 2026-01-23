import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useQuery } from '@tanstack/react-query';
import {
  Home,
  Camera,
  Zap,
  Cloud,
  Shield,
  Settings,
  Monitor
} from 'lucide-react';
import { NavItem } from '../../types';
import { cn } from '../../utils/cn';
import { mcpHealthService } from '../../services/api';

const navigationItems: NavItem[] = [
  {
    id: 'dashboard',
    label: 'Dashboard',
    icon: 'Home',
    path: '/',
  },
  {
    id: 'cameras',
    label: 'Cameras',
    icon: 'Camera',
    path: '/cameras',
  },
  {
    id: 'energy',
    label: 'Energy',
    icon: 'Zap',
    path: '/energy',
  },
  {
    id: 'weather',
    label: 'Weather',
    icon: 'Cloud',
    path: '/weather',
  },
  {
    id: 'security',
    label: 'Security',
    icon: 'Shield',
    path: '/security',
  },
  {
    id: 'settings',
    label: 'Settings',
    icon: 'Settings',
    path: '/settings',
  },
];

const iconMap = {
  Home,
  Camera,
  Zap,
  Cloud,
  Shield,
  Settings,
};

interface SidebarProps {
  className?: string;
}

export const Sidebar: React.FC<SidebarProps> = ({ className }) => {
  const location = useLocation();

  // Fetch MCP server health
  const { data: mcpServers } = useQuery({
    queryKey: ['mcp-health'],
    queryFn: () => mcpHealthService.checkAllServers(),
    refetchInterval: 30000, // Check every 30 seconds
  });

  // Calculate system status
  const connectedCount = mcpServers?.filter(server => server.status === 'connected').length || 0;
  const totalCount = mcpServers?.length || 7;

  return (
    <div className={cn("w-64 bg-card border-r border-border flex flex-col", className)}>
      {/* Logo/Brand */}
      <div className="p-6 border-b border-border">
        <div className="flex items-center space-x-2">
          <Monitor className="w-8 h-8 text-primary" />
          <h1 className="text-xl font-bold">MyHomeServer</h1>
        </div>
        <p className="text-sm text-muted-foreground mt-1">
          Smart Home Dashboard
        </p>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4">
        <ul className="space-y-2">
          {navigationItems.map((item) => {
            const Icon = iconMap[item.icon as keyof typeof iconMap];
            const isActive = location.pathname === item.path;

            return (
              <li key={item.id}>
                <Link
                  to={item.path}
                  className={cn(
                    "flex items-center space-x-3 px-3 py-2 rounded-lg transition-colors",
                    "hover:bg-accent hover:text-accent-foreground",
                    isActive && "bg-accent text-accent-foreground"
                  )}
                >
                  <Icon className="w-5 h-5" />
                  <span className="font-medium">{item.label}</span>
                  {item.badge && (
                    <span className="ml-auto bg-primary text-primary-foreground text-xs px-2 py-1 rounded-full">
                      {item.badge}
                    </span>
                  )}
                </Link>
              </li>
            );
          })}
        </ul>
      </nav>

      {/* System Status */}
      <div className="p-4 border-t border-border">
        <div className="flex items-center justify-between text-sm">
          <span className="text-muted-foreground">System Status</span>
          <div className="flex items-center space-x-1">
            <div className={`w-2 h-2 rounded-full ${connectedCount > 0 ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
            <span className={connectedCount > 0 ? 'text-green-500' : 'text-yellow-500'}>
              {connectedCount > 0 ? 'Active' : 'Limited'}
            </span>
          </div>
        </div>

        <div className="mt-2 text-xs text-muted-foreground space-y-1">
          <div>Backend: Connected</div>
          <div>MCP: {connectedCount}/{totalCount} online</div>
        </div>
      </div>
    </div>
  );
};