// Mock Sentry for testing
const mockSentry = {
  init: jest.fn(),
  ErrorBoundary: ({ children }) => children,
  captureException: jest.fn(),
  captureMessage: jest.fn(),
  setUser: jest.fn(),
  SeverityLevel: {
    info: 'info',
    warning: 'warning',
    error: 'error',
    fatal: 'fatal',
  },
};

export default mockSentry;
export const initSentry = jest.fn();
export const SentryErrorBoundary = mockSentry.ErrorBoundary;
export const captureException = jest.fn();
export const captureMessage = jest.fn();
export const setUserContext = jest.fn();
export const clearUserContext = jest.fn();