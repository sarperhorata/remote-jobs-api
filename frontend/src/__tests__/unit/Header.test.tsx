import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Header from '../../components/Header';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';

// Mock the auth context
const mockAuthContext = {
  user: null,
  isAuthenticated: false,
  isLoading: false,
  login: jest.fn(),
  logout: jest.fn(),
  signup: jest.fn(),
  refreshUser: jest.fn(),
};

jest.mock('../../contexts/AuthContext', () => ({
  ...jest.requireActual('../../contexts/AuthContext'),
  useAuth: () => mockAuthContext,
}));

// Mock theme context
const mockThemeContext = {
  theme: 'light',
  toggleTheme: jest.fn(),
  applyTheme: jest.fn(),
};

jest.mock('../../contexts/ThemeContext', () => ({
  ...jest.requireActual('../../contexts/ThemeContext'),
  useTheme: () => mockThemeContext,
}));

const renderHeader = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <Header />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Header Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockAuthContext.user = null;
    mockAuthContext.isAuthenticated = false;
    process.env.NODE_ENV = 'test';
  });

  it('renders logo and navigation', () => {
    renderHeader();
    
    expect(screen.getByText('Buzz2Remote')).toBeInTheDocument();
    expect(screen.getByText('Jobs')).toBeInTheDocument();
    expect(screen.getByText('Companies')).toBeInTheDocument();
  });

  it('shows login button when not authenticated', () => {
    renderHeader();
    
    expect(screen.getByText('Sign In')).toBeInTheDocument();
    expect(screen.getByText('Get Started')).toBeInTheDocument();
    expect(screen.queryByText('Sign Out')).not.toBeInTheDocument();
  });

  it('shows user menu when authenticated', () => {
    mockAuthContext.user = {
      id: '1',
      name: 'Test User',
      email: 'test@example.com'
    };
    mockAuthContext.isAuthenticated = true;

    renderHeader();
    
    expect(screen.getByText('Sign Out')).toBeInTheDocument();
    expect(screen.queryByText('Sign In')).not.toBeInTheDocument();
    expect(screen.queryByText('Get Started')).not.toBeInTheDocument();
  });

  it('opens auth modal when login button clicked', () => {
    renderHeader();
    
    const signInButton = screen.getByText('Sign In');
    fireEvent.click(signInButton);
    
    // Auth modal should be visible
    expect(screen.getByRole('dialog')).toBeInTheDocument();
  });

  it('toggles theme when theme button is clicked', () => {
    renderHeader();
    
    const themeButton = screen.getByLabelText(/Switch to/i);
    fireEvent.click(themeButton);
    
    expect(mockThemeContext.toggleTheme).toHaveBeenCalled();
  });

  it('calls logout when logout button is clicked', async () => {
    mockAuthContext.user = {
      id: '1',
      name: 'Test User',
      email: 'test@example.com'
    };
    mockAuthContext.isAuthenticated = true;

    renderHeader();
    
    const logoutButton = screen.getByText('Sign Out');
    fireEvent.click(logoutButton);
    
    expect(mockAuthContext.logout).toHaveBeenCalled();
  });

  it('applies correct theme class', () => {
    mockThemeContext.theme = 'dark';
    renderHeader();
    
    const header = screen.getByRole('banner');
    expect(header).toHaveClass('dark:bg-gray-900');
  });

  it('highlights active navigation item', () => {
    // Mock useLocation
    jest.mock('react-router-dom', () => ({
      ...jest.requireActual('react-router-dom'),
      useLocation: () => ({ pathname: '/jobs' }),
    }));

    renderHeader();
    
    const jobsLink = screen.getByText('Jobs');
    expect(jobsLink).toHaveClass('text-primary-600');
  });

  it('renders proper navigation structure', () => {
    renderHeader();
    
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    
    const container = nav.querySelector('.container');
    expect(container).toBeInTheDocument();
  });

  it('shows correct button styles', () => {
    renderHeader();
    
    const signInButton = screen.getByText('Sign In');
    const getStartedButton = screen.getByText('Get Started');
    
    expect(signInButton).toHaveClass('hover:text-primary-600');
    expect(getStartedButton).toHaveClass('bg-gradient-to-r');
  });

  it('handles theme switching correctly', () => {
    // Test light mode
    mockThemeContext.theme = 'light';
    renderHeader();
    
    const themeButton = screen.getByLabelText('Switch to dark mode');
    expect(themeButton).toBeInTheDocument();
    
    fireEvent.click(themeButton);
    expect(mockThemeContext.toggleTheme).toHaveBeenCalled();
  });
}); 