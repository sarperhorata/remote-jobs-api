import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { 
  LoadingSpinner, 
  PageLoadingSkeleton, 
  LazyWrapper, 
  DefaultErrorFallback,
  withLazyLoading,
  LazyRoute 
} from '../../components/LazyComponent';

// Mock lucide-react
jest.mock('lucide-react', () => ({
  Loader2: ({ className, ...props }: any) => (
    <div data-testid="loader-icon" className={className} {...props}>
      Loader Icon
    </div>
  )
}));

describe('LazyComponent', () => {
  describe('LoadingSpinner', () => {
    it('renders with default size', () => {
      render(<LoadingSpinner />);
      
      expect(screen.getByTestId('loader-icon')).toBeInTheDocument();
      expect(screen.getByText('Loading...')).toBeInTheDocument();
      expect(screen.getByTestId('loader-icon')).toHaveClass('h-8', 'w-8');
    });

    it('renders with custom size', () => {
      const { rerender } = render(<LoadingSpinner size="sm" />);
      expect(screen.getByTestId('loader-icon')).toHaveClass('h-4', 'w-4');
      
      rerender(<LoadingSpinner size="lg" />);
      expect(screen.getByTestId('loader-icon')).toHaveClass('h-12', 'w-12');
    });

    it('has proper styling classes', () => {
      render(<LoadingSpinner />);
      
      const container = screen.getByText('Loading...').closest('.flex');
      expect(container).toHaveClass('flex', 'items-center', 'justify-center', 'p-8');
      
      expect(screen.getByTestId('loader-icon')).toHaveClass('animate-spin', 'text-blue-600');
    });
  });

  describe('PageLoadingSkeleton', () => {
    it('renders skeleton elements', () => {
      render(<PageLoadingSkeleton />);
      
      const container = document.querySelector('.animate-pulse');
      expect(container).toBeInTheDocument();
    });

    it('has proper skeleton styling', () => {
      render(<PageLoadingSkeleton />);
      
      const container = document.querySelector('.animate-pulse');
      expect(container).toHaveClass('animate-pulse');
      
      const skeletonElements = container?.querySelectorAll('.bg-gray-200');
      expect(skeletonElements?.length).toBeGreaterThan(0);
    });
  });

  describe('DefaultErrorFallback', () => {
    const mockError = new Error('Test error message');
    const mockRetry = jest.fn();

    beforeEach(() => {
      jest.clearAllMocks();
    });

    it('renders error message', () => {
      render(<DefaultErrorFallback error={mockError} retry={mockRetry} />);
      
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('Test error message')).toBeInTheDocument();
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    it('calls retry function when button is clicked', () => {
      render(<DefaultErrorFallback error={mockError} retry={mockRetry} />);
      
      const retryButton = screen.getByText('Try Again');
      fireEvent.click(retryButton);
      
      expect(mockRetry).toHaveBeenCalledTimes(1);
    });

    it('shows default error message when no message provided', () => {
      const errorWithoutMessage = new Error();
      render(<DefaultErrorFallback error={errorWithoutMessage} retry={mockRetry} />);
      
      expect(screen.getByText('An unexpected error occurred while loading this page.')).toBeInTheDocument();
    });

    it('has proper styling classes', () => {
      render(<DefaultErrorFallback error={mockError} retry={mockRetry} />);
      
      const container = screen.getByText('Something went wrong').closest('.bg-red-50');
      expect(container).toHaveClass('bg-red-50', 'border', 'border-red-200', 'rounded-lg', 'p-6');
    });
  });

  describe('LazyWrapper', () => {
    const TestComponent = () => <div>Test Component</div>;

    it('renders children when no error', () => {
      render(
        <LazyWrapper>
          <TestComponent />
        </LazyWrapper>
      );
      
      expect(screen.getByText('Test Component')).toBeInTheDocument();
    });

    it('handles basic functionality', () => {
      render(
        <LazyWrapper>
          <TestComponent />
        </LazyWrapper>
      );
      
      expect(screen.getByText('Test Component')).toBeInTheDocument();
    });
  });

  describe('withLazyLoading HOC', () => {
    const TestComponent = React.forwardRef<HTMLDivElement, { title: string }>(
      ({ title }, ref) => <div ref={ref}>{title}</div>
    );

    it('wraps component with lazy loading', () => {
      const LazyTestComponent = withLazyLoading(TestComponent);
      
      render(<LazyTestComponent title="Test Title" />);
      
      // Should show loading initially
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });

    it('handles basic functionality', () => {
      const LazyTestComponent = withLazyLoading(TestComponent);
      
      render(<LazyTestComponent title="Test Title" />);
      
      expect(screen.getByText('Loading...')).toBeInTheDocument();
    });
  });

  describe('LazyRoute', () => {
    const TestComponent = ({ title }: { title: string }) => <div>{title}</div>;
    const LazyTestComponent = React.lazy(() => Promise.resolve({ default: TestComponent }));

    it('renders lazy component', async () => {
      render(<LazyRoute component={LazyTestComponent} title="Route Test" />);
      
      await waitFor(() => {
        expect(screen.getByText('Route Test')).toBeInTheDocument();
      });
    });

    it('passes props to component', async () => {
      render(
        <LazyRoute 
          component={LazyTestComponent} 
          title="Route Props Test"
          extraProp="extra"
        />
      );
      
      await waitFor(() => {
        expect(screen.getByText('Route Props Test')).toBeInTheDocument();
      });
    });
  });

  describe('Error handling', () => {
    it('handles error gracefully', () => {
      const mockRetry = jest.fn();
      const mockError = new Error('Test error');
      
      render(<DefaultErrorFallback error={mockError} retry={mockRetry} />);
      
      expect(screen.getByText('Something went wrong')).toBeInTheDocument();
      expect(screen.getByText('Test error')).toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    it('has proper button role for retry', () => {
      const mockError = new Error('Test error');
      const mockRetry = jest.fn();
      
      render(<DefaultErrorFallback error={mockError} retry={mockRetry} />);
      
      const retryButton = screen.getByRole('button', { name: /try again/i });
      expect(retryButton).toBeInTheDocument();
    });

    it('has proper heading structure', () => {
      const mockError = new Error('Test error');
      const mockRetry = jest.fn();
      
      render(<DefaultErrorFallback error={mockError} retry={mockRetry} />);
      
      const heading = screen.getByRole('heading', { name: /something went wrong/i });
      expect(heading).toBeInTheDocument();
    });
  });
});