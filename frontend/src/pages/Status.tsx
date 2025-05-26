import React, { useState, useEffect } from 'react';
import { CheckCircle, XCircle, AlertCircle, Clock, Activity, Database, Globe, Bot } from 'lucide-react';

interface ServiceStatus {
  name: string;
  status: 'operational' | 'degraded' | 'down';
  responseTime: number;
  uptime: number;
  lastChecked: string;
  icon: React.ReactNode;
}

const Status: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    {
      name: 'API Backend',
      status: 'operational',
      responseTime: 120,
      uptime: 99.9,
      lastChecked: new Date().toISOString(),
      icon: <Globe className="w-6 h-6" />
    },
    {
      name: 'Database',
      status: 'operational',
      responseTime: 45,
      uptime: 99.8,
      lastChecked: new Date().toISOString(),
      icon: <Database className="w-6 h-6" />
    },
    {
      name: 'Job Crawler',
      status: 'operational',
      responseTime: 200,
      uptime: 98.5,
      lastChecked: new Date().toISOString(),
      icon: <Activity className="w-6 h-6" />
    },
    {
      name: 'Telegram Bot',
      status: 'operational',
      responseTime: 80,
      uptime: 99.2,
      lastChecked: new Date().toISOString(),
      icon: <Bot className="w-6 h-6" />
    }
  ]);

  const [overallStatus, setOverallStatus] = useState<'operational' | 'degraded' | 'down'>('operational');

  useEffect(() => {
    // Check overall status based on individual services
    const hasDown = services.some(service => service.status === 'down');
    const hasDegraded = services.some(service => service.status === 'degraded');
    
    if (hasDown) {
      setOverallStatus('down');
    } else if (hasDegraded) {
      setOverallStatus('degraded');
    } else {
      setOverallStatus('operational');
    }
  }, [services]);

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'operational':
        return 'text-green-600 bg-green-100';
      case 'degraded':
        return 'text-yellow-600 bg-yellow-100';
      case 'down':
        return 'text-red-600 bg-red-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircle className="w-5 h-5 text-green-600" />;
      case 'degraded':
        return <AlertCircle className="w-5 h-5 text-yellow-600" />;
      case 'down':
        return <XCircle className="w-5 h-5 text-red-600" />;
      default:
        return <Clock className="w-5 h-5 text-gray-600" />;
    }
  };

  const getOverallStatusMessage = () => {
    switch (overallStatus) {
      case 'operational':
        return 'All systems are operational';
      case 'degraded':
        return 'Some systems are experiencing issues';
      case 'down':
        return 'Major system outage detected';
      default:
        return 'Status unknown';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">System Status</h1>
              <p className="text-gray-600 mt-1">Real-time status of Buzz2Remote services</p>
            </div>
            <div className="text-right">
              <div className="text-sm text-gray-500">Last updated</div>
              <div className="text-sm font-medium">{new Date().toLocaleString()}</div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Overall Status */}
        <div className="mb-8">
          <div className={`rounded-lg p-6 ${getStatusColor(overallStatus)}`}>
            <div className="flex items-center">
              {getStatusIcon(overallStatus)}
              <div className="ml-3">
                <h2 className="text-lg font-semibold">{getOverallStatusMessage()}</h2>
                <p className="text-sm opacity-80">
                  {overallStatus === 'operational' 
                    ? 'All services are running smoothly'
                    : 'We are working to resolve any issues'
                  }
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Services Status */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          {services.map((service, index) => (
            <div key={index} className="bg-white rounded-lg shadow-sm border p-6">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <div className={`p-2 rounded-lg ${getStatusColor(service.status)}`}>
                    {service.icon}
                  </div>
                  <div className="ml-3">
                    <h3 className="text-lg font-semibold text-gray-900">{service.name}</h3>
                    <div className="flex items-center">
                      {getStatusIcon(service.status)}
                      <span className="ml-1 text-sm font-medium capitalize">{service.status}</span>
                    </div>
                  </div>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 text-sm">
                <div>
                  <div className="text-gray-500">Response Time</div>
                  <div className="font-semibold">{service.responseTime}ms</div>
                </div>
                <div>
                  <div className="text-gray-500">Uptime</div>
                  <div className="font-semibold">{service.uptime}%</div>
                </div>
              </div>

              <div className="mt-4 text-xs text-gray-500">
                Last checked: {new Date(service.lastChecked).toLocaleString()}
              </div>
            </div>
          ))}
        </div>

        {/* System Metrics */}
        <div className="bg-white rounded-lg shadow-sm border p-6 mb-8">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">System Metrics</h3>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-600">10,247</div>
              <div className="text-sm text-gray-500">Active Jobs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-green-600">471</div>
              <div className="text-sm text-gray-500">Companies</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-purple-600">5</div>
              <div className="text-sm text-gray-500">Active Cronjobs</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-orange-600">99.9%</div>
              <div className="text-sm text-gray-500">Overall Uptime</div>
            </div>
          </div>
        </div>

        {/* Recent Incidents */}
        <div className="bg-white rounded-lg shadow-sm border p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Incidents</h3>
          <div className="space-y-4">
            <div className="flex items-start">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 mr-3" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-gray-900">System Maintenance Completed</h4>
                  <span className="text-sm text-gray-500">2 hours ago</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Scheduled maintenance for database optimization has been completed successfully.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5 mr-3" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-gray-900">Increased Response Times</h4>
                  <span className="text-sm text-gray-500">1 day ago</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  We experienced slightly increased response times due to high traffic. Issue resolved.
                </p>
              </div>
            </div>

            <div className="flex items-start">
              <CheckCircle className="w-5 h-5 text-green-600 mt-0.5 mr-3" />
              <div className="flex-1">
                <div className="flex items-center justify-between">
                  <h4 className="font-medium text-gray-900">New Features Deployed</h4>
                  <span className="text-sm text-gray-500">3 days ago</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">
                  Successfully deployed new AI-powered job matching features and admin panel.
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="mt-8 text-center text-sm text-gray-500">
          <p>
            For real-time updates, follow us on{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700">Twitter</a> or{' '}
            <a href="#" className="text-blue-600 hover:text-blue-700">subscribe to our status page</a>.
          </p>
        </div>
      </div>
    </div>
  );
};

export default Status; 