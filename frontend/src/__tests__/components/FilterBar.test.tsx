import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { FilterBar } from '../../components/FilterBar';

const defaultFilters = {
  location: '',
  type: [],
  category: ''
};

const renderFilterBar = (props = {}) => {
  return render(
    <FilterBar 
      filters={defaultFilters} 
      onFilterChange={jest.fn()} 
      {...props} 
    />
  );
};

describe('FilterBar', () => {
  describe('Rendering', () => {
    test('renders all filter sections', () => {
    renderFilterBar();
    
    expect(screen.getByText('Location')).toBeInTheDocument();
    expect(screen.getByText('Job Type')).toBeInTheDocument();
    expect(screen.getByText('Category')).toBeInTheDocument();
  });

    test('renders location dropdown with all options', () => {
    renderFilterBar();
    
      const locationSelect = screen.getByDisplayValue('All Locations');
      expect(locationSelect).toBeInTheDocument();
      
      fireEvent.click(locationSelect);
      
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByText('US Remote')).toBeInTheDocument();
      expect(screen.getByText('Europe Remote')).toBeInTheDocument();
      expect(screen.getByText('Asia Pacific Remote')).toBeInTheDocument();
    });

    test('renders job type dropdown button', () => {
      renderFilterBar();
      
      const typeButton = screen.getByText('All Types');
      expect(typeButton).toBeInTheDocument();
    });

    test('renders category dropdown with all options', () => {
    renderFilterBar();
    
      const categorySelect = screen.getByDisplayValue('All Categories');
      expect(categorySelect).toBeInTheDocument();
      
      fireEvent.click(categorySelect);
      
    expect(screen.getByText('Software Development')).toBeInTheDocument();
    expect(screen.getByText('Data Science')).toBeInTheDocument();
      expect(screen.getByText('DevOps')).toBeInTheDocument();
      expect(screen.getByText('Product Management')).toBeInTheDocument();
      expect(screen.getByText('UX/UI Design')).toBeInTheDocument();
    });

    test('renders with correct styling classes', () => {
      renderFilterBar();
      
      const filterBar = screen.getByText('Location').closest('div');
      expect(filterBar).toHaveClass('bg-white', 'p-4', 'rounded-lg', 'shadow-sm', 'border', 'border-gray-200');
    });
  });

  describe('Location Filter', () => {
    test('handles location selection', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ onFilterChange: mockOnFilterChange });
      
      const locationSelect = screen.getByDisplayValue('All Locations');
      fireEvent.change(locationSelect, { target: { value: 'Remote' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: 'Remote',
        type: [],
        category: ''
      });
    });

    test('displays selected location', () => {
      renderFilterBar({ 
        filters: { ...defaultFilters, location: 'US Remote' } 
      });
      
      expect(screen.getByDisplayValue('US Remote')).toBeInTheDocument();
    });

    test('clears location when "All Locations" is selected', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: { ...defaultFilters, location: 'Remote' },
        onFilterChange: mockOnFilterChange 
      });
      
      const locationSelect = screen.getByDisplayValue('Remote');
      fireEvent.change(locationSelect, { target: { value: '' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: '',
        type: [],
        category: ''
      });
    });
  });

  describe('Job Type Filter', () => {
    test('opens job type dropdown when clicked', () => {
      renderFilterBar();
      
      const typeButton = screen.getByText('All Types');
      fireEvent.click(typeButton);
      
      expect(screen.getByText('Full-time')).toBeInTheDocument();
      expect(screen.getByText('Part-time')).toBeInTheDocument();
      expect(screen.getByText('Contract')).toBeInTheDocument();
      expect(screen.getByText('Freelance')).toBeInTheDocument();
      expect(screen.getByText('Internship')).toBeInTheDocument();
      expect(screen.getByText('Temporary')).toBeInTheDocument();
    });

    test('handles job type selection', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ onFilterChange: mockOnFilterChange });
      
      const typeButton = screen.getByText('All Types');
      fireEvent.click(typeButton);
      
      const fullTimeCheckbox = screen.getByLabelText('Full-time');
      fireEvent.click(fullTimeCheckbox);
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: '',
        type: ['Full-time'],
        category: ''
      });
    });

    test('handles multiple job type selections', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ onFilterChange: mockOnFilterChange });
      
      const typeButton = screen.getByText('All Types');
      fireEvent.click(typeButton);
      
      const fullTimeCheckbox = screen.getByLabelText('Full-time');
      const partTimeCheckbox = screen.getByLabelText('Part-time');
      
      fireEvent.click(fullTimeCheckbox);
      fireEvent.click(partTimeCheckbox);
      
      expect(mockOnFilterChange).toHaveBeenLastCalledWith({
        location: '',
        type: ['Full-time', 'Part-time'],
        category: ''
      });
    });

    test('handles job type deselection', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: { ...defaultFilters, type: ['Full-time', 'Part-time'] },
        onFilterChange: mockOnFilterChange 
      });
      
      const typeButton = screen.getByText('2 selected');
      fireEvent.click(typeButton);
      
      const fullTimeCheckbox = screen.getByLabelText('Full-time');
      fireEvent.click(fullTimeCheckbox);
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: '',
        type: ['Part-time'],
        category: ''
      });
    });

    test('displays selected count in button', () => {
      renderFilterBar({ 
        filters: { ...defaultFilters, type: ['Full-time', 'Part-time', 'Contract'] } 
      });
      
      expect(screen.getByText('3 selected')).toBeInTheDocument();
    });

    test('shows selected type tags', () => {
      renderFilterBar({ 
        filters: { ...defaultFilters, type: ['Full-time', 'Part-time'] } 
      });
      
      expect(screen.getByText('Full-time')).toBeInTheDocument();
      expect(screen.getByText('Part-time')).toBeInTheDocument();
    });

    test('removes type when X button is clicked', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: { ...defaultFilters, type: ['Full-time'] },
        onFilterChange: mockOnFilterChange 
      });
      
      const removeButton = screen.getByRole('button', { name: /remove full-time/i });
      fireEvent.click(removeButton);
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: '',
        type: [],
        category: ''
      });
    });

    test('clears all types when "Clear all" is clicked', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: { ...defaultFilters, type: ['Full-time', 'Part-time'] },
        onFilterChange: mockOnFilterChange 
      });
      
      const typeButton = screen.getByText('2 selected');
      fireEvent.click(typeButton);
      
      const clearAllButton = screen.getByText('Clear all');
      fireEvent.click(clearAllButton);
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: '',
        type: [],
        category: ''
      });
    });

    test('rotates chevron icon when dropdown is opened', () => {
      renderFilterBar();
      
      const typeButton = screen.getByText('All Types');
      const chevron = typeButton.querySelector('svg');
      
      expect(chevron).not.toHaveClass('rotate-180');
      
      fireEvent.click(typeButton);
      
      expect(chevron).toHaveClass('rotate-180');
    });

    test('closes dropdown when clicking outside', async () => {
    renderFilterBar();
    
      const typeButton = screen.getByText('All Types');
      fireEvent.click(typeButton);
      
      expect(screen.getByText('Full-time')).toBeInTheDocument();
      
      // Click outside the dropdown
      fireEvent.mouseDown(document.body);
      
      await waitFor(() => {
        expect(screen.queryByText('Full-time')).not.toBeInTheDocument();
  });
    });
  });

  describe('Category Filter', () => {
    test('handles category selection', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ onFilterChange: mockOnFilterChange });
      
      const categorySelect = screen.getByDisplayValue('All Categories');
      fireEvent.change(categorySelect, { target: { value: 'Software Development' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: '',
        type: [],
        category: 'Software Development'
      });
    });

    test('displays selected category', () => {
      renderFilterBar({ 
        filters: { ...defaultFilters, category: 'Data Science' } 
      });
      
      expect(screen.getByDisplayValue('Data Science')).toBeInTheDocument();
    });

    test('clears category when "All Categories" is selected', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: { ...defaultFilters, category: 'DevOps' },
        onFilterChange: mockOnFilterChange 
      });
      
      const categorySelect = screen.getByDisplayValue('DevOps');
      fireEvent.change(categorySelect, { target: { value: '' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: '',
        type: [],
        category: ''
      });
    });
  });

  describe('Combined Filters', () => {
    test('maintains other filters when one is changed', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: { 
          location: 'Remote', 
          type: ['Full-time'], 
          category: 'Software Development' 
        },
        onFilterChange: mockOnFilterChange 
      });
    
      const locationSelect = screen.getByDisplayValue('Remote');
      fireEvent.change(locationSelect, { target: { value: 'US Remote' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: 'US Remote',
        type: ['Full-time'],
        category: 'Software Development'
      });
    });

    test('handles multiple filter changes', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ onFilterChange: mockOnFilterChange });
      
      // Change location
      const locationSelect = screen.getByDisplayValue('All Locations');
      fireEvent.change(locationSelect, { target: { value: 'Remote' } });
      
      // Change category
      const categorySelect = screen.getByDisplayValue('All Categories');
      fireEvent.change(categorySelect, { target: { value: 'Data Science' } });
      
      // Add job type
      const typeButton = screen.getByText('All Types');
      fireEvent.click(typeButton);
      const fullTimeCheckbox = screen.getByLabelText('Full-time');
      fireEvent.click(fullTimeCheckbox);
      
      expect(mockOnFilterChange).toHaveBeenLastCalledWith({
        location: 'Remote',
        type: ['Full-time'],
        category: 'Data Science'
      });
    });
  });

  describe('Accessibility', () => {
    test('has proper labels for all form elements', () => {
      renderFilterBar();
      
      expect(screen.getByLabelText('Location')).toBeInTheDocument();
      expect(screen.getByLabelText('Category')).toBeInTheDocument();
      
      // Job type dropdown
      const typeButton = screen.getByText('All Types');
      expect(typeButton).toHaveAttribute('type', 'button');
  });

    test('has proper ARIA attributes for dropdown', () => {
      renderFilterBar();
      
      const typeButton = screen.getByText('All Types');
      fireEvent.click(typeButton);
      
      const checkboxes = screen.getAllByRole('checkbox');
      checkboxes.forEach(checkbox => {
        expect(checkbox).toHaveAttribute('type', 'checkbox');
      });
    });

    test('has proper focus management', () => {
      renderFilterBar();
      
      const typeButton = screen.getByText('All Types');
      fireEvent.click(typeButton);
      
      const firstCheckbox = screen.getByLabelText('Full-time');
      expect(firstCheckbox).toBeInTheDocument();
    });
  });

  describe('Edge Cases', () => {
    test('handles empty filters object', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: {},
        onFilterChange: mockOnFilterChange 
      });
      
      const locationSelect = screen.getByDisplayValue('All Locations');
      fireEvent.change(locationSelect, { target: { value: 'Remote' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: 'Remote'
      });
    });

    test('handles filters with additional properties', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ 
        filters: { 
          ...defaultFilters, 
          company: 'Google',
          salary: '100k+'
        },
        onFilterChange: mockOnFilterChange 
      });
    
      const locationSelect = screen.getByDisplayValue('All Locations');
      fireEvent.change(locationSelect, { target: { value: 'Remote' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledWith({
        location: 'Remote',
        type: [],
        category: '',
        company: 'Google',
        salary: '100k+'
      });
    });

    test('handles rapid filter changes', () => {
      const mockOnFilterChange = jest.fn();
      renderFilterBar({ onFilterChange: mockOnFilterChange });
      
      const locationSelect = screen.getByDisplayValue('All Locations');
      
      fireEvent.change(locationSelect, { target: { value: 'Remote' } });
      fireEvent.change(locationSelect, { target: { value: 'US Remote' } });
      fireEvent.change(locationSelect, { target: { value: 'Europe Remote' } });
      
      expect(mockOnFilterChange).toHaveBeenCalledTimes(3);
      expect(mockOnFilterChange).toHaveBeenLastCalledWith({
        location: 'Europe Remote',
        type: [],
        category: ''
      });
    });
  });
}); 