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

// Helper function to get system theme preference
const getSystemTheme = (): 'light' | 'dark' => {
  if (typeof window !== 'undefined' && window.matchMedia) {
    try {
      // Check if system prefers dark mode
      const systemPrefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      
      // Also check time of day for auto dark mode (20:00 - 07:00)
      const now = new Date();
      const hour = now.getHours();
      const isNightTime = hour >= 20 || hour < 7;
      
      return systemPrefersDark || isNightTime ? 'dark' : 'light';
    } catch (error) {
      // Fallback for test environments or when matchMedia fails
      return 'light';
    }
  }
  return 'light';
};

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [theme, setTheme] = useState<'light' | 'dark'>(() => {
    // Initialize theme from localStorage or system preference
    try {
      const savedTheme = localStorage.getItem('theme');
      if (savedTheme === 'light' || savedTheme === 'dark') {
        return savedTheme;
      }
      // If no saved theme, use system preference + time-based logic
      return getSystemTheme();
    } catch (error) {
      return getSystemTheme();
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

  // Auto theme check based on time
  useEffect(() => {
    const checkAutoTheme = () => {
      try {
        const savedTheme = localStorage.getItem('theme');
        // Only auto-switch if user hasn't manually set a preference
        if (!savedTheme) {
          const autoTheme = getSystemTheme();
          if (autoTheme !== theme) {
            setTheme(autoTheme);
          }
        }
      } catch (error) {
        console.warn('Could not check auto theme:', error);
      }
    };

    // Check immediately
    checkAutoTheme();

    // Check every hour for time-based theme changes
    const interval = setInterval(checkAutoTheme, 60 * 60 * 1000); // 1 hour

    return () => clearInterval(interval);
  }, [theme]);

  // Listen for system theme changes
  useEffect(() => {
    if (typeof window !== 'undefined' && window.matchMedia) {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      
      const handleSystemThemeChange = (e: MediaQueryListEvent) => {
        // Always apply system theme changes - remove localStorage override logic
        const systemTheme = e.matches ? 'dark' : 'light';
        setTheme(systemTheme);
        
        // Update localStorage to reflect system change
        try {
          localStorage.setItem('theme', systemTheme);
        } catch (error) {
          console.warn('Could not save theme to localStorage:', error);
        }
      };

      // Add listener for system theme changes
      if (mediaQuery && mediaQuery.addEventListener) {
        mediaQuery.addEventListener('change', handleSystemThemeChange);
        
        // Also check initial system preference
        const initialSystemTheme = mediaQuery.matches ? 'dark' : 'light';
        if (theme !== initialSystemTheme) {
          setTheme(initialSystemTheme);
          try {
            localStorage.setItem('theme', initialSystemTheme);
          } catch (error) {
            console.warn('Could not save initial theme to localStorage:', error);
          }
        }
      } else if (mediaQuery && mediaQuery.addListener) {
        // Fallback for older browsers
        mediaQuery.addListener(handleSystemThemeChange);
      }

      return () => {
        if (mediaQuery && mediaQuery.removeEventListener) {
          mediaQuery.removeEventListener('change', handleSystemThemeChange);
        } else if (mediaQuery && mediaQuery.removeListener) {
          // Fallback for older browsers
          mediaQuery.removeListener(handleSystemThemeChange);
        }
      };
    }
  }, [theme]);

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