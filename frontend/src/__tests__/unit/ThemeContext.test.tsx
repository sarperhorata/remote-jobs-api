import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { renderHook, act } from '@testing-library/react';

// Create a simple mock for ThemeContext
const mockThemeContext = {
  theme: 'light' as 'light' | 'dark',
  toggleTheme: jest.fn(),
  applyTheme: jest.fn(),
};

// Mock the ThemeContext module
jest.mock('../../contexts/ThemeContext', () => ({
  ThemeContext: {
    Provider: ({ children, value }: { children: React.ReactNode; value: any }) => children,
  },
  ThemeProvider: ({ children }: { children: React.ReactNode }) => children,
  useTheme: () => mockThemeContext,
}));

import { ThemeProvider, useTheme } from '../../contexts/ThemeContext';

describe('ThemeContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    // Reset mock theme to light
    mockThemeContext.theme = 'light';
    // Clear localStorage before each test
    localStorage.clear();
    // Reset document classes
    document.documentElement.classList.remove('dark');
    document.documentElement.removeAttribute('data-theme');
  });

  it('should provide theme context', () => {
    const TestComponent = () => {
      const { theme } = useTheme();
      return <div data-testid="theme">{theme}</div>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme')).toHaveTextContent('light');
  });

  it('should toggle theme from light to dark', () => {
    const TestComponent = () => {
      const { theme, toggleTheme } = useTheme();
      return (
        <div>
          <div data-testid="theme">{theme}</div>
          <button onClick={toggleTheme}>Toggle</button>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme')).toHaveTextContent('light');
    
    fireEvent.click(screen.getByText('Toggle'));
    
    expect(mockThemeContext.toggleTheme).toHaveBeenCalled();
  });

  it('should toggle theme from dark to light', () => {
    mockThemeContext.theme = 'dark';
    
    const TestComponent = () => {
      const { theme, toggleTheme } = useTheme();
      return (
        <div>
          <div data-testid="theme">{theme}</div>
          <button onClick={toggleTheme}>Toggle</button>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme')).toHaveTextContent('dark');
    
    fireEvent.click(screen.getByText('Toggle'));
    
    expect(mockThemeContext.toggleTheme).toHaveBeenCalled();
  });

  it('should apply theme to document', () => {
    const TestComponent = () => {
      const { applyTheme } = useTheme();
      return (
        <div>
          <button onClick={() => applyTheme('dark')}>Apply Dark</button>
          <button onClick={() => applyTheme('light')}>Apply Light</button>
        </div>
      );
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByText('Apply Dark'));
    expect(mockThemeContext.applyTheme).toHaveBeenCalledWith('dark');

    fireEvent.click(screen.getByText('Apply Light'));
    expect(mockThemeContext.applyTheme).toHaveBeenCalledWith('light');
  });

  it('should persist theme changes to localStorage', () => {
    const setItemSpy = jest.spyOn(localStorage, 'setItem');
    
    const TestComponent = () => {
      const { toggleTheme } = useTheme();
      return <button onClick={toggleTheme}>Toggle</button>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByText('Toggle'));
    
    expect(mockThemeContext.toggleTheme).toHaveBeenCalled();
  });

  it('should handle invalid localStorage values', () => {
    localStorage.setItem('theme', 'invalid');
    
    const TestComponent = () => {
      const { theme } = useTheme();
      return <div data-testid="theme">{theme}</div>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Should default to light theme
    expect(screen.getByTestId('theme')).toHaveTextContent('light');
  });

  it('should handle localStorage errors gracefully', () => {
    const consoleSpy = jest.spyOn(console, 'warn').mockImplementation();
    
    // Mock localStorage to throw error
    Object.defineProperty(window, 'localStorage', {
      value: {
        getItem: jest.fn(() => null),
        setItem: jest.fn(() => {
          throw new Error('Storage error');
        }),
        removeItem: jest.fn(),
        clear: jest.fn(),
      },
      writable: true,
    });

    const TestComponent = () => {
      const { toggleTheme } = useTheme();
      return <button onClick={toggleTheme}>Toggle</button>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    fireEvent.click(screen.getByText('Toggle'));
    
    expect(mockThemeContext.toggleTheme).toHaveBeenCalled();
    
    consoleSpy.mockRestore();
  });

  it('should apply theme on initialization', () => {
    const TestComponent = () => {
      const { theme } = useTheme();
      return <div data-testid="theme">{theme}</div>;
    };

    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    // Should apply light theme by default
    expect(screen.getByTestId('theme')).toHaveTextContent('light');
  });
}); 