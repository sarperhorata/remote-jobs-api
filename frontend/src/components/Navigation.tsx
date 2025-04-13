import React, { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/theme/ThemeContext';

const Navigation: React.FC = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const location = useLocation();

  const toggleMenu = () => {
    setIsMenuOpen(!isMenuOpen);
  };

  const isActive = (path: string) => {
    return location.pathname === path;
  };

  return (
    <nav className="bg-gradient-to-r from-blue-600 to-indigo-800 text-white">
      <div className="container mx-auto px-4">
        <div className="flex justify-between h-16">
          {/* Logo and Main Links */}
          <div className="flex space-x-4">
            <Link to="/" className="flex items-center">
              <span className="text-xl font-bold">Remote Jobs</span>
            </Link>
            <div className="hidden md:flex items-center space-x-4">
              <Link
                to="/jobs"
                className={`px-3 py-2 rounded-md ${
                  isActive('/jobs') ? 'bg-blue-700' : 'hover:bg-blue-700'
                }`}
              >
                Jobs
              </Link>
              <Link
                to="/dashboard"
                className={`px-3 py-2 rounded-md ${
                  isActive('/dashboard') ? 'bg-blue-700' : 'hover:bg-blue-700'
                }`}
              >
                Dashboard
              </Link>
              <Link
                to="/status"
                className={`px-3 py-2 rounded-md ${
                  isActive('/status') ? 'bg-blue-700' : 'hover:bg-blue-700'
                }`}
              >
                Status
              </Link>
            </div>
          </div>

          {/* Right Side Items */}
          <div className="hidden md:flex items-center space-x-4">
            {/* Dark/Light Mode Toggle */}
            <button 
              onClick={toggleTheme} 
              className="theme-toggle px-3 py-2 rounded-md text-white hover:bg-blue-700"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                  </svg>
                  <span className="hidden lg:inline">Light Mode</span>
                </>
              ) : (
                <>
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                    <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                  </svg>
                  <span className="hidden lg:inline">Dark Mode</span>
                </>
              )}
            </button>

            {/* Profile or Login */}
            {user ? (
              <div className="relative">
                <Link
                  to="/profile"
                  className={`flex items-center px-3 py-2 rounded-md ${
                    isActive('/profile') ? 'bg-blue-700' : 'hover:bg-blue-700'
                  }`}
                >
                  <div className="mr-2 h-8 w-8 rounded-full overflow-hidden bg-gray-200">
                    {user.profilePicture ? (
                      <img
                        src={user.profilePicture}
                        alt={user.name}
                        className="h-full w-full object-cover"
                      />
                    ) : (
                      <div className="h-full w-full flex items-center justify-center bg-blue-500 text-white">
                        {user.name.charAt(0)}
                      </div>
                    )}
                  </div>
                  <span>Profile</span>
                </Link>
              </div>
            ) : (
              <Link
                to="/login"
                className="px-3 py-2 rounded-md hover:bg-blue-700"
              >
                Login
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <div className="flex items-center md:hidden">
            <button 
              onClick={toggleTheme} 
              className="px-2 py-1 mr-2 rounded-md text-white"
              aria-label={theme === 'dark' ? 'Switch to light mode' : 'Switch to dark mode'}
            >
              {theme === 'dark' ? (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 8a4 4 0 11-8 0 4 4 0 018 0zm-.464 4.95l.707.707a1 1 0 001.414-1.414l-.707-.707a1 1 0 00-1.414 1.414zm2.12-10.607a1 1 0 010 1.414l-.706.707a1 1 0 11-1.414-1.414l.707-.707a1 1 0 011.414 0zM17 11a1 1 0 100-2h-1a1 1 0 100 2h1zm-7 4a1 1 0 011 1v1a1 1 0 11-2 0v-1a1 1 0 011-1zM5.05 6.464A1 1 0 106.465 5.05l-.708-.707a1 1 0 00-1.414 1.414l.707.707zm1.414 8.486l-.707.707a1 1 0 01-1.414-1.414l.707-.707a1 1 0 011.414 1.414zM4 11a1 1 0 100-2H3a1 1 0 000 2h1z" clipRule="evenodd" />
                </svg>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
              )}
            </button>
            <button
              onClick={toggleMenu}
              className="inline-flex items-center justify-center p-2 rounded-md text-white hover:bg-blue-700 focus:outline-none"
            >
              <svg
                className="h-6 w-6"
                xmlns="http://www.w3.org/2000/svg"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                {isMenuOpen ? (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M6 18L18 6M6 6l12 12"
                  />
                ) : (
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={2}
                    d="M4 6h16M4 12h16M4 18h16"
                  />
                )}
              </svg>
            </button>
          </div>
        </div>
      </div>

      {/* Mobile Menu */}
      {isMenuOpen && (
        <div className="md:hidden">
          <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3">
            <Link
              to="/jobs"
              className={`block px-3 py-2 rounded-md ${
                isActive('/jobs') ? 'bg-blue-700' : 'hover:bg-blue-700'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Jobs
            </Link>
            <Link
              to="/dashboard"
              className={`block px-3 py-2 rounded-md ${
                isActive('/dashboard') ? 'bg-blue-700' : 'hover:bg-blue-700'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Dashboard
            </Link>
            <Link
              to="/status"
              className={`block px-3 py-2 rounded-md ${
                isActive('/status') ? 'bg-blue-700' : 'hover:bg-blue-700'
              }`}
              onClick={() => setIsMenuOpen(false)}
            >
              Status
            </Link>
            {user ? (
              <Link
                to="/profile"
                className={`block px-3 py-2 rounded-md ${
                  isActive('/profile') ? 'bg-blue-700' : 'hover:bg-blue-700'
                }`}
                onClick={() => setIsMenuOpen(false)}
              >
                Profile
              </Link>
            ) : (
              <Link
                to="/login"
                className="block px-3 py-2 rounded-md hover:bg-blue-700"
                onClick={() => setIsMenuOpen(false)}
              >
                Login
              </Link>
            )}
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navigation; 