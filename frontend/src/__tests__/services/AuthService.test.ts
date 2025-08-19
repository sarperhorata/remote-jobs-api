import { authService } from '../../services/authService';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

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

describe('authService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
  });

  describe('validateEmail', () => {
    test('validates correct email format', () => {
      expect(authService.validateEmail('test@example.com')).toBe(true);
      expect(authService.validateEmail('user.name@domain.co.uk')).toBe(true);
    });

    test('rejects invalid email format', () => {
      expect(authService.validateEmail('invalid-email')).toBe(false);
      expect(authService.validateEmail('test@')).toBe(false);
      expect(authService.validateEmail('@example.com')).toBe(false);
    });
  });

  describe('validatePassword', () => {
    test('validates correct password length', () => {
      expect(authService.validatePassword('password123')).toBe(true);
      expect(authService.validatePassword('123456')).toBe(true);
    });

    test('rejects short password', () => {
      expect(authService.validatePassword('12345')).toBe(false);
      expect(authService.validatePassword('')).toBe(false);
    });
  });

  describe('isAuthenticated', () => {
    test('returns true when token exists', () => {
      localStorageMock.getItem.mockReturnValue('mock-token');
      expect(authService.isAuthenticated()).toBe(true);
    });

    test('returns false when no token', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(authService.isAuthenticated()).toBe(false);
    });
  });

  describe('getToken', () => {
    test('returns stored token', () => {
      localStorageMock.getItem.mockReturnValue('mock-token');
      expect(authService.getToken()).toBe('mock-token');
    });

    test('returns null when no token', () => {
      localStorageMock.getItem.mockReturnValue(null);
      expect(authService.getToken()).toBe(null);
    });
  });

  describe('login', () => {
    test('successfully logs in user', async () => {
      const mockResponse = {
        token: 'mock-token',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User'
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.login('test@example.com', 'password123');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password123',
            remember_me: false
          })
        })
      );

      expect(result).toEqual(mockResponse);
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'mock-token');
      expect(localStorage.setItem).toHaveBeenCalledWith('user_data', JSON.stringify(mockResponse.user));
    });

    test('handles invalid email format', async () => {
      await expect(authService.login('invalid-email', 'password123')).rejects.toThrow('Invalid email format');
    });

    test('handles short password', async () => {
      await expect(authService.login('test@example.com', '123')).rejects.toThrow('Password must be at least 6 characters');
    });

    test('handles login error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      });

      await expect(authService.login('test@example.com', 'wrongpassword')).rejects.toThrow('HTTP 401: Unauthorized');
    });

    test('handles network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(authService.login('test@example.com', 'password123')).rejects.toThrow('Network error');
    });
  });

  describe('register', () => {
    test('successfully registers user', async () => {
      const mockResponse = {
        message: 'User registered successfully',
        user: {
          id: '1',
          email: 'test@example.com',
          name: 'Test User'
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };

      const result = await authService.register(userData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(userData)
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles registration error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 409
      });

      const userData = {
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      };

      await expect(authService.register(userData)).rejects.toThrow('HTTP 409: Conflict');
    });
  });

  describe('logout', () => {
    test('successfully logs out user', async () => {
      localStorageMock.getItem.mockReturnValue('mock-token');
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logged out successfully' })
      });

      await authService.logout();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/logout'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json'
          })
        })
      );

      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('user_data');
    });

    test('handles logout error gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      // Should still clear local storage even if API call fails
      await authService.logout();

      expect(localStorage.removeItem).toHaveBeenCalledWith('auth_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('user_data');
    });
  });

  describe('getCurrentUser', () => {
    test('successfully gets current user', async () => {
      localStorageMock.getItem.mockReturnValue('mock-token');
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser
      });

      const result = await authService.getCurrentUser();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/me'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockUser);
    });

    test('returns null when no token', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = await authService.getCurrentUser();

      expect(result).toBeNull();
    });

    test('handles unauthorized error', async () => {
      localStorageMock.getItem.mockReturnValue('mock-token');
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      });

      const result = await authService.getCurrentUser();
      expect(result).toBeNull();
    });
  });

  describe('resetPassword', () => {
    test('successfully sends reset password email', async () => {
      const mockResponse = {
        message: 'Password reset email sent'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.resetPassword('test@example.com');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/reset-password'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({ email: 'test@example.com' })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles invalid email format', async () => {
      await expect(authService.resetPassword('invalid-email')).rejects.toThrow('Invalid email format');
    });

    test('handles reset password error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404
      });

      await expect(authService.resetPassword('nonexistent@example.com')).rejects.toThrow('Failed to send reset password email');
    });
  });

  describe('refreshToken', () => {
    test('successfully refreshes token', async () => {
      localStorageMock.getItem.mockReturnValue('mock-token');
      const mockResponse = {
        token: 'new-token'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.refreshToken();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/refresh'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockResponse);
      expect(localStorage.setItem).toHaveBeenCalledWith('auth_token', 'new-token');
    });

    test('returns null when no token', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      const result = await authService.refreshToken();

      expect(result).toBeNull();
    });

    test('handles refresh token error', async () => {
      localStorageMock.getItem.mockReturnValue('mock-token');
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401
      });

      const result = await authService.refreshToken();
      expect(result).toBeNull();
    });
  });
});