import { render, screen, fireEvent } from '@testing-library/react';
import { SearchBar } from '../../components/SearchBar';
import '@testing-library/jest-dom';

describe('SearchBar', () => {
  const mockOnChange = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders with default placeholder', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);
    
    const input = screen.getByPlaceholderText('Search jobs...');
    expect(input).toBeInTheDocument();
  });

  it('renders with custom placeholder', () => {
    render(<SearchBar value="" onChange={mockOnChange} placeholder="Find companies..." />);
    
    const input = screen.getByPlaceholderText('Find companies...');
    expect(input).toBeInTheDocument();
  });

  it('displays the current value', () => {
    render(<SearchBar value="React Developer" onChange={mockOnChange} />);
    
    const input = screen.getByDisplayValue('React Developer');
    expect(input).toBeInTheDocument();
  });

  it('calls onChange when input changes', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);
    
    const input = screen.getByPlaceholderText('Search jobs...');
    fireEvent.change(input, { target: { value: 'JavaScript' } });
    
    expect(mockOnChange).toHaveBeenCalledWith('JavaScript');
    expect(mockOnChange).toHaveBeenCalledTimes(1);
  });

  it('calls onChange with different values', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);
    
    const input = screen.getByPlaceholderText('Search jobs...');
    
    fireEvent.change(input, { target: { value: 'Python' } });
    expect(mockOnChange).toHaveBeenCalledWith('Python');
    
    fireEvent.change(input, { target: { value: 'React' } });
    expect(mockOnChange).toHaveBeenCalledWith('React');
    
    expect(mockOnChange).toHaveBeenCalledTimes(2);
  });

  it('renders search icon', () => {
    const { container } = render(<SearchBar value="" onChange={mockOnChange} />);
    
    const searchIcon = container.querySelector('svg');
    expect(searchIcon).toBeInTheDocument();
    expect(searchIcon).toHaveClass('h-5', 'w-5', 'text-gray-400');
  });

  it('has correct CSS classes', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);
    
    const input = screen.getByPlaceholderText('Search jobs...');
    expect(input).toHaveClass(
      'block',
      'w-full',
      'pl-10',
      'pr-3',
      'py-2',
      'border',
      'border-gray-300',
      'rounded-md'
    );
  });

  it('has correct input type', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);
    
    const input = screen.getByPlaceholderText('Search jobs...');
    expect(input).toHaveAttribute('type', 'text');
  });

  it('renders without crashing', () => {
    expect(() => render(<SearchBar value="" onChange={mockOnChange} />)).not.toThrow();
  });

  it('input can receive focus', () => {
    render(<SearchBar value="" onChange={mockOnChange} />);
    
    const input = screen.getByPlaceholderText('Search jobs...');
    input.focus();
    expect(document.activeElement).toBe(input);
  });
}); 