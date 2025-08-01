import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import MultiJobAutocomplete from '../../components/MultiJobAutocomplete';

// Mock the API config
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockReturnValue('http://localhost:8001/api/v1')
}));

// Mock fetch
global.fetch = jest.fn();

describe('MultiJobAutocomplete', () => {
  const mockOnSelect = jest.fn();
  
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockClear();
  });

  it('renders with default placeholder text', async () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    expect(screen.getByPlaceholderText(/Search keywords/)).toBeInTheDocument();
  });

  it('renders with custom placeholder text', async () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect}
        placeholder="Custom placeholder"
      />
    );
    expect(screen.getByPlaceholderText('Custom placeholder')).toBeInTheDocument();
  });

  it('handles input changes', async () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    await userEvent.type(input, 'react');
    
    expect(input).toHaveValue('react');
  });

  it('handles API errors gracefully', async () => {
    (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('API Error'));

    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    await userEvent.type(input, 'react');

    // Should not crash
    expect(input).toHaveValue('react');
  });

  it('handles empty API response', async () => {
    const mockEmptyResponse = {
      positions: []
    };

    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockEmptyResponse
    });

    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    await userEvent.type(input, 'nonexistent');

    // Should not crash
    expect(input).toHaveValue('nonexistent');
  });

  it('applies custom className', () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect}
        className="custom-class"
      />
    );
    
    const container = screen.getByPlaceholderText(/Search keywords/).closest('.relative');
    expect(container).toHaveClass('custom-class');
  });

  it('is disabled when disabled prop is true', () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect}
        disabled={true}
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    expect(input).toBeDisabled();
  });

  it('handles focus and blur events', () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    fireEvent.focus(input);
    fireEvent.blur(input);
    
    // Should not crash
    expect(input).toBeInTheDocument();
  });

  it('handles keyboard events', () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    fireEvent.keyDown(input, { key: 'Enter' });
    fireEvent.keyDown(input, { key: 'Escape' });
    
    // Should not crash
    expect(input).toBeInTheDocument();
  });

  it('handles different input values', () => {
    const { rerender } = render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    expect(input).toHaveValue('');
    
    // Test with different values
    fireEvent.change(input, { target: { value: 'python' } });
    expect(input).toHaveValue('python');
    
    fireEvent.change(input, { target: { value: 'javascript' } });
    expect(input).toHaveValue('javascript');
  });

  it('handles special characters in input', () => {
    render(
      <MultiJobAutocomplete 
        onSelect={mockOnSelect} 
      />
    );
    
    const input = screen.getByPlaceholderText(/Search keywords/);
    fireEvent.change(input, { target: { value: 'react/typescript & node.js' } });
    
    expect(input).toHaveValue('react/typescript & node.js');
  });
}); 