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

  test('renders all filter sections with associated controls', async () => {
    render(<SearchFilters {...mockProps} />);
    
    await waitFor(() => {
      expect(screen.getByRole('heading', { name: /filters/i })).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/job title, keywords.../i)).toBeInTheDocument();
      expect(screen.getAllByText(/work type/i).length).toBeGreaterThan(0);
      expect(screen.getAllByText(/job type/i).length).toBeGreaterThan(0);
      expect(screen.getByText(/experience level/i)).toBeInTheDocument();
      expect(screen.getByDisplayValue(/any time/i)).toBeInTheDocument();
      expect(screen.getAllByDisplayValue(/any/i).length).toBeGreaterThan(0);
      expect(screen.getByPlaceholderText(/city, country.../i)).toBeInTheDocument();
      expect(screen.getByPlaceholderText(/company name.../i)).toBeInTheDocument();
    });
  });

  test('updates experience level filter correctly', async () => {
    render(<SearchFilters {...mockProps} />);
    
    fireEvent.click(screen.getByText(/select experience.../i));
    
    await waitFor(() => {
      expect(screen.getByText(/senior/i)).toBeInTheDocument();
    });
    
    // Click on the senior option div instead of checkbox (since checkbox is disabled)
    const seniorOption = screen.getByText(/senior/i).closest('div');
    fireEvent.click(seniorOption!);

    await waitFor(() => {
      expect(mockOnFiltersChange).toHaveBeenCalledWith(expect.objectContaining({
        experiences: ['senior']
      }));
    });
  });

  test('clears all filters when "Clear All Filters" button is clicked', async () => {
    const filtersWithValues = { ...defaultFilters, query: 'Developer', experiences: ['senior'] };
    render(<SearchFilters {...mockProps} filters={filtersWithValues} />);

    const clearButton = screen.getByText(/clear all filters/i);
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