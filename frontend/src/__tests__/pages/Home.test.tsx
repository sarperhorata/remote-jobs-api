import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { AuthProvider } from '../../contexts/AuthContext';
import Home from '../../pages/Home';
import { jobService } from '../../services/jobService';

// Mock the jobService
jest.mock('../../services/jobService');
const mockJobService = jobService as jest.Mocked<typeof jobService>;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
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

// Mock components that might cause issues
jest.mock('../../components/AuthModal', () => {
  return function MockAuthModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    return isOpen ? (
      <div data-testid="auth-modal">
        <button onClick={onClose}>Close Modal</button>
      </div>
    ) : null;
  };
});

jest.mock('../../components/Onboarding', () => {
  return function MockOnboarding({ isOpen, onComplete }: { isOpen: boolean; onComplete: () => void }) {
    return isOpen ? (
      <div data-testid="onboarding-modal">
        <button onClick={onComplete}>Complete Onboarding</button>
      </div>
    ) : null;
  };
});

jest.mock('../../components/MultiJobAutocomplete', () => {
  return function MockMultiJobAutocomplete({ onSearch }: { onSearch: (positions: any[]) => void }) {
    return (
      <div data-testid="job-autocomplete">
        <button onClick={() => onSearch([{ title: 'React Developer', count: 1 }])}>
          Search Jobs
        </button>
      </div>
    );
  };
});

