import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import Jobs from '../../pages/Jobs';
import { jobService } from '../../services/jobService';
import '@testing-library/jest-dom';

// Mock jobService
jest.mock('../../services/jobService');
const mockjobService = jobService as jest.Mocked<typeof jobService>;

// Mock useSearchParams
const mockSearchParams = new URLSearchParams();
const mockSetSearchParams = jest.fn();

jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useSearchParams: () => [mockSearchParams, mockSetSearchParams],
  Link: ({ children, to }: { children: React.ReactNode; to: string }) => (
    <a href={to}>{children}</a>
  ),
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

const mockJobs = [
  {
    _id: '1',
    title: 'Senior Frontend Developer',
    company: 'TechBuzz Ltd.',
    location: 'Remote (Global)',
    job_type: 'Full-time',
    salary_range: '$90k - $130k',
    skills: ['React', 'TypeScript', 'Next.js'],
    created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    description: 'Join our team as a Senior Frontend Developer working on cutting-edge web applications.',
    company_logo: '💻',
    url: '#',
    is_active: true
  },
  {
    _id: '2',
    title: 'AI Product Manager',
    company: 'FutureAI Corp.',
    location: 'Remote (US)',
    job_type: 'Full-time',
    salary_range: '$120k - $170k',
    skills: ['AI', 'Product Management', 'Strategy'],
    created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
    description: 'Lead AI product development and strategy for innovative machine learning solutions.',
    company_logo: '🧠',
    url: '#',
    is_active: true
  }
];

describe('Jobs', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Clear URL search params
    const keys = Array.from(mockSearchParams.keys());
    keys.forEach(key => mockSearchParams.delete(key));
    
    mockjobService.searchJobs.mockResolvedValue({
      jobs: mockJobs,
      total: 1890
    });
  });

  it('renders jobs page with header and filters', async () => {
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      expect(screen.getByText('All Jobs')).toBeInTheDocument();
      expect(screen.getByText('1,890 remote jobs found')).toBeInTheDocument();
      expect(screen.getAllByText('Filters')[0]).toBeInTheDocument();
    });
  });

  it('displays search params in header when provided', async () => {
    mockSearchParams.set('position', 'Frontend Developer');
    mockSearchParams.set('location', 'Europe');
    
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      expect(screen.getByText((content, element) => {
        return element?.textContent === 'Frontend Developer in Europe';
      })).toBeInTheDocument();
    });
  });

  it('shows loading state initially', () => {
    renderWithRouter(<Jobs />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
    
    // Should show skeleton loaders
    const skeletons = document.querySelectorAll('.animate-pulse');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('displays job cards after loading', async () => {
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('AI Product Manager')).toBeInTheDocument();
      expect(screen.getByText('TechBuzz Ltd.')).toBeInTheDocument();
      expect(screen.getByText('FutureAI Corp.')).toBeInTheDocument();
    });
  });

  it('shows job details in cards', async () => {
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      // Check job details
      expect(screen.getByText('Remote (Global)')).toBeInTheDocument();
      expect(screen.getByText('$90k - $130k')).toBeInTheDocument();
      // Use getAllByText for elements that appear multiple times
      expect(screen.getAllByText('Full-time')[0]).toBeInTheDocument();
      
      // Check skills
      expect(screen.getByText('React')).toBeInTheDocument();
      expect(screen.getByText('TypeScript')).toBeInTheDocument();
      expect(screen.getByText('AI')).toBeInTheDocument();
    });
  });

  it('shows basic filter structure', async () => {
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      // Just check that basic filter structure exists - use getAllByText
      expect(screen.getAllByText('Filters')[0]).toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    mockjobService.searchJobs.mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching jobs:', expect.any(Error));
    });
    
    consoleSpy.mockRestore();
  });

  it('provides links to view job details', async () => {
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      const viewDetailsLinks = screen.getAllByText('View Details');
      expect(viewDetailsLinks).toHaveLength(mockJobs.length);
      
      // Check that links have correct href
      viewDetailsLinks.forEach((link, index) => {
        expect(link.closest('a')).toHaveAttribute('href', `/jobs/${mockJobs[index]._id}`);
      });
    });
  });

  it('displays job descriptions with truncation', async () => {
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      expect(screen.getByText(/Join our team as a Senior Frontend Developer/)).toBeInTheDocument();
      expect(screen.getByText(/Lead AI product development and strategy/)).toBeInTheDocument();
    });
  });

  it('shows time ago formatting correctly', async () => {
    renderWithRouter(<Jobs />);
    
    await waitFor(() => {
      expect(screen.getAllByText(/ago/)).toHaveLength(mockJobs.length * 2); // In both places
    });
  });
}); 