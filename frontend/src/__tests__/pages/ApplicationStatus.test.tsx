import React from 'react';
import { render, screen } from '@testing-library/react';

// Mock component for application status
const MockApplicationStatus = ({ status }: { status: string }) => {
  const getStatusColor = (status: string) => {
    switch (status) {
      case 'applied': return 'blue';
      case 'reviewed': return 'yellow';
      case 'accepted': return 'green';
      case 'rejected': return 'red';
      default: return 'gray';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'applied': return 'Application Submitted';
      case 'reviewed': return 'Under Review';
      case 'accepted': return 'Accepted';
      case 'rejected': return 'Not Selected';
      default: return 'Unknown Status';
    }
  };

  return (
    <div data-testid="application-status" style={{ color: getStatusColor(status) }}>
      <span data-testid="status-text">{getStatusText(status)}</span>
      <span data-testid="status-badge">{status}</span>
    </div>
  );
};

describe('Application Status Component', () => {
  it('should render applied status correctly', () => {
    render(<MockApplicationStatus status="applied" />);
    
    expect(screen.getByTestId('status-text')).toHaveTextContent('Application Submitted');
    expect(screen.getByTestId('status-badge')).toHaveTextContent('applied');
  });

  it('should render reviewed status correctly', () => {
    render(<MockApplicationStatus status="reviewed" />);
    
    expect(screen.getByTestId('status-text')).toHaveTextContent('Under Review');
    expect(screen.getByTestId('status-badge')).toHaveTextContent('reviewed');
  });

  it('should render accepted status correctly', () => {
    render(<MockApplicationStatus status="accepted" />);
    
    expect(screen.getByTestId('status-text')).toHaveTextContent('Accepted');
    expect(screen.getByTestId('status-badge')).toHaveTextContent('accepted');
  });

  it('should render rejected status correctly', () => {
    render(<MockApplicationStatus status="rejected" />);
    
    expect(screen.getByTestId('status-text')).toHaveTextContent('Not Selected');
    expect(screen.getByTestId('status-badge')).toHaveTextContent('rejected');
  });

  it('should handle unknown status', () => {
    render(<MockApplicationStatus status="unknown" />);
    
    expect(screen.getByTestId('status-text')).toHaveTextContent('Unknown Status');
    expect(screen.getByTestId('status-badge')).toHaveTextContent('unknown');
  });
});