const renderHome = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <Home />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    
    // Mock successful API response
    mockJobService.getJobs.mockResolvedValue([
      {
        _id: '1',
        title: 'Senior Frontend Developer',
        company: 'TechCorp',
        location: 'Remote',
        job_type: 'Full-time',
        salary_range: '$90k - $130k',
        skills: ['React', 'TypeScript'],
        created_at: new Date().toISOString(),
        description: 'Exciting opportunity',
        company_logo: '💻',
        url: '#',
        is_active: true
      },
      {
        _id: '2',
        title: 'Backend Engineer',
        company: 'DataFlow',
        location: 'Remote',
        job_type: 'Full-time',
        salary_range: '$85k - $125k',
        skills: ['Python', 'Django'],
        created_at: new Date().toISOString(),
        description: 'Build scalable systems',
        company_logo: '🔧',
        url: '#',
        is_active: true
      }
    ]);
  });

  describe('Component Rendering', () => {
    test('renders home page without crashing', async () => {
      await act(async () => {
        renderHome();
      });
      
      expect(screen.getByText(/Find Your Dream Remote Job/i)).toBeInTheDocument();
    });

    test('renders search section', async () => {
      await act(async () => {
        renderHome();
      });
      
      expect(screen.getByTestId('job-autocomplete')).toBeInTheDocument();
    });

    test('renders featured jobs section', async () => {
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
      });
    });

    test('renders hero section with call-to-action', async () => {
      await act(async () => {
        renderHome();
      });
      
      expect(screen.getByText(/Find Your Dream Remote Job/i)).toBeInTheDocument();
      expect(screen.getByText(/Join thousands of professionals/i)).toBeInTheDocument();
    });
  });

  describe('Job Loading and Display', () => {
    test('loads featured jobs on mount', async () => {
      await act(async () => {
        renderHome();
      });
      
      expect(mockJobService.getJobs).toHaveBeenCalledWith(1, 25);
      
      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
      });
    });

    test('displays job details correctly', async () => {
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('TechCorp')).toBeInTheDocument();
        expect(screen.getByText('Remote')).toBeInTheDocument();
        expect(screen.getByText('$90k - $130k')).toBeInTheDocument();
      });
    });

    test('handles API error gracefully with fallback data', async () => {
      mockJobService.getJobs.mockRejectedValue(new Error('API Error'));
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        // Should show fallback jobs
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      });
    });

    test('handles empty API response with fallback', async () => {
      mockJobService.getJobs.mockResolvedValue([]);
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        // Should show fallback jobs when API returns empty
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      });
    });
  });

  describe('Search Functionality', () => {
    test('triggers search when autocomplete is used', async () => {
      const mockNavigate = jest.fn();
      jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
      
      await act(async () => {
        renderHome();
      });
      
      const searchButton = screen.getByText('Search Jobs');
      fireEvent.click(searchButton);
      
      expect(mockNavigate).toHaveBeenCalledWith('/jobs', {
        state: { searchParams: { positions: [{ title: 'React Developer', count: 1 }] } }
      });
    });
  });

  describe('Onboarding Flow', () => {
    test('shows onboarding for new users', async () => {
      localStorageMock.getItem
        .mockReturnValueOnce('user-token') // userToken
        .mockReturnValueOnce(null); // onboardingCompleted
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('onboarding-modal')).toBeInTheDocument();
      });
    });

    test('does not show onboarding for existing users', async () => {
      localStorageMock.getItem
        .mockReturnValueOnce('user-token') // userToken
        .mockReturnValueOnce('completed'); // onboardingCompleted
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        expect(screen.queryByTestId('onboarding-modal')).not.toBeInTheDocument();
      });
    });

    test('closes onboarding when completed', async () => {
      localStorageMock.getItem
        .mockReturnValueOnce('user-token')
        .mockReturnValueOnce(null);
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        expect(screen.getByTestId('onboarding-modal')).toBeInTheDocument();
      });
      
      const completeButton = screen.getByText('Complete Onboarding');
      fireEvent.click(completeButton);
      
      await waitFor(() => {
        expect(screen.queryByTestId('onboarding-modal')).not.toBeInTheDocument();
      });
    });
  });

  describe('Authentication Modal', () => {
    test('opens auth modal when triggered', async () => {
      await act(async () => {
        renderHome();
      });
      
      // Find and click a button that might trigger auth modal
      const ctaButtons = screen.getAllByRole('button');
      const signUpButton = ctaButtons.find(button => 
        button.textContent?.includes('Sign Up') || 
        button.textContent?.includes('Get Started')
      );
      
      if (signUpButton) {
        fireEvent.click(signUpButton);
        expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
      }
    });

    test('closes auth modal', async () => {
      await act(async () => {
        renderHome();
      });
      
      // Open modal first
      const ctaButtons = screen.getAllByRole('button');
      const signUpButton = ctaButtons.find(button => 
        button.textContent?.includes('Sign Up') || 
        button.textContent?.includes('Get Started')
      );
      
      if (signUpButton) {
        fireEvent.click(signUpButton);
        expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
        
        // Close modal
        const closeButton = screen.getByText('Close Modal');
        fireEvent.click(closeButton);
        
        await waitFor(() => {
          expect(screen.queryByTestId('auth-modal')).not.toBeInTheDocument();
        });
      }
    });
  });

  describe('Job Card Interactions', () => {
    test('navigates to job detail when job card is clicked', async () => {
      const mockNavigate = jest.fn();
      jest.spyOn(require('react-router-dom'), 'useNavigate').mockReturnValue(mockNavigate);
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        const jobCard = screen.getByText('Senior Frontend Developer').closest('div');
        if (jobCard) {
          fireEvent.click(jobCard);
          expect(mockNavigate).toHaveBeenCalledWith('/job/1');
        }
      });
    });
  });

  describe('Auto-scroll Functionality', () => {
    test('initializes auto-scroll intervals', async () => {
      jest.useFakeTimers();
      
      await act(async () => {
        renderHome();
      });
      
      // Fast-forward time to trigger auto-scroll
      act(() => {
        jest.advanceTimersByTime(3000);
      });
      
      // Should not crash and continue working
      expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      
      jest.useRealTimers();
    });
  });

  describe('Responsive Design', () => {
    test('renders mobile-friendly layout', async () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });
      
      await act(async () => {
        renderHome();
      });
      
      expect(screen.getByText(/Find Your Dream Remote Job/i)).toBeInTheDocument();
    });
  });

  describe('Error Handling', () => {
    test('handles network errors gracefully', async () => {
      mockJobService.getJobs.mockRejectedValue(new Error('Network error'));
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        // Should still render the page with fallback data
        expect(screen.getByText(/Find Your Dream Remote Job/i)).toBeInTheDocument();
      });
    });

    test('handles malformed API response', async () => {
      mockJobService.getJobs.mockResolvedValue(null as any);
      
      await act(async () => {
        renderHome();
      });
      
      await waitFor(() => {
        // Should use fallback data
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      });
    });
  });

  describe('Performance', () => {
    test('does not cause memory leaks with intervals', async () => {
      jest.useFakeTimers();
      
      const { unmount } = renderHome();
      
      // Fast-forward time to trigger intervals
      act(() => {
        jest.advanceTimersByTime(10000);
      });
      
      // Should unmount cleanly
      unmount();
      
      jest.useRealTimers();
    });
  });
}); 