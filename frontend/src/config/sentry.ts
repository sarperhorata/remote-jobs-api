import * as Sentry from '@sentry/react';

// Sentry configuration optimized for free tier
export const initSentry = () => {
  // Only initialize in production
  if (process.env.NODE_ENV !== 'production') {
    return;
  }

  Sentry.init({
    dsn: process.env.REACT_APP_SENTRY_DSN || '',
    
    // Free tier optimizations
    tracesSampleRate: 0.1, // Only sample 10% of transactions to stay within limits
    maxBreadcrumbs: 10, // Limit breadcrumbs to reduce data usage
    
    // Error filtering to avoid spam
    beforeSend(event) {
      // Filter out common non-critical errors
      if (event.exception) {
        const exception = event.exception.values?.[0];
        if (exception) {
          // Ignore common browser errors
          if (exception.value?.includes('ResizeObserver loop limit exceeded')) {
            return null;
          }
          if (exception.value?.includes('Script error')) {
            return null;
          }
          if (exception.value?.includes('Network Error')) {
            return null;
          }
        }
      }
      
      // Filter out performance events for non-critical routes
      if (event.transaction) {
        const nonCriticalRoutes = [
          '/static/',
          '/_next/',
          '/favicon.ico',
          '/robots.txt',
        ];
        
        if (nonCriticalRoutes.some(route => event.transaction?.includes(route))) {
          return null;
        }
      }
      
      return event;
    },
    
    // Environment configuration
    environment: process.env.REACT_APP_ENVIRONMENT || 'development',
    release: process.env.REACT_APP_VERSION || '1.0.0',
    
    // Debug mode (only in development)
    debug: process.env.NODE_ENV !== 'production',
  });
};

// Custom error boundary component
export const SentryErrorBoundary = Sentry.ErrorBoundary;

// Performance monitoring utilities
export const captureException = (error: Error, context?: any) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.captureException(error, {
      tags: context?.tags || {},
      extra: context?.extra || {},
    });
  }
};

export const captureMessage = (message: string, level: Sentry.SeverityLevel = 'info') => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.captureMessage(message, level);
  }
};

// User context tracking (only for authenticated users)
export const setUserContext = (user: { id: string; email?: string; username?: string }) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.setUser({
      id: user.id,
      email: user.email,
      username: user.username,
    });
  }
};

// Clear user context on logout
export const clearUserContext = () => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.setUser(null);
  }
}; 