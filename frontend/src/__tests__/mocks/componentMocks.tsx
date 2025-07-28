import React from 'react';

// Mock components for testing
export const MockRouter = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-router">{children}</div>
);

export const MockLink = ({ to, children, ...props }: { to: string; children: React.ReactNode; [key: string]: any }) => (
  <a href={to} {...props} data-testid="mock-link">
    {children}
  </a>
);

export const MockNavigate = ({ to }: { to: string }) => (
  <div data-testid="mock-navigate" data-to={to} />
);

export const MockOutlet = () => (
  <div data-testid="mock-outlet" />
);

// Mock hooks
export const mockUseNavigate = jest.fn();
export const mockUseLocation = jest.fn(() => ({
  pathname: '/',
  search: '',
  hash: '',
  state: null
}));

export const mockUseParams = jest.fn(() => ({}));

// Mock context providers
export const MockAuthProvider = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-auth-provider">{children}</div>
);

export const MockThemeProvider = ({ children }: { children: React.ReactNode }) => (
  <div data-testid="mock-theme-provider">{children}</div>
);

// Mock services
export const mockJobService = {
  getJobs: jest.fn(),
  getJobById: jest.fn(),
  searchJobs: jest.fn(),
  getSimilarJobs: jest.fn(),
  applyToJob: jest.fn(),
  saveJob: jest.fn(),
  unsaveJob: jest.fn()
};

export const mockAuthService = {
  login: jest.fn(),
  register: jest.fn(),
  logout: jest.fn(),
  getCurrentUser: jest.fn(),
  isAuthenticated: jest.fn()
};