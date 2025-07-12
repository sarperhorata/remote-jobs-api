import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import Header from '../../components/Header';

// Mock AuthModal component
jest.mock('../../components/AuthModal', () => {
  return function MockAuthModal({ isOpen, onClose }: { isOpen: boolean; onClose: () => void }) {
    if (!isOpen) return null;
    return (
      <div data-testid="auth-modal">
        <button onClick={onClose}>Close Modal</button>
      </div>
    );
  };
});

// Mock useNavigate
const mockNavigate = jest.fn();
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => mockNavigate,
}));

// Mock window.matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});

const renderHeader = () => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        <Header />
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('Header Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Basic Rendering', () => {
    test('renders logo and brand name', () => {
      renderHeader();
      
      expect(screen.getByText('Buzz2Remote')).toBeInTheDocument();
      expect(screen.getByText('Find Remote Jobs 🚀')).toBeInTheDocument();
      expect(screen.getByText('🐝')).toBeInTheDocument();
    });

    test('renders navigation links', () => {
      renderHeader();
      
      expect(screen.getByText('Jobs')).toBeInTheDocument();
      expect(screen.getByText('Companies')).toBeInTheDocument();
      expect(screen.getByText('About')).toBeInTheDocument();
      expect(screen.getByText('Contact')).toBeInTheDocument();
    });

    test('renders sign in and get started buttons when user is not authenticated', () => {
      renderHeader();
      
      expect(screen.getByText('Sign In')).toBeInTheDocument();
      expect(screen.getByText('Get Started')).toBeInTheDocument();
    });

    test('renders mobile menu button', () => {
      renderHeader();
      
      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      expect(mobileMenuButton).toBeInTheDocument();
    });
  });

  describe('Authentication Modal', () => {
    test('opens auth modal when sign in button is clicked', () => {
      renderHeader();
      
      const signInButton = screen.getByText('Sign In');
      fireEvent.click(signInButton);
      
      expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
    });

    test('opens auth modal when get started button is clicked', () => {
      renderHeader();
      
      const getStartedButton = screen.getByText('Get Started');
      fireEvent.click(getStartedButton);
      
      expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
    });

    test('closes auth modal when close button is clicked', async () => {
      renderHeader();
      
      const signInButton = screen.getByText('Sign In');
      fireEvent.click(signInButton);
      
      expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
      
      const closeButton = screen.getByText('Close Modal');
      fireEvent.click(closeButton);
      
      await waitFor(() => {
        expect(screen.queryByTestId('auth-modal')).not.toBeInTheDocument();
      });
    });
  });

  describe('Mobile Menu', () => {
    test('toggles mobile menu when menu button is clicked', () => {
      renderHeader();
      
      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      
      // Initially mobile menu should be closed
      expect(screen.queryByText('Jobs')).not.toBeInTheDocument();
      
      // Open mobile menu
      fireEvent.click(mobileMenuButton);
      
      // Mobile menu should be open
      expect(screen.getByText('Jobs')).toBeInTheDocument();
      expect(screen.getByText('Companies')).toBeInTheDocument();
      expect(screen.getByText('About')).toBeInTheDocument();
      expect(screen.getByText('Contact')).toBeInTheDocument();
    });

    test('closes mobile menu when navigation link is clicked', () => {
      renderHeader();
      
      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      fireEvent.click(mobileMenuButton);
      
      // Mobile menu should be open
      expect(screen.getByText('Jobs')).toBeInTheDocument();
      
      // Click on navigation link
      const jobsLink = screen.getByText('Jobs');
      fireEvent.click(jobsLink);
      
      // Mobile menu should be closed
      expect(screen.queryByText('Jobs')).not.toBeInTheDocument();
    });

    test('opens auth modal from mobile menu when user is not authenticated', () => {
      renderHeader();
      
      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      fireEvent.click(mobileMenuButton);
      
      const mobileSignInButton = screen.getByText('Sign In');
      fireEvent.click(mobileSignInButton);
      
      expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
    });
  });

  describe('User Menu (when authenticated)', () => {
    const mockUser = {
      id: '1',
      email: 'test@example.com',
      name: 'Test User',
      is_verified: true,
      created_at: '2023-01-01T00:00:00Z',
      updated_at: '2023-01-01T00:00:00Z'
    };

    const renderAuthenticatedHeader = () => {
      return render(
        <BrowserRouter>
          <AuthProvider>
            <Header />
          </AuthProvider>
        </BrowserRouter>
      );
    };

    test('renders user menu when user is authenticated', () => {
      // Mock authenticated user
      const mockUseAuth = jest.fn(() => ({
        user: mockUser,
        logout: jest.fn(),
        login: jest.fn(),
        register: jest.fn(),
        isAuthenticated: true,
        loading: false,
        error: null,
        clearError: jest.fn(),
      }));

      jest.doMock('../../contexts/AuthContext', () => ({
        useAuth: mockUseAuth,
      }));

      renderAuthenticatedHeader();
      
      // Should show user email (first part before @)
      expect(screen.getByText('test')).toBeInTheDocument();
    });

    test('toggles profile dropdown when user button is clicked', () => {
      // Mock authenticated user
      const mockUseAuth = jest.fn(() => ({
        user: mockUser,
        logout: jest.fn(),
        login: jest.fn(),
        register: jest.fn(),
        isAuthenticated: true,
        loading: false,
        error: null,
        clearError: jest.fn(),
      }));

      jest.doMock('../../contexts/AuthContext', () => ({
        useAuth: mockUseAuth,
      }));

      renderAuthenticatedHeader();
      
      const userButton = screen.getByText('test');
      fireEvent.click(userButton);
      
      // Dropdown should be visible
      expect(screen.getByText('My Profile')).toBeInTheDocument();
      expect(screen.getByText('Saved Jobs')).toBeInTheDocument();
      expect(screen.getByText('Applications')).toBeInTheDocument();
      expect(screen.getByText('Settings')).toBeInTheDocument();
      expect(screen.getByText('Sign Out')).toBeInTheDocument();
    });
  });

  describe('Navigation Links', () => {
    test('navigates to jobs page when jobs link is clicked', () => {
      renderHeader();
      
      const jobsLink = screen.getByText('Jobs');
      fireEvent.click(jobsLink);
      
      // Should navigate to /jobs
      expect(mockNavigate).toHaveBeenCalledWith('/jobs');
    });

    test('navigates to companies page when companies link is clicked', () => {
      renderHeader();
      
      const companiesLink = screen.getByText('Companies');
      fireEvent.click(companiesLink);
      
      // Should navigate to /companies
      expect(mockNavigate).toHaveBeenCalledWith('/companies');
    });

    test('navigates to about page when about link is clicked', () => {
      renderHeader();
      
      const aboutLink = screen.getByText('About');
      fireEvent.click(aboutLink);
      
      // Should navigate to /about
      expect(mockNavigate).toHaveBeenCalledWith('/about');
    });

    test('navigates to contact page when contact link is clicked', () => {
      renderHeader();
      
      const contactLink = screen.getByText('Contact');
      fireEvent.click(contactLink);
      
      // Should navigate to /contact
      expect(mockNavigate).toHaveBeenCalledWith('/contact');
    });
  });

  describe('Logo Navigation', () => {
    test('navigates to home page when logo is clicked', () => {
      renderHeader();
      
      const logo = screen.getByText('Buzz2Remote');
      fireEvent.click(logo);
      
      // Should navigate to home page
      expect(mockNavigate).toHaveBeenCalledWith('/');
    });
  });

  describe('Click Outside Behavior', () => {
    test('closes dropdowns when clicking outside', () => {
      renderHeader();
      
      // Open mobile menu
      const mobileMenuButton = screen.getByRole('button', { name: /menu/i });
      fireEvent.click(mobileMenuButton);
      
      // Mobile menu should be open
      expect(screen.getByText('Jobs')).toBeInTheDocument();
      
      // Click outside
      fireEvent.click(document.body);
      
      // Mobile menu should be closed
      expect(screen.queryByText('Jobs')).not.toBeInTheDocument();
    });
  });

  describe('Accessibility', () => {
    test('has proper ARIA labels and roles', () => {
      renderHeader();
      
      // Check for navigation role
      expect(screen.getByRole('navigation')).toBeInTheDocument();
      
      // Check for button roles
      expect(screen.getByRole('button', { name: /menu/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /sign in/i })).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /get started/i })).toBeInTheDocument();
    });

    test('has proper link elements for navigation', () => {
      renderHeader();
      
      const jobsLink = screen.getByText('Jobs');
      const companiesLink = screen.getByText('Companies');
      const aboutLink = screen.getByText('About');
      const contactLink = screen.getByText('Contact');
      
      expect(jobsLink.closest('a')).toHaveAttribute('href', '/jobs');
      expect(companiesLink.closest('a')).toHaveAttribute('href', '/companies');
      expect(aboutLink.closest('a')).toHaveAttribute('href', '/about');
      expect(contactLink.closest('a')).toHaveAttribute('href', '/contact');
    });
  });
});