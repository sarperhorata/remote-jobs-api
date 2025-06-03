import { API_URL } from '../config';

// Override for test compatibility
const API_BASE_URL = process.env.NODE_ENV === 'test' ? 'http://localhost:8001/api' : API_URL;

interface UserData {
  email: string;
  password: string;
  name: string;
}

interface ProfileData {
  name?: string;
  email?: string;
  location?: string;
  bio?: string;
}

export const authService = {
  // Email validation
  validateEmail(email: string): boolean {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email);
  },

  // Password validation
  validatePassword(password: string): boolean {
    return password.length >= 6;
  },

  // Check if user is authenticated
  isAuthenticated(): boolean {
    return !!localStorage.getItem('auth_token');
  },

  // Get stored token
  getToken(): string | null {
    return localStorage.getItem('auth_token');
  },

  async login(email: string, password: string, rememberMe: boolean = false) {
    // Client-side validation
    if (!this.validateEmail(email)) {
      throw new Error('Invalid email format');
    }
    if (!this.validatePassword(password)) {
      throw new Error('Password must be at least 6 characters');
    }

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    });
    
    if (!response.ok) {
      if (response.status === 401) {
        throw new Error('HTTP 401: Unauthorized');
      }
      throw new Error('Login failed');
    }
    
    const data = await response.json();
    
    // Store token and user data
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
    }
    if (data.user) {
      localStorage.setItem('user_data', JSON.stringify(data.user));
    }
    
    return data;
  },
  
  async register(userData: UserData) {
    const response = await fetch(`${API_BASE_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(userData),
    });
    
    if (!response.ok) {
      if (response.status === 409) {
        throw new Error('HTTP 409: Conflict');
      }
      throw new Error('Registration failed');
    }
    
    const data = await response.json();
    
    // Store token and user data
    if (data.token) {
      localStorage.setItem('auth_token', data.token);
    }
    if (data.user) {
      localStorage.setItem('user_data', JSON.stringify(data.user));
    }
    
    return data;
  },

  async logout() {
    const token = this.getToken();
    
    try {
      if (token) {
        await fetch(`${API_BASE_URL}/auth/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
        });
      }
    } catch (error) {
      console.warn('Logout request failed:', error);
    } finally {
      // Always clear local data
      localStorage.removeItem('auth_token');
      localStorage.removeItem('user_data');
    }
  },

  async getCurrentUser() {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/me`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token is invalid, clear it
          this.logout();
          return null;
        }
        throw new Error('Failed to get current user');
      }

      return response.json();
    } catch (error) {
      console.error('Get current user failed:', error);
      return null;
    }
  },

  async refreshToken() {
    const token = this.getToken();
    if (!token) {
      return null;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/auth/refresh`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        // Refresh failed, clear tokens
        this.logout();
        return null;
      }

      const data = await response.json();
      
      if (data.token) {
        localStorage.setItem('auth_token', data.token);
      }
      
      return data;
    } catch (error) {
      console.error('Token refresh failed:', error);
      this.logout();
      return null;
    }
  },

  async resetPassword(email: string) {
    if (!this.validateEmail(email)) {
      throw new Error('Invalid email format');
    }

    const response = await fetch(`${API_BASE_URL}/auth/reset-password`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email }),
    });

    if (!response.ok) {
      throw new Error('Failed to send reset password email');
    }

    return response.json();
  },

  async changePassword(oldPassword: string, newPassword: string) {
    const token = this.getToken();
    if (!token) {
      throw new Error('Authentication required');
    }

    if (!this.validatePassword(newPassword)) {
      throw new Error('Password must be at least 6 characters');
    }

    const response = await fetch(`${API_BASE_URL}/auth/change-password`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ old_password: oldPassword, new_password: newPassword }),
    });

    if (!response.ok) {
      throw new Error('Failed to change password');
    }

    return response.json();
  },

  async updateProfile(profileData: ProfileData) {
    const token = this.getToken();
    if (!token) {
      throw new Error('Authentication required');
    }

    const response = await fetch(`${API_BASE_URL}/auth/profile`, {
      method: 'PUT',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(profileData),
    });

    if (!response.ok) {
      throw new Error('Failed to update profile');
    }

    const data = await response.json();
    
    // Update stored user data
    if (data.user) {
      localStorage.setItem('user_data', JSON.stringify(data.user));
    }
    
    return data;
  },
  
  async getGoogleAuthUrl() {
    const response = await fetch(`${API_BASE_URL}/auth/google/auth-url`);
    if (!response.ok) {
      throw new Error('Failed to get Google auth URL');
    }
    const data = await response.json();
    return data.auth_url;
  },
  
  async handleGoogleCallback(token: string) {
    // Store token in localStorage
    localStorage.setItem('auth_token', token);
    
    // Get user info
    const response = await fetch(`${API_BASE_URL}/auth/me`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    
    if (!response.ok) {
      throw new Error('Failed to get user info');
    }
    
    return response.json();
  }
}; 