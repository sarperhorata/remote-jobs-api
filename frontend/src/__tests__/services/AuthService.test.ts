import { authService } from '../../services/authService';

// Mock fetch globally
global.fetch = jest.fn();

describe('AuthService', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
    localStorage.clear();
  });

  describe('login', () => {
    it('should login successfully with valid credentials', async () => {
      const mockResponse = {
        token: 'test-token',
        user: { id: '1', email: 'test@example.com', name: 'Test User' }
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.login('test@example.com', 'password');
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@example.com', password: 'password', remember_me: false })
      });
      
      expect(result).toEqual(mockResponse);
      expect(localStorage.getItem('auth_token')).toBe('test-token');
    });

    it('should handle login failure with invalid credentials', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      });

      await expect(authService.login('test@example.com', 'wrong-password'))
        .rejects.toThrow('HTTP 401: Unauthorized');
      
      expect(localStorage.getItem('auth_token')).toBeNull();
    });

    it('should handle network errors during login', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(authService.login('test@example.com', 'password'))
        .rejects.toThrow('Network error');
    });

    it('should validate email format', async () => {
      await expect(authService.login('invalid-email', 'password'))
        .rejects.toThrow('Invalid email format');
    });

    it('should validate password length', async () => {
      await expect(authService.login('test@example.com', '123'))
        .rejects.toThrow('Password must be at least 6 characters');
    });
  });

  describe('register', () => {
    it('should register successfully with valid data', async () => {
      const userData = {
        email: 'new@example.com',
        password: 'password123',
        name: 'New User'
      };

      const mockResponse = {
        token: 'new-token',
        user: { id: '2', ...userData }
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await authService.register(userData);
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(userData)
      });
      
      expect(result).toEqual(mockResponse);
    });

    it('should handle registration with existing email', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 409,
        statusText: 'Conflict'
      });

      await expect(authService.register({
        email: 'existing@example.com',
        password: 'password',
        name: 'User'
      })).rejects.toThrow('HTTP 409: Conflict');
    });

    it('should validate registration data', async () => {
      const invalidData = [
        { email: '', password: 'password', name: 'User' },
        { email: 'test@example.com', password: '', name: 'User' },
        { email: 'test@example.com', password: 'password', name: '' },
        { email: 'invalid-email', password: 'password', name: 'User' }
      ];

      for (const data of invalidData) {
        await expect(authService.register(data))
          .rejects.toThrow();
      }
    });
  });

  describe('logout', () => {
    it('should logout successfully', async () => {
      localStorage.setItem('auth_token', 'test-token');

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logout successful' })
      });

      await authService.logout();
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/logout', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer test-token'
        }
      });
      
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('user_data')).toBeNull();
    });

    it('should clear local data even if server logout fails', async () => {
      localStorage.setItem('auth_token', 'test-token');
      localStorage.setItem('user_data', JSON.stringify({ id: '1' }));

      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Server error'));

      await authService.logout();
      
      expect(localStorage.getItem('auth_token')).toBeNull();
      expect(localStorage.getItem('user_data')).toBeNull();
    });
  });

  describe('getCurrentUser', () => {
    it('should get current user with valid token', async () => {
      const mockUser = { id: '1', email: 'test@example.com', name: 'Test User' };
      localStorage.setItem('auth_token', 'valid-token');

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockUser
      });

      const result = await authService.getCurrentUser();
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/me', {
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid-token'
        }
      });
      
      expect(result).toEqual(mockUser);
    });

    it('should return null when no token exists', async () => {
      const result = await authService.getCurrentUser();
      expect(result).toBeNull();
      expect(fetch).not.toHaveBeenCalled();
    });

    it('should handle invalid token', async () => {
      localStorage.setItem('auth_token', 'invalid-token');

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      });

      const result = await authService.getCurrentUser();
      expect(result).toBeNull();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('refreshToken', () => {
    it('should refresh token successfully', async () => {
      const oldToken = 'old-token';
      const newToken = 'new-token';
      localStorage.setItem('auth_token', oldToken);

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ token: newToken })
      });

      const result = await authService.refreshToken();
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/refresh', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${oldToken}`
        }
      });
      
      expect(result).toEqual({ token: newToken });
      expect(localStorage.getItem('auth_token')).toBe(newToken);
    });

    it('should handle refresh failure', async () => {
      localStorage.setItem('auth_token', 'expired-token');

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Token expired'
      });

      const result = await authService.refreshToken();
      expect(result).toBeNull();
      expect(localStorage.getItem('auth_token')).toBeNull();
    });
  });

  describe('resetPassword', () => {
    it('should send reset password email successfully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Reset email sent' })
      });

      const result = await authService.resetPassword('test@example.com');
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: 'test@example.com' })
      });
      
      expect(result).toEqual({ message: 'Reset email sent' });
    });

    it('should handle invalid email for reset', async () => {
      await expect(authService.resetPassword('invalid-email'))
        .rejects.toThrow('Invalid email format');
    });
  });

  describe('changePassword', () => {
    it('should change password successfully', async () => {
      localStorage.setItem('auth_token', 'valid-token');

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Password changed' })
      });

      const result = await authService.changePassword('oldPassword', 'newPassword123');
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/change-password', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid-token'
        },
        body: JSON.stringify({
          old_password: 'oldPassword',
          new_password: 'newPassword123'
        })
      });
      
      expect(result).toEqual({ message: 'Password changed' });
    });

    it('should require authentication for password change', async () => {
      await expect(authService.changePassword('old', 'new'))
        .rejects.toThrow('Authentication required');
    });
  });

  describe('updateProfile', () => {
    it('should update user profile successfully', async () => {
      localStorage.setItem('auth_token', 'valid-token');
      const profileData = { name: 'Updated Name', phone: '123-456-7890' };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ id: '1', ...profileData })
      });

      const result = await authService.updateProfile(profileData);
      
      expect(fetch).toHaveBeenCalledWith('http://localhost:8000/api/v1/auth/profile', {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': 'Bearer valid-token'
        },
        body: JSON.stringify(profileData)
      });
      
      expect(result).toEqual({ id: '1', ...profileData });
    });
  });

  describe('utility methods', () => {
    it('should check if user is authenticated', () => {
      expect(authService.isAuthenticated()).toBe(false);
      
      localStorage.setItem('auth_token', 'test-token');
      expect(authService.isAuthenticated()).toBe(true);
    });

    it('should get stored token', () => {
      expect(authService.getToken()).toBeNull();
      
      localStorage.setItem('auth_token', 'test-token');
      expect(authService.getToken()).toBe('test-token');
    });

    it('should validate email format', () => {
      expect(authService.validateEmail('test@example.com')).toBe(true);
      expect(authService.validateEmail('invalid-email')).toBe(false);
      expect(authService.validateEmail('')).toBe(false);
    });

    it('should validate password strength', () => {
      expect(authService.validatePassword('123')).toBe(false);
      expect(authService.validatePassword('password123')).toBe(true);
      expect(authService.validatePassword('')).toBe(false);
    });
  });

  describe('error handling', () => {
    it('should handle malformed JSON responses', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });

      await expect(authService.login('test@example.com', 'password'))
        .rejects.toThrow('Invalid JSON');
    });

    it('should handle network timeouts', async () => {
      (fetch as jest.Mock).mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      await expect(authService.login('test@example.com', 'password'))
        .rejects.toThrow('Request timeout');
    });
  });
}); 