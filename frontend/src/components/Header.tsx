import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';
import AuthModal from './AuthModal';
import { Menu, X, User, LogOut, Settings, Heart, FileText, Bell, Sun, Moon } from 'lucide-react';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [unreadNotifications, setUnreadNotifications] = useState(0);
  const navigate = useNavigate();

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handleClickOutside = () => {
      setShowProfileDropdown(false);
      setIsMobileMenuOpen(false);
    };

    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  // Load unread notifications count
  useEffect(() => {
    if (user) {
      loadUnreadCount();
    }
  }, [user]);

  const loadUnreadCount = async () => {
    try {
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/notifications/unread-count`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setUnreadNotifications(data.unread_count);
      }
    } catch (error) {
      // Silently handle errors to avoid console spam
      console.debug('Notification count not available:', error);
    }
  };

  const navigation = [
    { name: 'Browse Jobs', href: '/jobs/search' },
    { name: 'Companies', href: '/companies' },
    { name: 'Pricing', href: '/pricing' },
    { name: 'Remote Tips', href: '/remote-tips' },
    { name: 'Career Tips', href: '/career-tips' },
    { name: 'Remote Hints', href: '/remote-hints' },
    { name: 'Salary Guide', href: '/salary-guide' },
    { name: 'About', href: '/about' },
    { name: 'Contact', href: '/contact' },
  ];

  const handleProfileAction = (action: string) => {
    setShowProfileDropdown(false);
    
    switch (action) {
      case 'profile':
        navigate('/my-profile');
        break;
      case 'saved':
        navigate('/favorites');
        break;
      case 'applications':
        navigate('/my-applications');
        break;
      case 'notifications':
        navigate('/notifications');
        break;
      case 'settings':
        navigate('/settings');
        break;
      case 'logout':
        logout();
        navigate('/');
        break;
    }
  };

  return (
    <>
      <header className="relative z-50">
        {/* Glassmorphism navbar */}
        <nav className="fixed top-0 left-0 right-0 z-50 bg-white/10 backdrop-blur-md border-b border-white/20 shadow-lg">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between items-center h-16">
              {/* Logo */}
              <Link to="/" className="flex items-center space-x-2 group">
                <div className="relative">
                  <div className="w-10 h-10 rounded-xl border-2 border-yellow-400/80 flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-200 bg-white/20 dark:bg-gray-800/20 backdrop-blur-sm">
                    <span className="text-yellow-400 font-bold text-lg animate-pulse drop-shadow-[0_1px_4px_rgba(251,191,36,0.7)]">🐝</span>
                  </div>
                  <div className="absolute -inset-1 bg-gradient-to-r from-yellow-400/40 to-orange-500/30 rounded-xl blur opacity-30 group-hover:opacity-50 transition-opacity duration-200 pointer-events-none"></div>
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-lg bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                    Buzz2Remote
                  </span>
                  <span
                    className={
                      theme === 'dark'
                        ? 'text-white/70 -mt-1 text-xs'
                        : 'text-gray-800 -mt-1 font-medium text-xs'
                    }
                  >
                    Find Remote Jobs 🚀
                  </span>
                </div>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-6">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition-all duration-200 font-medium"
                  >
                    {item.name}
                  </Link>
                ))}
              </div>

              {/* Right side */}
              <div className="flex items-center space-x-4">
                {/* Theme Toggle */}
                <button
                  onClick={toggleTheme}
                  className="p-2 text-white/90 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200"
                  title={theme === 'dark' ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
                >
                  {theme === 'dark' ? (
                    <Sun className="w-5 h-5" />
                  ) : (
                    <Moon className="w-5 h-5" />
                  )}
                </button>

                {user ? (
                  /* User Menu */
                  <div className="flex items-center space-x-3">
                    {/* Notifications */}
                    <Link
                      to="/notifications"
                      className="relative p-2 text-white/90 hover:text-white hover:bg-white/10 rounded-lg transition-all duration-200"
                    >
                      <Bell className="w-5 h-5" />
                      {unreadNotifications > 0 && (
                        <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                          {unreadNotifications > 99 ? '99+' : unreadNotifications}
                        </span>
                      )}
                    </Link>

                    <div className="relative">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          setShowProfileDropdown(!showProfileDropdown);
                        }}
                        className="flex items-center space-x-2 bg-white/10 backdrop-blur-sm border border-white/20 rounded-lg px-3 py-2 text-white hover:bg-white/20 transition-all duration-200"
                      >
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-500 rounded-full flex items-center justify-center">
                          <User className="w-4 h-4 text-white" />
                        </div>
                        <span className="font-medium hidden md:inline">{user.email?.split('@')[0] || 'User'}</span>
                      </button>

                      {/* Dropdown Menu */}
                      {showProfileDropdown && (
                        <div className="absolute right-0 mt-2 w-56 bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg rounded-xl shadow-xl border border-white/20 dark:border-gray-700/50 py-2 z-50">
                          <div className="px-4 py-2 border-b border-gray-200/50 dark:border-gray-600/50">
                            <p className="text-sm font-medium text-gray-900 dark:text-white">{user.email}</p>
                            <p className="text-xs text-gray-500 dark:text-gray-400">Free Plan</p>
                          </div>
                          
                          <button
                            onClick={() => handleProfileAction('profile')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                          >
                            <User className="w-4 h-4 mr-3 text-gray-600 dark:text-gray-300" />
                            My Profile
                          </button>
                          
                          <button
                            onClick={() => handleProfileAction('saved')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                          >
                            <Heart className="w-4 h-4 mr-3 text-gray-600 dark:text-gray-300" />
                            Saved Jobs
                          </button>
                          
                          <button
                            onClick={() => handleProfileAction('applications')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                          >
                            <FileText className="w-4 h-4 mr-3 text-gray-600 dark:text-gray-300" />
                            Applications
                          </button>
                          
                          <button
                            onClick={() => handleProfileAction('notifications')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                          >
                            <Bell className="w-4 h-4 mr-3 text-gray-600 dark:text-gray-300" />
                            Notifications
                            {unreadNotifications > 0 && (
                              <span className="ml-auto bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                                {unreadNotifications > 99 ? '99+' : unreadNotifications}
                              </span>
                            )}
                          </button>
                          
                          <button
                            onClick={() => handleProfileAction('settings')}
                            className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors"
                          >
                            <Settings className="w-4 h-4 mr-3 text-gray-600 dark:text-gray-300" />
                            Settings
                          </button>
                          
                          <div className="border-t border-gray-200/50 dark:border-gray-600/50 mt-2 pt-2">
                            <button
                              onClick={() => handleProfileAction('logout')}
                              className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                            >
                              <LogOut className="w-4 h-4 mr-3 text-red-600 dark:text-red-400" />
                              Sign Out
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                ) : (
                  /* Login/Register Buttons */
                  <div className="flex items-center space-x-3">
                    <button
                      onClick={() => setShowAuthModal(true)}
                      className="text-white/90 hover:text-white font-medium px-4 py-2 transition-colors"
                    >
                      Sign In
                    </button>
                    <button
                      onClick={() => setShowAuthModal(true)}
                      className="bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white font-medium px-4 py-2 rounded-lg transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
                    >
                      Get Started
                    </button>
                  </div>
                )}

                {/* Mobile menu button */}
                <button
                  onClick={(e) => {
                    e.stopPropagation();
                    setIsMobileMenuOpen(!isMobileMenuOpen);
                  }}
                  className="md:hidden text-white p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  {isMobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
                </button>
              </div>
            </div>
          </div>

          {/* Mobile Navigation */}
          {isMobileMenuOpen && (
            <div className="md:hidden bg-white/10 backdrop-blur-lg border-t border-white/20">
              <div className="px-4 py-3 space-y-2">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="block text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition-colors"
                  >
                    {item.name}
                  </Link>
                ))}
                
                {user && (
                  <>
                    <div className="border-t border-white/20 pt-2 mt-2">
                      <Link
                        to="/notifications"
                        className="flex items-center justify-between text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition-colors"
                      >
                        <span>Notifications</span>
                        {unreadNotifications > 0 && (
                          <span className="bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-medium">
                            {unreadNotifications > 99 ? '99+' : unreadNotifications}
                          </span>
                        )}
                      </Link>
                    </div>
                  </>
                )}
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Auth Modal */}
      <AuthModal isOpen={showAuthModal} onClose={() => setShowAuthModal(false)} />
    </>
  );
};

export default Header; 