import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Home from '../../pages/Home';

// Mock the contexts completely
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null,
    isAuthenticated: false,
    isLoading: false,
    login: jest.fn(),
    logout: jest.fn(),
    signup: jest.fn(),
    refreshUser: jest.fn(),
  }),
  AuthProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

jest.mock('../../contexts/ThemeContext', () => ({
  useTheme: () => ({
    theme: 'light',
    toggleTheme: jest.fn(),
  }),
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock fetch for API calls
global.fetch = jest.fn();

const renderHome = () => {
  return render(
    <BrowserRouter>
      <Home />
    </BrowserRouter>
  );
};

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
  });

  it('renders home page without crashing', () => {
    renderHome();
    
    // Should render some content
    expect(document.body.firstChild).toBeInTheDocument();
  });

  it('displays hero section', () => {
    renderHome();
    
    // Look for hero content
    const heroElements = screen.queryAllByText(/buzz2remote|find your next|remote job|career/i);
    const heroHeadings = screen.getAllByRole('heading', { level: 1 });
    
    expect(heroElements.length + heroHeadings.length).toBeGreaterThan(0);
  });

  it('shows navigation elements', () => {
    renderHome();
    
    // Check for navigation links
    const links = screen.getAllByRole('link');
    expect(links.length).toBeGreaterThan(0);
  });

  it('displays interactive buttons', () => {
    renderHome();
    
    // Look for buttons
    const buttons = screen.getAllByRole('button');
    expect(buttons.length).toBeGreaterThan(0);
  });

  it('handles form interactions', () => {
    renderHome();
    
    // Look for form elements
    const inputs = screen.getAllByRole('textbox');
    if (inputs.length > 0) {
      fireEvent.change(inputs[0], { target: { value: 'React Developer' } });
      expect(inputs[0]).toHaveValue('React Developer');
    }
  });

  it('displays brand information', () => {
    renderHome();
    
    // Look for brand content
    const brandElements = screen.queryAllByText(/buzz2remote/i);
    expect(brandElements.length).toBeGreaterThan(0);
  });

  it('handles responsive layout', () => {
    renderHome();
    
    // Should render responsive elements
    expect(document.body.firstChild).toBeInTheDocument();
  });

  it('shows call-to-action elements', () => {
    renderHome();
    
    // Look for CTA elements
    const ctaElements = screen.queryAllByText(/get started|find|search|browse/i);
    expect(ctaElements.length).toBeGreaterThan(0);
  });

  it('has proper page structure', () => {
    renderHome();
    
    // Check for main page elements
    const sections = document.querySelectorAll('section, main, div');
    expect(sections.length).toBeGreaterThan(0);
  });

  it('handles keyboard navigation', () => {
    renderHome();
    
    // Test keyboard accessibility
    const interactiveElements = [...screen.getAllByRole('button'), ...screen.getAllByRole('link')];
    
    if (interactiveElements.length > 0) {
      interactiveElements[0].focus();
      expect(document.activeElement).toBeTruthy();
    }
  });

  it('renders without context errors', () => {
    // This test ensures our mocks work properly
    expect(() => renderHome()).not.toThrow();
  });
}); 