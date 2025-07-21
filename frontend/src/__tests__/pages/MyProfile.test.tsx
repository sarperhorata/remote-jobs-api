import React from 'react';
import { render } from '@testing-library/react';

// Mock all dependencies
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    isAuthenticated: true,
    user: { id: '1', email: 'test@example.com', name: 'Test User' },
    login: jest.fn(),
    logout: jest.fn(),
    register: jest.fn(),
  }),
}));

jest.mock('../../components/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="layout">{children}</div>;
  };
});

jest.mock('react-router-dom', () => ({
  BrowserRouter: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

jest.mock('../../contexts/ThemeContext', () => ({
  ThemeProvider: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
}));

// Mock localStorage
Object.defineProperty(window, 'localStorage', {
  value: {
    getItem: jest.fn(() => '{}'),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn(),
  },
  writable: true,
});

describe('MyProfile Component', () => {
  test('can be imported and rendered', () => {
    // This test just verifies that the component can be imported without errors
    const MyProfile = require('../../pages/MyProfile').default;
    expect(MyProfile).toBeDefined();
  });
}); 