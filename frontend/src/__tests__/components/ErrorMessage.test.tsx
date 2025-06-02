import { render, screen } from '@testing-library/react';
import { ErrorMessage } from '../../components/ErrorMessage';

describe('ErrorMessage', () => {
  it('renders error message with provided text', () => {
    const errorText = 'Something went wrong!';
    render(<ErrorMessage message={errorText} />);
    
    expect(screen.getByText(errorText)).toBeInTheDocument();
  });

  it('has correct CSS classes for error container', () => {
    const { container } = render(<ErrorMessage message="Error" />);
    
    const errorElement = container.firstChild;
    expect(errorElement).toHaveClass('bg-red-50', 'border', 'border-red-200', 'rounded-md', 'p-4');
  });

  it('renders error message text', () => {
    const message = "Test error message";
    render(<ErrorMessage message={message} />);
    
    expect(screen.getByText(message)).toBeInTheDocument();
    expect(screen.getByText('Error')).toBeInTheDocument(); // Header text
  });

  it('renders without crashing', () => {
    expect(() => render(<ErrorMessage message="Test error" />)).not.toThrow();
  });

  it('displays error icon', () => {
    const { container } = render(<ErrorMessage message="Test" />);
    
    const svgIcon = container.querySelector('svg');
    expect(svgIcon).toBeInTheDocument();
    expect(svgIcon).toHaveClass('h-5', 'w-5', 'text-red-400');
  });

  it('handles long error messages', () => {
    const longMessage = 'This is a very long error message that should still be displayed correctly even if it spans multiple lines and contains a lot of text.';
    render(<ErrorMessage message={longMessage} />);
    
    expect(screen.getByText(longMessage)).toBeInTheDocument();
  });

  it('renders with special characters', () => {
    const specialMessage = 'Error: 404 - Resource not found! @#$%^&*()';
    render(<ErrorMessage message={specialMessage} />);
    
    expect(screen.getByText(specialMessage)).toBeInTheDocument();
  });

  it('has proper semantic structure', () => {
    const { container } = render(<ErrorMessage message="Test error" />);
    
    const errorTitle = screen.getByText('Error');
    expect(errorTitle.tagName).toBe('H3');
    expect(errorTitle).toHaveClass('text-sm', 'font-medium', 'text-red-800');
  });
}); 