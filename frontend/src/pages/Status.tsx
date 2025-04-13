import React from 'react';
import { useQuery } from 'react-query';
import { jobService } from '../services/AllServices';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import ErrorIcon from '@mui/icons-material/Error';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

const Status: React.FC = () => {
  const { data: status, isLoading } = useQuery(
    ['systemStatus'],
    () => jobService.getSystemStatus()
  );

  // Mock data since we don't have actual API endpoint
  const mockStatus = {
    api: { status: 'operational', latency: '38ms' },
    database: { status: 'operational', latency: '62ms' },
    crawler: { status: 'operational', lastRun: '2025-04-11 12:30' },
    website: { status: 'operational', uptime: '99.98%' },
    search: { status: 'degraded', message: 'Minor search delays' },
    notification: { status: 'operational', message: '' },
    incidents: [
      { 
        date: '2025-04-07', 
        title: 'Search indexing delay', 
        status: 'resolved',
        message: 'Search indexing was delayed for approximately 2 hours due to database maintenance.'
      },
      { 
        date: '2025-03-15', 
        title: 'API rate limiting issue', 
        status: 'resolved',
        message: 'Some API requests were incorrectly rate limited. The issue has been fixed.'
      }
    ]
  };

  const data = status || mockStatus;

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'operational':
        return <CheckCircleIcon className="h-6 w-6 text-green-500" />;
      case 'degraded':
        return <AccessTimeIcon className="h-6 w-6 text-yellow-500" />;
      case 'down':
        return <ErrorIcon className="h-6 w-6 text-red-500" />;
      default:
        return <AccessTimeIcon className="h-6 w-6 text-gray-500" />;
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto px-4 py-12">
        <h1 className="text-3xl font-bold mb-8 text-center">System Status</h1>
        
        {isLoading ? (
          <div className="flex justify-center my-12">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <>
            <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
              <div className="p-6 bg-blue-50 border-b border-blue-100">
                <h2 className="text-xl font-semibold">Current Status</h2>
              </div>
              <div className="p-6">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                    {getStatusIcon(data.api.status)}
                    <div className="ml-4">
                      <h3 className="font-medium">API</h3>
                      <p className="text-sm text-gray-600">Latency: {data.api.latency}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                    {getStatusIcon(data.database.status)}
                    <div className="ml-4">
                      <h3 className="font-medium">Database</h3>
                      <p className="text-sm text-gray-600">Latency: {data.database.latency}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                    {getStatusIcon(data.crawler.status)}
                    <div className="ml-4">
                      <h3 className="font-medium">Job Crawler</h3>
                      <p className="text-sm text-gray-600">Last run: {data.crawler.lastRun}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                    {getStatusIcon(data.website.status)}
                    <div className="ml-4">
                      <h3 className="font-medium">Website</h3>
                      <p className="text-sm text-gray-600">Uptime: {data.website.uptime}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                    {getStatusIcon(data.search.status)}
                    <div className="ml-4">
                      <h3 className="font-medium">Search</h3>
                      <p className="text-sm text-gray-600">{data.search.message || 'Operational'}</p>
                    </div>
                  </div>
                  
                  <div className="flex items-center p-4 bg-gray-50 rounded-lg">
                    {getStatusIcon(data.notification.status)}
                    <div className="ml-4">
                      <h3 className="font-medium">Notifications</h3>
                      <p className="text-sm text-gray-600">{data.notification.message || 'Operational'}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <div className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6 bg-blue-50 border-b border-blue-100">
                <h2 className="text-xl font-semibold">Recent Incidents</h2>
              </div>
              <div className="p-6">
                {data.incidents.length === 0 ? (
                  <p className="text-gray-600">No incidents reported in the last 30 days.</p>
                ) : (
                  <div className="space-y-6">
                    {data.incidents.map((incident, index) => (
                      <div key={index} className="border-b border-gray-200 pb-4 last:border-b-0 last:pb-0">
                        <div className="flex items-center mb-2">
                          <span className="text-sm font-medium text-gray-600">{incident.date}</span>
                          <span className={`ml-3 px-2 py-1 text-xs rounded-full ${
                            incident.status === 'resolved' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-yellow-100 text-yellow-800'
                          }`}>
                            {incident.status.charAt(0).toUpperCase() + incident.status.slice(1)}
                          </span>
                        </div>
                        <h3 className="font-medium">{incident.title}</h3>
                        <p className="text-gray-600 mt-1">{incident.message}</p>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          </>
        )}
        
        <div className="mt-8 text-center text-gray-600">
          <p>Last updated: {new Date().toLocaleString()}</p>
          <p className="mt-2">
            For any issues, please contact <a href="mailto:support@jobsfromspace.com" className="text-blue-600 hover:underline">support@jobsfromspace.com</a>
          </p>
        </div>
      </div>
    </div>
  );
};

export default Status; 