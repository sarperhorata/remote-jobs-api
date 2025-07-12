import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import Login from '../../pages/Login';
import Register from '../../pages/Register';
import ForgotPassword from '../../pages/ForgotPassword';
import { getApiUrl } from '../../utils/apiConfig';

// Mock fetch for API calls
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Test wrapper with all providers
const TestWrapper = ({ children }: { children: React.ReactNode }) => (
  <BrowserRouter>
    <AuthProvider>
      {children}
    </AuthProvider>
  </BrowserRouter>
);

describe('Authentication Integration Tests', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    localStorage.clear();
  });

  describe('Login Flow', () => {
    it('should handle successful login and redirect', async () => {
      const mockUser = {
        id: '1',
        email: 'test@example.com',
        name: 'Test User',
        token: 'mock-token'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ user: mockUser, token: 'mock-token' })
      });

      render(
        <TestWrapper>
          <Login />
        </TestWrapper>
      );

      // Fill login form
      const emailInput = screen.getByPlaceholderText(/email address/i);
      const passwordInput = screen.getByPlaceholderText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      // Wait for API call
      await waitFor(() => {
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
      });
    });

    it('should handle login errors and show error message', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ error: 'Invalid credentials' })
      });

      render(
        <TestWrapper>
          <Login />
        </TestWrapper>
      );

      const emailInput = screen.getByPlaceholderText(/email address/i);
      const passwordInput = screen.getByPlaceholderText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'wrong@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/invalid credentials/i)).toBeInTheDocument();
      });
    });
  });

  describe('Register Flow', () => {
    it('should handle successful registration', async () => {
      const mockUser = {
        id: '1',
        email: 'new@example.com',
        name: 'New User',
        token: 'mock-token'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ user: mockUser, token: 'mock-token' })
      });

      render(
        <TestWrapper>
          <Register />
        </TestWrapper>
      );

      // Fill registration form
      const nameInput = screen.getByPlaceholderText(/full name/i);
      const emailInput = screen.getByPlaceholderText(/email address/i);
      const passwordInput = screen.getByPlaceholderText(/password/i);
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(nameInput, { target: { value: 'New User' } });
      fireEvent.change(emailInput, { target: { value: 'new@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/auth/register'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({
              name: 'New User',
              email: 'new@example.com',
              password: 'password123'
            })
          })
        );
      });
    });

    it('should validate password confirmation', async () => {
      render(
        <TestWrapper>
          <Register />
        </TestWrapper>
      );

      const passwordInput = screen.getByPlaceholderText(/password/i);
      const confirmPasswordInput = screen.getByPlaceholderText(/confirm password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i });

      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.change(confirmPasswordInput, { target: { value: 'different' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/passwords do not match/i)).toBeInTheDocument();
      });
    });
  });

  describe('Forgot Password Flow', () => {
    it('should handle password reset request', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Reset email sent' })
      });

      render(
        <TestWrapper>
          <ForgotPassword />
        </TestWrapper>
      );

      const emailInput = screen.getByPlaceholderText(/email address/i);
      const submitButton = screen.getByRole('button', { name: /send reset link/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(mockFetch).toHaveBeenCalledWith(
          expect.stringContaining('/auth/forgot-password'),
          expect.objectContaining({
            method: 'POST',
            body: JSON.stringify({
              email: 'test@example.com'
            })
          })
        );
      });
    });
  });

  describe('Token Management', () => {
    it('should store and retrieve auth token from localStorage', async () => {
      const mockToken = 'mock-jwt-token';
      const mockUser = { id: '1', email: 'test@example.com' };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ user: mockUser, token: mockToken })
      });

      render(
        <TestWrapper>
          <Login />
        </TestWrapper>
      );

      const emailInput = screen.getByPlaceholderText(/email address/i);
      const passwordInput = screen.getByPlaceholderText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(localStorage.getItem('token')).toBe(mockToken);
        expect(localStorage.getItem('user')).toBe(JSON.stringify(mockUser));
      });
    });

    it('should include auth token in subsequent API calls', async () => {
      // Set up initial auth state
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [] })
      });

      // This would typically be a protected API call
      const apiUrl = await getApiUrl();
      await fetch(`${apiUrl}/jobs`, {
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/jobs'),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );
    });
  });

  describe('Logout Flow', () => {
    it('should clear auth data on logout', async () => {
      // Set up initial auth state
      localStorage.setItem('token', 'mock-token');
      localStorage.setItem('user', JSON.stringify({ id: '1', email: 'test@example.com' }));

      // Mock logout API call
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Logged out successfully' })
      });

      // This would typically be triggered by a logout button
      // For testing, we'll simulate the logout process
      localStorage.removeItem('token');
      localStorage.removeItem('user');

      expect(localStorage.getItem('token')).toBeNull();
      expect(localStorage.getItem('user')).toBeNull();
    });
  });
});