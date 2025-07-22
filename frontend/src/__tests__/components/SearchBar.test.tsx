import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import SearchBar from '../../components/SearchBar';

// Mock data
const mockProps = {
  placeholder: 'Search jobs...',
  value: '',
  onChange: jest.fn(),
  onSubmit: jest.fn(),
  suggestions: [],
  onSuggestionClick: jest.fn(),
  isLoading: false,
};

describe('SearchBar Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders search input with placeholder', () => {
    render(<SearchBar {...mockProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search jobs...');
    expect(searchInput).toBeInTheDocument();
  });

  test('calls onChange when input value changes', () => {
    render(<SearchBar {...mockProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search jobs...');
    fireEvent.change(searchInput, { target: { value: 'react developer' } });
    
    expect(mockProps.onChange).toHaveBeenCalledWith('react developer');
  });

  test('calls onSubmit when form is submitted', () => {
    render(<SearchBar {...mockProps} />);
    
    const searchInput = screen.getByPlaceholderText('Search jobs...');
    fireEvent.change(searchInput, { target: { value: 'react developer' } });
    
    const form = searchInput.closest('form');
    if (form) {
      fireEvent.submit(form);
    }
    
    expect(mockProps.onSubmit).toHaveBeenCalled();
  });

  test('displays loading spinner when isLoading is true', () => {
    render(<SearchBar {...mockProps} isLoading={true} />);
    
    const loadingSpinner = screen.getByRole('status');
    expect(loadingSpinner).toBeInTheDocument();
  });

  test('does not display loading spinner when isLoading is false', () => {
    render(<SearchBar {...mockProps} isLoading={false} />);
    
    const loadingSpinner = screen.queryByRole('status');
    expect(loadingSpinner).not.toBeInTheDocument();
  });

  test('displays suggestions when provided', () => {
    const suggestions = ['React Developer', 'React Native Developer', 'Frontend Developer'];
    render(<SearchBar {...mockProps} suggestions={suggestions} />);
    
    expect(screen.getByText('React Developer')).toBeInTheDocument();
    expect(screen.getByText('React Native Developer')).toBeInTheDocument();
    expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
  });

  test('calls onSuggestionClick when suggestion is clicked', () => {
    const suggestions = ['React Developer'];
    render(<SearchBar {...mockProps} suggestions={suggestions} />);
    
    const suggestion = screen.getByText('React Developer');
    fireEvent.click(suggestion);
    
    expect(mockProps.onSuggestionClick).toHaveBeenCalledWith('React Developer');
  });

  test('displays search button', () => {
    render(<SearchBar {...mockProps} />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toBeInTheDocument();
  });

  test('calls onSubmit when search button is clicked', () => {
    render(<SearchBar {...mockProps} />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);
    
    expect(mockProps.onSubmit).toHaveBeenCalled();
  });

  test('handles empty suggestions gracefully', () => {
    render(<SearchBar {...mockProps} suggestions={[]} />);
    
    // Should render without crashing
    expect(screen.getByPlaceholderText('Search jobs...')).toBeInTheDocument();
  });

  test('displays current value in input', () => {
    render(<SearchBar {...mockProps} value="react developer" />);
    
    const searchInput = screen.getByPlaceholderText('Search jobs...');
    expect(searchInput).toHaveValue('react developer');
  });
}); 