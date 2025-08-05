import * as Sentry from '@sentry/react';
import { BrowserTracing } from '@sentry/tracing';

// Sentry konfigürasyonu - geçici olarak devre dışı
export const initSentry = () => {
  // Sentry geçici olarak devre dışı
  console.log('Sentry disabled for now');
};

// Error reporting helper
export const reportError = (error: Error, context?: Record<string, any>) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.captureException(error, {
      extra: context,
    });
  } else {
    console.error('Error (development):', error, context);
  }
};

// Custom performance metrics
export const trackPageLoad = (pageName: string, loadTime: number) => {
  if (process.env.NODE_ENV === 'production') {
    console.log(`Page load time for ${pageName}: ${loadTime}ms`);
  }
};

export const trackApiCall = (endpoint: string, responseTime: number, success: boolean) => {
  if (process.env.NODE_ENV === 'production') {
    console.log(`API call to ${endpoint}: ${responseTime}ms (${success ? 'success' : 'failed'})`);
  }
};

// Sentry Error Boundary component
export const SentryErrorBoundary = Sentry.ErrorBoundary;

// User context helper
export const setUserContext = (user: any) => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.setUser({
      id: user.id,
      email: user.email,
      username: user.username || user.email,
    });
  }
};

export const clearUserContext = () => {
  if (process.env.NODE_ENV === 'production') {
    Sentry.setUser(null);
  }
}; 