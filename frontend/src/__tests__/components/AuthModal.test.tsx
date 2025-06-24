import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import AuthModal from '../../components/AuthModal';
import * as authService from '../../services/authService';

// Mock authService
jest.mock('../../services/authService');

const mockAuthService = authService as jest.Mocked<typeof authService>;

const defaultProps = {
  isOpen: true,
  onClose: jest.fn(),
  login: jest.fn(),
  signup: jest.fn()
};

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <AuthProvider>
        {component}
      </AuthProvider>
    </BrowserRouter>
  );
};

describe('AuthModal', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders login form when open', () => {
    renderWithProviders(<AuthModal {...defaultProps} />);
    
    expect(screen.getByText(/Sign In/i)).toBeInTheDocument();
    expect(screen.getByText(/Create Account/i)).toBeInTheDocument();
  });

  it('shows Google sign-in button', () => {
    renderWithProviders(<AuthModal {...defaultProps} />);
    
    expect(screen.getByText(/Sign in with Google/i)).toBeInTheDocument();
  });
}); 