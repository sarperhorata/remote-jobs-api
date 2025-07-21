import React from 'react';

// Mock ThemeContext values
export const mockThemeContext = {
  theme: 'light' as 'light' | 'dark',
  toggleTheme: jest.fn(),
  applyTheme: jest.fn(),
};

// Mock ThemeContext
export const ThemeContext = React.createContext(mockThemeContext);

// Mock ThemeProvider component
export const ThemeProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  return (
    <ThemeContext.Provider value={mockThemeContext}>
      {children}
    </ThemeContext.Provider>
  );
};

// Mock useTheme hook
export const useTheme = () => {
  const context = React.useContext(ThemeContext);
  if (!context) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

// Reset mock functions before each test
export const resetThemeMock = () => {
  mockThemeContext.theme = 'light';
  mockThemeContext.toggleTheme.mockClear();
  mockThemeContext.applyTheme.mockClear();
};

// Set theme for testing
export const setMockTheme = (theme: 'light' | 'dark') => {
  mockThemeContext.theme = theme;
};