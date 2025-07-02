import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import SearchFilters from '../../components/JobSearch/SearchFilters';

// Mock API Config
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('http://localhost:8001/api/v1')
}));

// Mock fetch
global.fetch = jest.fn();

const mockProps = {
  filters: {
    workTypes: [],
    jobTypes: [],
    experiences: [],
    postedAge: '30DAYS',
    sortBy: 'relevance',
    salaryRange: '',
    location: '',
    company: '',
    page: 1,
    limit: 10
  },
  onFiltersChange: jest.fn(),
  availableCompanies: ['TechCorp', 'StartupX'],
  availableLocations: ['Remote', 'New York']
};

describe('SearchFilters Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
  });

  it('renders all filter sections', () => {
    render(<SearchFilters {...mockProps} />);

    expect(screen.getByText('Work Type')).toBeInTheDocument();
    expect(screen.getByText('Job Type')).toBeInTheDocument();
    expect(screen.getByText('Experience Level')).toBeInTheDocument();
    expect(screen.getByText('Salary Range')).toBeInTheDocument();
    expect(screen.getByText('Posted Within')).toBeInTheDocument();
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Company')).toBeInTheDocument();
  });

  it('calls onFiltersChange when work type is selected', () => {
    render(<SearchFilters {...mockProps} />);

    const remoteCheckbox = screen.getByLabelText('Remote');
    fireEvent.click(remoteCheckbox);

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      ...mockProps.filters,
      workTypes: ['remote'],
      page: 1
    });
  });

  it('calls onFiltersChange when job type is selected', () => {
    render(<SearchFilters {...mockProps} />);

    const fullTimeCheckbox = screen.getByLabelText('Full-time');
    fireEvent.click(fullTimeCheckbox);

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      ...mockProps.filters,
      jobTypes: ['full-time'],
      page: 1
    });
  });

  it('calls onFiltersChange when experience level is selected', () => {
    render(<SearchFilters {...mockProps} />);

    const seniorCheckbox = screen.getByLabelText('Senior (6y+)');
    fireEvent.click(seniorCheckbox);

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      ...mockProps.filters,
      experiences: ['senior'],
      page: 1
    });
  });

  it('calls onFiltersChange when salary range is selected', () => {
    render(<SearchFilters {...mockProps} />);

    const salarySelect = screen.getByDisplayValue('Any');
    fireEvent.change(salarySelect, { target: { value: '72000-108000' } });

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      ...mockProps.filters,
      salaryRange: '72000-108000',
      page: 1
    });
  });

  it('calls onFiltersChange when posted age is selected', () => {
    render(<SearchFilters {...mockProps} />);

    const postedSelect = screen.getByDisplayValue('1 month');
    fireEvent.change(postedSelect, { target: { value: '7DAYS' } });

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      ...mockProps.filters,
      postedAge: '7DAYS',
      page: 1
    });
  });

  it('renders location and company input fields', () => {
    render(<SearchFilters {...mockProps} />);

    const locationInput = screen.getByPlaceholderText('City, country...');
    const companyInput = screen.getByPlaceholderText('Company name...');

    expect(locationInput).toBeInTheDocument();
    expect(companyInput).toBeInTheDocument();
  });

  it('updates filter state when location input changes', () => {
    render(<SearchFilters {...mockProps} />);

    const locationInput = screen.getByPlaceholderText('City, country...');
    fireEvent.change(locationInput, { target: { value: 'New York' } });

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      ...mockProps.filters,
      location: 'New York',
      page: 1
    });
  });

  it('updates filter state when company input changes', () => {
    render(<SearchFilters {...mockProps} />);

    const companyInput = screen.getByPlaceholderText('Company name...');
    fireEvent.change(companyInput, { target: { value: 'Google' } });

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      ...mockProps.filters,
      company: 'Google',
      page: 1
    });
  });

  it('pre-selects filters based on props', () => {
    const propsWithFilters = {
      ...mockProps,
      filters: {
        ...mockProps.filters,
        workTypes: ['remote'],
        jobTypes: ['full-time'],
        experiences: ['senior'],
        salaryRange: '72000-108000',
        postedAge: '7DAYS'
      }
    };

    render(<SearchFilters {...propsWithFilters} />);

    expect(screen.getByLabelText('Remote')).toBeChecked();
    expect(screen.getByLabelText('Full-time')).toBeChecked();
    expect(screen.getByLabelText('Senior (6y+)')).toBeChecked();
    expect(screen.getByDisplayValue('$72K-108K')).toBeInTheDocument();
    expect(screen.getByDisplayValue('1 week')).toBeInTheDocument();
  });

  it('clears all filters when clear button is clicked', () => {
    render(<SearchFilters {...mockProps} />);

    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);

    expect(mockProps.onFiltersChange).toHaveBeenCalledWith({
      workTypes: [],
      jobTypes: [],
      experiences: [],
      postedAge: '30DAYS',
      sortBy: 'relevance',
      salaryRange: '',
      location: '',
      company: '',
      page: 1,
      limit: mockProps.filters.limit
    });
  });
}); 