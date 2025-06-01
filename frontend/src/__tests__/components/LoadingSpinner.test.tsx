import { render, screen } from '@testing-library/react';
import LoadingSpinner from '../../components/LoadingSpinner';

describe('LoadingSpinner', () => {
  it('renders loading spinner', () => {
    render(<LoadingSpinner />);
    
    const spinner = screen.getByText('Loading...');
    expect(spinner).toBeInTheDocument();
  });

  it('has correct CSS classes', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerElement = container.firstChild;
    expect(spinnerElement).toHaveClass('flex', 'justify-center', 'items-center', 'py-8');
  });

  it('displays loading text', () => {
    render(<LoadingSpinner />);
    
    expect(screen.getByText('Loading...')).toBeInTheDocument();
  });

  it('renders without crashing', () => {
    expect(() => render(<LoadingSpinner />)).not.toThrow();
  });
}); 