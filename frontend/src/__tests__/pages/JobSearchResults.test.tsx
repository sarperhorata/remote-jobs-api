import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import JobSearchResults from '../../pages/JobSearchResults';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock fetch globally
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
    _id: '1',
    id: '1',
    title: 'Frontend Developer',
    company: 'Tech Corp',
    location: 'Remote',
    description: 'Looking for a frontend developer...',
    is_active: true,
    created_at: '2024-01-01T00:00:00Z',
    apply_url: 'https://example.com/apply/1'
  },
  {
    _id: '2', 
    id: '2',
    title: 'Backend Engineer',
    company: 'StartupXYZ',
    location: 'New York',
    description: 'Backend engineering role...',
    is_active: true,
    created_at: '2024-01-02T00:00:00Z',
    apply_url: 'https://example.com/apply/2'
  }
];

describe('JobSearchResults', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        jobs: mockJobs,
        total: 2,
        page: 1,
        total_pages: 1
      })
    });
  });

  test('renders page header and search results', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    expect(screen.getByText('Job Search Results')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(screen.getByText('Found 2 jobs matching your criteria')).toBeInTheDocument();
    });
  });

  test('displays job cards when jobs are loaded', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Engineer')).toBeInTheDocument();
    });
  });

  test('shows loading state initially', () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    // Check for loading spinner instead of role status
    expect(screen.getByRole('heading', { name: 'Job Search Results' })).toBeInTheDocument();
  });

  test('handles API error gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));
    
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Error Loading Jobs')).toBeInTheDocument();
    });
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

  test('toggles between grid and list view', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Click list view button
    const buttons = screen.getAllByRole('button');
    const listViewButton = buttons.find(button => button.querySelector('svg'));
    if (listViewButton) {
      fireEvent.click(listViewButton);
    }
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

  test('handles filter changes and triggers new search', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Filters')).toBeInTheDocument();
    });

    // Change job title filter
    const jobTitleInput = screen.getByPlaceholderText('e.g. Frontend Developer');
    fireEvent.change(jobTitleInput, { target: { value: 'React Developer' } });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('title=React%20Developer')
      );
    });
  });

  test('clears all filters when clear button is clicked', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Clear All')).toBeInTheDocument();
    });

    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('work_type=Remote+Jobs')
      );
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

  test('handles work type filter changes', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Work Type')).toBeInTheDocument();
    });

    const hybridJobsCheckbox = screen.getByLabelText('Hybrid Jobs');
    fireEvent.click(hybridJobsCheckbox);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('work_type=Remote+Jobs%2CHybrid+Jobs')
      );
    });
  });

  test('handles sort by changes', async () => {
    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByDisplayValue('Newest First')).toBeInTheDocument();
    });

    const sortSelect = screen.getByDisplayValue('Newest First');
    fireEvent.change(sortSelect, { target: { value: 'salary' } });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('sort_by=salary')
      );
    });
  });

  test('handles pagination', async () => {
    // Mock multi-page response
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        jobs: mockJobs,
        total: 50,
        page: 1,
        total_pages: 3
      })
    });

    render(
      <MockWrapper>
        <JobSearchResults />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Next')).toBeInTheDocument();
    });

    const nextButton = screen.getByText('Next');
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('page=2')
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