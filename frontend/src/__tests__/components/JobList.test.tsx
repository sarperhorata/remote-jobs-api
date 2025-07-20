import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobList from '../../components/JobList';

// Mock the jobService
jest.mock('../../services/AllServices', () => ({
  jobService: {
    getJobs: jest.fn()
  }
}));

// Import the mocked service
import { jobService } from '../../services/AllServices';
const mockGetJobs = jobService.getJobs as jest.MockedFunction<typeof jobService.getJobs>;

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
  },
  {
    _id: '2',
    id: '2',
    title: 'Backend Engineer',
    company: { id: 'company2', name: 'DataFlow' },
    location: 'San Francisco',
    job_type: 'Full-time',
    description: 'Backend engineer position',
    created_at: '2023-01-01T00:00:00Z',
    company_logo: '🔧',
    url: '#',
    is_active: true
  }
];

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
      mockGetJobs.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      renderJobList();
      
      expect(screen.getByText('Loading jobs...')).toBeInTheDocument();
    });
  });

  describe('Success State', () => {
    test('renders jobs when data is loaded successfully', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Latest Jobs')).toBeInTheDocument();
      }, { timeout: 3000 });
      
      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('renders company names correctly', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
        expect(screen.getByText('DataFlow')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('renders job locations correctly', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Remote')).toBeInTheDocument();
        expect(screen.getByText('San Francisco')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('creates correct links for each job', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const jobLinks = screen.getAllByRole('link');
        expect(jobLinks).toHaveLength(2);
        
        expect(jobLinks[0]).toHaveAttribute('href', '/jobs/1');
        expect(jobLinks[1]).toHaveAttribute('href', '/jobs/2');
      }, { timeout: 3000 });
    });
  });

  describe('Empty State', () => {
    test('shows no jobs message when data is empty', async () => {
      mockGetJobs.mockResolvedValue([]);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('No jobs available')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('shows no jobs message when data is null', async () => {
      mockGetJobs.mockResolvedValue(null);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('No jobs available')).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Error State', () => {
    test('shows error message when API call fails', async () => {
      mockGetJobs.mockRejectedValue(new Error('Network error'));
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Error loading jobs')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('handles generic error when error is not an Error instance', async () => {
      mockGetJobs.mockRejectedValue('Unknown error');
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Error loading jobs')).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });

  describe('Filters', () => {
    test('passes filters to jobService.getJobs', async () => {
      const filters = { location: 'Remote', job_type: 'Full-time' };
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList({ filters });
      
      await waitFor(() => {
        expect(mockGetJobs).toHaveBeenCalledWith(filters);
      }, { timeout: 3000 });
    });
  });

  describe('Styling', () => {
    test('has correct title styling', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const titles = screen.getAllByText(/Developer|Engineer/);
        titles.forEach(title => {
          expect(title).toHaveClass('text-lg', 'font-medium');
        });
      }, { timeout: 3000 });
    });

    test('has correct container styling', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const container = screen.getByText('Latest Jobs').closest('div');
        expect(container).toHaveClass('space-y-6');
      }, { timeout: 3000 });
    });
  });

  describe('Accessibility', () => {
    test('has proper heading structure', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const heading = screen.getByRole('heading', { level: 2 });
        expect(heading).toHaveTextContent('Latest Jobs');
      }, { timeout: 3000 });
    });

    test('has proper link elements', async () => {
      mockGetJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const links = screen.getAllByRole('link');
        expect(links).toHaveLength(2);
        
        links.forEach(link => {
          expect(link).toHaveAttribute('href');
        });
      }, { timeout: 3000 });
    });
  });

  describe('Edge Cases', () => {
    test('handles jobs with missing company name', async () => {
      const jobsWithMissingCompany = [
        {
          ...mockJobs[0],
          company: { id: 'company1', name: undefined }
        }
      ];
      mockGetJobs.mockResolvedValue(jobsWithMissingCompany);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Developer')).toBeInTheDocument();
        expect(screen.getByText('Unknown Company')).toBeInTheDocument();
      }, { timeout: 3000 });
    });

    test('handles jobs with missing location', async () => {
      const jobsWithMissingLocation = [
        {
          ...mockJobs[0],
          location: undefined
        }
      ];
      mockGetJobs.mockResolvedValue(jobsWithMissingLocation);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Developer')).toBeInTheDocument();
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
        expect(screen.getByText('Location not specified')).toBeInTheDocument();
      }, { timeout: 3000 });
    });
  });
});