import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import MultiJobAutocomplete from '../../components/MultiJobAutocomplete';

// Mock the API configuration
jest.mock('../../utils/apiConfig', () => ({
  API_BASE_URL: 'http://localhost:5001'
}));

// Mock fetch
global.fetch = jest.fn();

describe('MultiJobAutocomplete', () => {
  const mockOnPositionsChange = jest.fn();
  const mockOnSearch = jest.fn();

  const defaultProps = {
    selectedPositions: [],
    onPositionsChange: mockOnPositionsChange,
    onSearch: mockOnSearch
  };

  const mockJobTitles = [
    { title: 'Frontend Developer', count: 25, category: 'Engineering' },
    { title: 'Backend Developer', count: 30, category: 'Engineering' },
    { title: 'Full Stack Developer', count: 20, category: 'Engineering' },
    { title: 'React Developer', count: 15, category: 'Engineering' },
    { title: 'Node.js Developer', count: 18, category: 'Engineering' }
  ];

  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({
        job_titles: mockJobTitles
      })
    });
  });

  test('renders search input with placeholder', () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    expect(input).toBeInTheDocument();
  });

  test('shows help text when no positions selected', () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    expect(screen.getByText(/start typing to search job positions/i)).toBeInTheDocument();
  });

  test('fetches job titles when typing', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'frontend' } });

    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/v1/jobs/job-titles/search?q=frontend')
      );
    });
  });

  test('shows dropdown with search results', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'developer' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();
    });

    expect(screen.getByText('5 positions found')).toBeInTheDocument();
  });

  test('adds position when clicked', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'frontend' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Frontend Developer'));

    expect(mockOnPositionsChange).toHaveBeenCalledWith([
      { title: 'Frontend Developer', count: 25, category: 'Engineering' }
    ]);
  });

  test('shows selected positions as chips', () => {
    const selectedPositions = [
      { title: 'Frontend Developer', count: 25, category: 'Engineering' },
      { title: 'Backend Developer', count: 30, category: 'Engineering' }
    ];

    render(
      <MultiJobAutocomplete 
        {...defaultProps} 
        selectedPositions={selectedPositions} 
      />
    );

    expect(screen.getByText('Selected Positions (2/10):')).toBeInTheDocument();
    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    expect(screen.getByText('Backend Developer')).toBeInTheDocument();
    expect(screen.getByText('(25)')).toBeInTheDocument();
    expect(screen.getByText('(30)')).toBeInTheDocument();
  });

  test('removes position when X button clicked', () => {
    const selectedPositions = [
      { title: 'Frontend Developer', count: 25, category: 'Engineering' }
    ];

    render(
      <MultiJobAutocomplete 
        {...defaultProps} 
        selectedPositions={selectedPositions} 
      />
    );

    const removeButton = screen.getAllByRole('button').find(btn => 
      btn.querySelector('svg') // X icon
    );
    
    if (removeButton) {
      fireEvent.click(removeButton);
    }

    expect(mockOnPositionsChange).toHaveBeenCalledWith([]);
  });

  test('clears all positions when Clear All clicked', () => {
    const selectedPositions = [
      { title: 'Frontend Developer', count: 25, category: 'Engineering' },
      { title: 'Backend Developer', count: 30, category: 'Engineering' }
    ];

    render(
      <MultiJobAutocomplete 
        {...defaultProps} 
        selectedPositions={selectedPositions} 
      />
    );

    const clearButton = screen.getByText('Clear All');
    fireEvent.click(clearButton);

    expect(mockOnPositionsChange).toHaveBeenCalledWith([]);
  });

  test('enables search button only when positions selected', () => {
    const { rerender } = render(<MultiJobAutocomplete {...defaultProps} />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toBeDisabled();

    const selectedPositions = [
      { title: 'Frontend Developer', count: 25, category: 'Engineering' }
    ];

    rerender(
      <MultiJobAutocomplete 
        {...defaultProps} 
        selectedPositions={selectedPositions} 
      />
    );

    expect(searchButton).not.toBeDisabled();
  });

  test('calls onSearch when search button clicked', () => {
    const selectedPositions = [
      { title: 'Frontend Developer', count: 25, category: 'Engineering' }
    ];

    render(
      <MultiJobAutocomplete 
        {...defaultProps} 
        selectedPositions={selectedPositions} 
      />
    );

    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);

    expect(mockOnSearch).toHaveBeenCalledWith(selectedPositions);
  });

  test('prevents duplicate selections', async () => {
    const selectedPositions = [
      { title: 'Frontend Developer', count: 25, category: 'Engineering' }
    ];

    render(
      <MultiJobAutocomplete 
        {...defaultProps} 
        selectedPositions={selectedPositions} 
      />
    );

    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'frontend' } });
    fireEvent.focus(input);

    await waitFor(() => {
      // The dropdown should show other developers but not the already selected one
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();
    });
    
    // The already selected "Frontend Developer" should not appear in dropdown
    const dropdownItems = screen.queryAllByText('Frontend Developer');
    // Should only find the one in the selected chips, not in dropdown
    expect(dropdownItems.length).toBe(1); // Only in the chips section
  });

  test('respects maximum selections limit', async () => {
    const selectedPositions = Array.from({ length: 10 }, (_, i) => ({
      title: `Developer ${i + 1}`,
      count: 10,
      category: 'Engineering'
    }));

    render(
      <MultiJobAutocomplete 
        {...defaultProps} 
        selectedPositions={selectedPositions}
        maxSelections={10}
      />
    );

    const input = screen.getByPlaceholderText(/search and select job titles/i);
    expect(input).toBeDisabled();

    expect(screen.getByText('10/10 positions selected. Maximum reached.')).toBeInTheDocument();
  });

  test('handles keyboard navigation', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'developer' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Test arrow down navigation
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    // First item should be highlighted (visual feedback)

    // Test enter key selection
    fireEvent.keyDown(input, { key: 'Enter' });

    expect(mockOnPositionsChange).toHaveBeenCalledWith([
      { title: 'Frontend Developer', count: 25, category: 'Engineering' }
    ]);
  });

  test('handles API error gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValue(new Error('API Error'));

    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'developer' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText(/no positions found/i)).toBeInTheDocument();
    });
  });

  test('shows loading state while fetching', async () => {
    // Mock a delayed response
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: () => Promise.resolve({ job_titles: mockJobTitles })
        }), 100)
      )
    );

    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'developer' } });
    fireEvent.focus(input);

    // Wait for loading state to appear
    await waitFor(() => {
      expect(screen.getByText('Searching positions...')).toBeInTheDocument();
    }, { timeout: 3000 });
  });

  test('closes dropdown when clicking outside', async () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'developer' } });
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
    });

    // Click outside
    fireEvent.mouseDown(document.body);

    await waitFor(() => {
      expect(screen.queryByText('Frontend Developer')).not.toBeInTheDocument();
    });
  });

  test('shows minimum character requirement', () => {
    render(<MultiJobAutocomplete {...defaultProps} />);
    
    const input = screen.getByPlaceholderText(/search and select job titles/i);
    fireEvent.change(input, { target: { value: 'a' } });
    fireEvent.focus(input);

    expect(screen.getByText('Type at least 2 characters to search')).toBeInTheDocument();
  });
}); 