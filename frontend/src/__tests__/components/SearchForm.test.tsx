import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import SearchForm from '../../components/SearchForm';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock AuthContext
const mockAuthContext = {
  isAuthenticated: false,
  user: null,
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

describe('SearchForm', () => {
  const mockOnSearch = jest.fn();

  beforeEach(() => {
    mockFetch.mockClear();
    mockOnSearch.mockClear();
  });

  it('renders search form with all fields', () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    expect(screen.getByPlaceholderText('Job title, keywords, or company')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Location or remote')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /advanced filters/i })).toBeInTheDocument();
  });

  it('handles basic search submission', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const keywordInput = screen.getByPlaceholderText('Job title, keywords, or company');
    const locationInput = screen.getByPlaceholderText('Location or remote');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(keywordInput, { target: { value: 'React Developer' } });
    fireEvent.change(locationInput, { target: { value: 'Remote' } });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith({
        keywords: 'React Developer',
        location: 'Remote',
        jobType: '',
        experienceLevel: '',
        salaryMin: '',
        salaryMax: '',
        isRemote: false,
        skills: []
      });
    });
  });

  it('handles empty search submission', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith({
        keywords: '',
        location: '',
        jobType: '',
        experienceLevel: '',
        salaryMin: '',
        salaryMax: '',
        isRemote: false,
        skills: []
      });
    });
  });

  it('toggles advanced filters', () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const advancedButton = screen.getByRole('button', { name: /advanced filters/i });
    fireEvent.click(advancedButton);

    // Should show advanced filter fields
    expect(screen.getByLabelText('Job Type')).toBeInTheDocument();
    expect(screen.getByLabelText('Experience Level')).toBeInTheDocument();
    expect(screen.getByLabelText('Minimum Salary')).toBeInTheDocument();
    expect(screen.getByLabelText('Maximum Salary')).toBeInTheDocument();
    expect(screen.getByLabelText('Remote Only')).toBeInTheDocument();
  });

  it('handles advanced search with all filters', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    // Open advanced filters
    const advancedButton = screen.getByRole('button', { name: /advanced filters/i });
    fireEvent.click(advancedButton);

    // Fill in all fields
    const keywordInput = screen.getByPlaceholderText('Job title, keywords, or company');
    const locationInput = screen.getByPlaceholderText('Location or remote');
    const jobTypeSelect = screen.getByLabelText('Job Type');
    const experienceSelect = screen.getByLabelText('Experience Level');
    const salaryMinInput = screen.getByLabelText('Minimum Salary');
    const salaryMaxInput = screen.getByLabelText('Maximum Salary');
    const remoteCheckbox = screen.getByLabelText('Remote Only');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(keywordInput, { target: { value: 'Frontend Developer' } });
    fireEvent.change(locationInput, { target: { value: 'United States' } });
    fireEvent.change(jobTypeSelect, { target: { value: 'Full-time' } });
    fireEvent.change(experienceSelect, { target: { value: 'Senior' } });
    fireEvent.change(salaryMinInput, { target: { value: '80000' } });
    fireEvent.change(salaryMaxInput, { target: { value: '120000' } });
    fireEvent.click(remoteCheckbox);
    fireEvent.click(searchButton);

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalledWith({
        keywords: 'Frontend Developer',
        location: 'United States',
        jobType: 'Full-time',
        experienceLevel: 'Senior',
        salaryMin: '80000',
        salaryMax: '120000',
        isRemote: true,
        skills: []
      });
    });
  });

  it('handles skills selection', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    // Open advanced filters
    const advancedButton = screen.getByRole('button', { name: /advanced filters/i });
    fireEvent.click(advancedButton);

    // Mock skills suggestions
    const mockSkills = ['React', 'TypeScript', 'JavaScript', 'Node.js'];
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSkills
    });

    const skillsInput = screen.getByPlaceholderText('Add skills...');
    fireEvent.change(skillsInput, { target: { value: 'React' } });

    // Wait for suggestions to appear
    await waitFor(() => {
      expect(screen.getByText('React')).toBeInTheDocument();
    });

    // Select a skill
    fireEvent.click(screen.getByText('React'));

    // Should show selected skill as a tag
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /remove react/i })).toBeInTheDocument();
  });

  it('removes selected skills', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    // Open advanced filters
    const advancedButton = screen.getByRole('button', { name: /advanced filters/i });
    fireEvent.click(advancedButton);

    // Mock skills suggestions
    const mockSkills = ['React', 'TypeScript'];
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSkills
    });

    const skillsInput = screen.getByPlaceholderText('Add skills...');
    fireEvent.change(skillsInput, { target: { value: 'React' } });

    await waitFor(() => {
      expect(screen.getByText('React')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('React'));

    // Remove the skill
    const removeButton = screen.getByRole('button', { name: /remove react/i });
    fireEvent.click(removeButton);

    expect(screen.queryByText('React')).not.toBeInTheDocument();
  });

  it('handles salary validation', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    // Open advanced filters
    const advancedButton = screen.getByRole('button', { name: /advanced filters/i });
    fireEvent.click(advancedButton);

    const salaryMinInput = screen.getByLabelText('Minimum Salary');
    const salaryMaxInput = screen.getByLabelText('Maximum Salary');

    // Test invalid salary range (min > max)
    fireEvent.change(salaryMinInput, { target: { value: '120000' } });
    fireEvent.change(salaryMaxInput, { target: { value: '80000' } });

    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);

    // Should show validation error
    await waitFor(() => {
      expect(screen.getByText('Minimum salary cannot be greater than maximum salary')).toBeInTheDocument();
    });
  });

  it('handles form reset', () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const keywordInput = screen.getByPlaceholderText('Job title, keywords, or company');
    const locationInput = screen.getByPlaceholderText('Location or remote');

    fireEvent.change(keywordInput, { target: { value: 'React Developer' } });
    fireEvent.change(locationInput, { target: { value: 'Remote' } });

    const resetButton = screen.getByRole('button', { name: /reset/i });
    fireEvent.click(resetButton);

    expect(keywordInput).toHaveValue('');
    expect(locationInput).toHaveValue('');
  });

  it('handles keyboard navigation', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const keywordInput = screen.getByPlaceholderText('Job title, keywords, or company');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(keywordInput, { target: { value: 'React Developer' } });
    fireEvent.keyDown(keywordInput, { key: 'Enter' });

    await waitFor(() => {
      expect(mockOnSearch).toHaveBeenCalled();
    });
  });

  it('shows loading state during search', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const keywordInput = screen.getByPlaceholderText('Job title, keywords, or company');
    const searchButton = screen.getByRole('button', { name: /search/i });

    fireEvent.change(keywordInput, { target: { value: 'React Developer' } });
    fireEvent.click(searchButton);

    // Should show loading state
    expect(screen.getByText('Searching...')).toBeInTheDocument();
    expect(searchButton).toBeDisabled();
  });

  it('handles search suggestions', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const keywordInput = screen.getByPlaceholderText('Job title, keywords, or company');

    // Mock suggestions API
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ['React Developer', 'React Native Developer', 'Frontend Developer']
    });

    fireEvent.change(keywordInput, { target: { value: 'React' } });

    // Wait for suggestions to appear
    await waitFor(() => {
      expect(screen.getByText('React Developer')).toBeInTheDocument();
      expect(screen.getByText('React Native Developer')).toBeInTheDocument();
    });

    // Click on a suggestion
    fireEvent.click(screen.getByText('React Developer'));

    expect(keywordInput).toHaveValue('React Developer');
  });

  it('handles location autocomplete', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const locationInput = screen.getByPlaceholderText('Location or remote');

    // Mock location suggestions
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ['New York, NY', 'San Francisco, CA', 'Remote']
    });

    fireEvent.change(locationInput, { target: { value: 'New' } });

    await waitFor(() => {
      expect(screen.getByText('New York, NY')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('New York, NY'));

    expect(locationInput).toHaveValue('New York, NY');
  });

  it('handles API errors gracefully', async () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} />);

    const keywordInput = screen.getByPlaceholderText('Job title, keywords, or company');

    // Mock API error
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    fireEvent.change(keywordInput, { target: { value: 'React' } });

    // Should not crash and should not show suggestions
    await waitFor(() => {
      expect(screen.queryByText('React Developer')).not.toBeInTheDocument();
    });
  });

  it('applies custom className prop', () => {
    renderWithProviders(<SearchForm onSearch={mockOnSearch} className="custom-search-form" />);

    const form = screen.getByRole('form');
    expect(form).toHaveClass('custom-search-form');
  });

  it('handles initial values', () => {
    const initialValues = {
      keywords: 'React Developer',
      location: 'Remote',
      jobType: 'Full-time',
      experienceLevel: 'Senior',
      salaryMin: '80000',
      salaryMax: '120000',
      isRemote: true,
      skills: ['React', 'TypeScript']
    };

    renderWithProviders(<SearchForm onSearch={mockOnSearch} initialValues={initialValues} />);

    expect(screen.getByDisplayValue('React Developer')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Remote')).toBeInTheDocument();
  });
}); 