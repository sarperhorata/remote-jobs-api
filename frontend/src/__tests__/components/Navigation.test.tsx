import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Navigation from '../../components/Navigation';
import { useAuth } from '../../contexts/AuthContext';
import { useTheme } from '../../contexts/theme/ThemeContext';
import '@testing-library/jest-dom';

// Mock the contexts
jest.mock('../../contexts/AuthContext');
jest.mock('../../contexts/theme/ThemeContext');

const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;
const mockUseTheme = useTheme as jest.MockedFunction<typeof useTheme>;

const renderNavigation = () => {
  return render(
    <BrowserRouter>
      <Navigation />
    </BrowserRouter>
  );
};

describe('Navigation', () => {
  const mockLogout = jest.fn();
  const mockToggleTheme = jest.fn();

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
    });
  });

  it('renders the brand name', () => {
    renderNavigation();
    expect(screen.getByText('Remote Jobs')).toBeInTheDocument();
  });

  it('renders dashboard link', () => {
    renderNavigation();
    expect(screen.getByText('Dashboard')).toBeInTheDocument();
  });

  it('shows login and register when not authenticated', () => {
    renderNavigation();
    expect(screen.getByText('Login')).toBeInTheDocument();
    expect(screen.getByText('Register')).toBeInTheDocument();
  });

  it('shows logout when authenticated', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'John Doe', email: 'john@example.com', role: 'user' },
      login: jest.fn(),
      logout: mockLogout,
      signup: jest.fn(),
      refreshUser: jest.fn(),
      isLoading: false,
    });

    renderNavigation();
    expect(screen.getByText('Logout')).toBeInTheDocument();
    expect(screen.queryByText('Login')).not.toBeInTheDocument();
    expect(screen.queryByText('Register')).not.toBeInTheDocument();
  });

  it('calls logout when logout button is clicked', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'John Doe', email: 'john@example.com', role: 'user' },
      login: jest.fn(),
      logout: mockLogout,
      signup: jest.fn(),
      refreshUser: jest.fn(),
      isLoading: false,
    });

    renderNavigation();
    const logoutButton = screen.getByText('Logout');
    fireEvent.click(logoutButton);
    expect(mockLogout).toHaveBeenCalledTimes(1);
  });

  it('shows admin links when user is admin', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'Admin User', email: 'admin@example.com', role: 'admin' },
      login: jest.fn(),
      logout: mockLogout,
      signup: jest.fn(),
      refreshUser: jest.fn(),
      isLoading: false,
    });

    renderNavigation();
    expect(screen.getByText('Cronjobs')).toBeInTheDocument();
    expect(screen.getByText('External API Services')).toBeInTheDocument();
  });

  it('does not show admin links when user is not admin', () => {
    mockUseAuth.mockReturnValue({
      isAuthenticated: true,
      user: { id: '1', name: 'Regular User', email: 'user@example.com', role: 'user' },
      login: jest.fn(),
      logout: mockLogout,
      signup: jest.fn(),
      refreshUser: jest.fn(),
      isLoading: false,
    });

    renderNavigation();
    expect(screen.queryByText('Cronjobs')).not.toBeInTheDocument();
    expect(screen.queryByText('External API Services')).not.toBeInTheDocument();
  });

  it('shows dark mode icon when in light theme', () => {
    renderNavigation();
    const themeButtons = screen.getAllByLabelText('Switch to dark mode');
    expect(themeButtons.length).toBeGreaterThan(0);
  });

  it('shows light mode icon when in dark theme', () => {
    mockUseTheme.mockReturnValue({
      theme: 'dark',
      toggleTheme: mockToggleTheme,
    });

    renderNavigation();
    const themeButtons = screen.getAllByLabelText('Switch to light mode');
    expect(themeButtons.length).toBeGreaterThan(0);
  });

  it('calls toggleTheme when theme button is clicked', () => {
    renderNavigation();
    const themeButton = screen.getAllByLabelText('Switch to dark mode')[0];
    fireEvent.click(themeButton);
    expect(mockToggleTheme).toHaveBeenCalledTimes(1);
  });

  it('opens mobile menu when menu button is clicked', () => {
    renderNavigation();
    
    // Find the mobile menu button by its classes/structure
    const buttons = screen.getAllByRole('button');
    const menuButton = buttons.find(button => 
      button.classList.contains('inline-flex') && 
      button.querySelector('svg')
    );
    
    expect(menuButton).toBeTruthy();
    fireEvent.click(menuButton!);
    
    // In mobile menu, there should be additional links
    const dashboardLinks = screen.getAllByText('Dashboard');
    expect(dashboardLinks.length).toBeGreaterThan(1); // One in desktop, one in mobile
  });

  it('closes mobile menu when a link is clicked', () => {
    renderNavigation();
    
    // Find and click the mobile menu button
    const buttons = screen.getAllByRole('button');
    const menuButton = buttons.find(button => 
      button.classList.contains('inline-flex') && 
      button.querySelector('svg')
    );
    
    expect(menuButton).toBeTruthy();
    fireEvent.click(menuButton!);
    
    // Click a link in mobile menu
    const mobileLinks = screen.getAllByText('Dashboard');
    const mobileDashboardLink = mobileLinks[1]; // Second one is mobile
    fireEvent.click(mobileDashboardLink);
    
    // Mobile menu should close (no additional dashboard link)
    expect(screen.getAllByText('Dashboard')).toHaveLength(1);
  });

  it('renders without crashing', () => {
    expect(() => renderNavigation()).not.toThrow();
  });

  it('has correct navigation structure', () => {
    renderNavigation();
    
    const nav = screen.getByRole('navigation');
    expect(nav).toBeInTheDocument();
    expect(nav).toHaveClass('bg-gradient-to-r', 'from-blue-600', 'to-indigo-800');
  });
}); 