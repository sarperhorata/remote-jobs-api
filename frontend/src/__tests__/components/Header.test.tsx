import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from '../../components/Header';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/ThemeContext';
import '@testing-library/jest-dom';

// Mock the contexts
jest.mock('../../contexts/AuthContext');
jest.mock('../../contexts/ThemeContext');
jest.mock('../../components/AuthModal', () => {
  return function MockAuthModal({ isOpen, onClose, defaultTab }: any) {
    return isOpen ? (
      <div data-testid="auth-modal">
        <div>Auth Modal - {defaultTab}</div>
        <button onClick={onClose}>Close</button>
      </div>
    ) : null;
  };
});

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
const mockUseTheme = useTheme as jest.MockedFunction<typeof useTheme>;

const renderHeader = () => {
  return render(
    <BrowserRouter>
      <Header />
    </BrowserRouter>
  );
};

describe('Header', () => {
  const mockLogout = jest.fn();
  const mockToggleTheme = jest.fn();
  const mockApplyTheme = jest.fn();

  beforeEach(() => {
    jest.clearAllMocks();
    
    mockUseAuth.mockReturnValue({
      isAuthenticated: false,
      user: null,
      login: jest.fn(),
      logout: mockLogout,
      signup: jest.fn(),
      refreshUser: jest.fn(),
      isLoading: false,
    });

    mockUseTheme.mockReturnValue({
      theme: 'light',
      toggleTheme: mockToggleTheme,
      applyTheme: mockApplyTheme,
    });
  });

  it('renders the brand name', () => {
    renderHeader();
    expect(screen.getByText('Buzz2Remote')).toBeInTheDocument();
  });

  it('renders navigation links', () => {
    renderHeader();
    expect(screen.getByText('Jobs')).toBeInTheDocument();
    expect(screen.getByText('Companies')).toBeInTheDocument();
  });

  it('shows sign in and get started buttons when not authenticated', () => {
    renderHeader();
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByText('Get Started')).toBeInTheDocument();
  });

  it('shows sign out button when authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'John Doe', email: 'john@example.com' },
      login: jest.fn(),
      logout: mockLogout,
      signup: jest.fn(),
      refreshUser: jest.fn(),
      isLoading: false,
    });

    renderHeader();
    expect(screen.getByText('Sign Out')).toBeInTheDocument();
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
    expect(screen.queryByText('Get Started')).not.toBeInTheDocument();
  });

  it('calls logout when sign out button is clicked', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'John Doe', email: 'john@example.com' },
      login: jest.fn(),
      logout: mockLogout,
      signup: jest.fn(),
      refreshUser: jest.fn(),
      isLoading: false,
    });

    renderHeader();
    const signOutButton = screen.getByText('Sign Out');
    fireEvent.click(signOutButton);
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('shows light theme icon when in dark theme', () => {
    mockUseTheme.mockReturnValue({
      theme: 'dark',
      toggleTheme: mockToggleTheme,
      applyTheme: mockApplyTheme,
    });

    renderHeader();
    const themeButton = screen.getByLabelText('Switch to light mode');
    expect(themeButton).toBeInTheDocument();
  });

  it('shows dark theme icon when in light theme', () => {
    renderHeader();
    const themeButton = screen.getByLabelText('Switch to dark mode');
    expect(themeButton).toBeInTheDocument();
  });

  it('calls toggleTheme when theme button is clicked', () => {
    renderHeader();
    const themeButton = screen.getByLabelText('Switch to dark mode');
    fireEvent.click(themeButton);
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  it('opens login modal when sign in is clicked', () => {
    renderHeader();
    const signInButton = screen.getByText('Sign In');
    fireEvent.click(signInButton);
    
    expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
    expect(screen.getByText('Auth Modal - login')).toBeInTheDocument();
  });

  it('opens register modal when get started is clicked', () => {
    renderHeader();
    const getStartedButton = screen.getByText('Get Started');
    fireEvent.click(getStartedButton);
    
    expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
    expect(screen.getByText('Auth Modal - register')).toBeInTheDocument();
  });

  it('can close auth modal', () => {
    renderHeader();
    const signInButton = screen.getByText('Sign In');
    fireEvent.click(signInButton);
    
    expect(screen.getByTestId('auth-modal')).toBeInTheDocument();
    
    const closeButton = screen.getByText('Close');
    fireEvent.click(closeButton);
    
    expect(screen.queryByTestId('auth-modal')).not.toBeInTheDocument();
  });

  it('renders without crashing', () => {
    expect(() => renderHeader()).not.toThrow();
  });
}); 