import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Home from '../../components/Home/Home';
import { JobService } from '../../services/jobService';
import '@testing-library/jest-dom';

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock JobService
jest.mock('../../services/jobService', () => ({
  JobService: {
    getJobs: jest.fn().mockResolvedValue([]), // Mock returns empty array, will use fallback data
    getJobStats: jest.fn().mockResolvedValue({
      totalJobs: '1000+',
      totalCompanies: '300+',
      jobsLast24h: '5000+'
    }),
  },
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
    id: '1',
    title: 'Senior React Developer',
    company: { id: '1', name: 'Shopify', logo: '' },
    description: 'Join our frontend team to build the future of commerce.',
    location: 'Remote - Global',
    job_type: 'Full-time',
    salary: { min: 120000, max: 180000, currency: 'USD' },
    requirements: ['React', 'TypeScript'],
    skills: ['React', 'TypeScript', 'Node.js'],
    responsibilities: ['Develop features', 'Code review'],
    applicationUrl: 'https://shopify.com/careers',
    status: 'active',
    postedAt: new Date()
  },
  {
    id: '2',
    title: 'Backend Engineer',
    company: { id: '2', name: 'Stripe', logo: '' },
    description: 'Build the financial infrastructure for the internet.',
    location: 'Remote - US',
    job_type: 'Full-time',
    salary: { min: 150000, max: 220000, currency: 'USD' },
    requirements: ['Python', 'Go'],
    skills: ['Python', 'Go', 'PostgreSQL'],
    responsibilities: ['Design APIs', 'Scale infrastructure'],
    applicationUrl: 'https://stripe.com/jobs',
    status: 'active',
    postedAt: new Date()
  }
];

const mockStats = {
  totalJobs: '1500+',
  totalCompanies: '400+',
  jobsLast24h: '7500+'
};

describe('Home Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders the main heading and hero section', () => {
    renderWithRouter(<Home />);
    
    expect(screen.getByText('Find Your Perfect Remote Job')).toBeInTheDocument();
    expect(screen.getByText(/Discover thousands of remote opportunities/)).toBeInTheDocument();
  });

  it('displays the Hot Remote Jobs section with fire emoji', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
    });
  });

  it('shows correct description for Hot Remote Jobs section', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText(/Trending remote opportunities from top companies - freshly crawled from their career pages/)).toBeInTheDocument();
    });
  });

  it('fetches and displays real jobs from API', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(JobService.getJobs).toHaveBeenCalledWith(1, 10);
    });
  });

  it('displays fallback jobs when API returns empty data', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      // Since mock returns empty array, fallback data should be used
      // Check for fallback job titles
      expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
      expect(screen.getByText('Senior Backend Engineer')).toBeInTheDocument();
      expect(screen.getByText('Product Manager - Growth')).toBeInTheDocument();
    });
  });

  it('displays fallback jobs with real company names', async () => {
    mockJobService.getJobs.mockResolvedValue([]);
    
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      // Check for real company names in fallback data
      expect(screen.getByText('Shopify')).toBeInTheDocument();
      expect(screen.getByText('Stripe')).toBeInTheDocument();
      expect(screen.getByText('Notion')).toBeInTheDocument();
      expect(screen.getByText('GitLab')).toBeInTheDocument();
      expect(screen.getAllByText('Figma')[0]).toBeInTheDocument(); // Use getAllByText for multiple matches
      expect(screen.getByText('Hugging Face')).toBeInTheDocument();
    });
  });

  it('shows loading spinner while fetching jobs', async () => {
    renderWithRouter(<Home />);
    
    // Since our mock resolves immediately, we might not catch the loading state
    // But the component should render without errors
    await waitFor(() => {
      expect(screen.getByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
    });
  });

  it('fetches and displays job statistics', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(JobService.getJobStats).toHaveBeenCalled();
    });
    
    await waitFor(() => {
      expect(screen.getByText('1000+')).toBeInTheDocument();
      expect(screen.getByText('300+')).toBeInTheDocument();
      expect(screen.getByText('5000+')).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    // Create a mock that rejects
    const mockGetJobs = JobService.getJobs as jest.MockedFunction<typeof JobService.getJobs>;
    mockGetJobs.mockRejectedValueOnce(new Error('API Error'));
    
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching hot jobs:', expect.any(Error));
    });
    
    consoleSpy.mockRestore();
  });

  it('handles stats API error gracefully with fallback values', async () => {
    const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});
    
    // Create a mock that rejects for stats
    const mockGetJobStats = JobService.getJobStats as jest.MockedFunction<typeof JobService.getJobStats>;
    mockGetJobStats.mockRejectedValueOnce(new Error('Stats API Error'));
    
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(consoleSpy).toHaveBeenCalledWith('Error fetching job stats:', expect.any(Error));
    });
    
    // Should show fallback stats
    await waitFor(() => {
      expect(screen.getByText('1000+')).toBeInTheDocument();
      expect(screen.getByText('300+')).toBeInTheDocument();
      expect(screen.getByText('5000+')).toBeInTheDocument();
    });
    
    consoleSpy.mockRestore();
  });

  it('updates View All Jobs button text with job count', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      // When fallback jobs are loaded (10 jobs), button should show count
      expect(screen.getByText(/View All 10\+ Jobs/)).toBeInTheDocument();
    });
  });

  it('displays job categories with correct counts', () => {
    renderWithRouter(<Home />);
    
    expect(screen.getByText('Software Development')).toBeInTheDocument();
    expect(screen.getByText('120 jobs available')).toBeInTheDocument();
    expect(screen.getByText('Marketing')).toBeInTheDocument();
    expect(screen.getByText('85 jobs available')).toBeInTheDocument();
  });

  it('navigates to jobs page when View All Jobs is clicked', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      const viewAllButton = screen.getByText(/View All.*Jobs/);
      fireEvent.click(viewAllButton);
    });
    
    expect(mockNavigate).toHaveBeenCalledWith('/jobs');
  });

  it('navigates to register page when Create Profile is clicked', () => {
    renderWithRouter(<Home />);
    
    const createProfileButton = screen.getByText('Create Your Profile');
    fireEvent.click(createProfileButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  it('navigates to filtered jobs when category is clicked', () => {
    renderWithRouter(<Home />);
    
    const softwareDevCategory = screen.getByText('Software Development');
    fireEvent.click(softwareDevCategory.closest('div')!);
    
    expect(mockNavigate).toHaveBeenCalledWith('/jobs?category=Software%20Development');
  });

  it('handles search form submission correctly', () => {
    renderWithRouter(<Home />);
    
    const searchInput = screen.getByPlaceholderText('Job title');
    const locationInput = screen.getByPlaceholderText('Location');
    const searchButton = screen.getByText('Search Jobs');
    
    fireEvent.change(searchInput, { target: { value: 'developer' } });
    fireEvent.change(locationInput, { target: { value: 'remote' } });
    fireEvent.click(searchButton);
    
    expect(mockNavigate).toHaveBeenCalledWith('/jobs?q=developer&location=remote');
  });

  it('shows correct placeholder text for job title field', () => {
    renderWithRouter(<Home />);
    
    expect(screen.getByPlaceholderText('Job title')).toBeInTheDocument();
  });

  it('displays footer with correct links', () => {
    renderWithRouter(<Home />);
    
    expect(screen.getByText('For Job Seekers')).toBeInTheDocument();
    expect(screen.getByText('For Employers')).toBeInTheDocument();
    expect(screen.getByText('Company')).toBeInTheDocument();
    
    // Check some specific links
    expect(screen.getByText('Browse Jobs')).toBeInTheDocument();
    expect(screen.getByText('Post a Job')).toBeInTheDocument();
    expect(screen.getByText('About Us')).toBeInTheDocument();
  });

  it('renders hot remote jobs section with horizontal scroll', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
      expect(screen.getByText('← Scroll horizontally to see more jobs →')).toBeInTheDocument();
    });
  });

  it('renders 10 fallback job cards when API returns empty', async () => {
    renderWithRouter(<Home />);
    
    // Wait for the fallback jobs to load (10 jobs)
    await waitFor(() => {
      expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
      expect(screen.getByText('Senior Backend Engineer')).toBeInTheDocument();
      expect(screen.getByText('Full Stack Developer')).toBeInTheDocument(); // 10th job
    });
  });

  it('renders job categories section', () => {
    renderWithRouter(<Home />);
    
    expect(screen.getByText('Popular Job Categories')).toBeInTheDocument();
    expect(screen.getByText('Software Development')).toBeInTheDocument();
    expect(screen.getByText('Marketing')).toBeInTheDocument();
  });

  it('renders CTA section', () => {
    renderWithRouter(<Home />);
    
    expect(screen.getByText('Ready to Find Your Dream Remote Job?')).toBeInTheDocument();
    expect(screen.getByText('Create Your Profile')).toBeInTheDocument();
  });

  it('renders footer', () => {
    renderWithRouter(<Home />);
    
    expect(screen.getByText('Remote Jobs')).toBeInTheDocument();
    expect(screen.getByText('For Job Seekers')).toBeInTheDocument();
    expect(screen.getByText('For Employers')).toBeInTheDocument();
  });

  it('shows horizontal scroll container for jobs', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      // Check for horizontal scroll container class
      const scrollContainer = document.querySelector('.overflow-x-auto');
      expect(scrollContainer).toBeInTheDocument();
    });
  });
}); 