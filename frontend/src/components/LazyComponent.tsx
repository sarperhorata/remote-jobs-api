import React, { Suspense, ComponentType } from 'react';
import { Loader2 } from 'lucide-react';

// Loading component
const LoadingSpinner: React.FC<{ size?: 'sm' | 'md' | 'lg' }> = ({ size = 'md' }) => {
  const sizeClasses = {
    sm: 'h-4 w-4',
    md: 'h-8 w-8',
    lg: 'h-12 w-12'
  };

  return (
    <div className="flex items-center justify-center p-8">
      <Loader2 className={`animate-spin text-blue-600 ${sizeClasses[size]}`} />
      <span className="ml-2 text-gray-600">Loading...</span>
    </div>
  );
};

// Page loading skeleton
const PageLoadingSkeleton: React.FC = () => {
  return (
    <div className="animate-pulse">
      <div className="space-y-4 p-6">
        <div className="h-8 bg-gray-200 rounded w-1/4"></div>
        <div className="space-y-2">
          <div className="h-4 bg-gray-200 rounded"></div>
          <div className="h-4 bg-gray-200 rounded w-5/6"></div>
          <div className="h-4 bg-gray-200 rounded w-4/6"></div>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[...Array(6)].map((_, i) => (
            <div key={i} className="border border-gray-200 rounded-lg p-4">
              <div className="h-4 bg-gray-200 rounded mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-3/4 mb-2"></div>
              <div className="h-4 bg-gray-200 rounded w-1/2"></div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};

// Lazy wrapper with error boundary
interface LazyWrapperProps {
  fallback?: React.ComponentType;
  errorFallback?: React.ComponentType<{ error: Error; retry: () => void }>;
  children: React.ReactNode;
}

const LazyWrapper: React.FC<LazyWrapperProps> = ({ 
  fallback: Fallback = LoadingSpinner,
  errorFallback: ErrorFallback,
  children 
}) => {
  const [hasError, setHasError] = React.useState(false);
  const [error, setError] = React.useState<Error | null>(null);

  const retry = React.useCallback(() => {
    setHasError(false);
    setError(null);
  }, []);

  React.useEffect(() => {
    const handleError = (event: ErrorEvent) => {
      setHasError(true);
      setError(new Error(event.message));
    };

    window.addEventListener('error', handleError);
    return () => window.removeEventListener('error', handleError);
  }, []);

  if (hasError && ErrorFallback && error) {
    return <ErrorFallback error={error} retry={retry} />;
  }

  return (
    <Suspense fallback={<Fallback />}>
      {children}
    </Suspense>
  );
};

// Error fallback component
const DefaultErrorFallback: React.FC<{ error: Error; retry: () => void }> = ({ error, retry }) => {
  return (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
        <h3 className="text-lg font-semibold text-red-800 mb-2">
          Something went wrong
        </h3>
        <p className="text-red-600 mb-4">
          {error.message || 'An unexpected error occurred while loading this page.'}
        </p>
        <button
          onClick={retry}
          className="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
};

// Higher-order component for lazy loading
export const withLazyLoading = <P extends object>(
  Component: ComponentType<P>,
  fallback?: React.ComponentType,
  errorFallback?: React.ComponentType<{ error: Error; retry: () => void }>
) => {
  const LazyComponent = React.lazy(() => Promise.resolve({ default: Component }));
  
  return React.forwardRef<any, P>((props, ref) => (
    <LazyWrapper 
      fallback={fallback} 
      errorFallback={errorFallback || DefaultErrorFallback}
    >
      <LazyComponent {...props} ref={ref} />
    </LazyWrapper>
  ));
};

// Route-based lazy loading
export const LazyRoute: React.FC<{
  component: React.LazyExoticComponent<ComponentType<any>>;
  fallback?: React.ComponentType;
  errorFallback?: React.ComponentType<{ error: Error; retry: () => void }>;
  [key: string]: any;
}> = ({ 
  component: Component, 
  fallback = PageLoadingSkeleton,
  errorFallback = DefaultErrorFallback,
  ...props 
}) => {
  return (
    <LazyWrapper fallback={fallback} errorFallback={errorFallback}>
      <Component {...props} />
    </LazyWrapper>
  );
};

export { LoadingSpinner, PageLoadingSkeleton, LazyWrapper, DefaultErrorFallback }; 