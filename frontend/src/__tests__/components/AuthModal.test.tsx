import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import AuthModal from '../../components/AuthModal';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock AuthContext
const mockAuthContext = {
  isAuthenticated: false,
  user: null,
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

describe('AuthModal', () => {
  const mockOnClose = jest.fn();
  const mockOnSuccess = jest.fn();

  beforeEach(() => {
    mockFetch.mockClear();
    mockOnClose.mockClear();
    mockOnSuccess.mockClear();
    mockAuthContext.login.mockClear();
    mockAuthContext.signup.mockClear();
  });

  it('renders login form by default', () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Password')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Sign In' })).toBeInTheDocument();
  });

  it('switches to signup form when clicking signup link', () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const signupLink = screen.getByText("Don't have an account? Sign up");
    fireEvent.click(signupLink);
    
    expect(screen.getByText('Create Account')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Full Name')).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Create Account' })).toBeInTheDocument();
  });

  it('switches back to login form when clicking login link', () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    // Switch to signup first
    const signupLink = screen.getByText("Don't have an account? Sign up");
    fireEvent.click(signupLink);
    
    // Switch back to login
    const loginLink = screen.getByText('Already have an account? Sign in');
    fireEvent.click(loginLink);
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Email')).toBeInTheDocument();
  });

  it('handles login form submission', async () => {
    mockAuthContext.login.mockResolvedValueOnce({ success: true });

    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockAuthContext.login).toHaveBeenCalledWith('test@example.com', 'password123', false);
    });
    
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('handles signup form submission', async () => {
    mockAuthContext.signup.mockResolvedValueOnce({ success: true });

    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    // Switch to signup
    const signupLink = screen.getByText("Don't have an account? Sign up");
    fireEvent.click(signupLink);
    
    const nameInput = screen.getByPlaceholderText('Full Name');
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Create Account' });
    
    fireEvent.change(nameInput, { target: { value: 'Test User' } });
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockAuthContext.signup).toHaveBeenCalledWith({
        name: 'Test User',
        email: 'test@example.com',
        password: 'password123'
      });
    });
    
    expect(mockOnSuccess).toHaveBeenCalled();
  });

  it('shows validation errors for invalid email', async () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Please enter a valid email address')).toBeInTheDocument();
    });
  });

  it('shows validation errors for short password', async () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: '123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Password must be at least 6 characters')).toBeInTheDocument();
    });
  });

  it('shows loading state during form submission', async () => {
    mockAuthContext.login.mockImplementation(() => 
      new Promise(resolve => setTimeout(() => resolve({ success: true }), 100))
    );

    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    expect(screen.getByText('Signing in...')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });

  it('handles login errors', async () => {
    mockAuthContext.login.mockRejectedValueOnce(new Error('Invalid credentials'));

    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
    });
  });

  it('handles signup errors', async () => {
    mockAuthContext.signup.mockRejectedValueOnce(new Error('Email already exists'));

    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    // Switch to signup
    const signupLink = screen.getByText("Don't have an account? Sign up");
    fireEvent.click(signupLink);
    
    const nameInput = screen.getByPlaceholderText('Full Name');
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const submitButton = screen.getByRole('button', { name: 'Create Account' });
    
    fireEvent.change(nameInput, { target: { value: 'Test User' } });
    fireEvent.change(emailInput, { target: { value: 'existing@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(screen.getByText('Email already exists')).toBeInTheDocument();
    });
  });

  it('closes modal when clicking close button', () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const closeButton = screen.getByRole('button', { name: /close/i });
    fireEvent.click(closeButton);
    
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('closes modal when clicking outside', () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const backdrop = screen.getByTestId('modal-backdrop');
    fireEvent.click(backdrop);
    
    expect(mockOnClose).toHaveBeenCalled();
  });

  it('does not render when isOpen is false', () => {
    renderWithProviders(
      <AuthModal isOpen={false} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
  });

  it('handles remember me checkbox', async () => {
    mockAuthContext.login.mockResolvedValueOnce({ success: true });

    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const emailInput = screen.getByPlaceholderText('Email');
    const passwordInput = screen.getByPlaceholderText('Password');
    const rememberMeCheckbox = screen.getByLabelText('Remember me');
    const submitButton = screen.getByRole('button', { name: 'Sign In' });
    
    fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
    fireEvent.change(passwordInput, { target: { value: 'password123' } });
    fireEvent.click(rememberMeCheckbox);
    fireEvent.click(submitButton);
    
    await waitFor(() => {
      expect(mockAuthContext.login).toHaveBeenCalledWith('test@example.com', 'password123', true);
    });
  });

  it('handles forgot password link', () => {
    renderWithProviders(
      <AuthModal isOpen={true} onClose={mockOnClose} onSuccess={mockOnSuccess} />
    );
    
    const forgotPasswordLink = screen.getByText('Forgot your password?');
    fireEvent.click(forgotPasswordLink);
    
    expect(screen.getByText('Reset Password')).toBeInTheDocument();
    expect(screen.getByPlaceholderText('Enter your email address')).toBeInTheDocument();
  });
});