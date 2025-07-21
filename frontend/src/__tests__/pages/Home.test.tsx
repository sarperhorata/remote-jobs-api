import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Home from '../../pages/Home';

// Mock the job service functions
jest.mock('../../services/jobService', () => ({
  getJobs: jest.fn(),
  getTopPositions: jest.fn(),
  getJobStatistics: jest.fn(),
}));

// Import the mocked functions
import { getJobs, getTopPositions, getJobStatistics } from '../../services/jobService';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Helper function to render with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    
    // Mock successful API responses
    (getJobs as jest.Mock).mockResolvedValue({
      jobs: [
        {
          _id: '1',
          title: 'Frontend Developer',
          company: 'Tech Corp',
          location: 'Remote',
          salary: '$80,000 - $120,000',
          type: 'Full-time',
          description: 'We are looking for a talented frontend developer...',
          requirements: ['React', 'TypeScript', '3+ years experience'],
          benefits: ['Health insurance', 'Remote work', 'Flexible hours'],
          posted_date: '2024-01-15',
          application_deadline: '2024-02-15',
          contact_email: 'jobs@techcorp.com',
          company_logo: 'https://example.com/logo.png',
          tags: ['React', 'TypeScript', 'Frontend'],
          experience_level: 'Mid-level',
          remote_friendly: true,
          visa_sponsorship: false,
          equity: false,
          relocation_assistance: false,
        },
        {
          _id: '2',
          title: 'Backend Developer',
          company: 'Startup Inc',
          location: 'San Francisco, CA',
          salary: '$100,000 - $150,000',
          type: 'Full-time',
          description: 'Join our growing team as a backend developer...',
          requirements: ['Python', 'Django', 'PostgreSQL'],
          benefits: ['Stock options', 'Health insurance', 'Unlimited PTO'],
          posted_date: '2024-01-10',
          application_deadline: '2024-02-10',
          contact_email: 'careers@startupinc.com',
          company_logo: 'https://example.com/startup-logo.png',
          tags: ['Python', 'Django', 'Backend'],
          experience_level: 'Senior',
          remote_friendly: true,
          visa_sponsorship: true,
          equity: true,
          relocation_assistance: true,
        },
      ],
      total: 2,
      page: 1,
      totalPages: 1,
    });

    (getTopPositions as jest.Mock).mockResolvedValue([
      { _id: 'Developer', count: 5000 },
      { _id: 'Manager', count: 3000 },
      { _id: 'Designer', count: 2000 },
      { _id: 'Analyst', count: 1500 },
      { _id: 'Engineer', count: 4000 },
    ]);

    (getJobStatistics as jest.Mock).mockResolvedValue({
      total_jobs: 38500,
      active_jobs: 32000,
      total_companies: 1500,
      remote_jobs: 28000,
    });
  });

  it('renders main heading and hero section correctly', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText(/Uzaktan Çalışma Hayallerini Gerçeğe Dönüştür/i)).toBeInTheDocument();
    });
    
    expect(screen.getByText(/Dünyanın en iyi uzaktan çalışma fırsatlarını keşfet/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /iş ara/i })).toBeInTheDocument();
  });

  it('renders statistics section with data from API', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('38,500+')).toBeInTheDocument();
      expect(screen.getByText('32,000+')).toBeInTheDocument();
      expect(screen.getByText('1,500+')).toBeInTheDocument();
      expect(screen.getByText('28,000+')).toBeInTheDocument();
    });
  });

  it('renders "Hot Remote Jobs" and displays job cards', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText(/Hot Remote Jobs/i)).toBeInTheDocument();
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();
    });
  });

  it('job cards are clickable and navigate to job details', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      const jobCard = screen.getByText('Frontend Developer');
      fireEvent.click(jobCard);
      expect(mockNavigate).toHaveBeenCalledWith('/jobs/1');
    });
  });

  it('calls jobService.getJobs on component mount with correct pagination', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(getJobs).toHaveBeenCalledWith({
        page: 1,
        limit: 6,
        sort: 'posted_date',
        order: 'desc',
      });
    });
  });

  it('renders all feature cards in "Why Choose Buzz2Remote?" section', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText(/Why Choose Buzz2Remote\?/i)).toBeInTheDocument();
      expect(screen.getByText(/Curated Remote Jobs/i)).toBeInTheDocument();
      expect(screen.getByText(/Smart Matching/i)).toBeInTheDocument();
      expect(screen.getByText(/Global Opportunities/i)).toBeInTheDocument();
      expect(screen.getByText(/Career Growth/i)).toBeInTheDocument();
    });
  });

  it('displays top positions from API', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText('Developer')).toBeInTheDocument();
      expect(screen.getByText('Manager')).toBeInTheDocument();
      expect(screen.getByText('Designer')).toBeInTheDocument();
    });
  });

  it('search form is functional', async () => {
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      const searchInput = screen.getByPlaceholderText(/job title, keywords, or company/i);
      const locationInput = screen.getByPlaceholderText(/location/i);
      const searchButton = screen.getByRole('button', { name: /iş ara/i });
      
      expect(searchInput).toBeInTheDocument();
      expect(locationInput).toBeInTheDocument();
      expect(searchButton).toBeInTheDocument();
    });
  });

  it('handles loading states correctly', async () => {
    // Mock a delayed response
    (getJobs as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        jobs: [],
        total: 0,
        page: 1,
        totalPages: 0,
      }), 100))
    );
    
    renderWithRouter(<Home />);
    
    // Should show loading state initially
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.queryByTestId('loading-spinner')).not.toBeInTheDocument();
    });
  });

  it('handles API errors gracefully', async () => {
    (getJobs as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    renderWithRouter(<Home />);
    
    await waitFor(() => {
      expect(screen.getByText(/Something went wrong/i)).toBeInTheDocument();
    });
  });
}); 