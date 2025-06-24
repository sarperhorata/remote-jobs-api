import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import '@testing-library/jest-dom';
import Home from '../../pages/Home/Home';
import * as jobService from '../../services/jobService';

// Mock jobService
jest.mock('../../services/jobService');

const mockjobService = jobService as jest.Mocked<typeof jobService>;

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

const mockJobs = [
  {
    id: '1',
    title: 'Frontend Developer',
    company: 'Tech Corp',
    location: 'Remote',
    description: 'We are looking for a skilled frontend developer...',
    salary_min: 80000,
    salary_max: 120000,
    salary_currency: 'USD',
    posted_date: '2024-01-15T10:00:00Z',
    job_type: 'Full-time',
    experience_level: 'Mid-level',
    skills: ['React', 'TypeScript', 'CSS'],
    benefits: ['Health insurance', 'Remote work'],
    application_deadline: '2024-12-31',
    contact_email: 'hr@techcorp.com',
    contact_phone: '+1234567890',
    application_url: 'https://techcorp.com/apply/frontend-dev'
  },
  {
    id: '2',
    title: 'Backend Engineer',
    company: 'Startup Inc',
    location: 'San Francisco, CA',
    description: 'Join our growing team as a backend engineer...',
    salary_min: 90000,
    salary_max: 140000,
    salary_currency: 'USD',
    posted_date: '2024-01-14T15:30:00Z',
    job_type: 'Full-time',
    experience_level: 'Senior',
    skills: ['Node.js', 'Python', 'PostgreSQL'],
    benefits: ['Stock options', 'Flexible hours'],
    application_deadline: '2024-12-31',
    contact_email: 'jobs@startupinc.com',
    contact_phone: '+1987654321',
    application_url: 'https://startupinc.com/careers/backend'
  }
];

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

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockjobService.getFeaturedJobs.mockResolvedValue({
      success: true,
      jobs: mockJobs,
      total: 2
    });
  });

  it('renders main heading and description', () => {
    renderHome();
    
    expect(screen.getByText(/Find Your Next Remote Buzz/i)).toBeInTheDocument();
    expect(screen.getByText(/AI-powered job matching/i)).toBeInTheDocument();
  });

  it('renders search form', () => {
    renderHome();
    
    expect(screen.getByPlaceholderText(/Job title/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Location/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Search/i })).toBeInTheDocument();
  });

  it('renders featured jobs section', () => {
    renderHome();
    
    expect(screen.getByText(/Hot Remote Jobs/i)).toBeInTheDocument();
  });

  it('loads featured jobs from API', async () => {
    renderHome();
    
    await waitFor(() => {
      expect(mockjobService.getFeaturedJobs).toHaveBeenCalled();
    });
  });

  it('renders job cards when data is loaded', async () => {
    renderHome();
    
    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    });
  });

  it('handles search form submission', async () => {
    const mockNavigate = jest.fn();
    jest.doMock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useNavigate: () => mockNavigate
    }));

    renderHome();
    
    const searchButton = screen.getByRole('button', { name: /Search/i });
    fireEvent.click(searchButton);

    // Should navigate to jobs page
    expect(mockNavigate).toHaveBeenCalled();
  });

  test('renders search input with extended width', () => {
    renderHome();
    
    const keywordsInput = screen.getByLabelText(/Please enter job title/);
    const keywordsDiv = keywordsInput.closest('.md\\:col-span-4');
    expect(keywordsDiv).toBeInTheDocument();
  });

  test('does not render removed fields (Region/City, Date Posted, Type)', () => {
    renderHome();
    
    // These fields should not be present
    expect(screen.queryByLabelText(/Region\/City/)).not.toBeInTheDocument();
    expect(screen.queryByLabelText(/Date Posted/)).not.toBeInTheDocument();
    expect(screen.queryByText(/Type:/)).not.toBeInTheDocument();
    expect(screen.queryByRole('radio')).not.toBeInTheDocument();
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
    mockjobService.getFeaturedJobs.mockRejectedValue(new Error('API Error'));
    
    renderHome();
    
    await waitFor(() => {
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('TechBuzz Ltd.')).toBeInTheDocument();
    });
  });

  test('formats time ago correctly for job posting dates', async () => {
    const recentJob = {
      ...mockJobs[0],
      posted_date: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString() // 2 hours ago
    };
    
    mockjobService.getFeaturedJobs.mockResolvedValue({
      success: true,
      jobs: [recentJob],
      total: 1
    });
    
    renderHome();
    
    await waitFor(() => {
      expect(screen.getByText(/2 hours ago/)).toBeInTheDocument();
    });
  });
}); 