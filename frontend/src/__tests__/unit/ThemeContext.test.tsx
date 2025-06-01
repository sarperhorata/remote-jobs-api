import React from 'react';
import { renderHook, act } from '@testing-library/react';
import { ThemeProvider, useTheme } from '../../contexts/ThemeContext';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

// Mock document methods
Object.defineProperty(document, 'documentElement', {
  value: {
    classList: {
      add: jest.fn(),
      remove: jest.fn(),
      contains: jest.fn(),
    },
    setAttribute: jest.fn(),
  },
  writable: true,
});

describe('ThemeContext', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  const wrapper = ({ children }: { children: React.ReactNode }) => (
    <ThemeProvider>{children}</ThemeProvider>
  );

  it('should provide initial theme state as light', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    expect(result.current.theme).toBe('light');
  });

  it('should load theme from localStorage', () => {
    localStorageMock.getItem.mockReturnValue('dark');
    
    const { result } = renderHook(() => useTheme(), { wrapper });

    expect(result.current.theme).toBe('dark');
  });

  it('should toggle theme from light to dark', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).toBe('dark');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');
  });

  it('should toggle theme from dark to light', () => {
    localStorageMock.getItem.mockReturnValue('dark');
    
    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.toggleTheme();
    });

    expect(result.current.theme).toBe('light');
    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
  });

  it('should apply theme to document', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.applyTheme();
    });

    const docElement = document.documentElement;
    expect(docElement.classList.remove).toHaveBeenCalledWith('dark');
    expect(docElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
  });

  it('should apply dark theme to document', () => {
    localStorageMock.getItem.mockReturnValue('dark');
    
    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.applyTheme();
    });

    const docElement = document.documentElement;
    expect(docElement.classList.add).toHaveBeenCalledWith('dark');
    expect(docElement.setAttribute).toHaveBeenCalledWith('data-theme', 'dark');
  });

  it('should persist theme changes to localStorage', () => {
    const { result } = renderHook(() => useTheme(), { wrapper });

    act(() => {
      result.current.toggleTheme();
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'dark');

    act(() => {
      result.current.toggleTheme();
    });

    expect(localStorageMock.setItem).toHaveBeenCalledWith('theme', 'light');
  });

  it('should handle invalid localStorage values', () => {
    localStorageMock.getItem.mockReturnValue('invalid-theme');
    
    const { result } = renderHook(() => useTheme(), { wrapper });

    expect(result.current.theme).toBe('light'); // Should fallback to light
  });

  it('should handle localStorage errors gracefully', () => {
    localStorageMock.getItem.mockImplementation(() => {
      throw new Error('Storage error');
    });
    
    const { result } = renderHook(() => useTheme(), { wrapper });

    expect(result.current.theme).toBe('light'); // Should fallback to light
  });

  it('should apply theme on initialization', () => {
    renderHook(() => useTheme(), { wrapper });

    const docElement = document.documentElement;
    expect(docElement.setAttribute).toHaveBeenCalledWith('data-theme', 'light');
  });
}); 