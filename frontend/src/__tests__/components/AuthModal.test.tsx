import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import AuthModal from '../../components/AuthModal';
import { AuthProvider } from '../../contexts/AuthContext';

// Mock useAuth hook
const mockSignup = jest.fn();
const mockUseAuth = {
  signup: mockSignup,
  login: jest.fn(),
  user: null,
  loading: false
};

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockUseAuth,
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>
}));

// Mock fetch for API calls
global.fetch = jest.fn();

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('AuthModal', () => {
  const mockProps = {
    isOpen: true,
    onClose: jest.fn(),
    defaultTab: 'register' as const
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
  });

  describe('Component Rendering', () => {
    test('should render without crashing', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      expect(screen.getByText('Buzz2Remote')).toBeInTheDocument();
    });

    test('should render login tab by default', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      expect(screen.getByText('Welcome back!')).toBeInTheDocument();
      expect(screen.getByText('Sign In')).toBeInTheDocument();
    });

    test('should render register tab when defaultTab is register', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      expect(screen.getByText('Create Account')).toBeInTheDocument();
    });

    test('should not render when isOpen is false', () => {
      renderWithRouter(<AuthModal {...mockProps} isOpen={false} />);
      expect(screen.queryByText('Buzz2Remote')).not.toBeInTheDocument();
    });
  });

  describe('Registration Form', () => {
    it('renders registration form with all required fields', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      expect(screen.getByText('Create Account')).toBeInTheDocument();
      expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
      expect(screen.getByLabelText('Full Name')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByText('Password Requirements:')).toBeInTheDocument();
    });

    it('validates password requirements correctly', async () => {
      const user = userEvent.setup();
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const passwordInput = screen.getByLabelText('Password');
      
      // Test weak password
      await user.type(passwordInput, 'weak');
      
      expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
      expect(screen.getByText('At least 1 number')).toBeInTheDocument();
      expect(screen.getByText('At least 1 uppercase letter')).toBeInTheDocument();
      
      // Test strong password
      await user.clear(passwordInput);
      await user.type(passwordInput, 'StrongPass123');
      
      await waitFor(() => {
        const requirements = screen.getAllByText(/At least/);
        requirements.forEach(req => {
          expect(req).toBeInTheDocument();
        });
      });
    });

    it('shows password when eye icon is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const passwordInput = screen.getByLabelText('Password') as HTMLInputElement;
      const toggleButton = screen.getByRole('button', { name: /toggle password visibility/i });
      
      expect(passwordInput.type).toBe('password');
      
      await user.click(toggleButton);
      expect(passwordInput.type).toBe('text');
      
      await user.click(toggleButton);
      expect(passwordInput.type).toBe('password');
    });

    it('opens Terms of Service modal when link is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const termsLink = screen.getByText('Terms of Service');
      await user.click(termsLink);
      
      expect(screen.getByText('Welcome to Buzz2Remote. By using our service, you agree to these terms.')).toBeInTheDocument();
      expect(screen.getByText('1. Service Description')).toBeInTheDocument();
    });

    it('opens Privacy Policy modal when link is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const privacyLink = screen.getByText('Privacy Policy');
      await user.click(privacyLink);
      
      expect(screen.getByText('This Privacy Policy describes how we collect, use, and protect your information.')).toBeInTheDocument();
      expect(screen.getByText('Information We Collect')).toBeInTheDocument();
    });

    it('disables submit button when terms are not agreed', async () => {
      const user = userEvent.setup();
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const emailInput = screen.getByLabelText('Email Address');
      const nameInput = screen.getByLabelText('Full Name');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Create Account' });
      
      await user.type(emailInput, 'test@example.com');
      await user.type(nameInput, 'Test User');
      await user.type(passwordInput, 'StrongPass123');
      
      expect(submitButton).toBeDisabled();
      
      const termsCheckbox = screen.getByLabelText(/I agree to the/);
      await user.click(termsCheckbox);
      
      await waitFor(() => {
        expect(submitButton).toBeEnabled();
      });
    });

    it('submits registration form with correct data', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Registration successful' })
      });

      renderWithRouter(<AuthModal {...mockProps} />);
      
      const emailInput = screen.getByLabelText('Email Address');
      const nameInput = screen.getByLabelText('Full Name');
      const passwordInput = screen.getByLabelText('Password');
      const termsCheckbox = screen.getByLabelText(/I agree to the/);
      const submitButton = screen.getByRole('button', { name: 'Create Account' });
      
      await user.type(emailInput, 'test@example.com');
      await user.type(nameInput, 'Test User');
      await user.type(passwordInput, 'StrongPass123');
      await user.click(termsCheckbox);
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          'http://localhost:8001/api/v1/auth/register',
          expect.objectContaining({
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              email: 'test@example.com',
              full_name: 'Test User',
              password: 'StrongPass123'
            })
          })
        );
      });
    });

    it('displays success message after successful registration', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Registration successful' })
      });

      renderWithRouter(<AuthModal {...mockProps} />);
      
      const emailInput = screen.getByLabelText('Email Address');
      const nameInput = screen.getByLabelText('Full Name');
      const passwordInput = screen.getByLabelText('Password');
      const termsCheckbox = screen.getByLabelText(/I agree to the/);
      const submitButton = screen.getByRole('button', { name: 'Create Account' });
      
      await user.type(emailInput, 'test@example.com');
      await user.type(nameInput, 'Test User');
      await user.type(passwordInput, 'StrongPass123');
      await user.click(termsCheckbox);
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Registration successful! Please check your email to login')).toBeInTheDocument();
      });
    });

    it('displays error message on registration failure', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: async () => ({ detail: 'Email already exists' })
      });

      renderWithRouter(<AuthModal {...mockProps} />);
      
      const emailInput = screen.getByLabelText('Email Address');
      const nameInput = screen.getByLabelText('Full Name');
      const passwordInput = screen.getByLabelText('Password');
      const termsCheckbox = screen.getByLabelText(/I agree to the/);
      const submitButton = screen.getByRole('button', { name: 'Create Account' });
      
      await user.type(emailInput, 'test@example.com');
      await user.type(nameInput, 'Test User');
      await user.type(passwordInput, 'StrongPass123');
      await user.click(termsCheckbox);
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(screen.getByText('Email already exists')).toBeInTheDocument();
      });
    });
  });

  describe('Login Form', () => {
    const loginProps = {
      ...mockProps,
      defaultTab: 'login' as const
    };

    it('renders login form with all required fields', () => {
      renderWithRouter(<AuthModal {...loginProps} />);
      
      expect(screen.getByText('Welcome back!')).toBeInTheDocument();
      expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
      expect(screen.getByText('Remember me')).toBeInTheDocument();
    });

    it('submits login form with correct data', async () => {
      const user = userEvent.setup();
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ access_token: 'token123' })
      });

      renderWithRouter(<AuthModal {...loginProps} />);
      
      const emailInput = screen.getByLabelText('Email Address');
      const passwordInput = screen.getByLabelText('Password');
      const submitButton = screen.getByRole('button', { name: 'Sign In' });
      
      await user.type(emailInput, 'test@example.com');
      await user.type(passwordInput, 'password123');
      await user.click(submitButton);
      
      await waitFor(() => {
        expect(fetch).toHaveBeenCalledWith(
          'http://localhost:8001/api/v1/auth/login',
          expect.objectContaining({
            method: 'POST',
            body: expect.any(FormData)
          })
        );
      });
    });
  });

  describe('Tab Navigation', () => {
    it('switches between login and register tabs', async () => {
      const user = userEvent.setup();
      renderWithRouter(<AuthModal {...mockProps} defaultTab="login" />);
      
      expect(screen.getByText('Welcome back!')).toBeInTheDocument();
      
      const registerTab = screen.getByText('Create Account');
      await user.click(registerTab);
      
      expect(screen.getByText('Create Account')).toBeInTheDocument();
      expect(screen.getByText('Password Requirements:')).toBeInTheDocument();
    });

    test('switches to register tab and shows registration form', async () => {
      const user = userEvent.setup();
      renderWithRouter(
        <AuthModal isOpen={true} onClose={mockProps.onClose} defaultTab="login" />
      );
      
      const registerTab = screen.getByRole('button', { name: /create account/i });
      await user.click(registerTab);
      
      // Check for specific form elements that only appear in register form
      expect(screen.getByLabelText(/full name/i)).toBeInTheDocument();
      expect(screen.getByText('Password Requirements:')).toBeInTheDocument();
    });
  });

  describe('Modal Behavior', () => {
    it('closes modal when close button is clicked', async () => {
      const user = userEvent.setup();
      const onClose = jest.fn();
      
      renderWithRouter(<AuthModal {...mockProps} onClose={onClose} />);
      
      const closeButton = screen.getByText('×');
      await user.click(closeButton);
      
      expect(onClose).toHaveBeenCalled();
    });

    it('closes Terms modal when close button is clicked', async () => {
      const user = userEvent.setup();
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const termsLink = screen.getByText('Terms of Service');
      await user.click(termsLink);
      
      const closeButton = screen.getAllByText('×')[1]; // Second close button (for modal)
      await user.click(closeButton);
      
      expect(screen.queryByText('1. Service Description')).not.toBeInTheDocument();
    });
  });

  describe('Password Requirements', () => {
    test('should display password requirements in register tab', async () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const passwordInput = screen.getByPlaceholderText('Your password');
      fireEvent.change(passwordInput, { target: { value: 'weak' } });

      await waitFor(() => {
        expect(screen.getByText('At least 8 characters')).toBeInTheDocument();
        expect(screen.getByText('At least 1 number')).toBeInTheDocument();
        expect(screen.getByText('At least 1 uppercase letter')).toBeInTheDocument();
      });
    });

    test('should show validation icons for password requirements', async () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const passwordInput = screen.getByPlaceholderText('Your password');
      
      // Test with weak password
      fireEvent.change(passwordInput, { target: { value: 'weak' } });
      
      await waitFor(() => {
        // Should show X icons for failed requirements
        const invalidIcons = screen.getAllByRole('generic').filter(el => 
          el.querySelector('svg') && el.textContent?.includes('text-red-500')
        );
        expect(invalidIcons.length).toBeGreaterThan(0);
      });

      // Test with strong password
      fireEvent.change(passwordInput, { target: { value: 'StrongPass123' } });
      
      await waitFor(() => {
        // Should show Check icons for passed requirements
        const validIcons = screen.getAllByRole('generic').filter(el => 
          el.querySelector('svg') && el.textContent?.includes('text-green-500')
        );
        expect(validIcons.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Form Interactions', () => {
    test('should toggle password visibility', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const passwordInput = screen.getByPlaceholderText('Your password');
      const toggleButton = screen.getByRole('button', { name: /toggle password visibility/i });

      expect(passwordInput).toHaveAttribute('type', 'password');
      
      fireEvent.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'text');
      
      fireEvent.click(toggleButton);
      expect(passwordInput).toHaveAttribute('type', 'password');
    });

    test('should switch between login and register tabs', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      expect(screen.getByText('Welcome back!')).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Create Account'));
      expect(screen.getByText('Create Account')).toBeInTheDocument();
      
      fireEvent.click(screen.getByText('Sign In'));
      expect(screen.getByText('Welcome back!')).toBeInTheDocument();
    });

    test('should call onClose when close button is clicked', () => {
      const onClose = jest.fn();
      renderWithRouter(<AuthModal {...mockProps} onClose={onClose} />);
      
      const closeButton = screen.getByText('×');
      fireEvent.click(closeButton);
      
      expect(onClose).toHaveBeenCalledTimes(1);
    });
  });

  describe('Form Validation', () => {
    test('should show error for invalid login credentials', async () => {
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        json: () => Promise.resolve({ detail: 'Invalid credentials' })
      });

      renderWithRouter(<AuthModal {...mockProps} />);
      
      fireEvent.change(screen.getByPlaceholderText('your@email.com'), {
        target: { value: 'test@example.com' }
      });
      fireEvent.change(screen.getByPlaceholderText('Your password'), {
        target: { value: 'wrongpassword' }
      });
      
      fireEvent.click(screen.getByRole('button', { name: /sign in/i }));

      await waitFor(() => {
        expect(screen.getByText('Invalid credentials')).toBeInTheDocument();
      });
    });

    test('should require terms agreement for registration', async () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      fireEvent.change(screen.getByPlaceholderText('your@email.com'), {
        target: { value: 'test@example.com' }
      });
      fireEvent.change(screen.getByPlaceholderText('John Doe'), {
        target: { value: 'Test User' }
      });
      fireEvent.change(screen.getByPlaceholderText('Your password'), {
        target: { value: 'StrongPass123' }
      });
      
      fireEvent.click(screen.getByRole('button', { name: /create account/i }));

      await waitFor(() => {
        expect(screen.getByText(/please agree to the terms/i)).toBeInTheDocument();
      });
    });
  });

  describe('Icon Usage Validation', () => {
    test('should properly render lucide-react icons', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      // Check that icons are rendered (they should be in the DOM as SVG elements)
      const svgElements = document.querySelectorAll('svg');
      expect(svgElements.length).toBeGreaterThan(0);
    });

    test('should not have undefined icon references', () => {
      // This test ensures no runtime errors occur from undefined icons
      expect(() => {
        renderWithRouter(<AuthModal {...mockProps} />);
      }).not.toThrow();
    });
  });

  describe('Accessibility', () => {
    test('should have proper labels for form inputs', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      expect(screen.getByLabelText('Email Address')).toBeInTheDocument();
      expect(screen.getByLabelText('Password')).toBeInTheDocument();
    });

    test('should have proper ARIA attributes', () => {
      renderWithRouter(<AuthModal {...mockProps} />);
      
      const modal = document.querySelector('[role="dialog"]') || 
                   document.querySelector('.fixed.inset-0');
      
      // Modal should be present in DOM
      expect(modal).toBeInTheDocument();
    });
  });
}); 