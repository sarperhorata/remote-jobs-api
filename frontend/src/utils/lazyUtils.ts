import { lazy, ComponentType } from 'react';

/**
 * Enhanced lazy loading with retry functionality
 */
export const lazyWithRetry = <T extends ComponentType<any>>(
  componentImport: () => Promise<{ default: T }>,
  retries = 3
): ComponentType<any> => {
  return lazy(() => {
    return new Promise<{ default: T }>((resolve, reject) => {
      let attempts = 0;
      
      const attemptImport = async () => {
        try {
          const component = await componentImport();
          resolve(component);
        } catch (error) {
          attempts++;
          if (attempts >= retries) {
            reject(error);
          } else {
            // Exponential backoff
            setTimeout(attemptImport, Math.pow(2, attempts) * 1000);
          }
        }
      };
      
      attemptImport();
    });
  });
};

/**
 * Create a loading component with customizable content
 */
export const createLoadingComponent = (
  message = 'Loading...',
  className = 'flex items-center justify-center p-8'
) => {
  return () => (
    <div className={className}>
      <div className="flex items-center space-x-2">
        <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
        <span className="text-gray-600">{message}</span>
      </div>
    </div>
  );
};

/**
 * Error boundary for lazy loaded components
 */
export const createErrorFallback = (
  message = 'Something went wrong.',
  onRetry?: () => void
) => {
  return ({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => (
    <div className="flex flex-col items-center justify-center p-8 text-center">
      <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
        <svg
          className="w-12 h-12 text-red-500 mx-auto mb-4"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
          />
        </svg>
        <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Component</h3>
        <p className="text-red-600 mb-4">{message}</p>
        <button
          onClick={() => {
            onRetry?.();
            resetErrorBoundary();
          }}
          className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Try Again
        </button>
      </div>
    </div>
  );
};

/**
 * Preload a lazy component
 */
export const preloadComponent = (componentImport: () => Promise<any>) => {
  const promise = componentImport();
  return promise;
};

/**
 * Intersection Observer based lazy loader
 */
export class LazyLoader {
  private observer: IntersectionObserver;
  private elements: Map<Element, () => void> = new Map();

  constructor(options?: IntersectionObserverInit) {
    this.observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            const callback = this.elements.get(entry.target);
            if (callback) {
              callback();
              this.unobserve(entry.target);
            }
          }
        });
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
        ...options,
      }
    );
  }

  observe(element: Element, callback: () => void) {
    this.elements.set(element, callback);
    this.observer.observe(element);
  }

  unobserve(element: Element) {
    this.elements.delete(element);
    this.observer.unobserve(element);
  }

  disconnect() {
    this.observer.disconnect();
    this.elements.clear();
  }
}

/**
 * Hook for lazy loading content based on visibility
 */
export const useLazyLoad = (callback: () => void, options?: IntersectionObserverInit) => {
  return (element: Element | null) => {
    if (!element) return;

    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          callback();
          observer.disconnect();
        }
      },
      {
        rootMargin: '50px',
        threshold: 0.1,
        ...options,
      }
    );

    observer.observe(element);
    return () => observer.disconnect();
  };
}; 