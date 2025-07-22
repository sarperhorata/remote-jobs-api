import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobList from '../../components/JobList';

// Increase timeout for all tests in this file
jest.setTimeout(15000);

// Mock the jobService
jest.mock('../../services/AllServices', () => ({
  jobService: {
    getJobs: jest.fn()
  }
}));

// Import the mocked service
import { jobService } from '../../services/AllServices';
const mockGetJobs = jobService.getJobs as jest.MockedFunction<typeof jobService.getJobs>;

const renderJobList = (props = {}) => {
  return render(
    <BrowserRouter>
      <JobList {...props} />
    </BrowserRouter>
  );
};

describe('JobList Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockGetJobs.mockClear();
  });

  describe('Loading State', () => {
    test('shows loading message initially', () => {
      // Mock that never resolves to test loading state
      mockGetJobs.mockImplementation(() => new Promise(() => {}));
      
      renderJobList();
      
      expect(screen.getByText('Loading jobs...')).toBeInTheDocument();
    });
  });

  describe('Error State', () => {
    test('shows error message when API call fails', async () => {
      // Mock that rejects immediately
      mockGetJobs.mockRejectedValue(new Error('Network error'));
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Error loading jobs')).toBeInTheDocument();
      }, { timeout: 10000 });
    });
  });

  describe('Empty State', () => {
    test('shows no jobs message when data is empty', async () => {
      // Mock that resolves with empty array immediately
      mockGetJobs.mockResolvedValue([]);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('No jobs available')).toBeInTheDocument();
      }, { timeout: 10000 });
    });
  });

  describe('Success State', () => {
    test('renders jobs when data is loaded successfully', async () => {
      const mockJobs = [
        {
          _id: '1',
          id: '1',
          title: 'Senior Frontend Developer',
          company: { id: 'company1', name: 'TechCorp' },
          location: 'Remote',
          job_type: 'Full-time',
          description: 'Frontend developer position',
          created_at: '2023-01-01T00:00:00Z',
          company_logo: '💻',
          url: '#',
          is_active: true
        }
      ];
      
      // Mock that resolves with data immediately
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Latest Jobs')).toBeInTheDocument();
      }, { timeout: 10000 });
      
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('TechCorp')).toBeInTheDocument();
      expect(screen.getByText('Remote')).toBeInTheDocument();
    });
  });

  describe('Filters', () => {
    test('passes filters to jobService.getJobs', async () => {
      const filters = { location: 'Remote', job_type: 'Full-time' };
      mockGetJobs.mockResolvedValue([]);
      
      renderJobList({ filters });
      
      await waitFor(() => {
        expect(mockGetJobs).toHaveBeenCalledWith(filters);
      }, { timeout: 10000 });
    });
  });
});