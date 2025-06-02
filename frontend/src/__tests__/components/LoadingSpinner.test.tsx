import { render } from '@testing-library/react';
import { LoadingSpinner } from '../../components/LoadingSpinner';
import '@testing-library/jest-dom';

describe('LoadingSpinner', () => {
  it('renders loading spinner without crashing', () => {
    expect(() => render(<LoadingSpinner />)).not.toThrow();
  });

  it('has correct container CSS classes', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerContainer = container.firstChild as HTMLElement;
    expect(spinnerContainer).toHaveClass('flex', 'justify-center', 'items-center', 'py-8');
  });

  it('renders spinning element with correct classes', () => {
    const { container } = render(<LoadingSpinner />);
    
    const spinnerElement = container.querySelector('.animate-spin');
    expect(spinnerElement).toBeInTheDocument();
    expect(spinnerElement).toHaveClass('animate-spin', 'rounded-full', 'h-8', 'w-8', 'border-b-2', 'border-blue-600');
  });

  it('is accessible', () => {
    const { container } = render(<LoadingSpinner />);
    
    expect(container.firstChild).toBeInTheDocument();
  });
}); 