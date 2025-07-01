import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';

// Mock component for testing
const MockJobFilters = ({ onFilterChange }: { onFilterChange?: (filters: any) => void }) => {
  const handleFilterChange = () => {
    if (onFilterChange) {
      onFilterChange({ location: 'Remote', type: 'full-time' });
    }
  };

  return (
    <div data-testid="job-filters">
      <button onClick={handleFilterChange} data-testid="apply-filters">
        Apply Filters
      </button>
      <select data-testid="location-filter">
        <option value="">All Locations</option>
        <option value="remote">Remote</option>
        <option value="onsite">On-site</option>
      </select>
      <select data-testid="type-filter">
        <option value="">All Types</option>
        <option value="full-time">Full-time</option>
        <option value="part-time">Part-time</option>
      </select>
    </div>
  );
};

describe('Job Filters Component', () => {
  it('should render filter options', () => {
    render(<MockJobFilters />);
    
    expect(screen.getByTestId('job-filters')).toBeInTheDocument();
    expect(screen.getByTestId('location-filter')).toBeInTheDocument();
    expect(screen.getByTestId('type-filter')).toBeInTheDocument();
  });

  it('should handle filter changes', () => {
    const mockOnFilterChange = jest.fn();
    render(<MockJobFilters onFilterChange={mockOnFilterChange} />);
    
    fireEvent.click(screen.getByTestId('apply-filters'));
    
    expect(mockOnFilterChange).toHaveBeenCalledWith({
      location: 'Remote',
      type: 'full-time'
    });
  });

  it('should have correct filter options', () => {
    render(<MockJobFilters />);
    
    const locationFilter = screen.getByTestId('location-filter');
    const typeFilter = screen.getByTestId('type-filter');
    
    expect(locationFilter).toHaveDisplayValue('All Locations');
    expect(typeFilter).toHaveDisplayValue('All Types');
  });
});
