import React from 'react';
import { render, screen } from '@testing-library/react';
import { LoadingSpinner } from '../../components/LoadingSpinner';

describe('LoadingSpinner Component', () => {
  it('should render loading spinner with default props', () => {
    render(<LoadingSpinner />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
    expect(spinner).toHaveAttribute('aria-label', 'Loading...');
  });

  it('should render with custom size', () => {
    const { rerender } = render(<LoadingSpinner size="sm" />);
    let spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-4', 'h-4');
    
    rerender(<LoadingSpinner size="md" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-6', 'h-6');
    
    rerender(<LoadingSpinner size="lg" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-8', 'h-8');
    
    rerender(<LoadingSpinner size="xl" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-12', 'h-12');
  });

  it('should render with custom color', () => {
    const { rerender } = render(<LoadingSpinner color="blue" />);
    let spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('text-blue-500');
    
    rerender(<LoadingSpinner color="green" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('text-green-500');
    
    rerender(<LoadingSpinner color="red" />);
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('text-red-500');
  });

  it('should render with custom text', () => {
    render(<LoadingSpinner text="Please wait..." />);
    
    expect(screen.getByText('Please wait...')).toBeInTheDocument();
    expect(screen.getByRole('status')).toHaveAttribute('aria-label', 'Please wait...');
  });

  it('should render with custom className', () => {
    render(<LoadingSpinner className="custom-spinner" />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('custom-spinner');
  });

  it('should render without text when text prop is empty', () => {
    render(<LoadingSpinner text="" />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toBeInTheDocument();
    expect(screen.queryByText('Loading...')).not.toBeInTheDocument();
  });

  it('should render with full screen overlay', () => {
    render(<LoadingSpinner fullScreen />);
    
    const overlay = screen.getByTestId('loading-overlay');
    expect(overlay).toBeInTheDocument();
    expect(overlay).toHaveClass('fixed', 'inset-0', 'bg-black', 'bg-opacity-50');
  });

  it('should render inline without overlay', () => {
    render(<LoadingSpinner />);
    
    expect(screen.queryByTestId('loading-overlay')).not.toBeInTheDocument();
    expect(screen.getByRole('status')).toBeInTheDocument();
  });

  it('should be accessible with proper ARIA attributes', () => {
    render(<LoadingSpinner text="Loading data..." />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveAttribute('aria-label', 'Loading data...');
    expect(spinner).toHaveAttribute('aria-live', 'polite');
  });

  it('should handle different combinations of props', () => {
    const { rerender } = render(
      <LoadingSpinner 
        size="lg" 
        color="blue" 
        text="Processing..." 
        className="test-class" 
      />
    );
    
    let spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-8', 'h-8', 'text-blue-500', 'test-class');
    expect(screen.getByText('Processing...')).toBeInTheDocument();
    
    rerender(
      <LoadingSpinner 
        size="sm" 
        color="green" 
        text="Saving..." 
        fullScreen 
      />
    );
    
    spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('w-4', 'h-4', 'text-green-500');
    expect(screen.getByText('Saving...')).toBeInTheDocument();
    expect(screen.getByTestId('loading-overlay')).toBeInTheDocument();
  });

  it('should render spinner animation correctly', () => {
    render(<LoadingSpinner />);
    
    const spinner = screen.getByRole('status');
    expect(spinner).toHaveClass('animate-spin');
  });

  it('should handle undefined and null props gracefully', () => {
    const { rerender } = render(<LoadingSpinner text={undefined} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    
    rerender(<LoadingSpinner text={null} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    
    rerender(<LoadingSpinner size={undefined} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
    
    rerender(<LoadingSpinner color={undefined} />);
    expect(screen.getByRole('status')).toBeInTheDocument();
  });
}); 