import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import JobAutocomplete from '../../components/JobAutocomplete';

// Mock the API config
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockReturnValue('http://localhost:8001/api/v1')
}));

// Mock fetch
global.fetch = jest.fn();

describe('JobAutocomplete', () => {
  const mockOnSelect = jest.fn();
  const mockOnChange = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  it('renders with placeholder text', async () => {
    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    expect(screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/)).toBeInTheDocument();
  });

  it('shows popular positions when focused with empty input', async () => {
    const mockPopularResponse = {
      positions: [
        { title: 'Software Engineer', count: 100, category: 'Technology' },
        { title: 'Product Manager', count: 80, category: 'Management' }
      ]
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPopularResponse
    });

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      expect(screen.getByText('Product Manager')).toBeInTheDocument();
    });
  });

  it('shows search count result for "react" after 1 second', async () => {
    const mockSearchResponse = {
      count: 29,
      query: 'react',
      cached_at: '2024-01-01T00:00:00Z'
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockSearchResponse
    });

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    await userEvent.type(input, 'react');

    // Wait for 1 second debounce
    await waitFor(() => {
      expect(screen.getByText(/We have \(29\) 'react' jobs available./)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('calls onSelect when a popular position is clicked', async () => {
    const mockPopularResponse = {
      positions: [
        { title: 'Software Engineer', count: 100, category: 'Technology' },
        { title: 'Product Manager', count: 80, category: 'Management' }
      ]
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPopularResponse
    });

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Software Engineer'));
    expect(mockOnSelect).toHaveBeenCalledWith({
      title: 'Software Engineer',
      count: 100,
      category: 'Technology'
    });
  });

  it('clears input and suggestions after selection', async () => {
    const mockPopularResponse = {
      positions: [
        { title: 'Software Engineer', count: 100, category: 'Technology' }
      ]
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockPopularResponse
    });

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    fireEvent.focus(input);

    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });

    fireEvent.click(screen.getByText('Software Engineer'));
    
    // Should call onChange with the selected title
    expect(mockOnChange).toHaveBeenCalledWith('Software Engineer');
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    await userEvent.type(input, 'react');

    // Should not crash and should not show dropdown
    await waitFor(() => {
      expect(screen.queryByText(/We have/)).not.toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('handles empty API response', async () => {
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => ({ count: 0, query: 'nonexistent' })
    });

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    await userEvent.type(input, 'nonexistent');

    // Should show 0 results
    await waitFor(() => {
      expect(screen.getByText(/We have \(0\) 'nonexistent' jobs available./)).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('debounces search requests', async () => {
    const mockSearchResponse = {
      count: 10,
      query: 'react',
      cached_at: '2024-01-01T00:00:00Z'
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockSearchResponse
    });

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    
    // Type quickly
    await userEvent.type(input, 'r');
    await userEvent.type(input, 'e');
    await userEvent.type(input, 'a');
    await userEvent.type(input, 'c');
    await userEvent.type(input, 't');

    // Should only make one API call after 1 second
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledTimes(1);
    }, { timeout: 2000 });
  });

  it('does not search for queries shorter than 3 characters', async () => {
    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    await userEvent.type(input, 're');

    // Should not make API call for 2 characters
    await new Promise(resolve => setTimeout(resolve, 1100));
    expect(global.fetch).not.toHaveBeenCalled();
  });

  it('shows loading state while fetching', async () => {
    // Mock a delayed response
    (global.fetch as jest.Mock).mockImplementationOnce(() => 
      new Promise(resolve => 
        setTimeout(() => resolve({
          ok: true,
          json: async () => ({ count: 10, query: 'react' })
        }), 500)
      )
    );

    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/e.g. Software Engineer, Product Manager, Data Scientist/);
    await userEvent.type(input, 'react');

    // Should show loading state
    await waitFor(() => {
      expect(screen.getByText('Searching for jobs...')).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('applies custom placeholder', () => {
    render(
      <JobAutocomplete 
        value="" 
        onChange={mockOnChange} 
        onSelect={mockOnSelect} 
        placeholder="Custom placeholder"
      />
    );
    
    expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument();
  });
}); 