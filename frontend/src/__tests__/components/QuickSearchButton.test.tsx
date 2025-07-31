import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import QuickSearchButton from '../../components/QuickSearchButton';

describe('QuickSearchButton Component', () => {
  const defaultProps = {
    title: 'React Developer',
    onClick: jest.fn(),
  };

  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render button with provided title', () => {
    render(<QuickSearchButton {...defaultProps} />);
    
    expect(screen.getByRole('button')).toBeInTheDocument();
    expect(screen.getByText('React Developer')).toBeInTheDocument();
  });

  it('should call onClick when button is clicked', () => {
    const onClick = jest.fn();
    render(<QuickSearchButton {...defaultProps} onClick={onClick} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    
    expect(onClick).toHaveBeenCalledTimes(1);
  });

  it('should render with different titles', () => {
    const { rerender } = render(<QuickSearchButton {...defaultProps} title="Frontend Engineer" />);
    expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
    
    rerender(<QuickSearchButton {...defaultProps} title="Backend Developer" />);
    expect(screen.getByText('Backend Developer')).toBeInTheDocument();
    
    rerender(<QuickSearchButton {...defaultProps} title="Full Stack Developer" />);
    expect(screen.getByText('Full Stack Developer')).toBeInTheDocument();
  });

  it('should have proper CSS classes for styling', () => {
    render(<QuickSearchButton {...defaultProps} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass(
      'px-4', 'py-2', 'bg-white', 'dark:bg-slate-800', 'border', 'border-gray-200',
      'dark:border-slate-600', 'rounded-lg', 'hover:bg-blue-50', 'dark:hover:bg-slate-700',
      'hover:border-blue-300', 'dark:hover:border-blue-500', 'transition-colors',
      'duration-200', 'text-sm', 'font-medium', 'text-gray-700', 'dark:text-gray-300',
      'hover:text-blue-600', 'dark:hover:text-blue-400'
    );
  });

  it('should handle empty title', () => {
    render(<QuickSearchButton {...defaultProps} title="" />);
    
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    expect(button).toHaveTextContent('');
  });

  it('should handle long titles', () => {
    const longTitle = 'This is a very long button title that should be displayed properly';
    render(<QuickSearchButton {...defaultProps} title={longTitle} />);
    
    expect(screen.getByText(longTitle)).toBeInTheDocument();
  });

  it('should handle special characters in title', () => {
    const specialTitle = 'React/TypeScript & Node.js Developer (Remote)';
    render(<QuickSearchButton {...defaultProps} title={specialTitle} />);
    
    expect(screen.getByText(specialTitle)).toBeInTheDocument();
  });

  it('should handle multiple clicks', () => {
    const onClick = jest.fn();
    render(<QuickSearchButton {...defaultProps} onClick={onClick} />);
    
    const button = screen.getByRole('button');
    fireEvent.click(button);
    fireEvent.click(button);
    fireEvent.click(button);
    
    expect(onClick).toHaveBeenCalledTimes(3);
  });

  it('should be accessible with proper button role', () => {
    render(<QuickSearchButton {...defaultProps} />);
    
    const button = screen.getByRole('button');
    expect(button).toBeInTheDocument();
    // Note: HTML buttons default to type="submit" when not specified
  });

  it('should handle undefined onClick gracefully', () => {
    render(<QuickSearchButton title="Test Button" onClick={undefined as any} />);
    
    const button = screen.getByRole('button');
    expect(() => fireEvent.click(button)).not.toThrow();
  });

  it('should handle null onClick gracefully', () => {
    render(<QuickSearchButton title="Test Button" onClick={null as any} />);
    
    const button = screen.getByRole('button');
    expect(() => fireEvent.click(button)).not.toThrow();
  });

  it('should render multiple buttons correctly', () => {
    const { rerender } = render(<QuickSearchButton {...defaultProps} title="Button 1" />);
    expect(screen.getByText('Button 1')).toBeInTheDocument();
    
    rerender(<QuickSearchButton {...defaultProps} title="Button 2" />);
    expect(screen.getByText('Button 2')).toBeInTheDocument();
    expect(screen.queryByText('Button 1')).not.toBeInTheDocument();
  });

  it('should have proper hover and focus states', () => {
    render(<QuickSearchButton {...defaultProps} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('hover:bg-blue-50', 'hover:border-blue-300', 'hover:text-blue-600');
  });

  it('should handle dark mode classes', () => {
    render(<QuickSearchButton {...defaultProps} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass(
      'dark:bg-slate-800', 'dark:border-slate-600', 'dark:hover:bg-slate-700',
      'dark:hover:border-blue-500', 'dark:text-gray-300', 'dark:hover:text-blue-400'
    );
  });

  it('should have proper transition classes', () => {
    render(<QuickSearchButton {...defaultProps} />);
    
    const button = screen.getByRole('button');
    expect(button).toHaveClass('transition-colors', 'duration-200');
  });

  it('should handle button with numbers in title', () => {
    render(<QuickSearchButton {...defaultProps} title="React 18 Developer" />);
    
    expect(screen.getByText('React 18 Developer')).toBeInTheDocument();
  });

  it('should handle button with emojis in title', () => {
    render(<QuickSearchButton {...defaultProps} title="🚀 Remote Developer" />);
    
    expect(screen.getByText('🚀 Remote Developer')).toBeInTheDocument();
  });
});