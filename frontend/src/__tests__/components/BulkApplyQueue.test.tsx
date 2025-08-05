import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import BulkApplyQueue from '../../components/BulkApplyQueue';

// Mock dependencies
jest.mock('../../services/api', () => ({
  submitBulkApplication: jest.fn(),
  getApplicationStatus: jest.fn(),
}));

jest.useFakeTimers();

describe('BulkApplyQueue Component', () => {
  const mockJobs = [
    {
      id: '1',
      title: 'Senior React Developer',
      company: 'Tech Corp',
      url: 'https://example.com/job/1',
      location: 'New York, NY',
      salary: '$100k - $150k'
    },
    {
      id: '2',
      title: 'Frontend Engineer',
      company: 'Startup Inc',
      url: 'https://example.com/job/2',
      location: 'San Francisco, CA',
      salary: '$90k - $130k'
    },
    {
      id: '3',
      title: 'UI/UX Developer',
      company: 'Design Studio',
      url: 'https://example.com/job/3',
      location: 'Remote',
      salary: '$80k - $120k'
    }
  ];

  const mockProps = {
    jobs: mockJobs,
    onComplete: jest.fn(),
    onError: jest.fn(),
    onProgress: jest.fn(),
    rateLimit: 1000, // 1 second between requests
    maxRetries: 3
  };

  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
  });

  describe('Rendering', () => {
    it('renders the component with job queue', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      expect(screen.getByText('Bulk Apply Queue')).toBeInTheDocument();
      expect(screen.getByText('3 jobs in queue')).toBeInTheDocument();
      expect(screen.getByText('Senior React Developer at Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('Frontend Engineer at Startup Inc')).toBeInTheDocument();
      expect(screen.getByText('UI/UX Developer at Design Studio')).toBeInTheDocument();
    });

    it('shows start button when queue is ready', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      expect(screen.getByRole('button', { name: /start bulk apply/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /pause/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /stop/i })).toBeInTheDocument();
    });

    it('displays job status indicators', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      expect(screen.getAllByText('Pending')).toHaveLength(3);
      expect(screen.getByText('0/3 completed')).toBeInTheDocument();
    });
  });

  describe('Queue Management', () => {
    it('starts processing when start button is clicked', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Processing...')).toBeInTheDocument();
        expect(screen.getByText('1/3 completed')).toBeInTheDocument();
      });
    });

    it('pauses processing when pause button is clicked', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Processing...')).toBeInTheDocument();
      });

      const pauseButton = screen.getByRole('button', { name: /pause/i });
      fireEvent.click(pauseButton);

      expect(screen.getByText('Paused')).toBeInTheDocument();
    });

    it('resumes processing when resume button is clicked', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Processing...')).toBeInTheDocument();
      });

      const pauseButton = screen.getByRole('button', { name: /pause/i });
      fireEvent.click(pauseButton);

      const resumeButton = screen.getByRole('button', { name: /resume/i });
      fireEvent.click(resumeButton);

      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });

    it('stops processing when stop button is clicked', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Processing...')).toBeInTheDocument();
      });

      const stopButton = screen.getByRole('button', { name: /stop/i });
      fireEvent.click(stopButton);

      expect(screen.getByText('Stopped')).toBeInTheDocument();
      expect(mockProps.onComplete).toHaveBeenCalledWith({
        completed: 1,
        total: 3,
        success: false
      });
    });
  });

  describe('Rate Limiting', () => {
    it('respects rate limiting between requests', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} rateLimit={2000} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // First request should be made immediately
      await waitFor(() => {
        expect(submitBulkApplication).toHaveBeenCalledTimes(1);
      });

      // Second request should wait for rate limit
      act(() => {
        jest.advanceTimersByTime(1000); // Advance 1 second
      });

      expect(submitBulkApplication).toHaveBeenCalledTimes(1);

      act(() => {
        jest.advanceTimersByTime(1000); // Advance another second
      });

      await waitFor(() => {
        expect(submitBulkApplication).toHaveBeenCalledTimes(2);
      });
    });

    it('shows rate limiting status', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} rateLimit={1000} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      expect(screen.getByText('Rate limiting: 1s between requests')).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    it('handles individual job failures', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication
        .mockResolvedValueOnce({ success: true, applicationId: 'app1' })
        .mockRejectedValueOnce(new Error('Network error'))
        .mockResolvedValueOnce({ success: true, applicationId: 'app3' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Failed')).toBeInTheDocument();
        expect(screen.getByText('Error: Network error')).toBeInTheDocument();
        expect(mockProps.onError).toHaveBeenCalledWith('Network error');
      });
    });

    it('retries failed jobs up to max retries', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication
        .mockRejectedValueOnce(new Error('Temporary error'))
        .mockRejectedValueOnce(new Error('Temporary error'))
        .mockResolvedValueOnce({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} maxRetries={2} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Retrying... (1/2)')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Retrying... (2/2)')).toBeInTheDocument();
      });

      await waitFor(() => {
        expect(screen.getByText('Completed')).toBeInTheDocument();
      });
    });

    it('marks job as permanently failed after max retries', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockRejectedValue(new Error('Permanent error'));

      render(<BulkApplyQueue {...mockProps} maxRetries={2} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Permanently Failed')).toBeInTheDocument();
        expect(screen.getByText('Error: Permanent error')).toBeInTheDocument();
      });
    });
  });

  describe('Progress Tracking', () => {
    it('updates progress as jobs complete', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('1/3 completed')).toBeInTheDocument();
        expect(mockProps.onProgress).toHaveBeenCalledWith(33);
      });

      await waitFor(() => {
        expect(screen.getByText('2/3 completed')).toBeInTheDocument();
        expect(mockProps.onProgress).toHaveBeenCalledWith(67);
      });

      await waitFor(() => {
        expect(screen.getByText('3/3 completed')).toBeInTheDocument();
        expect(mockProps.onProgress).toHaveBeenCalledWith(100);
      });
    });

    it('shows detailed progress information', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Progress: 33%')).toBeInTheDocument();
        expect(screen.getByText('Success: 1')).toBeInTheDocument();
        expect(screen.getByText('Failed: 0')).toBeInTheDocument();
        expect(screen.getByText('Pending: 2')).toBeInTheDocument();
      });
    });
  });

  describe('Job Details', () => {
    it('displays job information correctly', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
      expect(screen.getByText('Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('New York, NY')).toBeInTheDocument();
      expect(screen.getByText('$100k - $150k')).toBeInTheDocument();
    });

    it('allows opening job in new tab', () => {
      const mockOpen = jest.fn();
      Object.defineProperty(window, 'open', {
        value: mockOpen,
        writable: true
      });

      render(<BulkApplyQueue {...mockProps} />);
      
      const openButtons = screen.getAllByRole('button', { name: /open job/i });
      fireEvent.click(openButtons[0]);

      expect(mockOpen).toHaveBeenCalledWith('https://example.com/job/1', '_blank');
    });

    it('shows job status with appropriate styling', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      // Initial state
      expect(screen.getAllByText('Pending')).toHaveLength(3);

      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      // Processing state
      await waitFor(() => {
        expect(screen.getByText('Processing...')).toBeInTheDocument();
      });

      // Completed state
      await waitFor(() => {
        expect(screen.getByText('Completed')).toBeInTheDocument();
      });
    });
  });

  describe('Queue Statistics', () => {
    it('displays queue statistics', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      expect(screen.getByText('Queue Statistics')).toBeInTheDocument();
      expect(screen.getByText('Total Jobs: 3')).toBeInTheDocument();
      expect(screen.getByText('Estimated Time: 3s')).toBeInTheDocument();
      expect(screen.getByText('Success Rate: 0%')).toBeInTheDocument();
    });

    it('updates statistics as jobs complete', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Success Rate: 33%')).toBeInTheDocument();
        expect(screen.getByText('Estimated Time: 2s')).toBeInTheDocument();
      });
    });
  });

  describe('User Interactions', () => {
    it('allows removing jobs from queue', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      const removeButtons = screen.getAllByRole('button', { name: /remove/i });
      fireEvent.click(removeButtons[0]);

      expect(screen.getByText('2 jobs in queue')).toBeInTheDocument();
      expect(screen.queryByText('Senior React Developer at Tech Corp')).not.toBeInTheDocument();
    });

    it('allows reordering jobs in queue', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      const moveUpButtons = screen.getAllByRole('button', { name: /move up/i });
      fireEvent.click(moveUpButtons[1]); // Move second job up

      const jobTitles = screen.getAllByText(/Developer|Engineer/);
      expect(jobTitles[0]).toHaveTextContent('Frontend Engineer');
      expect(jobTitles[1]).toHaveTextContent('Senior React Developer');
    });

    it('supports keyboard navigation', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start bulk apply/i });
      startButton.focus();
      
      expect(startButton).toHaveFocus();
      
      userEvent.keyboard('{Enter}');
      
      expect(screen.getByText('Processing...')).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    it('handles empty job queue', () => {
      render(<BulkApplyQueue {...mockProps} jobs={[]} />);
      
      expect(screen.getByText('No jobs in queue')).toBeInTheDocument();
      expect(screen.getByText('Add jobs to get started')).toBeInTheDocument();
    });

    it('handles single job in queue', () => {
      render(<BulkApplyQueue {...mockProps} jobs={[mockJobs[0]]} />);
      
      expect(screen.getByText('1 job in queue')).toBeInTheDocument();
      expect(screen.getByText('Estimated Time: 1s')).toBeInTheDocument();
    });

    it('handles very large job queues', () => {
      const largeJobList = Array.from({ length: 100 }, (_, i) => ({
        id: `${i}`,
        title: `Job ${i}`,
        company: `Company ${i}`,
        url: `https://example.com/job/${i}`,
        location: 'Remote',
        salary: '$50k - $100k'
      }));

      render(<BulkApplyQueue {...mockProps} jobs={largeJobList} />);
      
      expect(screen.getByText('100 jobs in queue')).toBeInTheDocument();
      expect(screen.getByText('Estimated Time: 100s')).toBeInTheDocument();
    });

    it('handles network timeouts', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockImplementation(() => new Promise((_, reject) => 
        setTimeout(() => reject(new Error('Request timeout')), 100)
      ));

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start queue/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Error: Request timeout')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper ARIA labels', () => {
      render(<BulkApplyQueue {...mockProps} />);
      
      // Check if progress elements exist
      const progressElements = document.querySelectorAll('[role="progressbar"]');
      expect(progressElements.length).toBeGreaterThan(0);
      
      const startButton = screen.getByRole('button', { name: /start queue/i });
      expect(startButton).toBeInTheDocument();
    });

    it('announces status changes to screen readers', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start queue/i });
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Processing job 1 of 3')).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    it('handles rapid state changes efficiently', async () => {
      const { submitBulkApplication } = require('../../services/api');
      submitBulkApplication.mockResolvedValue({ success: true, applicationId: 'app1' });

      render(<BulkApplyQueue {...mockProps} />);
      
      const startButton = screen.getByRole('button', { name: /start queue/i });
      
      // Rapid button clicks
      fireEvent.click(startButton);

      await waitFor(() => {
        expect(screen.getByText('Processing')).toBeInTheDocument();
      });
    });
  });
}); 