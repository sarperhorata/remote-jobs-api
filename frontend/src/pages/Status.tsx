import React from 'react';
import { useQuery } from 'react-query';
import axios from 'axios';

interface SystemStatus {
  status: string;
  uptime: number;
  lastUpdated: string;
  jobs: {
    total: number;
    sources: Record<string, number>;
  };
}

const Status: React.FC = () => {
  const fetchStatus = async () => {
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    const response = await axios.get(`${API_URL}/health`);
    return response.data;
  };
  
  const { data: status, isLoading, error } = useQuery<SystemStatus>(
    'systemStatus', 
    fetchStatus,
    { refetchInterval: 60000 } // Refetch every minute
  );
  
  if (isLoading) return <div>Loading system status...</div>;
  
  if (error) return <div>Error loading system status. Please try again later.</div>;
  
  return (
    <div className="status-page">
      <h1>System Status</h1>
      
      <div className="status-card">
        <div className="status-header">
          <h2>API Status</h2>
          <span className={`status-indicator ${status?.status === 'healthy' ? 'status-healthy' : 'status-down'}`}>
            {status?.status === 'healthy' ? 'Operational' : 'Issues Detected'}
          </span>
        </div>
        
        <div className="status-details">
          <div className="status-item">
            <span className="status-label">Uptime:</span>
            <span className="status-value">{status?.uptime} hours</span>
          </div>
          <div className="status-item">
            <span className="status-label">Last Updated:</span>
            <span className="status-value">{status?.lastUpdated}</span>
          </div>
          <div className="status-item">
            <span className="status-label">Total Jobs:</span>
            <span className="status-value">{status?.jobs.total}</span>
          </div>
        </div>
      </div>
      
      <div className="sources-section">
        <h2>Job Sources</h2>
        <div className="sources-list">
          {status?.jobs.sources && Object.entries(status.jobs.sources).map(([source, count]) => (
            <div key={source} className="source-item">
              <span className="source-name">{source}</span>
              <span className="source-count">{count} jobs</span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default Status; 