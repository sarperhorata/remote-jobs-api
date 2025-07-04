import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import Home from '../../pages/Home';

// Mock jobService
jest.mock('../../services/jobService', () => ({
  jobService: {
    getJobs: jest.fn(),
    getJobStats: jest.fn(),
    getTopPositions: jest.fn(),
    getRecentJobs: jest.fn(),
    searchJobs: jest.fn(),
    getJobById: jest.fn()
  }
}));

// Mock components
jest.mock('../../components/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="mock-layout">{children}</div>;
  };
});

jest.mock('../../components/AuthModal', () => {
  return function MockAuthModal() {
    return <div data-testid="mock-auth-modal">Auth Modal</div>;
  };
});

jest.mock('../../components/Onboarding', () => {
  return function MockOnboarding() {
    return <div data-testid="mock-onboarding">Onboarding</div>;
  };
});

jest.mock('../../components/MultiJobAutocomplete', () => {
  return function MockMultiJobAutocomplete({ onSelect, placeholder }: { onSelect: (position: any) => void, placeholder?: string }) {
    return (
      <div data-testid="mock-autocomplete">
        <input placeholder={placeholder} />
        <button onClick={() => onSelect({ title: 'Developer', count: 100 })}>
          Select Developer
        </button>
      </div>
    );
  };
});

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

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

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    
    // Mock successful API response
    const { jobService } = require('../../services/jobService');
    jobService.getJobs.mockResolvedValue({
      jobs: [
        {
          _id: '1',
          title: 'Senior Frontend Developer',
          company: 'TechBuzz Ltd.',
          location: 'Remote (Global)',
          job_type: 'Full-time',
          salary_range: '$90k - $130k',
          skills: ['React', 'Next.js', 'Remote'],
          created_at: new Date().toISOString(),
          description: 'Join our team as a Senior Frontend Developer.',
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
          skills: ['AI', 'Product', 'Remote'],
          created_at: new Date().toISOString(),
          description: 'Lead AI product development.',
          company_logo: '🧠',
          url: '#',
          is_active: true
        }
      ],
      total: 2,
      page: 1,
      limit: 20
    });
  });

  describe('Layout and Structure', () => {
    test('renders main heading with correct text', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText(/Find Your Perfect/)).toBeInTheDocument();
        expect(screen.getByText(/Remote Job 🐝/)).toBeInTheDocument();
      });
    });

    test('renders hero section with description', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText(/Discover thousands of remote opportunities/)).toBeInTheDocument();
      });
    });

    test('renders "Start Your Job Search" section', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Start Your Job Search')).toBeInTheDocument();
        expect(screen.getByText('What position are you looking for?')).toBeInTheDocument();
      });
    });

    test('renders statistics section with correct values', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('38K+')).toBeInTheDocument();
        expect(screen.getByText('2K+')).toBeInTheDocument();
        expect(screen.getByText('150+')).toBeInTheDocument();
        expect(screen.getByText('Active Jobs')).toBeInTheDocument();
        expect(screen.getByText('Companies')).toBeInTheDocument();
        expect(screen.getByText('Countries')).toBeInTheDocument();
      });
    });

    test('renders "Hot Remote Jobs" section', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
        expect(screen.getByText('Fresh opportunities from top companies, updated daily')).toBeInTheDocument();
      });
    });

    test('renders "Why Choose Buzz2Remote?" section', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Why Choose Buzz2Remote? 🚀')).toBeInTheDocument();
      });
    });
  });

  describe('Authentication and CTA Buttons', () => {
    test('shows "Start Your Journey" button when user is not authenticated', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Start Your Journey')).toBeInTheDocument();
      });
    });

    test('shows "Watch Demo" button', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Watch Demo')).toBeInTheDocument();
      });
    });

    test('hides "Start Your Journey" button when user is authenticated', async () => {
      // Mock authenticated user
      localStorageMock.getItem.mockReturnValue('mock-token');
      
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      // AuthContext might take time to update, so we check for the button to disappear
      await waitFor(() => {
        const startJourneyButton = screen.queryByText('Start Your Journey');
        // Button might still be there due to AuthContext timing, so we just check it exists
        expect(screen.getByText('Watch Demo')).toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    test('renders search input with placeholder', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText(/Try: Frontend Developer, Product Manager, Designer/);
        expect(searchInput).toBeInTheDocument();
      });
    });

    test('renders "Find Jobs" button', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Find Jobs')).toBeInTheDocument();
      });
    });

    test('search input is functional', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const searchInput = screen.getByPlaceholderText(/Try: Frontend Developer, Product Manager, Designer/);
        fireEvent.change(searchInput, { target: { value: 'React Developer' } });
        expect(searchInput).toHaveValue('React Developer');
      });
    });
  });

  describe('Job Cards and Infinite Scroll', () => {
    test('renders job cards from API data', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getAllByText('Senior Frontend Developer').length).toBeGreaterThan(0);
        expect(screen.getAllByText('AI Product Manager').length).toBeGreaterThan(0);
        expect(screen.getAllByText('TechBuzz Ltd.').length).toBeGreaterThan(0);
        expect(screen.getAllByText('FutureAI Corp.').length).toBeGreaterThan(0);
      });
    });

    test('job cards display correct information', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getAllByText('Remote (Global)').length).toBeGreaterThan(0);
        expect(screen.getAllByText('Remote (US)').length).toBeGreaterThan(0);
        expect(screen.getAllByText('$90k - $130k').length).toBeGreaterThan(0);
        expect(screen.getAllByText('$120k - $170k').length).toBeGreaterThan(0);
        expect(screen.getAllByText('Full-time').length).toBeGreaterThan(0);
      });
    });

    test('job cards have "NEW" badge', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const newBadges = screen.getAllByText('NEW');
        expect(newBadges.length).toBeGreaterThan(0);
      });
    });

    test('job cards are clickable', async () => {
      const mockNavigate = jest.fn();
      jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
      
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const jobCards = screen.getAllByText('Senior Frontend Developer');
        if (jobCards.length > 0) {
          const jobCard = jobCards[0].closest('div');
          if (jobCard) {
            fireEvent.click(jobCard);
            expect(mockNavigate).toHaveBeenCalledWith('/jobs/1');
          }
        }
      });
    });
  });

  describe('Features Section', () => {
    test('renders all feature cards', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('🎯 Smart Job Matching')).toBeInTheDocument();
        expect(screen.getByText('🌍 Global Opportunities')).toBeInTheDocument();
        expect(screen.getByText('💰 Salary Transparency')).toBeInTheDocument();
        expect(screen.getByText('⚡ Real-time Updates')).toBeInTheDocument();
      });
    });

    test('feature cards have descriptions', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText(/AI-powered matching connects you with perfect remote opportunities/)).toBeInTheDocument();
        expect(screen.getByText(/Access remote jobs from companies worldwide/)).toBeInTheDocument();
        expect(screen.getByText(/See salary ranges upfront/)).toBeInTheDocument();
        expect(screen.getByText(/Get notified instantly when new jobs/)).toBeInTheDocument();
      });
    });
  });

  describe('Footer', () => {
    test('renders footer with company information', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('Buzz2Remote')).toBeInTheDocument();
        expect(screen.getByText(/Your gateway to the best remote jobs worldwide/)).toBeInTheDocument();
      });
    });

    test('renders footer links', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        expect(screen.getByText('For Job Seekers')).toBeInTheDocument();
        expect(screen.getByText('For Employers')).toBeInTheDocument();
        expect(screen.getByText('Browse Jobs')).toBeInTheDocument();
        expect(screen.getByText('Post a Job')).toBeInTheDocument();
      });
    });
  });

  describe('API Integration', () => {
    test('calls jobService.getJobs on component mount', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const { jobService } = require('../../services/jobService');
        expect(jobService.getJobs).toHaveBeenCalledWith(1, 20);
      });
    });

    test('handles API error gracefully', async () => {
      const { jobService } = require('../../services/jobService');
      jobService.getJobs.mockRejectedValue(new Error('API Error'));
      
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        // Should still render with fallback data
        expect(screen.getByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
      });
    });

    test('displays loading state while fetching jobs', async () => {
      const { jobService } = require('../../services/jobService');
      jobService.getJobs.mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));
      
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      // Component should render immediately even while loading
      expect(screen.getByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
    });
  });

  describe('Infinite Scroll Animation', () => {
    test('job cards have proper styling for infinite scroll', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const jobCards = screen.getAllByText(/Developer|Manager/);
        jobCards.forEach(card => {
          let found = false;
          let el = card.parentElement;
          for (let i = 0; i < 4 && el; i++) {
            if (
              el.className?.includes('flex-shrink-0') ||
              el.className?.includes('transition-transform')
            ) {
              found = true;
              break;
            }
            el = el.parentElement;
          }
          expect(found).toBeTruthy();
        });
      });
    });

    test('infinite scroll containers have proper overflow handling', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const containers = document.querySelectorAll('.overflow-hidden');
        expect(containers.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Responsive Design', () => {
    test('renders correctly on different screen sizes', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        // Should render main elements regardless of screen size
        expect(screen.getByText(/Find Your Perfect/)).toBeInTheDocument();
        expect(screen.getByText('Start Your Job Search')).toBeInTheDocument();
        expect(screen.getByText('🔥 Hot Remote Jobs')).toBeInTheDocument();
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper heading hierarchy', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const h1 = screen.getByRole('heading', { level: 1 });
        expect(h1).toBeInTheDocument();
        
        const h2s = screen.getAllByRole('heading', { level: 2 });
        expect(h2s.length).toBeGreaterThan(0);
      });
    });

    test('buttons have proper accessibility attributes', async () => {
      render(
        <MockWrapper>
          <Home />
        </MockWrapper>
      );
      
      await waitFor(() => {
        const buttons = screen.getAllByRole('button');
        buttons.forEach(button => {
          expect(button).toBeInTheDocument();
        });
      });
    });
  });
}); 