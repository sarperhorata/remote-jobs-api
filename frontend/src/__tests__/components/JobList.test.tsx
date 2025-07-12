import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import JobList from '../../components/JobList';
import { jobService } from '../../services/AllServices';

// Mock the jobService
jest.mock('../../services/AllServices', () => ({
  jobService: {
    getJobs: jest.fn()
  }
}));

const mockJobService = jobService as jest.Mocked<typeof jobService>;

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

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
  },
  {
    _id: '3',
    id: '3',
    title: 'Full Stack Developer',
    company: { id: 'company3', name: 'StartupXYZ' },
    location: 'New York',
    job_type: 'Full-time',
    description: 'Full stack developer position',
    created_at: '2023-01-01T00:00:00Z',
    company_logo: '🚀',
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
  });

  describe('Loading State', () => {
    test('shows loading message initially', () => {
      mockJobService.getJobs.mockImplementation(() => new Promise(() => {})); // Never resolves
      
      renderJobList();
      
      expect(screen.getByText('Loading jobs...')).toBeInTheDocument();
    });
  });

  describe('Success State', () => {
    test('renders jobs when data is loaded successfully', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Latest Jobs')).toBeInTheDocument();
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
        expect(screen.getByText('Full Stack Developer')).toBeInTheDocument();
      });
    });

    test('renders company names correctly', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
        expect(screen.getByText('DataFlow')).toBeInTheDocument();
        expect(screen.getByText('StartupXYZ')).toBeInTheDocument();
      });
    });

    test('renders job locations correctly', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Remote')).toBeInTheDocument();
        expect(screen.getByText('San Francisco')).toBeInTheDocument();
        expect(screen.getByText('New York')).toBeInTheDocument();
      });
    });

    test('creates correct links for each job', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const jobLinks = screen.getAllByRole('link');
        expect(jobLinks).toHaveLength(3);
        
        expect(jobLinks[0]).toHaveAttribute('href', '/jobs/1');
        expect(jobLinks[1]).toHaveAttribute('href', '/jobs/2');
        expect(jobLinks[2]).toHaveAttribute('href', '/jobs/3');
      });
    });
  });

  describe('Empty State', () => {
    test('shows no jobs message when data is empty', async () => {
      mockJobService.getJobs.mockResolvedValue([]);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('No jobs available')).toBeInTheDocument();
      });
    });

    test('shows no jobs message when data is null', async () => {
      mockJobService.getJobs.mockResolvedValue(null);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('No jobs available')).toBeInTheDocument();
      });
    });
  });

  describe('Error State', () => {
    test('shows error message when API call fails', async () => {
      mockJobService.getJobs.mockRejectedValue(new Error('Network error'));
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Error loading jobs')).toBeInTheDocument();
      });
    });

    test('handles generic error when error is not an Error instance', async () => {
      mockJobService.getJobs.mockRejectedValue('Unknown error');
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Error loading jobs')).toBeInTheDocument();
      });
    });
  });

  describe('Filters', () => {
    test('passes filters to jobService.getJobs', async () => {
      const filters = { location: 'Remote', job_type: 'Full-time' };
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList({ filters });
      
      await waitFor(() => {
        expect(mockJobService.getJobs).toHaveBeenCalledWith(filters);
      });
    });

    test('uses empty object as default filters', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        expect(mockJobService.getJobs).toHaveBeenCalledWith({});
      });
    });

    test('refetches when filters change', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      const { rerender } = renderJobList({ filters: { location: 'Remote' } });
      
      await waitFor(() => {
        expect(mockJobService.getJobs).toHaveBeenCalledWith({ location: 'Remote' });
      });

      // Change filters
      rerender(
        <BrowserRouter>
          <JobList filters={{ location: 'San Francisco' }} />
        </BrowserRouter>
      );

      await waitFor(() => {
        expect(mockJobService.getJobs).toHaveBeenCalledWith({ location: 'San Francisco' });
      });
    });
  });

  describe('Limit Prop', () => {
    test('renders with limit prop (though not used in current implementation)', () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList({ limit: 5 });
      
      // Component should still render normally
      expect(screen.getByText('Latest Jobs')).toBeInTheDocument();
    });
  });

  describe('onJobSelected Callback', () => {
    test('renders with onJobSelected prop (though not used in current implementation)', () => {
      const mockOnJobSelected = jest.fn();
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList({ onJobSelected: mockOnJobSelected });
      
      // Component should still render normally
      expect(screen.getByText('Latest Jobs')).toBeInTheDocument();
    });
  });

  describe('Styling', () => {
    test('has correct container styling', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const container = screen.getByText('Latest Jobs').closest('div');
        expect(container).toHaveClass('space-y-6');
      });
    });

    test('has correct job item styling', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const jobItems = screen.getAllByText(/Developer|Engineer/);
        jobItems.forEach(item => {
          const jobContainer = item.closest('div');
          expect(jobContainer).toHaveClass('border', 'p-4', 'rounded-lg', 'hover:shadow-md', 'transition');
        });
      });
    });

    test('has correct title styling', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const titles = screen.getAllByText(/Developer|Engineer/);
        titles.forEach(title => {
          expect(title).toHaveClass('text-lg', 'font-medium');
        });
      });
    });

    test('has correct subtitle styling', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const companyNames = screen.getAllByText(/TechCorp|DataFlow|StartupXYZ/);
        companyNames.forEach(name => {
          const container = name.closest('div');
          expect(container).toHaveClass('flex', 'items-center', 'text-gray-600', 'mt-2');
        });
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper heading structure', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const heading = screen.getByRole('heading', { level: 2 });
        expect(heading).toHaveTextContent('Latest Jobs');
      });
    });

    test('has proper link elements', async () => {
      mockJobService.getJobs.mockResolvedValue(mockJobs);
      
      renderJobList();
      
      await waitFor(() => {
        const links = screen.getAllByRole('link');
        expect(links).toHaveLength(3);
        
        links.forEach(link => {
          expect(link).toHaveAttribute('href');
        });
      });
    });
  });

  describe('Edge Cases', () => {
    test('handles jobs with missing company name', async () => {
      const jobsWithMissingCompany = [
        {
          _id: '1',
          id: '1',
          title: 'Developer',
          company: { id: 'company1', name: undefined as any },
          location: 'Remote',
          job_type: 'Full-time',
          description: 'Developer position',
          created_at: '2023-01-01T00:00:00Z',
          company_logo: '💻',
          url: '#',
          is_active: true
        }
      ];
      mockJobService.getJobs.mockResolvedValue(jobsWithMissingCompany);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Developer')).toBeInTheDocument();
        // Should not crash when company name is undefined
      });
    });

    test('handles jobs with missing location', async () => {
      const jobsWithMissingLocation = [
        {
          _id: '1',
          id: '1',
          title: 'Developer',
          company: { id: 'company1', name: 'TechCorp' },
          location: undefined as any,
          job_type: 'Full-time',
          description: 'Developer position',
          created_at: '2023-01-01T00:00:00Z',
          company_logo: '💻',
          url: '#',
          is_active: true
        }
      ];
      mockJobService.getJobs.mockResolvedValue(jobsWithMissingLocation);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Developer')).toBeInTheDocument();
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
        // Should not crash when location is undefined
      });
    });

    test('handles jobs with missing id', async () => {
      const jobsWithMissingId = [
        {
          _id: '1',
          id: undefined as any,
          title: 'Developer',
          company: { id: 'company1', name: 'TechCorp' },
          location: 'Remote',
          job_type: 'Full-time',
          description: 'Developer position',
          created_at: '2023-01-01T00:00:00Z',
          company_logo: '💻',
          url: '#',
          is_active: true
        }
      ];
      mockJobService.getJobs.mockResolvedValue(jobsWithMissingId);
      
      renderJobList();
      
      await waitFor(() => {
        expect(screen.getByText('Developer')).toBeInTheDocument();
        // Should not crash when id is undefined
      });
    });
  });
});