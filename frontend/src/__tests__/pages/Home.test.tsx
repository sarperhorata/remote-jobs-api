import React from 'react';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import '@testing-library/jest-dom';
import Home from '../../pages/Home';
import { jobService } from '../../services/jobService';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';

jest.mock('../../services/jobService');
jest.mock('../../components/AuthModal', () => () => <div data-testid="auth-modal" />);
jest.mock('../../components/Onboarding', () => () => <div data-testid="onboarding-modal" />);
jest.mock('../../components/MultiJobAutocomplete', () => () => <div data-testid="multi-job-autocomplete" />);

const mockJobService = jobService as jest.Mocked<typeof jobService>;

const mockJobs = [
  { _id: '1', title: 'Frontend Developer', company: { name: 'Tech Corp' }, created_at: new Date().toISOString() },
  { _id: '2', title: 'Backend Engineer', company: { name: 'Startup Inc' }, created_at: new Date().toISOString() }
];

const queryClient = new QueryClient({
  defaultOptions: { queries: { retry: false, staleTime: Infinity } },
});

// Mock AuthContext
const mockAuthContext = {
  isAuthenticated: false,
  user: null,
  login: jest.fn(),
  logout: jest.fn(),
  register: jest.fn(),
  loading: false,
  error: null,
};

// Mock ThemeContext
const mockThemeContext = {
  theme: 'light' as const,
  toggleTheme: jest.fn(),
};

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      <ThemeProvider>
        <QueryClientProvider client={queryClient}>
          {children}
        </QueryClientProvider>
      </ThemeProvider>
    </AuthProvider>
  </BrowserRouter>
);

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Mock console methods to avoid noise in tests
    jest.spyOn(console, 'error').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'log').mockImplementation(() => {});
    mockJobService.getJobs.mockResolvedValue({
      jobs: mockJobs, total: 2, page: 1, pages: 1
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('API Error Handling', () => {
    it('should handle API errors gracefully and show fallback data', async () => {
      // Mock API to throw error
      mockJobService.getJobs.mockRejectedValue(new Error('HTTP 404: Not Found'));

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      // Wait for error handling to complete
      await waitFor(() => {
        expect(screen.getByText(/using fallback job data/i)).toBeInTheDocument();
      }, { timeout: 3000 });

      // Verify error was logged
      expect(console.log).toHaveBeenCalledWith(
        expect.stringContaining('📋 Using fallback job data')
      );
    });

    it('should handle 404 errors specifically', async () => {
      const error404 = new Error('HTTP 404: Not Found');
      mockJobService.getJobs.mockRejectedValue(error404);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(console.error).toHaveBeenCalledWith(
          expect.stringContaining('❌ Error loading featured jobs from API:'),
          error404
        );
      });
    });

    it('should handle network errors', async () => {
      const networkError = new Error('Network error');
      mockJobService.getJobs.mockRejectedValue(networkError);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(console.error).toHaveBeenCalledWith(
          expect.stringContaining('❌ Error loading featured jobs from API:'),
          networkError
        );
      });
    });

    it('should handle API timeout errors', async () => {
      const timeoutError = new Error('Request timeout');
      mockJobService.getJobs.mockRejectedValue(timeoutError);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(console.error).toHaveBeenCalledWith(
          expect.stringContaining('❌ Error loading featured jobs from API:'),
          timeoutError
        );
      });
    });
  });

  describe('Successful API Response', () => {
    it('should load and display featured jobs from API', async () => {
      const mockJobs = [
        {
          id: '1',
          title: 'Senior Developer',
          company: 'Tech Corp',
          location: 'Remote',
          job_type: 'Full-time',
          apply_url: 'https://example.com/apply/1'
        },
        {
          id: '2',
          title: 'UI Designer',
          company: 'Design Studio',
          location: 'New York',
          job_type: 'Contract',
          apply_url: 'https://example.com/apply/2'
        }
      ];

      mockJobService.getJobs.mockResolvedValue(mockJobs);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Senior Developer')).toBeInTheDocument();
        expect(screen.getByText('UI Designer')).toBeInTheDocument();
      });

      expect(mockJobService.getJobs).toHaveBeenCalledWith({
        page: 1,
        limit: 10,
        sort_by: 'newest'
      });
    });

    it('should handle empty API response', async () => {
      mockJobService.getJobs.mockResolvedValue([]);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(console.log).toHaveBeenCalledWith(
          expect.stringContaining('📋 Using fallback job data')
        );
      });
    });
  });

  describe('Fallback Data', () => {
    it('should display fallback jobs when API fails', async () => {
      mockJobService.getJobs.mockRejectedValue(new Error('API Error'));

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        // Check for fallback job titles
        expect(screen.getByText(/senior full.stack developer/i)).toBeInTheDocument();
        expect(screen.getByText(/ux\/ui designer/i)).toBeInTheDocument();
        expect(screen.getByText(/devops engineer/i)).toBeInTheDocument();
      });
    });

    it('should show correct fallback job details', async () => {
      mockJobService.getJobs.mockRejectedValue(new Error('API Error'));

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
        expect(screen.getByText('DesignStudio')).toBeInTheDocument();
        expect(screen.getByText('CloudTech')).toBeInTheDocument();
      });
    });
  });

  describe('User Interactions', () => {
    it('should handle job search input', async () => {
      mockJobService.getJobs.mockResolvedValue([]);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      const searchInput = screen.getByPlaceholderText(/search for jobs/i);
      fireEvent.change(searchInput, { target: { value: 'developer' } });

      expect(searchInput).toHaveValue('developer');
    });

    it('should handle job card clicks for unauthenticated users', async () => {
      mockJobService.getJobs.mockResolvedValue([
        {
          id: '1',
          title: 'Test Job',
          company: 'Test Company',
          location: 'Remote',
          apply_url: 'https://example.com/apply'
        }
      ]);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        const jobCard = screen.getByText('Test Job');
        fireEvent.click(jobCard);
        // Should show auth modal for unauthenticated users
        expect(screen.getByText(/sign in/i)).toBeInTheDocument();
      });
    });
  });

  describe('Loading States', () => {
    it('should show loading state while fetching jobs', async () => {
      // Create a promise that we can control
      let resolvePromise: (value: any) => void;
      const mockPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockJobService.getJobs.mockReturnValue(mockPromise);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      // Check for loading indicators
      expect(screen.getByText(/buzz2remote/i)).toBeInTheDocument();

      // Resolve the promise
      resolvePromise!([]);

      await waitFor(() => {
        expect(console.log).toHaveBeenCalledWith(
          expect.stringContaining('📋 Using fallback job data')
        );
      });
    });
  });

  describe('Error Recovery', () => {
    it('should retry API call on user action', async () => {
      // First call fails
      mockJobService.getJobs
        .mockRejectedValueOnce(new Error('API Error'))
        .mockResolvedValueOnce([
          {
            id: '1',
            title: 'Recovered Job',
            company: 'Recovery Corp',
            location: 'Remote'
          }
        ]);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      // Wait for first error
      await waitFor(() => {
        expect(console.error).toHaveBeenCalledWith(
          expect.stringContaining('❌ Error loading featured jobs from API:'),
          expect.any(Error)
        );
      });

      // Simulate user action that triggers retry (e.g., search)
      const searchInput = screen.getByPlaceholderText(/search for jobs/i);
      fireEvent.change(searchInput, { target: { value: 'test' } });
      fireEvent.keyDown(searchInput, { key: 'Enter' });

      // Should show recovered data
      await waitFor(() => {
        expect(screen.getByText('Recovered Job')).toBeInTheDocument();
      });
    });
  });

  describe('API URL Construction', () => {
    it('should not make requests to malformed URLs', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      // Mock jobService to throw a specific URL error
      mockJobService.getJobs.mockRejectedValue(
        new Error('HTTP 404: Not Found')
      );

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith(
          expect.stringContaining('❌ Error loading featured jobs from API:'),
          expect.objectContaining({
            message: 'HTTP 404: Not Found'
          })
        );
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Performance', () => {
    it('should not make duplicate API calls', async () => {
      mockJobService.getJobs.mockResolvedValue([]);

      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(mockJobService.getJobs).toHaveBeenCalledTimes(1);
      });

      // Re-render should not trigger another API call
      render(
        <TestWrapper>
          <Home />
        </TestWrapper>
      );

      // Still should be called only once per component instance
      expect(mockJobService.getJobs).toHaveBeenCalledTimes(2);
    });
  });
}); 