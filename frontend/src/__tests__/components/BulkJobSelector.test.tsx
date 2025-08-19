import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import BulkJobSelector from '../../components/BulkJobSelector';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock AuthContext
const mockAuthContext = {
  isAuthenticated: true,
  user: { _id: 'test-user-id', email: 'test@example.com' },
  login: jest.fn(),
  logout: jest.fn(),
  signup: jest.fn(),
  isLoading: false
};

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('BulkJobSelector', () => {
  const mockJobs = [
    {
      _id: '1',
      id: '1',
      title: 'Senior Frontend Developer',
      company: {
        name: 'TechCorp',
        logo: '💻'
      },
      location: 'Remote',
      job_type: 'Full-time',
      salary_min: 80000,
      salary_max: 120000,
      url: 'https://example.com/job/1',
      is_active: true,
      created_at: '2024-01-15T10:00:00Z'
    },
    {
      _id: '2',
      id: '2',
      title: 'React Developer',
      company: {
        name: 'StartupInc',
        logo: '🚀'
      },
      location: 'New York, NY',
      job_type: 'Full-time',
      salary_min: 70000,
      salary_max: 100000,
      url: 'https://example.com/job/2',
      is_active: true,
      created_at: '2024-01-15T11:00:00Z'
    },
    {
      _id: '3',
      id: '3',
      title: 'Full Stack Developer',
      company: {
        name: 'BigTech',
        logo: '🏢'
      },
      location: 'San Francisco, CA',
      job_type: 'Full-time',
      salary_min: 100000,
      salary_max: 150000,
      url: 'https://example.com/job/3',
      is_active: true,
      created_at: '2024-01-15T12:00:00Z'
    }
  ];

  const mockOnSelectionChange = jest.fn();
  const mockOnBulkApply = jest.fn();

  beforeEach(() => {
    mockFetch.mockClear();
    mockOnSelectionChange.mockClear();
    mockOnBulkApply.mockClear();
  });

  it('renders bulk job selector with jobs', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    expect(screen.getByText('Select All (3 jobs)')).toBeInTheDocument();
    expect(screen.getByText('Senior Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('React Developer')).toBeInTheDocument();
    expect(screen.getByText('Full Stack Developer')).toBeInTheDocument();
  });

  it('handles select all functionality', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    const selectAllButton = screen.getByText('Select All (3 jobs)');
    fireEvent.click(selectAllButton);

    expect(screen.getByText('3 jobs selected')).toBeInTheDocument();
    expect(mockOnSelectionChange).toHaveBeenCalledWith(mockJobs);
  });

  it('handles individual job selection', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    // Select first job
    const firstJob = screen.getByText('Senior Frontend Developer').closest('div');
    fireEvent.click(firstJob!);

    expect(screen.getByText('1 job selected')).toBeInTheDocument();
    expect(mockOnSelectionChange).toHaveBeenCalledWith([mockJobs[0]]);
  });

  it('shows bulk apply button when jobs are selected', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    // Select all jobs
    const selectAllButton = screen.getByText('Select All (3 jobs)');
    fireEvent.click(selectAllButton);

    expect(screen.getByText('Bulk Apply (3)')).toBeInTheDocument();
  });

  it('handles bulk apply with settings', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ auto_apply_supported: true })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    // Select all jobs
    const selectAllButton = screen.getByText('Select All (3 jobs)');
    fireEvent.click(selectAllButton);

    // Open settings
    const settingsButton = screen.getByTitle('Bulk Apply Settings');
    fireEvent.click(settingsButton);

    // Configure settings
    const delayInput = screen.getByLabelText('Delay between applications (ms)');
    fireEvent.change(delayInput, { target: { value: '5000' } });

    const maxJobsInput = screen.getByLabelText('Max applications per session');
    fireEvent.change(maxJobsInput, { target: { value: '5' } });

    // Start bulk apply
    const bulkApplyButton = screen.getByText('Bulk Apply (3)');
    fireEvent.click(bulkApplyButton);

    await waitFor(() => {
      expect(mockOnBulkApply).toHaveBeenCalledWith(mockJobs);
    });
  });

  it('shows progress bar during bulk apply', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ auto_apply_supported: true })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    // Select all jobs
    const selectAllButton = screen.getByText('Select All (3 jobs)');
    fireEvent.click(selectAllButton);

    // Start bulk apply
    const bulkApplyButton = screen.getByText('Bulk Apply (3)');
    fireEvent.click(bulkApplyButton);

    await waitFor(() => {
      expect(screen.getByText('Bulk Apply Progress')).toBeInTheDocument();
    });
  });

  it('handles pause and resume functionality', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ auto_apply_supported: true })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    // Select all jobs
    const selectAllButton = screen.getByText('Select All (3 jobs)');
    fireEvent.click(selectAllButton);

    // Start bulk apply
    const bulkApplyButton = screen.getByText('Bulk Apply (3)');
    fireEvent.click(bulkApplyButton);

    await waitFor(() => {
      expect(screen.getByText('Pause')).toBeInTheDocument();
    });

    // Pause
    const pauseButton = screen.getByText('Pause');
    fireEvent.click(pauseButton);

    expect(screen.getByText('Resume')).toBeInTheDocument();
  });

  it('handles job opening in new tab', () => {
    const mockOpen = jest.fn();
    Object.defineProperty(window, 'open', {
      value: mockOpen,
      writable: true
    });

    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    const openButtons = screen.getAllByTitle('Open in new tab');
    fireEvent.click(openButtons[0]);

    expect(mockOpen).toHaveBeenCalledWith('https://example.com/job/1', '_blank');
  });

  it('displays job information correctly', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    expect(screen.getByText('TechCorp')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByText('Full-time')).toBeInTheDocument();
    expect(screen.getByText('$80,000 - $120,000')).toBeInTheDocument();
  });

  it('handles settings panel toggle', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    const settingsButton = screen.getByTitle('Bulk Apply Settings');
    fireEvent.click(settingsButton);

    expect(screen.getByText('Bulk Apply Settings')).toBeInTheDocument();
    expect(screen.getByLabelText('Delay between applications (ms)')).toBeInTheDocument();
    expect(screen.getByLabelText('Max applications per session')).toBeInTheDocument();
  });

  it('handles settings changes', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    const settingsButton = screen.getByTitle('Bulk Apply Settings');
    fireEvent.click(settingsButton);

    const delayInput = screen.getByLabelText('Delay between applications (ms)');
    fireEvent.change(delayInput, { target: { value: '4000' } });

    expect(delayInput).toHaveValue(4000);
  });

  it('handles checkbox settings', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    const settingsButton = screen.getByTitle('Bulk Apply Settings');
    fireEvent.click(settingsButton);

    const openInNewTabCheckbox = screen.getByLabelText('Open jobs in new tabs');
    const autoFillFormsCheckbox = screen.getByLabelText('Auto-fill application forms');
    const skipComplexFormsCheckbox = screen.getByLabelText('Skip complex forms');

    expect(openInNewTabCheckbox).toBeChecked();
    expect(autoFillFormsCheckbox).toBeChecked();
    expect(skipComplexFormsCheckbox).toBeChecked();

    fireEvent.click(openInNewTabCheckbox);
    expect(openInNewTabCheckbox).not.toBeChecked();
  });

  it('handles empty jobs list', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={[]}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    expect(screen.getByText('Select All (0 jobs)')).toBeInTheDocument();
    expect(screen.queryByText('Bulk Apply')).not.toBeInTheDocument();
  });

  it('handles API errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    // Select all jobs
    const selectAllButton = screen.getByText('Select All (3 jobs)');
    fireEvent.click(selectAllButton);

    // Start bulk apply
    const bulkApplyButton = screen.getByText('Bulk Apply (3)');
    fireEvent.click(bulkApplyButton);

    await waitFor(() => {
      expect(screen.getByText('Bulk Apply Progress')).toBeInTheDocument();
    });
  });

  it('handles rate limiting', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ auto_apply_supported: true })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ success: true })
      });

    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
      />
    );

    // Select all jobs
    const selectAllButton = screen.getByText('Select All (3 jobs)');
    fireEvent.click(selectAllButton);

    // Start bulk apply
    const bulkApplyButton = screen.getByText('Bulk Apply (3)');
    fireEvent.click(bulkApplyButton);

    await waitFor(() => {
      expect(screen.getByText('Bulk Apply Progress')).toBeInTheDocument();
    });
  });

  it('applies custom className', () => {
    renderWithProviders(
      <BulkJobSelector
        jobs={mockJobs}
        onSelectionChange={mockOnSelectionChange}
        onBulkApply={mockOnBulkApply}
        className="custom-bulk-selector"
      />
    );

    const container = screen.getByText('Select All (3 jobs)').closest('div');
    expect(container).toHaveClass('custom-bulk-selector');
  });
}); 