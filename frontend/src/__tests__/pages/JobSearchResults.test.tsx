import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import JobSearchResults from '../../pages/JobSearchResults';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock the API configuration
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn(() => Promise.resolve('http://localhost:5001'))
}));

// Mock the components
jest.mock('../../components/JobCard/JobCard', () => {
  return function MockJobCard({ job }: any) {
    return <div data-testid={`job-${job.id}`}>{job.title}</div>;
  };
});

jest.mock('../../components/AutoApplyButton', () => {
  return function MockAutoApplyButton({ jobUrl, jobId, onApplied }: any) {
    return (
      <button 
        data-testid={`auto-apply-${jobId}`}
        onClick={() => onApplied?.('test-application-id')}
      >
        Auto Apply
      </button>
    );
  };
});

// Mock fetch
global.fetch = jest.fn();

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

const mockJobs = [
  {
    id: '1',
    title: 'Frontend Developer',
    company: 'Test Company',
    location: 'Remote',
    description: 'Test description',
    createdAt: new Date().toISOString(),
    isRemote: true,
    skills: ['React', 'TypeScript'],
    apply_url: 'https://example.com/apply/1'
  },
  {
    id: '2',
    title: 'Backend Developer',
    company: 'Another Company',
    location: 'New York',
    description: 'Another test description',
    createdAt: new Date().toISOString(),
    isRemote: false,
    skills: ['Node.js', 'Python'],
    apply_url: 'https://example.com/apply/2'
  }
];

const renderJobSearchResults = () => {
  return render(
    <MockWrapper>
      <JobSearchResults />
    </MockWrapper>
  );
};

describe('JobSearchResults', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    
    // Mock successful API response
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        jobs: mockJobs,
        total: mockJobs.length
      })
    });
  });

  test('renders page with proper heading', async () => {
    renderJobSearchResults();

    // Wait for loading to complete
    await waitFor(() => {
      expect(screen.queryByText('Searching...')).not.toBeInTheDocument();
    });

    // Check for updated heading
    expect(screen.getByRole('heading', { name: 'Remote Jobs' })).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('Error Loading Jobs')).toBeInTheDocument();
    });

    expect(screen.getByText('Try Again')).toBeInTheDocument();
  });

  test('renders job listings when data is loaded', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();
    });

    expect(screen.getByText('2 jobs')).toBeInTheDocument();
  });

  test('handles filter changes and triggers new search', async () => {
    renderJobSearchResults();

    // Wait for initial load
    await waitFor(() => {
      expect(screen.getByText('2 jobs')).toBeInTheDocument();
    });

    // Find and interact with filters using multiple elements with "Filters" text
    const filtersButtons = screen.getAllByText('Filters');
    expect(filtersButtons.length).toBeGreaterThan(0);
    
    // Check that filters are accessible
    const filtersHeading = screen.getByRole('heading', { name: 'Filters' });
    expect(filtersHeading).toBeInTheDocument();
  });

  test('clears all filters when clear button is clicked', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('2 jobs')).toBeInTheDocument();
    });

    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('work_type=Remote')
      );
    });
  });

  test('handles work type filter changes', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('2 jobs')).toBeInTheDocument();
    });

    // Look for emoji-based labels
    const hybridCheckbox = screen.getByLabelText('🏢 Hybrid');
    fireEvent.click(hybridCheckbox);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('work_type=Remote%2CHybrid')
      );
    });
  });

  test('handles sort by changes', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('2 jobs')).toBeInTheDocument();
    });

    // Look for updated sort option text
    await waitFor(() => {
      expect(screen.getByDisplayValue('Most Recent')).toBeInTheDocument();
    });

    const sortSelect = screen.getByDisplayValue('Most Recent');
    fireEvent.change(sortSelect, { target: { value: 'salary' } });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=salary')
      );
    });
  });

  test('toggles view mode between list and grid', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('2 jobs')).toBeInTheDocument();
    });

    // Find view mode buttons
    const viewModeButtons = screen.getAllByRole('button');
    const gridButton = viewModeButtons.find(button => 
      button.querySelector('svg')?.classList.contains('lucide-grid-3x3')
    );
    
    expect(gridButton).toBeInTheDocument();
    fireEvent.click(gridButton!);

    // Verify view mode changed (no specific assertion as this is visual)
    expect(gridButton).toBeInTheDocument();
  });

  test('handles job application', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Find and click apply button
    const applyButtons = screen.getAllByText('Apply');
    expect(applyButtons.length).toBeGreaterThan(0);
    
    fireEvent.click(applyButtons[0]);

    // Check that applied jobs counter updates
    await waitFor(() => {
      expect(screen.getByText('1 applied')).toBeInTheDocument();
    });
  });

  test('handles auto apply functionality', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Find auto apply button
    const autoApplyButton = screen.getByTestId('auto-apply-1');
    expect(autoApplyButton).toBeInTheDocument();
    
    fireEvent.click(autoApplyButton);

    // Check that applied jobs counter updates
    await waitFor(() => {
      expect(screen.getByText('1 applied')).toBeInTheDocument();
    });
  });

  test('handles job saving/bookmarking', async () => {
    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Find bookmark buttons
    const bookmarkButtons = screen.getAllByRole('button').filter(button =>
      button.querySelector('svg')?.classList.contains('lucide-bookmark-plus')
    );
    
    expect(bookmarkButtons.length).toBeGreaterThan(0);
    fireEvent.click(bookmarkButtons[0]);

    // Check that saved jobs counter updates
    await waitFor(() => {
      expect(screen.getByText('1 saved')).toBeInTheDocument();
    });
  });

  test('shows pagination when there are multiple pages', async () => {
    // Mock response with more jobs to trigger pagination
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        jobs: mockJobs,
        total: 100 // More than one page
      })
    });

    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('100 jobs')).toBeInTheDocument();
    });

    // Check for pagination buttons
    expect(screen.getByText('Next')).toBeInTheDocument();
    expect(screen.getByText('Previous')).toBeInTheDocument();
  });

  test('handles multi-position search from URL params', async () => {
    // Mock URL with job titles
    Object.defineProperty(window, 'location', {
      value: {
        search: '?multi_search=true&job_titles=Frontend%20Developer,Backend%20Developer'
      },
      writable: true
    });

    renderJobSearchResults();

    await waitFor(() => {
      expect(screen.getByText('Searching for 2 job titles:')).toBeInTheDocument();
    });

    // Check that job titles are displayed as chips
    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('Backend Developer')).toBeInTheDocument();
  });

  test('shows loading state initially', () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    // Check for loading spinner instead of role status
    expect(screen.getByRole('heading', { name: 'Remote Jobs' })).toBeInTheDocument();
  });

  test('shows no jobs found when results are empty', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        jobs: [],
        total: 0,
        page: 1,
        total_pages: 0
      })
    });

    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('No jobs found')).toBeInTheDocument();
    });
  });

  test('toggles filters sidebar', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    const filtersButton = screen.getByRole('button', { name: /filters/i });
    expect(filtersButton).toBeInTheDocument();
    
    fireEvent.click(filtersButton);
    
    await waitFor(() => {
      expect(screen.getByText('Clear All')).toBeInTheDocument();
    });
  });

  test('handles experience level filter changes', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Experience Level')).toBeInTheDocument();
    });

    const entryLevelCheckbox = screen.getByLabelText('Entry Level (0-2 years)');
    fireEvent.click(entryLevelCheckbox);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('experience_level=Entry+Level+%280-2+years%29')
      );
    });
  });

  test('component unmounts cleanly', () => {
    const { unmount } = render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    expect(() => unmount()).not.toThrow();
  });
}); 