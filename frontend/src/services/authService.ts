import { API_URL } from '../config';

export const authService = {
  async login(email: string, password: string, rememberMe: boolean = false) {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, remember_me: rememberMe }),
    });
    
    if (!response.ok) {
      throw new Error('Login failed');
    }
    
    return response.json();
  },
  
  async register(email: string, password: string, name: string) {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ email, password, name }),
    });
    
    if (!response.ok) {
      throw new Error('Registration failed');
    }
    
    return response.json();
  },
  
  async getGoogleAuthUrl() {
    const response = await fetch(`${API_URL}/auth/google/auth-url`);
    if (!response.ok) {
      throw new Error('Failed to get Google auth URL');
    }
    const data = await response.json();
    return data.auth_url;
  },
  
  async handleGoogleCallback(token: string) {
    // Store token in localStorage
    localStorage.setItem('token', token);
    
    // Get user info
    const response = await fetch(`${API_URL}/auth/me`, {
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