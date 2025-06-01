import { render, screen } from '@testing-library/react';
import ErrorMessage from '../../components/ErrorMessage';

describe('ErrorMessage', () => {
  it('renders error message with provided text', () => {
    const errorText = 'Something went wrong!';
    render(<ErrorMessage message={errorText} />);
    
    expect(screen.getByText(errorText)).toBeInTheDocument();
  });

  it('has correct CSS classes', () => {
    const { container } = render(<ErrorMessage message="Error" />);
    
    const errorElement = container.firstChild;
    expect(errorElement).toHaveClass('text-red-600', 'text-center', 'py-4');
  });

  it('renders empty message', () => {
    render(<ErrorMessage message="" />);
    
    const errorElement = screen.getByText('');
    expect(errorElement).toBeInTheDocument();
  });

  it('renders without crashing', () => {
    expect(() => render(<ErrorMessage message="Test error" />)).not.toThrow();
  });

  it('handles undefined message gracefully', () => {
    // @ts-ignore - testing edge case
    render(<ErrorMessage />);
    
    const { container } = render(<ErrorMessage message={undefined as any} />);
    expect(container.firstChild).toBeInTheDocument();
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
}); 