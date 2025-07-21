import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { AuthProvider } from '../../contexts/AuthContext';
import Header from '../../components/Header';

// Mock the AuthContext
jest.mock('../../contexts/AuthContext', () => ({
  AuthContext: {
    Provider: ({ children, value }: { children: React.ReactNode; value: any }) => children,
  },
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
  }),
}));

// Helper function to render with providers
const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          {component}
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Header Component', () => {
  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
  });

  it('renders header without crashing', () => {
    renderWithProviders(<Header />);
    
    // Check if header is rendered
    expect(screen.getByRole('banner')).toBeInTheDocument();
  });

  it('displays logo and navigation', () => {
    renderWithProviders(<Header />);
    
    // Check for logo
    expect(screen.getByText(/Buzz2Remote/i)).toBeInTheDocument();
    
    // Check for navigation items that actually exist
    expect(screen.getByText(/Browse Jobs/i)).toBeInTheDocument();
    expect(screen.getByText(/Companies/i)).toBeInTheDocument();
    expect(screen.getByText(/Pricing/i)).toBeInTheDocument();
  });

  it('shows sign in button when user is not authenticated', () => {
    renderWithProviders(<Header />);
    
    // Check for sign in button
    expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
  });

  it('has theme toggle button', () => {
    renderWithProviders(<Header />);
    
    // Check for theme toggle button (it has a title attribute)
    const themeButton = screen.getByTitle(/Switch to Dark Mode/i);
    expect(themeButton).toBeInTheDocument();
  });

  it('has mobile menu button', () => {
    renderWithProviders(<Header />);
    
    // Check for mobile menu button (it's a button with menu icon)
    const menuButton = screen.getByRole('button', { name: '' }); // Menu button without text
    expect(menuButton).toBeInTheDocument();
  });

  it('has get started button', () => {
    renderWithProviders(<Header />);
    
    // Check for get started button
    expect(screen.getByText(/Get Started/i)).toBeInTheDocument();
  });

  it('has all navigation links', () => {
    renderWithProviders(<Header />);
    
    // Check for all navigation links that should be present
    expect(screen.getByText(/Browse Jobs/i)).toBeInTheDocument();
    expect(screen.getByText(/Companies/i)).toBeInTheDocument();
    expect(screen.getByText(/Pricing/i)).toBeInTheDocument();
    expect(screen.getByText(/Remote Tips/i)).toBeInTheDocument();
    expect(screen.getByText(/Career Tips/i)).toBeInTheDocument();
    expect(screen.getByText(/Remote Hints/i)).toBeInTheDocument();
    expect(screen.getByText(/Salary Guide/i)).toBeInTheDocument();
    expect(screen.getByText(/About/i)).toBeInTheDocument();
    expect(screen.getByText(/Contact/i)).toBeInTheDocument();
  });

  it('has proper logo structure', () => {
    renderWithProviders(<Header />);
    
    // Check for logo elements
    expect(screen.getByText(/Buzz2Remote/i)).toBeInTheDocument();
    expect(screen.getByText(/Find Remote Jobs/i)).toBeInTheDocument();
    expect(screen.getByText(/🐝/)).toBeInTheDocument(); // Bee emoji
  });
});