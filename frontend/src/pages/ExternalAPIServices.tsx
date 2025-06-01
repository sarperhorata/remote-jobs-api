import React, { useState } from 'react';
import { API_URL } from '../config';
import axios from 'axios';

interface ServiceStatus {
  name: string;
  status: 'operational' | 'degraded' | 'down';
  lastRun: string;
  progress?: number;
}

const ExternalAPIServices: React.FC = () => {
  const [services, setServices] = useState<ServiceStatus[]>([
    {
      name: 'Buzz2remote Companies',
      status: 'operational',
      lastRun: new Date().toISOString(),
      progress: 0
    },
    {
      name: 'LinkedIn Jobs',
      status: 'operational',
      lastRun: new Date().toISOString()
    },
    {
      name: 'Indeed Jobs',
      status: 'operational',
      lastRun: new Date().toISOString()
    },
    {
      name: 'Glassdoor Jobs',
      status: 'operational',
      lastRun: new Date().toISOString()
    }
  ]);

  const [isRunning, setIsRunning] = useState<{ [key: string]: boolean }>({});
  const [error, setError] = useState<string | null>(null);

  const handleRunService = async (serviceName: string) => {
    try {
      setError(null);
      setIsRunning(prev => ({ ...prev, [serviceName]: true }));

      if (serviceName === 'Buzz2remote Companies') {
        // Start progress bar
        let progress = 0;
        const interval = setInterval(() => {
          progress += 1;
          setServices(prev => prev.map(service => 
            service.name === serviceName 
              ? { ...service, progress: Math.min(progress, 100) }
              : service
          ));
        }, 100);

        // Call API to start scanning
        const response = await axios.post(`${API_URL}/api/admin/scan-companies`);
        
        // Clear interval and set final progress
        clearInterval(interval);
        setServices(prev => prev.map(service => 
          service.name === serviceName 
            ? { ...service, progress: 100, lastRun: new Date().toISOString() }
            : service
        ));

        // Send Telegram notification
        await axios.post(`${API_URL}/api/admin/notify-telegram`, {
          message: `Company scanning completed successfully! Total companies scanned: ${response.data.totalCompanies}`
        });
      } else {
        // Handle other services
        await axios.post(`${API_URL}/api/admin/run-service`, { service: serviceName });
        setServices(prev => prev.map(service => 
          service.name === serviceName 
            ? { ...service, lastRun: new Date().toISOString() }
            : service
        ));
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'An error occurred');
    } finally {
      setIsRunning(prev => ({ ...prev, [serviceName]: false }));
    }
  };

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

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            External API Services
          </h1>
          <p className="mt-4 text-lg text-gray-500">
            Manage and monitor external API services
          </p>
        </div>

        {error && (
          <div className="mt-4 p-4 bg-red-100 text-red-700 rounded-md">
            {error}
          </div>
        )}

        <div className="mt-8 space-y-6">
          {services.map((service) => (
            <div
              key={service.name}
              className="bg-white shadow rounded-lg overflow-hidden"
            >
              <div className="p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <h3 className="text-lg font-medium text-gray-900">
                      {service.name}
                    </h3>
                    <p className="mt-1 text-sm text-gray-500">
                      Last run: {new Date(service.lastRun).toLocaleString()}
                    </p>
                  </div>
                  <div className="flex items-center space-x-4">
                    <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(service.status)}`}>
                      {service.status}
                    </span>
                    <button
                      onClick={() => handleRunService(service.name)}
                      disabled={isRunning[service.name]}
                      className={`px-4 py-2 rounded-md text-sm font-medium ${
                        isRunning[service.name]
                          ? 'bg-gray-100 text-gray-400 cursor-not-allowed'
                          : 'bg-indigo-600 text-white hover:bg-indigo-700'
                      }`}
                    >
                      {isRunning[service.name] ? 'Running...' : 'Run'}
                    </button>
                  </div>
                </div>

                {service.name === 'Buzz2remote Companies' && service.progress !== undefined && (
                  <div className="mt-4">
                    <div className="w-full bg-gray-200 rounded-full h-2.5">
                      <div
                        className="bg-indigo-600 h-2.5 rounded-full transition-all duration-300"
                        style={{ width: `${service.progress}%` }}
                      ></div>
                    </div>
                    <p className="mt-2 text-sm text-gray-500 text-right">
                      {service.progress}% Complete
                    </p>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default ExternalAPIServices; 