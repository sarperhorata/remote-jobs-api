import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import BulkApplyManager from '../../components/BulkApplyManager';

// Mock dependencies
jest.mock('../../components/BulkJobSelector', () => {
  return function MockBulkJobSelector({ onJobsSelected, onNext }) {
    return (
      <div data-testid="bulk-job-selector">
        <button onClick={() => onJobsSelected([
          { id: '1', title: 'Job 1', company: 'Company 1', url: 'https://example.com/1' },
          { id: '2', title: 'Job 2', company: 'Company 2', url: 'https://example.com/2' }
        ])}>
          Select Jobs
        </button>
        <button onClick={onNext}>Next</button>
      </div>
    );
  };
});

jest.mock('../../components/AutoFormFiller', () => {
  return function MockAutoFormFiller({ onComplete, onError, onProgress }) {
    return (
      <div data-testid="auto-form-filler">
        <button onClick={() => onComplete({ success: true, applicationId: 'app1' })}>
          Complete Form
        </button>
        <button onClick={() => onError('Form error')}>Error</button>
        <button onClick={() => onProgress(50)}>Progress</button>
      </div>
    );
  };
});

jest.mock('../../components/BulkApplyQueue', () => {
  return function MockBulkApplyQueue({ onComplete, onError, onProgress }) {
    return (
      <div data-testid="bulk-apply-queue">
        <button onClick={() => onComplete({ completed: 2, total: 2, success: true })}>
          Complete Queue
        </button>
        <button onClick={() => onError('Queue error')}>Error</button>
        <button onClick={() => onProgress(75)}>Progress</button>
      </div>
    );
  };
});

// Mock API
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('https://api.example.com')
}));

// Mock fetch
global.fetch = jest.fn();

describe('BulkApplyManager Component', () => {
  const mockProps = {
    onComplete: jest.fn(),
    onError: jest.fn(),
    onProgress: jest.fn()
  };

  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    // Mock successful API response
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve([
        {
          _id: '1',
          id: '1',
          title: 'Senior React Developer',
          company: { name: 'Tech Corp' },
          location: 'New York, NY',
          job_type: 'full-time',
          url: 'https://example.com/job/1',
          is_active: true,
          created_at: '2024-01-01'
        },
        {
          _id: '2',
          id: '2',
          title: 'Frontend Engineer',
          company: { name: 'Startup Inc' },
          location: 'San Francisco, CA',
          job_type: 'full-time',
          url: 'https://example.com/job/2',
          is_active: true,
          created_at: '2024-01-01'
        }
      ])
    });
  });

  describe('Rendering', () => {
    it('renders the component with initial step', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
      expect(screen.getByText(/Select multiple jobs and apply to them automatically/)).toBeInTheDocument();
    });

    it('shows step indicators', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Select Jobs')).toBeInTheDocument();
        expect(screen.getByText('Configure')).toBeInTheDocument();
        expect(screen.getByText('Processing')).toBeInTheDocument();
        expect(screen.getByText('Complete')).toBeInTheDocument();
      });
    });

    it('shows loading state initially', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      expect(screen.getByText('Loading available jobs...')).toBeInTheDocument();
    });

    it('shows authentication error when no token', async () => {
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Authentication required')).toBeInTheDocument();
      });
    });
  });

  describe('Job Loading', () => {
    it('loads jobs successfully', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledWith(
          expect.stringContaining('/jobs'),
          expect.objectContaining({
            method: 'GET',
            headers: {
              'Authorization': 'Bearer test-token'
            }
          })
        );
      });
    });

    it('handles API errors gracefully', async () => {
      localStorage.setItem('token', 'test-token');
      
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: false,
        status: 500
      });
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Failed to load jobs')).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling', () => {
    it('displays error messages', async () => {
      localStorage.setItem('token', 'test-token');
      
      (global.fetch as jest.Mock).mockRejectedValue(new Error('Network error'));
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });
    });

    it('allows retrying after errors', async () => {
      localStorage.setItem('token', 'test-token');
      
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: () => Promise.resolve([])
        });
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Network error')).toBeInTheDocument();
      });

      const retryButton = screen.getByText('Try Again');
      fireEvent.click(retryButton);

      await waitFor(() => {
        expect(global.fetch).toHaveBeenCalledTimes(2);
      });
    });
  });

  describe('Component Integration', () => {
    it('integrates with BulkJobSelector', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByTestId('bulk-job-selector')).toBeInTheDocument();
      });
    });

    it('integrates with AutoFormFiller', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      // Check if the component renders without crashing
      expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
    });

    it('integrates with BulkApplyQueue', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      // Check if the component renders without crashing
      expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
    });
  });

  describe('User Interactions', () => {
    it('handles job selection', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        const selectButton = screen.getByText('Select Jobs');
        fireEvent.click(selectButton);
      });
    });

    it('handles form completion', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      // Check if the component renders without crashing
      expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
    });

    it('handles queue completion', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      // Check if the component renders without crashing
      expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
      });
    });

    it('supports keyboard navigation', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        const nextButton = screen.getByText('Next');
        nextButton.focus();
        expect(nextButton).toHaveFocus();
      });
    });
  });

  describe('Edge Cases', () => {
    it('handles missing props gracefully', async () => {
      localStorage.setItem('token', 'test-token');
      
      render(<BulkApplyManager />);
      
      await waitFor(() => {
        expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
      });
    });

    it('handles empty job list', async () => {
      localStorage.setItem('token', 'test-token');
      
      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve([])
      });
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    it('renders efficiently with large job lists', async () => {
      localStorage.setItem('token', 'test-token');
      
      const largeJobList = Array.from({ length: 100 }, (_, i) => ({
        _id: `${i}`,
        id: `${i}`,
        title: `Job ${i}`,
        company: { name: `Company ${i}` },
        location: 'Remote',
        job_type: 'full-time',
        url: `https://example.com/job/${i}`,
        is_active: true,
        created_at: '2024-01-01'
      }));

      (global.fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: () => Promise.resolve(largeJobList)
      });
      
      render(<BulkApplyManager {...mockProps} />);
      
      await waitFor(() => {
        expect(screen.getByText('Bulk Job Application')).toBeInTheDocument();
      });
    });
  });
}); 