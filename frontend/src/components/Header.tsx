import React, { useState, useEffect, useRef } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useTheme } from '../contexts/ThemeContext';
import { useAuth, AuthContextType } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import { Sun, Moon, User, LogOut, FileText, Heart } from 'lucide-react';

const Header: React.FC = () => {
  const { theme, toggleTheme } = useTheme();
  const { user, isAuthenticated, logout }: AuthContextType = useAuth();
  const location = useLocation();
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState<'login' | 'register'>('login');
  const [isProfileMenuOpen, setProfileMenuOpen] = useState(false);
  const profileMenuRef = useRef<HTMLDivElement>(null);

  const isActive = (path: string) => location.pathname === path;

  // Auto-detect OS theme - commented out to allow manual control
  // useEffect(() => {
  //   const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
  //   applyTheme(mediaQuery.matches ? 'dark' : 'light');
  //   const handler = (e: MediaQueryListEvent) => applyTheme(e.matches ? 'dark' : 'light');
  //   mediaQuery.addEventListener('change', handler);
  //   return () => mediaQuery.removeEventListener('change', handler);
  // }, [applyTheme]);
  
  // Close profile menu on outside click
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (profileMenuRef.current && !profileMenuRef.current.contains(event.target as Node)) {
        setProfileMenuOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleSignInClick = () => {
    setAuthModalTab('login');
    setIsAuthModalOpen(true);
  };

  const handleGetStartedClick = () => {
    setAuthModalTab('register');
    setIsAuthModalOpen(true);
  };

  const handleLogout = () => {
    logout();
    setProfileMenuOpen(false);
  }

  return (
    <>
      <header className="bg-white dark:bg-gray-900 text-gray-800 dark:text-gray-200 py-3 shadow-sm border-b border-gray-200 dark:border-gray-800 sticky top-0 z-50">
        <div className="container mx-auto px-4">
          <nav className="flex items-center justify-between">
            <div className="flex items-center space-x-8">
              <Link to="/" className="text-2xl font-bold flex items-center gap-2 text-gray-900 dark:text-white">
                <span className="text-3xl">🐝</span>
                Buzz2Remote
              </Link>
              <div className="hidden md:flex space-x-6">
                <Link
                  to="/jobs/search"
                  className={`hover:text-yellow-500 dark:hover:text-yellow-400 ${
                    isActive('/jobs/search') ? 'font-semibold text-yellow-600 dark:text-yellow-400' : 'text-gray-600 dark:text-gray-300'
                  }`}
                >
                  Find Jobs
                </Link>
                {/* Add other links here if needed */}
              </div>
            </div>

            <div className="flex items-center space-x-4">
              <button
                onClick={toggleTheme}
                className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-500 dark:text-gray-400 transition-colors"
                aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
              >
                {theme === 'dark' ? (
                  <Sun className="h-5 w-5" />
                ) : (
                  <Moon className="h-5 w-5" />
                )}
              </button>

              {isAuthenticated && user ? (
                 <div className="relative" ref={profileMenuRef}>
                  <button 
                    onClick={() => setProfileMenuOpen(!isProfileMenuOpen)} 
                    className="flex items-center space-x-2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                  >
                    <div className="w-8 h-8 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-semibold text-sm shadow-md">
                      {user.name?.charAt(0)?.toUpperCase() || 'U'}
                    </div>
                    <span className="hidden sm:inline text-sm font-medium text-gray-700 dark:text-gray-300">{user.name}</span>
                  </button>

                  {isProfileMenuOpen && (
                    <div className="absolute right-0 mt-2 w-48 bg-white dark:bg-gray-800 rounded-md shadow-lg py-1 border dark:border-gray-700">
                      <div className="px-4 py-2 border-b dark:border-gray-700">
                        <p className="text-sm font-semibold text-gray-900 dark:text-white">{user.name}</p>
                        <p className="text-xs text-gray-500 dark:text-gray-400 truncate">{user.email}</p>
                      </div>
                      <Link to="/my-profile" className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                        <User className="w-4 h-4 mr-2" /> My Profile
                      </Link>
                      <Link to="/favorites" className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                        <Heart className="w-4 h-4 mr-2" /> My Favorites
                      </Link>
                      <Link to="/my-applications" className="flex items-center w-full text-left px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                        <FileText className="w-4 h-4 mr-2" /> My Applications
                      </Link>
                      <button
                        onClick={handleLogout}
                        className="flex items-center w-full text-left px-4 py-2 text-sm text-red-600 dark:text-red-500 hover:bg-gray-100 dark:hover:bg-gray-700"
                      >
                        <LogOut className="w-4 h-4 mr-2" /> Sign Out
                      </button>
                    </div>
                  )}
                 </div>
              ) : (
                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleSignInClick}
                    className="px-4 py-2 text-gray-700 dark:text-gray-300 hover:text-yellow-600 dark:hover:text-yellow-400 transition-colors text-sm font-medium"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={handleGetStartedClick}
                    className="px-4 py-2 bg-gradient-to-r from-orange-500 to-yellow-400 text-white rounded-md hover:from-orange-600 hover:to-yellow-500 transition-colors font-medium text-sm"
                  >
                    Get Started
                  </button>
                </div>
              )}
            </div>
          </nav>
        </div>
      </header>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
        defaultTab={authModalTab}
      />
    </>
  );
};

export default Header; 