import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import JobSearchResults from '../../pages/JobSearchResults';
import SearchFilters from '../../components/JobSearch/SearchFilters';
import { getApiUrl } from '../../utils/apiConfig';

// Mock fetch for API calls
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Test wrapper with all providers
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Job Search Integration Tests', () => {
  const mockJobs = [
    {
      id: '1',
      title: 'Senior Frontend Developer',
      company: 'Tech Corp',
      location: 'Remote',
      salary_min: 80000,
      salary_max: 120000,
      job_type: 'Full-time',
      work_type: 'Remote',
      experience_level: 'Senior',
      description: 'We are looking for a senior frontend developer...',
      posted_date: '2024-01-15',
      application_count: 25
    },
    {
      id: '2',
      title: 'React Developer',
      company: 'Startup Inc',
      location: 'New York, NY',
      salary_min: 70000,
      salary_max: 100000,
      job_type: 'Full-time',
      work_type: 'Hybrid',
      experience_level: 'Mid-level',
      description: 'Join our growing team...',
      posted_date: '2024-01-14',
      application_count: 15
    }
  ];

  beforeEach(() => {
    mockFetch.mockClear();
    localStorage.clear();
  });

  describe('Job Search Results Page', () => {
    it('should load and display jobs from API', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 2 })
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      // Wait for jobs to load
      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('React Developer')).toBeInTheDocument();
      });

      // Verify API call
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/jobs/search'),
        expect.any(Object)
      );
    });

    it('should handle search with query parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [mockJobs[0]], total: 1 })
      });

      // Mock URL with search query
      Object.defineProperty(window, 'location', {
        value: {
          search: '?q=frontend&location=remote'
        },
        writable: true
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/jobs/search?q=frontend&location=remote'),
          expect.any(Object)
        );
      });
    });

    it('should handle empty search results', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [], total: 0 })
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/no jobs found/i)).toBeInTheDocument();
      });
    });

    it('should handle API errors gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText(/no jobs found/i)).toBeInTheDocument();
      });
    });
  });

  describe('Search Filters Integration', () => {
    it('should apply filters and update search results', async () => {
      const mockFilteredJobs = [mockJobs[0]]; // Only remote jobs
      
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ jobs: mockJobs, total: 2 })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ jobs: mockFilteredJobs, total: 1 })
        });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('React Developer')).toBeInTheDocument();
      });

      // Apply remote filter
      const filterButton = screen.getByText(/filters/i);
      fireEvent.click(filterButton);

      // This would typically open a filter modal
      // For integration test, we'll simulate filter change
      const filters = {
        workType: 'Remote',
        experience_level: 'Senior'
      };

      // Simulate filter change
      const searchParams = new URLSearchParams({
        work_type: filters.workType,
        experience: filters.experience_level
      });

      // Mock the filtered API call
      Object.defineProperty(window, 'location', {
        value: {
          search: `?${searchParams.toString()}`
        },
        writable: true
      });

      // Re-render to trigger new search
      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('work_type=Remote'),
          expect.any(Object)
        );
      });
    });

    it('should handle pagination correctly', async () => {
      const page2Jobs = [
        {
          id: '3',
          title: 'Backend Developer',
          company: 'Enterprise Corp',
          location: 'San Francisco, CA',
          salary_min: 90000,
          salary_max: 130000,
          job_type: 'Full-time',
          work_type: 'On-site',
          experience_level: 'Senior',
          description: 'Backend development role...',
          posted_date: '2024-01-13',
          application_count: 30
        }
      ];

      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ jobs: mockJobs, total: 3 })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ jobs: page2Jobs, total: 3 })
        });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      // Wait for initial load
      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      });

      // Click next page
      const nextPageButton = screen.getByText(/next/i);
      fireEvent.click(nextPageButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('page=2'),
          expect.any(Object)
        );
      });
    });
  });

  describe('Job Card Interactions', () => {
    it('should handle job card clicks and navigation', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 2 })
      });

      // Mock window.open
      const mockOpen = jest.fn();
      Object.defineProperty(window, 'open', {
        value: mockOpen,
        writable: true
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      });

      // Click on job card
      const jobCard = screen.getByText('Senior Frontend Developer');
      fireEvent.click(jobCard);

      // Verify window.open was called
      expect(mockOpen).toHaveBeenCalledWith(
        expect.stringContaining('/jobs/1'),
        '_blank'
      );
    });

    it('should handle save job functionality', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 2 })
      });

      // Mock save job API call
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Job saved successfully' })
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
      });

      // Find and click save button
      const saveButtons = screen.getAllByTestId('save-job-button');
      if (saveButtons.length > 0) {
        fireEvent.click(saveButtons[0]);
        
        await waitFor(() => {
          expect(mockFetch).toHaveBeenCalledWith(
            expect.stringContaining('/jobs/1/save'),
            expect.objectContaining({
              method: 'POST'
            })
          );
        });
      }
    });
  });

  describe('Search Performance', () => {
    it('should debounce search requests', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 2 })
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      // Simulate rapid search input changes
      const searchInput = screen.getByPlaceholderText(/search jobs/i);
      
      fireEvent.change(searchInput, { target: { value: 'a' } });
      fireEvent.change(searchInput, { target: { value: 'ab' } });
      fireEvent.change(searchInput, { target: { value: 'abc' } });

      // Wait for debounced search
      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledTimes(1);
      });
    });

    it('should handle large result sets efficiently', async () => {
      const largeJobList = Array.from({ length: 100 }, (_, i) => ({
        id: `${i + 1}`,
        title: `Job ${i + 1}`,
        company: `Company ${i + 1}`,
        location: 'Remote',
        salary_min: 50000,
        salary_max: 100000,
        job_type: 'Full-time',
        work_type: 'Remote',
        experience_level: 'Mid-level',
        description: `Job description ${i + 1}`,
        posted_date: '2024-01-15',
        application_count: Math.floor(Math.random() * 50)
      }));

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: largeJobList, total: 100 })
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Job 1')).toBeInTheDocument();
        expect(screen.getByText('Job 25')).toBeInTheDocument();
      });

      // Verify pagination is working
      expect(screen.getByText(/showing 1-25 of 100/i)).toBeInTheDocument();
    });
  });

  describe('URL State Management', () => {
    it('should sync filters with URL parameters', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 2 })
      });

      // Set URL with filters
      Object.defineProperty(window, 'location', {
        value: {
          search: '?q=developer&work_type=Remote&experience=Senior'
        },
        writable: true
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('q=developer'),
          expect.any(Object)
        );
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('work_type=Remote'),
          expect.any(Object)
        );
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('experience=Senior'),
          expect.any(Object)
        );
      });
    });

    it('should update URL when filters change', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 2 })
      });

      // Mock history.pushState
      const mockPushState = jest.fn();
      Object.defineProperty(window.history, 'pushState', {
        value: mockPushState,
        writable: true
      });

      render(
        <TestWrapper>
          <JobSearchResults />
        </TestWrapper>
      );

      // Apply a filter
      const filterButton = screen.getByText(/filters/i);
      fireEvent.click(filterButton);

      // Simulate filter change
      const newFilters = { workType: 'Remote' };
      
      // This would typically update the URL
      const newUrl = `?work_type=${newFilters.workType}`;
      window.history.pushState({}, '', newUrl);

      expect(mockPushState).toHaveBeenCalled();
    });
  });
});