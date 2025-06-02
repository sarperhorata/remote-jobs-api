import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import '@testing-library/jest-dom';
import Home from '../../pages/Home';
import { JobService } from '../../services/jobService';

// Mock JobService
jest.mock('../../services/jobService');
const mockJobService = JobService as jest.Mocked<typeof JobService>;

// Mock AuthModal component
jest.mock('../../components/AuthModal', () => {
  return function MockAuthModal({ isOpen, onClose }: any) {
    return isOpen ? (
      <div data-testid="auth-modal">
        <button onClick={onClose}>Close Modal</button>
      </div>
    ) : null;
  };
});

const renderHome = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: {
        retry: false,
      },
    },
  });

  return render(
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Home />
      </BrowserRouter>
    </QueryClientProvider>
  );
};

const mockFeaturedJobs = [
  {
    _id: '1',
    title: 'Frontend Developer',
    company: 'Tech Corp',
    location: 'Remote',
    job_type: 'Full-time',
    salary_range: '$60k - $80k',
    skills: ['React', 'TypeScript'],
    created_at: new Date().toISOString(),
    description: 'Great frontend role',
    is_active: true,
    url: 'https://example.com/job1'
  },
  {
    _id: '2',
    title: 'Backend Engineer',
    company: 'Software Inc',
    location: 'Remote (US)',
    job_type: 'Full-time',
    salary_range: '$70k - $90k',
    skills: ['Node.js', 'Python'],
    created_at: new Date().toISOString(),
    description: 'Backend development role',
    is_active: true,
    url: 'https://example.com/job2'
  }
];

describe('Home Page', () => {
  beforeEach(() => {
    mockJobService.getFeaturedJobs.mockResolvedValue(mockFeaturedJobs);
  });

  afterEach(() => {
    jest.clearAllMocks();
  });

  test('renders main heading and description', () => {
    renderHome();
    
    expect(screen.getByText(/Find Your Next/)).toBeInTheDocument();
    expect(screen.getByText(/Remote Buzz/)).toBeInTheDocument();
    expect(screen.getByText(/AI-powered job matching/)).toBeInTheDocument();
  });

  test('renders search form with keywords input', () => {
    renderHome();
    
    expect(screen.getByLabelText(/Keywords/)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Job title, skill, or company/)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Search/ })).toBeInTheDocument();
  });

  test('does not render removed fields (Region/City, Date Posted, Type)', () => {
    renderHome();
    
    // These fields should not be present
    expect(screen.queryByLabelText(/Region\/City/)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Date Posted/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Type:/)).not.toBeInTheDocument();
    expect(screen.queryByRole('radio')).not.toBeInTheDocument();
  });

  test('renders search input with extended width', () => {
    renderHome();
    
    const keywordsInput = screen.getByLabelText(/Keywords/);
    const keywordsDiv = keywordsInput.closest('.md\\:col-span-4');
    expect(keywordsDiv).toBeInTheDocument();
  });

  test('handles search form submission', async () => {
    renderHome();
    
    const input = screen.getByPlaceholderText('Job title, skill, or company');
    
    // Type in the input field
    fireEvent.change(input, { target: { value: 'React Developer' } });
    expect(input.value).toBe('React Developer');
    
    // Check the submit button with correct name
    const submitButton = screen.getByRole('button', { name: 'Search' });
    expect(submitButton).toBeInTheDocument();
    
    // Submit the form
    fireEvent.click(submitButton);
    
    // Check loading state
    await waitFor(() => {
      expect(submitButton).toBeDisabled();
    });
  });

  test('loads and renders featured jobs from API', async () => {
    renderHome();
    
    await waitFor(() => {
      expect(mockJobService.getFeaturedJobs).toHaveBeenCalled();
    });

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    });
  });

  test('renders Hot Remote Jobs section', async () => {
    renderHome();
    
    expect(screen.getByText(/Hot Remote Jobs/)).toBeInTheDocument();
    expect(screen.getByText(/Fresh opportunities from leading remote companies/)).toBeInTheDocument();
  });

  test('renders featured job cards with correct information', async () => {
    renderHome();
    
    await waitFor(() => {
      // Check job titles
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
      
      // Check companies
      expect(screen.getByText('Tech Corp')).toBeInTheDocument();
      expect(screen.getByText('Software Inc')).toBeInTheDocument();
      
      // Check job types
      expect(screen.getAllByText('Full-time')).toHaveLength(2);
      
      // Check skills tags
      expect(screen.getByText('React')).toBeInTheDocument();
      expect(screen.getByText('Node.js')).toBeInTheDocument();
    });
  });

  test('renders Buzz2Remote logo with bee icon', () => {
    renderHome();
    
    // Check for the main logo text in header
    const headerLogoText = screen.getAllByText('Buzz2Remote')[0]; // Get first occurrence (header)
    expect(headerLogoText).toBeInTheDocument();
    expect(screen.getByText(/Your Hive for Remote Opportunities/)).toBeInTheDocument();
  });

  test('does not render social media icons in footer', () => {
    renderHome();
    
    // The bug icon in header should not be counted as social media
    // Check that there are no typical social media patterns in footer
    const footer = screen.getByRole('contentinfo');
    const socialLinks = footer.querySelectorAll('a[href*="facebook"], a[href*="twitter"], a[href*="linkedin"], a[href*="instagram"]');
    expect(socialLinks).toHaveLength(0);
  });

  test('renders Help Center in For Job Seekers section', () => {
    renderHome();
    
    const jobSeekersSection = screen.getByText('For Job Seekers').closest('div');
    expect(jobSeekersSection).toBeInTheDocument();
    
    const helpCenterLink = screen.getByRole('link', { name: /Help Center/ });
    expect(helpCenterLink).toBeInTheDocument();
  });

  test('does not render Resources section', () => {
    renderHome();
    
    expect(screen.queryByText('Resources')).not.toBeInTheDocument();
  });

  test('opens auth modal when Get Started is clicked', () => {
    renderHome();
    
    const getStartedButton = screen.getByText('Get Started');
    fireEvent.click(getStartedButton);
    
    expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
  });

  test('opens auth modal when Sign up with Google is clicked', () => {
    renderHome();
    
    const signUpButton = screen.getByText('Sign up with Google');
    fireEvent.click(signUpButton);
    
    expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
  });

  test('renders Why Buzz2Remote features section', () => {
    renderHome();
    
    expect(screen.getByText('Why Buzz2Remote?')).toBeInTheDocument();
    expect(screen.getByText('AI-Powered Matching')).toBeInTheDocument();
    expect(screen.getByText('One-Click Apply')).toBeInTheDocument();
    expect(screen.getByText('Global Opportunities')).toBeInTheDocument();
  });

  test('fallback to static data when API fails', async () => {
    mockJobService.getFeaturedJobs.mockRejectedValue(new Error('API Error'));
    
    renderHome();
    
    await waitFor(() => {
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('TechBuzz Ltd.')).toBeInTheDocument();
    });
  });

  test('formats time ago correctly for job posting dates', async () => {
    const recentJob = {
      ...mockFeaturedJobs[0],
      created_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2 hours ago
    };
    
    mockJobService.getFeaturedJobs.mockResolvedValue([recentJob]);
    
    renderHome();
    
    await waitFor(() => {
      expect(screen.getByText(/2 hours ago/)).toBeInTheDocument();
    });
  });
}); 