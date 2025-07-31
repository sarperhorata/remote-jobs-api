import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { SearchBar } from '../../components/SearchBar';

describe('SearchBar Component', () => {
  const defaultProps = {
    value: '',
    onChange: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render search bar with default props', () => {
    render(<SearchBar {...defaultProps} />);
    
    expect(screen.getByRole('textbox')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /search/i })).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Search jobs...')).toBeInTheDocument();
  });

  it('should render with custom placeholder', () => {
    render(<SearchBar {...defaultProps} placeholder="Search companies..." />);
    
    expect(screen.getByPlaceholderText('Search companies...')).toBeInTheDocument();
  });

  it('should display the provided value', () => {
    render(<SearchBar {...defaultProps} value="React Developer" />);
    
    expect(screen.getByDisplayValue('React Developer')).toBeInTheDocument();
  });

  it('should call onChange when input value changes', () => {
    const onChange = jest.fn();
    render(<SearchBar {...defaultProps} onChange={onChange} />);
    
    const input = screen.getByRole('textbox');
    fireEvent.change(input, { target: { value: 'Frontend Developer' } });
    
    expect(onChange).toHaveBeenCalledWith('Frontend Developer');
  });

  it('should call onSubmit when form is submitted', () => {
    const onSubmit = jest.fn();
    render(<SearchBar {...defaultProps} onSubmit={onSubmit} />);
    
    const form = screen.getByRole('textbox').closest('form');
    fireEvent.submit(form!);
    
    expect(onSubmit).toHaveBeenCalled();
  });

  it('should call onSubmit when search button is clicked', () => {
    const onSubmit = jest.fn();
    render(<SearchBar {...defaultProps} onSubmit={onSubmit} />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    fireEvent.click(searchButton);
    
    expect(onSubmit).toHaveBeenCalled();
  });

  it('should display loading indicator when isLoading is true', () => {
    render(<SearchBar {...defaultProps} isLoading={true} />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('should not display loading indicator when isLoading is false', () => {
    render(<SearchBar {...defaultProps} isLoading={false} />);
    
    expect(screen.queryByRole('status')).not.toBeInTheDocument();
  });

  it('should display suggestions when provided', () => {
    const suggestions = ['React Developer', 'Frontend Engineer', 'JavaScript Developer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} />);
    
    expect(screen.getByText('React Developer')).toBeInTheDocument();
    expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
    expect(screen.getByText('JavaScript Developer')).toBeInTheDocument();
  });

  it('should not display suggestions when empty array is provided', () => {
    render(<SearchBar {...defaultProps} suggestions={[]} />);
    
    expect(screen.queryByRole('list')).not.toBeInTheDocument();
  });

  it('should call onSuggestionClick when suggestion is clicked', () => {
    const onSuggestionClick = jest.fn();
    const suggestions = ['React Developer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} onSuggestionClick={onSuggestionClick} />);
    
    const suggestion = screen.getByText('React Developer');
    fireEvent.click(suggestion);
    
    expect(onSuggestionClick).toHaveBeenCalledWith('React Developer');
  });

  it('should have proper CSS classes for styling', () => {
    render(<SearchBar {...defaultProps} />);
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveClass(
      'block', 'w-full', 'pl-10', 'pr-3', 'py-2', 'border', 'border-gray-300', 
      'rounded-md', 'leading-5', 'bg-white', 'placeholder-gray-500', 
      'focus:outline-none', 'focus:placeholder-gray-400', 'focus:ring-1', 
      'focus:ring-blue-500', 'focus:border-blue-500'
    );
  });

  it('should have proper search button styling', () => {
    render(<SearchBar {...defaultProps} />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toHaveClass('bg-blue-500', 'text-white', 'px-3', 'py-1', 'rounded');
  });

  it('should have proper suggestion list styling', () => {
    const suggestions = ['React Developer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} />);
    
    const suggestionList = screen.getByRole('list');
    expect(suggestionList).toHaveClass('bg-white', 'border', 'border-gray-300', 'rounded-md', 'mt-1', 'absolute', 'z-10', 'w-full');
  });

  it('should have proper suggestion item styling', () => {
    const suggestions = ['React Developer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} />);
    
    const suggestionItem = screen.getByText('React Developer');
    expect(suggestionItem).toHaveClass('px-4', 'py-2', 'hover:bg-gray-100', 'cursor-pointer');
  });

  it('should have search icon', () => {
    render(<SearchBar {...defaultProps} />);
    
    const searchIcon = screen.getByRole('textbox').parentElement?.querySelector('svg');
    expect(searchIcon).toBeInTheDocument();
    expect(searchIcon).toHaveClass('h-5', 'w-5', 'text-gray-400');
  });

  it('should handle multiple suggestions correctly', () => {
    const suggestions = ['React Developer', 'Frontend Engineer', 'JavaScript Developer', 'UI/UX Designer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} />);
    
    suggestions.forEach(suggestion => {
      expect(screen.getByText(suggestion)).toBeInTheDocument();
    });
  });

  it('should handle special characters in suggestions', () => {
    const suggestions = ['React/TypeScript Developer', 'Frontend & Backend Engineer', 'JavaScript (ES6+) Developer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} />);
    
    suggestions.forEach(suggestion => {
      expect(screen.getByText(suggestion)).toBeInTheDocument();
    });
  });

  it('should handle empty value correctly', () => {
    render(<SearchBar {...defaultProps} value="" />);
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveValue('');
  });

  it('should handle long input values', () => {
    const longValue = 'This is a very long search query that should be handled properly by the search bar component';
    render(<SearchBar {...defaultProps} value={longValue} />);
    
    expect(screen.getByDisplayValue(longValue)).toBeInTheDocument();
  });

  it('should have proper accessibility attributes', () => {
    render(<SearchBar {...defaultProps} />);
    
    const searchButton = screen.getByRole('button', { name: /search/i });
    expect(searchButton).toHaveAttribute('aria-label', 'search');
    
    const input = screen.getByRole('textbox');
    expect(input).toHaveAttribute('type', 'text');
  });

  it('should handle form submission with Enter key', () => {
    const onSubmit = jest.fn();
    render(<SearchBar {...defaultProps} onSubmit={onSubmit} />);
    
    const form = screen.getByRole('textbox').closest('form');
    fireEvent.submit(form!);
    
    expect(onSubmit).toHaveBeenCalled();
  });

  it('should not call onSubmit when onSuggestionClick is not provided', () => {
    const suggestions = ['React Developer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} />);
    
    const suggestion = screen.getByText('React Developer');
    expect(() => fireEvent.click(suggestion)).not.toThrow();
  });

  it('should handle loading state with suggestions', () => {
    const suggestions = ['React Developer'];
    render(<SearchBar {...defaultProps} suggestions={suggestions} isLoading={true} />);
    
    expect(screen.getByRole('status')).toBeInTheDocument();
    expect(screen.getByText('React Developer')).toBeInTheDocument();
  });
}); 