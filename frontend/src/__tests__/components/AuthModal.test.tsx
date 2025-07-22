import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AuthModal from '../../components/AuthModal';

// Mock the API config
jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('http://localhost:8000')
}));

// Mock fetch
global.fetch = jest.fn();

// Mock window.location
const mockLocation = {
  href: '',
  origin: 'http://localhost:3000'
};
Object.defineProperty(window, 'location', {
  value: mockLocation,
  writable: true
});

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

const renderAuthModal = (props = {}) => {
  return render(
    <BrowserRouter>
      <AuthModal isOpen={true} onClose={jest.fn()} {...props} />
    </BrowserRouter>
  );
};

describe('AuthModal', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.setItem.mockClear();
    localStorageMock.getItem.mockClear();
  });

  describe('Rendering', () => {
    test('renders login tab by default', () => {
      renderAuthModal();
      expect(screen.getByText('Sign In')).toBeInTheDocument();
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
    });

    test('renders register tab when defaultTab is register', () => {
      renderAuthModal({ defaultTab: 'register' });
      expect(screen.getByText('Create Account')).toBeInTheDocument();
      expect(screen.getByText('Full Name')).toBeInTheDocument();
      expect(screen.getByText('Email')).toBeInTheDocument();
      expect(screen.getByText('Password')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /create account/i })).toBeInTheDocument();
    });

    test('does not render when isOpen is false', () => {
      renderAuthModal({ isOpen: false });
      expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
    });

    test('renders close button', () => {
      renderAuthModal();
      expect(screen.getByRole('button', { name: /close/i })).toBeInTheDocument();
    });

    test('renders tab navigation', () => {
      renderAuthModal();
      expect(screen.getByRole('tab', { name: /sign in/i })).toBeInTheDocument();
      expect(screen.getByRole('tab', { name: /create account/i })).toBeInTheDocument();
    });
  });

  describe('Tab Navigation', () => {
    test('switches to register tab when clicked', () => {
      renderAuthModal();
      const registerTab = screen.getByRole('tab', { name: /create account/i });
      fireEvent.click(registerTab);
      expect(screen.getByText('Create Account')).toBeInTheDocument();
      expect(screen.getByText('Full Name')).toBeInTheDocument();
    });

    test('switches to login tab when clicked', () => {
      renderAuthModal({ defaultTab: 'register' });
      const loginTab = screen.getByRole('tab', { name: /sign in/i });
      fireEvent.click(loginTab);
      expect(screen.getByText('Sign In')).toBeInTheDocument();
      expect(screen.getByText('Email')).toBeInTheDocument();
    });
  });

  describe('Login Form', () => {
    test('handles email input', () => {
      renderAuthModal();
      const emailInput = screen.getByLabelText(/email address/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      expect(emailInput).toHaveValue('test@example.com');
    });

    test('handles password input', () => {
      renderAuthModal();
      const passwordInput = screen.getByLabelText(/password/i);
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      expect(passwordInput).toHaveValue('password123');
    });

    test('toggles password visibility', () => {
      renderAuthModal();
      const passwordInput = screen.getByLabelText(/password/i);
      const toggleButton = screen.getByRole('button', { name: /toggle password visibility/i });
      
      expect(passwordInput).toHaveAttribute('type', 'password');
      fireEvent.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'text');
      fireEvent.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('handles remember me checkbox', () => {
      renderAuthModal();
      const rememberMeCheckbox = screen.getByLabelText(/remember me/i);
      fireEvent.click(rememberMeCheckbox);
      expect(rememberMeCheckbox).toBeChecked();
    });

    test('shows validation error for empty fields', async () => {
      renderAuthModal();
      const submitButton = screen.getByRole('button', { name: /sign in/i });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Please fill in all fields')).toBeInTheDocument();
      });
    });

    test('handles successful login', async () => {
      const mockOnClose = jest.fn();
      const mockUserData = { id: 1, email: 'test@example.com', name: 'Test User' };
      
      (global.fetch as jest.Mock)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ access_token: 'mock-token', token_type: 'bearer' })
        })
        .mockResolvedValueOnce({
          ok: true,
          json: async () => mockUserData
        });

      renderAuthModal({ onClose: mockOnClose });
      
      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', 'mock-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('token_type', 'bearer');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('userToken', 'mock-token');
        expect(localStorageMock.setItem).toHaveBeenCalledWith('user_data', JSON.stringify(mockUserData));
      });
    });

    test('handles login error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Invalid email or password' })
      });

      renderAuthModal();
      
      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'wrongpassword' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Invalid email or password')).toBeInTheDocument();
      });
    });

    test('handles email not verified error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 403,
        json: async () => ({ detail: 'Email not verified' })
      });

      renderAuthModal();
      
      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/email not verified/i)).toBeInTheDocument();
      });
    });
  });

  describe('Register Form', () => {
    beforeEach(() => {
      renderAuthModal({ defaultTab: 'register' });
    });

    test('handles full name input', () => {
      const nameInput = screen.getByLabelText(/full name/i);
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      expect(nameInput).toHaveValue('John Doe');
    });

    test('handles email input in register form', () => {
      const emailInput = screen.getByLabelText(/email address/i);
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      expect(emailInput).toHaveValue('test@example.com');
    });

    test('handles password input in register form', () => {
      const passwordInput = screen.getByLabelText(/password/i);
      fireEvent.change(passwordInput, { target: { value: 'Password123' } });
      expect(passwordInput).toHaveValue('Password123');
    });

    test('shows password requirements', () => {
      const passwordInput = screen.getByLabelText(/password/i);
      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      
      expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
      expect(screen.getByText('At least 1 number')).toBeInTheDocument();
      expect(screen.getByText('At least 1 uppercase letter')).toBeInTheDocument();
    });

    test('validates password requirements', () => {
      const passwordInput = screen.getByLabelText(/password/i);
      
      // Weak password
      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      expect(screen.getByText('At least 8 characters')).toHaveClass('text-red-500');
      
      // Strong password
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      expect(screen.getByText('At least 8 characters')).toHaveClass('text-green-500');
    });

    test('handles terms agreement checkbox', () => {
      const termsCheckbox = screen.getByLabelText(/i agree to the terms of service/i);
      fireEvent.click(termsCheckbox);
      expect(termsCheckbox).toBeChecked();
    });

    test('shows validation error for empty fields', async () => {
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });
      fireEvent.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Please fill in all required fields')).toBeInTheDocument();
      });
    });

    test('shows validation error for invalid password', async () => {
      const emailInput = screen.getByLabelText(/email address/i);
      const nameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Password must meet all requirements')).toBeInTheDocument();
      });
    });

    test('shows validation error for unchecked terms', async () => {
      const emailInput = screen.getByLabelText(/email address/i);
      const nameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Please agree to the Terms of Service')).toBeInTheDocument();
      });
    });

    test('handles successful registration', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Registration successful' })
      });

      const emailInput = screen.getByLabelText(/email address/i);
      const nameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const termsCheckbox = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      fireEvent.click(termsCheckbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/registration successful/i)).toBeInTheDocument();
      });
    });

    test('handles registration error', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already exists' })
      });

      const emailInput = screen.getByLabelText(/email address/i);
      const nameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const termsCheckbox = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      fireEvent.click(termsCheckbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument();
      });
    });

    test('handles Pydantic validation errors', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ 
          detail: [
            { msg: 'Invalid email format' },
            { msg: 'Password too short' }
          ]
        })
      });

      const emailInput = screen.getByLabelText(/email address/i);
      const nameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const termsCheckbox = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      fireEvent.click(termsCheckbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Invalid email format, Password too short')).toBeInTheDocument();
      });
    });
  });

  describe('Google OAuth', () => {
    test('handles Google login button click', () => {
      renderAuthModal();
      const googleButton = screen.getByRole('button', { name: /continue with google/i });
      fireEvent.click(googleButton);
      
      expect(window.location.href).toContain('accounts.google.com');
      expect(window.location.href).toContain('oauth2');
    });

    test('handles Google auth error', async () => {
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      renderAuthModal();
      const googleButton = screen.getByRole('button', { name: /continue with google/i });
      
      // Mock window.location.href to throw error
      const originalHref = window.location.href;
      Object.defineProperty(window.location, 'href', {
        set: jest.fn().mockImplementation(() => {
          throw new Error('Navigation blocked');
        }),
        get: jest.fn().mockReturnValue(originalHref)
      });

      fireEvent.click(googleButton);

      await waitFor(() => {
        expect(screen.getByText('Google authentication failed. Please try again.')).toBeInTheDocument();
      });

      consoleSpy.mockRestore();
    });
  });

  describe('Modal Interactions', () => {
    test('calls onClose when close button is clicked', () => {
      const mockOnClose = jest.fn();
      renderAuthModal({ onClose: mockOnClose });
      
      const closeButton = screen.getByRole('button', { name: /close/i });
      fireEvent.click(closeButton);
      
      expect(mockOnClose).toHaveBeenCalled();
    });

    test('opens terms modal when terms link is clicked', () => {
      renderAuthModal({ defaultTab: 'register' });
      
      const termsLink = screen.getByText(/terms of service/i);
      fireEvent.click(termsLink);
      
      expect(screen.getByText('Terms of Service')).toBeInTheDocument();
      expect(screen.getByText(/by using our service/i)).toBeInTheDocument();
    });

    test('opens privacy modal when privacy link is clicked', () => {
      renderAuthModal({ defaultTab: 'register' });
      
      const privacyLink = screen.getByText(/privacy policy/i);
      fireEvent.click(privacyLink);
      
      expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
      expect(screen.getByText(/we respect your privacy/i)).toBeInTheDocument();
    });

    test('closes terms modal when close button is clicked', () => {
      renderAuthModal({ defaultTab: 'register' });
      
      const termsLink = screen.getByText(/terms of service/i);
      fireEvent.click(termsLink);
      
      const closeButton = screen.getByRole('button', { name: /close/i });
      fireEvent.click(closeButton);
      
      expect(screen.queryByText('Terms of Service')).not.toBeInTheDocument();
    });

    test('closes privacy modal when close button is clicked', () => {
      renderAuthModal({ defaultTab: 'register' });
      
      const privacyLink = screen.getByText(/privacy policy/i);
      fireEvent.click(privacyLink);
      
      const closeButton = screen.getByRole('button', { name: /close/i });
      fireEvent.click(closeButton);
      
      expect(screen.queryByText('Privacy Policy')).not.toBeInTheDocument();
    });
  });

  describe('Loading States', () => {
    test('shows loading state during login', async () => {
      (global.fetch as jest.Mock).mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      renderAuthModal();
      
      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      expect(screen.getByText(/signing in/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });

    test('shows loading state during registration', async () => {
      (global.fetch as jest.Mock).mockImplementation(() => new Promise(resolve => setTimeout(resolve, 100)));

      renderAuthModal({ defaultTab: 'register' });
      
      const emailInput = screen.getByLabelText(/email address/i);
      const nameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const termsCheckbox = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      fireEvent.click(termsCheckbox);
      fireEvent.click(submitButton);

      expect(screen.getByText(/creating account/i)).toBeInTheDocument();
      expect(submitButton).toBeDisabled();
    });
  });

  describe('Error Handling', () => {
    test('handles network error during login', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      renderAuthModal();
      
      const emailInput = screen.getByLabelText(/email address/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const submitButton = screen.getByRole('button', { name: /sign in/i });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password123' } });
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Login failed. Please try again.')).toBeInTheDocument();
      });
    });

    test('handles network error during registration', async () => {
      (global.fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      renderAuthModal({ defaultTab: 'register' });
      
      const emailInput = screen.getByLabelText(/email address/i);
      const nameInput = screen.getByLabelText(/full name/i);
      const passwordInput = screen.getByLabelText(/password/i);
      const termsCheckbox = screen.getByLabelText(/i agree to the terms of service/i);
      const submitButton = screen.getByRole('button', { name: /create account/i, type: 'submit' });

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      fireEvent.click(termsCheckbox);
      fireEvent.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText('Registration failed')).toBeInTheDocument();
      });
    });
  });
});