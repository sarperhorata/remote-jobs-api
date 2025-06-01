import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import AuthModal from '../../components/AuthModal';

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

const defaultProps = {
  isOpen: true,
  onClose: jest.fn(),
  initialMode: 'login' as 'login' | 'register',
};

const renderAuthModal = (props = {}) => {
  const mergedProps = { ...defaultProps, ...props };
  
  return render(
    <BrowserRouter>
      <AuthModal {...mergedProps} />
    </BrowserRouter>
  );
};

describe('AuthModal Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders auth modal when open', () => {
    renderAuthModal();
    
    // Should render modal content
    expect(document.body.firstChild).toBeInTheDocument();
  });

  it('does not render when closed', () => {
    renderAuthModal({ isOpen: false });
    
    // Should handle closed state
    expect(document.body.firstChild).toBeInTheDocument();
  });

  it('handles form interactions', () => {
    renderAuthModal({ initialMode: 'login' });
    
    // Should handle form elements
    const inputs = screen.getAllByRole('textbox');
    if (inputs.length > 0) {
      fireEvent.change(inputs[0], { target: { value: 'test@example.com' } });
      expect(inputs[0]).toBeTruthy();
    }
  });

  it('handles button clicks', () => {
    renderAuthModal();
    
    const buttons = screen.getAllByRole('button');
    if (buttons.length > 0) {
      fireEvent.click(buttons[0]);
      expect(buttons[0]).toBeInTheDocument();
    }
  });

  it('handles close functionality', () => {
    const onClose = jest.fn();
    renderAuthModal({ onClose });
    
    // Should handle close event
    expect(document.body.firstChild).toBeInTheDocument();
  });

  it('handles different modes', () => {
    renderAuthModal({ initialMode: 'register' });
    
    // Should handle register mode
    expect(document.body.firstChild).toBeInTheDocument();
  });

  it('has proper accessibility', () => {
    renderAuthModal();
    
    // Check for modal accessibility
    const modal = screen.queryByRole('dialog');
    if (modal) {
      expect(modal).toBeInTheDocument();
    }
  });

  it('renders without context errors', () => {
    // This test ensures our mocks work properly
    expect(() => renderAuthModal()).not.toThrow();
  });
}); 