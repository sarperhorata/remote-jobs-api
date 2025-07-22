import { 
  login, 
  register, 
  logout, 
  getCurrentUser, 
  resetPassword,
  verifyEmail,
  refreshToken
} from '../../services/authService';

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

  describe('login', () => {
    test('successfully logs in user', async () => {
      const mockResponse = {
        access_token: 'mock-access-token',
        refresh_token: 'mock-refresh-token',
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

      const result = await login('test@example.com', 'password123');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/login'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'password123'
          })
        })
      );

      expect(result).toEqual(mockResponse);
      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'mock-access-token');
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'mock-refresh-token');
    });

    test('handles login error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid credentials' })
      });

      await expect(login('test@example.com', 'wrongpassword')).rejects.toThrow('Invalid credentials');
    });

    test('handles network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(login('test@example.com', 'password123')).rejects.toThrow('Network error');
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

      const result = await register('Test User', 'test@example.com', 'password123');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/register'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            name: 'Test User',
            email: 'test@example.com',
            password: 'password123'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles registration error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Email already exists' })
      });

      await expect(register('Test User', 'test@example.com', 'password123')).rejects.toThrow('Email already exists');
    });
  });

  describe('logout', () => {
    test('successfully logs out user', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logged out successfully' })
      });

      await logout();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/logout'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer undefined'
          })
        })
      );

      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    });

    test('handles logout error gracefully', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      // Should still clear local storage even if API call fails
      await logout();

      expect(localStorage.removeItem).toHaveBeenCalledWith('access_token');
      expect(localStorage.removeItem).toHaveBeenCalledWith('refresh_token');
    });
  });

  describe('getCurrentUser', () => {
    test('successfully gets current user', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser
      });

      const result = await getCurrentUser();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/me'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer undefined'
          })
        })
      );

      expect(result).toEqual(mockUser);
    });

    test('handles unauthorized error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' })
      });

      await expect(getCurrentUser()).rejects.toThrow('Unauthorized');
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

      const result = await resetPassword('test@example.com');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/reset-password'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            email: 'test@example.com'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles reset password error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'User not found' })
      });

      await expect(resetPassword('nonexistent@example.com')).rejects.toThrow('User not found');
    });
  });

  describe('verifyEmail', () => {
    test('successfully verifies email', async () => {
      const mockResponse = {
        message: 'Email verified successfully'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await verifyEmail('test-token');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/verify-email'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            token: 'test-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles invalid token error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Invalid token' })
      });

      await expect(verifyEmail('invalid-token')).rejects.toThrow('Invalid token');
    });
  });

  describe('refreshToken', () => {
    test('successfully refreshes token', async () => {
      const mockResponse = {
        access_token: 'new-access-token',
        refresh_token: 'new-refresh-token'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await refreshToken('old-refresh-token');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/refresh'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify({
            refresh_token: 'old-refresh-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
      expect(localStorage.setItem).toHaveBeenCalledWith('access_token', 'new-access-token');
      expect(localStorage.setItem).toHaveBeenCalledWith('refresh_token', 'new-refresh-token');
    });

    test('handles refresh token error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid refresh token' })
      });

      await expect(refreshToken('invalid-refresh-token')).rejects.toThrow('Invalid refresh token');
    });
  });
});