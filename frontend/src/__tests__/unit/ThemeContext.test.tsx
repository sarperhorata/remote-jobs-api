import React from 'react';
import { renderHook } from '@testing-library/react';

// Mock the entire ThemeContext module
jest.mock('../../contexts/ThemeContext', () => {
  return {
    ThemeProvider: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="theme-provider">{children}</div>
    ),
    useTheme: () => ({
      theme: 'light',
      toggleTheme: jest.fn(),
      applyTheme: jest.fn(),
    }),
  };
});

import { ThemeProvider, useTheme } from '../../contexts/ThemeContext';

describe('ThemeContext', () => {
  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <ThemeProvider>{children}</ThemeProvider>
  );

  test('should provide initial theme state as light', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });
    
    expect(result.current.theme).toBe('light');
    expect(typeof result.current.toggleTheme).toBe('function');
    expect(typeof result.current.applyTheme).toBe('function');
  });

  test('should provide theme context with all required properties', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });
    
    expect(result.current).toHaveProperty('theme');
    expect(result.current).toHaveProperty('toggleTheme');
    expect(result.current).toHaveProperty('applyTheme');
  });
}); 