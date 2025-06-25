import React, { createContext, useContext, useState, useEffect, useCallback, ReactNode } from 'react';

interface ThemeContextType {
  theme: 'light' | 'dark';
  toggleTheme: () => void;
  applyTheme: (theme?: 'light' | 'dark') => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

export const useTheme = () => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};

interface ThemeProviderProps {
  children: ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    // Initialize theme from localStorage
    try {
      const savedTheme = localStorage.getItem('theme');
      return (savedTheme === 'light' || savedTheme === 'dark') ? savedTheme : 'light';
    } catch (error) {
      return 'light';
    }
  });

  const applyTheme = useCallback((newTheme?: 'light' | 'dark') => {
    const themeToApply = newTheme || theme;
    
    // Apply to document
    const docElement = document.documentElement;
    if (themeToApply === 'dark') {
      docElement.classList.add('dark');
    } else {
      docElement.classList.remove('dark');
    }
    docElement.setAttribute('data-theme', themeToApply);
  }, [theme]);

  const toggleTheme = () => {
    const newTheme = theme === 'light' ? 'dark' : 'light';
    setTheme(newTheme);
    
    // Save to localStorage
    try {
      localStorage.setItem('theme', newTheme);
    } catch (error) {
      console.warn('Could not save theme to localStorage:', error);
    }
  };

  // Apply theme on mount and theme changes
  useEffect(() => {
    applyTheme(theme);
  }, [theme, applyTheme]);

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme, applyTheme }}>
      <div className={theme === 'dark' ? 'dark' : ''}>
        {children}
      </div>
    </ThemeContext.Provider>
  );
}; 