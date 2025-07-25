import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import SearchFilters from '../../components/JobSearch/SearchFilters';

// Mock data and functions
const mockOnFiltersChange = jest.fn();

const defaultFilters = {
  query: '',
  location: '',
  jobType: '',
  workType: '',
  experiences: [],
  experience_level: '',
  salaryMin: '',
  salaryMax: '',
  company: '',
  postedWithin: '',
  postedAge: '',
  salaryRange: ''
};

const mockProps = {
  filters: defaultFilters,
  onFiltersChange: mockOnFiltersChange,
};

describe('SearchFilters Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders all filter sections with associated controls', () => {
    render(<SearchFilters {...mockProps} />);
    
    expect(screen.getByRole('heading', { name: /filters/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/job title, keywords.../i)).toBeInTheDocument();
    expect(screen.getByText(/work type/i)).toBeInTheDocument();
    expect(screen.getByText(/job type/i)).toBeInTheDocument();
    expect(screen.getByText(/experience level/i)).toBeInTheDocument();
    expect(screen.getByText(/posted/i)).toBeInTheDocument();
    expect(screen.getByText(/salary/i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/city, country.../i)).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/company name.../i)).toBeInTheDocument();
  });

  test('updates experience level filter correctly', async () => {
    render(<SearchFilters {...mockProps} />);
    
    // Deneyim seviyesi dropdown'unu aç
    fireEvent.click(screen.getByText(/select experience/i));
    // 'Senior' seçeneğini bul ve tıkla
    const seniorOption = await screen.findByText(/senior/i);
    fireEvent.click(seniorOption);

    await waitFor(() => {
      expect(mockOnFiltersChange).toHaveBeenCalledWith(expect.objectContaining({
        experiences: ['senior']
      }));
    });
  });

  test('clears all filters when "Clear All Filters" button is clicked', async () => {
    const filtersWithValues = { ...defaultFilters, query: 'Developer', experiences: ['senior'] };
    render(<SearchFilters {...mockProps} filters={filtersWithValues} />);

    const clearButton = screen.getByRole('button', { name: /clear all filters/i });
    fireEvent.click(clearButton);

    await waitFor(() => {
      expect(mockOnFiltersChange).toHaveBeenCalledWith({
        query: '',
        location: '',
        jobType: '',
        workType: '',
        experiences: [],
        company: '',
        postedAge: '',
        salaryRange: '',
      });
    });
  });
}); 