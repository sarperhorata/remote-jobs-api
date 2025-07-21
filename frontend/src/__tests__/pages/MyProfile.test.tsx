import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import { AuthProvider } from '../../contexts/AuthContext';
import MyProfile from '../../pages/MyProfile';

// Mock the auth context
jest.mock('../../contexts/AuthContext', () => ({
  AuthContext: {
    Provider: ({ children, value }: { children: React.ReactNode; value: any }) => children,
  },
  AuthProvider: ({ children }: { children: React.ReactNode }) => children,
  useAuth: () => ({
    isAuthenticated: true,
    user: {
      id: '1',
      email: 'test@example.com',
      name: 'Test User'
    },
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
  }),
}));

// Mock the Layout component
jest.mock('../../components/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="layout">{children}</div>;
  };
});

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(() => '{}'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

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

describe('MyProfile Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test('renders without crashing', () => {
    renderWithProviders(<MyProfile />);
    
    // Check if the component renders without throwing errors
    expect(screen.getByTestId('layout')).toBeInTheDocument();
  });

  test('displays user profile information', () => {
    renderWithProviders(<MyProfile />);
    
    // Check for basic profile elements
    expect(screen.getByText(/my profile/i)).toBeInTheDocument();
  });
}); 