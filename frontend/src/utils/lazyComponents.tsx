import React from 'react';

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
        <h3 className="text-lg font-semibold text-gray-900 mb-2">Error</h3>
        <p className="text-gray-600 mb-4">{message}</p>
        <div className="flex space-x-2 justify-center">
          <button
            onClick={resetErrorBoundary}
            className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 transition-colors"
          >
            Try Again
          </button>
          {onRetry && (
            <button
              onClick={onRetry}
              className="px-4 py-2 bg-gray-300 text-gray-700 rounded hover:bg-gray-400 transition-colors"
            >
              Retry
            </button>
          )}
        </div>
      </div>
    </div>
  );
}; 