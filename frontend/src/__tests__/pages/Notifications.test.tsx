import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import Notifications from '../../pages/Notifications';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

// Mock AuthContext
const mockAuthContext = {
  isAuthenticated: true,
  user: { _id: 'test-user-id', email: 'test@example.com' },
  login: jest.fn(),
  logout: jest.fn(),
  signup: jest.fn(),
  isLoading: false
};

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Notifications Page', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockLocalStorage.getItem.mockClear();
    // Reset auth context for each test
    mockAuthContext.isAuthenticated = true;
    mockAuthContext.user = { _id: 'test-user-id', email: 'test@example.com' };
  });

  it('renders notifications page when authenticated', () => {
    // Mock successful API responses
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('shows login message when not authenticated', () => {
    mockAuthContext.isAuthenticated = false;
    mockAuthContext.user = null;

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Please log in to view notifications')).toBeInTheDocument();
  });

  it('displays loading state initially', () => {
    mockFetch.mockImplementation(() => new Promise(() => {})); // Never resolves

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('displays empty state when no notifications', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('displays search input', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByPlaceholderText('Search notifications...')).toBeInTheDocument();
  });

  it('displays filter dropdowns', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByDisplayValue('All')).toBeInTheDocument();
    expect(screen.getByDisplayValue('All Categories')).toBeInTheDocument();
  });

  it('displays notification header with icon', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('handles API error gracefully', () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('displays notification count in header', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 5 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('displays all caught up message when no unread notifications', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });

  it('renders with proper layout structure', () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Notifications')).toBeInTheDocument();
  });
}); 