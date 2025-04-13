import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

type ThemeMode = 'light' | 'dark';

interface ThemeContextType {
  theme: ThemeMode;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: ReactNode;
}

export function ThemeProvider({ children }: ThemeProviderProps) {
  const [theme, setTheme] = useState<ThemeMode>('light');

  // Konum ve gün batımı saati kontrolü için yardımcı fonksiyon
  const checkIfAfterSunset = () => {
    const now = new Date();
    const hours = now.getHours();
    
    // Basit bir kontrol - saat 19:00'dan sonra gece modu
    // Gerçek uygulamalarda coğrafi konum API'leri kullanılabilir
    return hours >= 19 || hours < 6;
  };

  // Kullanıcı tercihlerini localStorage'dan alma
  useEffect(() => {
    const storedTheme = localStorage.getItem('theme');
    
    if (storedTheme) {
      setTheme(storedTheme as ThemeMode);
    } else {
      // Depolanan tema yoksa saat kontrolü yapılır
      const shouldUseDarkMode = checkIfAfterSunset();
      setTheme(shouldUseDarkMode ? 'dark' : 'light');
    }
  }, []);

  // Tema değiştiğinde body sınıfını ve CSS değişkenlerini güncelle
  useEffect(() => {
    const root = document.documentElement;
    
    if (theme === 'dark') {
      document.body.classList.add('dark-mode');
      root.style.setProperty('--bg-color', '#121212');
      root.style.setProperty('--text-color', '#e0e0e0');
      root.style.setProperty('--card-bg', '#1e1e1e');
      root.style.setProperty('--border-color', '#333');
      root.style.setProperty('--primary-color', '#4f8fc0');
      root.style.setProperty('--secondary-bg', '#252525');
    } else {
      document.body.classList.remove('dark-mode');
      root.style.setProperty('--bg-color', '#f5f7fa');
      root.style.setProperty('--text-color', '#333');
      root.style.setProperty('--card-bg', '#fff');
      root.style.setProperty('--border-color', '#e0e0e0');
      root.style.setProperty('--primary-color', '#3b82f6');
      root.style.setProperty('--secondary-bg', '#f0f2f5');
    }

    // Kullanıcı tercihini kaydet
    localStorage.setItem('theme', theme);
  }, [theme]);

  // Tema değiştirme fonksiyonu
  const toggleTheme = () => {
    setTheme(prevTheme => (prevTheme === 'light' ? 'dark' : 'light'));
  };

  return (
    <ThemeContext.Provider value={{ theme, toggleTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}

// Hook for using the theme context
export function useTheme() {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
} 