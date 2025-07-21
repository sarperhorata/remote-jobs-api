import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ForgotPassword from '../../pages/ForgotPassword';

// Mock fetch globally
global.fetch = jest.fn();

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock apiConfig
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('http://localhost:8000'),
}));

// Helper function to render with router
const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ForgotPassword', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });
  });

  it('should render forgot password form correctly', () => {
    renderWithRouter(<ForgotPassword />);
    
    expect(screen.getByText('Forgot your password?')).toBeInTheDocument();
    expect(screen.getByText('No worries! Enter your email and we\'ll send you a reset link.')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your email address')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send Reset Link' })).toBeInTheDocument();
  });

  it('should handle successful password reset request', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });
    
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/forgot-password'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test@example.com' }),
        })
      );
    });
    
    expect(screen.getByText('Check your email')).toBeInTheDocument();
  });

  it('should handle error during password reset', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ detail: 'User not found' }),
    });
    
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.change(emailInput, { target: { value: 'notfound@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('User not found')).toBeInTheDocument();
    });
  });

  it('should navigate back to login from success page', async () => {
    (global.fetch as jest.Mock).mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ success: true }),
    });
    
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Check your email')).toBeInTheDocument();
    });
    
    const backButton = screen.getByText('Back to Sign In');
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('should show loading state during submission', async () => {
    // Mock a delayed response
    (global.fetch as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({
        ok: true,
        json: () => Promise.resolve({ success: true }),
      }), 100))
    );
    
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    // Check if button is disabled during loading
    expect(submitButton).toBeDisabled();
    
    await waitFor(() => {
      expect(screen.getByText('Check your email')).toBeInTheDocument();
    });
  });

  it('should validate email format', async () => {
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    // Test with invalid email
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });
    
    // Test with valid email
    fireEvent.change(emailInput, { target: { value: 'valid@email.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(global.fetch).toHaveBeenCalledWith(
        expect.stringContaining('/auth/forgot-password'),
        expect.objectContaining({
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'valid@email.com' }),
        })
      );
    });
  });

  it('should handle empty email validation', async () => {
    renderWithRouter(<ForgotPassword />);
    
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter your email address')).toBeInTheDocument();
    });
  });
});
