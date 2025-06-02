import React from 'react';
import { render, screen } from '@testing-library/react';
import { FilterBar } from '../../components/FilterBar';
import '@testing-library/jest-dom';

const defaultFilters = {
  location: '',
  type: [],
  experienceLevel: '',
  category: '',
  salaryRange: ''
};

const renderFilterBar = (filters = defaultFilters) => {
  return render(
    <FilterBar 
      filters={filters} 
      onFilterChange={() => {}} 
    />
  );
};

describe('FilterBar Component', () => {
  it('renders filter bar component', () => {
    renderFilterBar();
    
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Job Type')).toBeInTheDocument();
    expect(screen.getByText('Category')).toBeInTheDocument();
  });

  it('renders location options', () => {
    renderFilterBar();
    
    expect(screen.getByText('All Locations')).toBeInTheDocument();
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByText('US Remote')).toBeInTheDocument();
  });

  it('renders category options', () => {
    renderFilterBar();
    
    expect(screen.getByText('All Categories')).toBeInTheDocument();
    expect(screen.getByText('Software Development')).toBeInTheDocument();
    expect(screen.getByText('Data Science')).toBeInTheDocument();
  });

  it('renders job type button', () => {
    renderFilterBar();
    
    expect(screen.getByText('All Types')).toBeInTheDocument();
  });

  it('renders with pre-selected location', () => {
    const filtersWithLocation = { ...defaultFilters, location: 'US Remote' };
    renderFilterBar(filtersWithLocation);
    
    const locationSelects = screen.getAllByRole('combobox');
    const locationSelect = locationSelects[0] as HTMLSelectElement; // First select is location
    expect(locationSelect.value).toBe('US Remote');
  });

  it('renders with pre-selected category', () => {
    const filtersWithCategory = { ...defaultFilters, category: 'DevOps' };
    renderFilterBar(filtersWithCategory);
    
    const categorySelects = screen.getAllByRole('combobox');
    const categorySelect = categorySelects[1] as HTMLSelectElement; // Second select is category  
    expect(categorySelect.value).toBe('DevOps');
  });
}); 