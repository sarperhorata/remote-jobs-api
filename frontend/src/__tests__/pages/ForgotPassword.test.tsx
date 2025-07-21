import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import ForgotPassword from '../../pages/ForgotPassword';

// Mock the auth service
jest.mock('../../services/authService', () => ({
  authService: {
    resetPassword: jest.fn(),
  },
}));

// Import the mocked service
import { authService } from '../../services/authService';

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
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
    (authService.resetPassword as jest.Mock).mockResolvedValue({ success: true });
  });

  it('should render forgot password form correctly', () => {
    renderWithRouter(<ForgotPassword />);
    
    expect(screen.getByText('Forgot your password?')).toBeInTheDocument();
    expect(screen.getByText('No worries! Enter your email and we\'ll send you a reset link.')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your email address')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Send Reset Link' })).toBeInTheDocument();
  });

  it('should handle successful password reset request', async () => {
    (authService.resetPassword as jest.Mock).mockResolvedValue({ success: true });
    
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authService.resetPassword).toHaveBeenCalledWith('test@example.com');
    });
    
    expect(screen.getByText('Reset link sent! Check your email.')).toBeInTheDocument();
  });

  it('should handle error during password reset', async () => {
    (authService.resetPassword as jest.Mock).mockRejectedValue(new Error('User not found'));
    
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.change(emailInput, { target: { value: 'notfound@example.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Error sending reset link. Please try again.')).toBeInTheDocument();
    });
  });

  it('should navigate back to login', () => {
    renderWithRouter(<ForgotPassword />);
    
    const backButton = screen.getByText('Back to Sign In');
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith('/login');
  });

  it('should show loading state during submission', async () => {
    // Mock a delayed response
    (authService.resetPassword as jest.Mock).mockImplementation(
      () => new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
    );
    
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.click(submitButton);
    
    // Check if button shows loading state
    expect(submitButton).toBeDisabled();
    expect(screen.getByText('Sending...')).toBeInTheDocument();
    
    await waitFor(() => {
      expect(submitButton).not.toBeDisabled();
    });
  });

  it('should validate email format', async () => {
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByPlaceholderText('Enter your email address');
    const submitButton = screen.getByRole('button', { name: 'Send Reset Link' });
    
    // Test invalid email
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    expect(authService.resetPassword).not.toHaveBeenCalled();
    
    // Test valid email
    fireEvent.change(emailInput, { target: { value: 'valid@email.com' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(authService.resetPassword).toHaveBeenCalledWith('valid@email.com');
    });
  });
});
