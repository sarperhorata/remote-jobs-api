import React from 'react';
import { render, renderHook, act, waitFor } from '@testing-library/react';
import { AuthProvider, useAuth } from '../../contexts/AuthContext';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock fetch
global.fetch = jest.fn();

const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('AuthContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
    // Clear any environment variables that might affect tests
    delete process.env.NODE_ENV;
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <AuthProvider>{children}</AuthProvider>
  );

  it('should provide mock user when in development mode', () => {
    process.env.NODE_ENV = 'development';
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.user).not.toBeNull();
    expect(result.current.isAuthenticated).toBe(true);
    expect(result.current.user?.name).toBe('Sarper Horata');
  });

  it('should provide null user when in test mode', () => {
    process.env.NODE_ENV = 'test';
    const { result } = renderHook(() => useAuth(), { wrapper });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(result.current.isLoading).toBe(false);
  });

  it('should handle successful login', async () => {
    process.env.NODE_ENV = 'test';
    const mockUser = {
      id: '1',
      name: 'Test User',
      email: 'test@example.com'
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user: mockUser, token: 'mock-token' })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.login('test@example.com', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'mock-token');
  });

  it('should handle login failure', async () => {
    process.env.NODE_ENV = 'test';
    mockFetch.mockResolvedValueOnce({
      ok: false,
      json: async () => ({ message: 'Invalid credentials' })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await expect(
      act(async () => {
        await result.current.login('test@example.com', 'wrong-password');
      })
    ).rejects.toThrow('Invalid credentials');

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
  });

  it('should handle successful signup', async () => {
    process.env.NODE_ENV = 'test';
    const mockUser = {
      id: '1',
      name: 'New User',
      email: 'new@example.com'
    };

    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({ user: mockUser, token: 'new-token' })
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.signup('New User', 'new@example.com', 'password');
    });

    expect(result.current.user).toEqual(mockUser);
    expect(result.current.isAuthenticated).toBe(true);
    expect(localStorageMock.setItem).toHaveBeenCalledWith('token', 'new-token');
  });

  it('should handle logout', () => {
    process.env.NODE_ENV = 'test';
    const { result } = renderHook(() => useAuth(), { wrapper });

    act(() => {
      result.current.logout();
    });

    expect(result.current.user).toBeNull();
    expect(result.current.isAuthenticated).toBe(false);
    expect(localStorageMock.removeItem).toHaveBeenCalledWith('token');
  });

  it('should restore user from localStorage on mount', async () => {
    process.env.NODE_ENV = 'test';
    const mockUser = {
      id: '1',
      name: 'Stored User',
      email: 'stored@example.com'
    };

    localStorageMock.getItem.mockReturnValue('stored-token');
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => mockUser
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await waitFor(() => {
      expect(result.current.user).toEqual(mockUser);
      expect(result.current.isAuthenticated).toBe(true);
    });
  });

  it('should handle refresh user', async () => {
    process.env.NODE_ENV = 'test';
    const updatedUser = {
      id: '1',
      name: 'Updated User',
      email: 'updated@example.com'
    };

    localStorageMock.getItem.mockReturnValue('token');
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => updatedUser
    } as Response);

    const { result } = renderHook(() => useAuth(), { wrapper });

    await act(async () => {
      await result.current.refreshUser();
    });

    expect(result.current.user).toEqual(updatedUser);
  });

  it('should handle network errors gracefully', async () => {
    process.env.NODE_ENV = 'test';
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    const { result } = renderHook(() => useAuth(), { wrapper });

    await expect(
      act(async () => {
        await result.current.login('test@example.com', 'password');
      })
    ).rejects.toThrow('Network error');
  });
}); 