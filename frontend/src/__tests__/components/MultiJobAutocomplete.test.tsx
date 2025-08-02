import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import MultiJobAutocomplete from '../../components/MultiJobAutocomplete';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('MultiJobAutocomplete', () => {
  const mockOnSelect = jest.fn();

  beforeEach(() => {
    mockFetch.mockClear();
    mockOnSelect.mockClear();
  });

  it('renders with default placeholder', () => {
    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    expect(screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)')).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    renderWithProviders(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
        placeholder="Custom placeholder" 
      />
    );
    
    expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument();
  });

  it('handles input change', () => {
    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    fireEvent.change(input, { target: { value: 'react' } });
    
    expect(input).toHaveValue('react');
  });

  it('shows loading state when fetching suggestions', async () => {
    mockFetch.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: async () => []
      }), 100))
    );

    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    fireEvent.change(input, { target: { value: 'react' } });
    
    // Wait for debounce
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    }, { timeout: 1000 });
  });

  it('displays suggestions from API', async () => {
    const mockSuggestions = [
      { title: 'React Developer', count: 100, category: 'Technology' },
      { title: 'React Native Developer', count: 50, category: 'Technology' }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSuggestions
    });

    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    fireEvent.change(input, { target: { value: 'react' } });
    
    await waitFor(() => {
      expect(screen.getByText('React Developer')).toBeInTheDocument();
      expect(screen.getByText('React Native Developer')).toBeInTheDocument();
    }, { timeout: 2000 });
  });

  it('handles suggestion selection', async () => {
    const mockSuggestions = [
      { title: 'React Developer', count: 100, category: 'Technology' }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSuggestions
    });

    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    fireEvent.change(input, { target: { value: 'react' } });
    
    await waitFor(() => {
      const suggestion = screen.getByText('React Developer');
      fireEvent.click(suggestion);
    }, { timeout: 2000 });
    
    expect(mockOnSelect).toHaveBeenCalledWith([{ title: 'React Developer', count: 100, category: 'Technology' }]);
  });

  it('handles keyboard navigation', async () => {
    const mockSuggestions = [
      { title: 'React Developer', count: 100, category: 'Technology' },
      { title: 'React Native Developer', count: 50, category: 'Technology' }
    ];

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockSuggestions
    });

    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    fireEvent.change(input, { target: { value: 'react' } });
    
    await waitFor(() => {
      expect(screen.getByText('React Developer')).toBeInTheDocument();
    }, { timeout: 2000 });
    
    // Press arrow down
    fireEvent.keyDown(input, { key: 'ArrowDown' });
    
    // Press Enter
    fireEvent.keyDown(input, { key: 'Enter' });
    
    expect(mockOnSelect).toHaveBeenCalled();
  });

  it('handles API error gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    fireEvent.change(input, { target: { value: 'react' } });
    
    // Should not throw error
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalled();
    }, { timeout: 1000 });
  });

  it('debounces input changes', async () => {
    jest.useFakeTimers();
    
    renderWithProviders(<MultiJobAutocomplete onSelect={mockOnSelect} />);
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    
    // Rapid changes
    fireEvent.change(input, { target: { value: 'r' } });
    fireEvent.change(input, { target: { value: 're' } });
    fireEvent.change(input, { target: { value: 'rea' } });
    fireEvent.change(input, { target: { value: 'reac' } });
    fireEvent.change(input, { target: { value: 'react' } });
    
    // Should not call API immediately
    expect(mockFetch).not.toHaveBeenCalled();
    
    // Fast forward time
    jest.advanceTimersByTime(500);
    
    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledTimes(1);
    });
    
    jest.useRealTimers();
  });

  it('handles disabled state', () => {
    renderWithProviders(
      <MultiJobAutocomplete onSelect={mockOnSelect} disabled={true} />
    );
    
    const input = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)');
    expect(input).toBeDisabled();
  });

  it('applies custom className', () => {
    renderWithProviders(
      <MultiJobAutocomplete onSelect={mockOnSelect} className="custom-class" />
    );
    
    const container = screen.getByPlaceholderText('Search keywords (e.g., react, python, remote)').closest('div');
    expect(container).toHaveClass('custom-class');
  });
}); 