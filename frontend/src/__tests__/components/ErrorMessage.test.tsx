import React from 'react';
import { render, screen } from '@testing-library/react';
import { ErrorMessage } from '../../components/ErrorMessage';

describe('ErrorMessage Component', () => {
  it('should render error message with default props', () => {
    render(<ErrorMessage message="Test error message" />);
    
    expect(screen.getByText('Test error message')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('should render with custom className', () => {
    render(
      <ErrorMessage 
        message="Custom error" 
        className="custom-error-class" 
      />
    );
    
    const errorElement = screen.getByRole('alert');
    expect(errorElement).toHaveClass('custom-error-class');
  });

  it('should render with different message types', () => {
    const { rerender } = render(
      <ErrorMessage message="Info message" type="info" />
    );
    
    expect(screen.getByText('Info message')).toBeInTheDocument();
    
    rerender(<ErrorMessage message="Warning message" type="warning" />);
    expect(screen.getByText('Warning message')).toBeInTheDocument();
    
    rerender(<ErrorMessage message="Success message" type="success" />);
    expect(screen.getByText('Success message')).toBeInTheDocument();
  });

  it('should handle empty message', () => {
    render(<ErrorMessage message="" />);
    
    const errorElement = screen.getByRole('alert');
    expect(errorElement).toBeInTheDocument();
    expect(errorElement).toBeInTheDocument();
  });

  it('should handle long messages', () => {
    const longMessage = 'This is a very long error message that should be displayed properly without breaking the layout or causing any issues with the component rendering';
    
    render(<ErrorMessage message={longMessage} />);
    
    expect(screen.getByText(longMessage)).toBeInTheDocument();
  });

  it('should handle special characters in message', () => {
    const specialMessage = 'Error with special chars: !@#$%^&*()_+-=[]{}|;:,.<>?';
    
    render(<ErrorMessage message={specialMessage} />);
    
    expect(screen.getByText(specialMessage)).toBeInTheDocument();
  });

  it('should handle HTML entities in message', () => {
    const htmlMessage = 'Error with HTML: &lt;script&gt;alert("test")&lt;/script&gt;';
    
    render(<ErrorMessage message={htmlMessage} />);
    
    expect(screen.getByText(htmlMessage)).toBeInTheDocument();
  });

  it('should be accessible with proper ARIA attributes', () => {
    render(<ErrorMessage message="Accessible error message" />);
    
    const errorElement = screen.getByRole('alert');
    expect(errorElement).toBeInTheDocument();
    expect(errorElement).toHaveAttribute('aria-live', 'polite');
  });

  it('should handle multiple error messages', () => {
    const { rerender } = render(<ErrorMessage message="First error" />);
    expect(screen.getByText('First error')).toBeInTheDocument();
    
    rerender(<ErrorMessage message="Second error" />);
    expect(screen.getByText('Second error')).toBeInTheDocument();
    expect(screen.queryByText('First error')).not.toBeInTheDocument();
  });
}); 