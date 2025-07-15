import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import { Menu, X, User, LogOut, Settings, Heart, FileText } from 'lucide-react';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [showMobileMenu, setShowMobileMenu] = useState(false);
  const navigate = useNavigate();

  const navigation = [
    {
      name: 'Pricing',
      href: '/pricing'
    }
  ];

  const handleProfileAction = (action: string) => {
    setShowProfileDropdown(false);

    switch (action) {
      case 'profile':
        navigate('/profile');
        break;
      case 'saved':
        navigate('/saved-jobs');
        break;
      case 'applications':
        navigate('/applications');
        break;
      case 'settings':
        navigate('/settings');
        break;
      case 'logout':
        logout();
        navigate('/');
        break;
      default:
        break;
    }
  };

  const handleClickOutside = () => {
    setShowProfileDropdown(false);
    setShowMobileMenu(false);
  };

  useEffect(() => {
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, []);

  return (
    <header className="sticky top-0 z-50">
      <nav className="bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 border-b border-white/10 backdrop-blur-lg">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            {/* Logo */}
            <div className="flex items-center">
              <Link to="/" className="flex items-center">
                <div className="w-10 h-10 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center mr-2 shadow-lg">
                  <span className="text-2xl">🐝</span>
                </div>
                <div className="block">
                  <h1 className="text-xl md:text-2xl font-extrabold bg-gradient-to-r from-yellow-400 via-orange-400 to-pink-500 bg-clip-text text-transparent drop-shadow-lg tracking-tight flex items-center gap-1 select-none">
                    <span className="inline-block animate-float">🐝</span>
                    Buzz2Remote
                  </h1>
                  <p className="text-xs text-gray-300 -mt-1 font-medium tracking-wide hidden sm:block">Remote Jobs Hub</p>
                </div>
              </Link>
            </div>

            {/* Desktop Navigation */}
            <div className="hidden md:block">
              <div className="ml-10 flex items-baseline space-x-8">
                {navigation.map((item) => (
                  <Link
                    key={item.name}
                    to={item.href}
                    className="text-gray-300 hover:text-white px-3 py-2 rounded-md text-sm font-medium transition-colors duration-200 hover:bg-white/10"
                  >
                    {item.name}
                  </Link>
                ))}
              </div>
            </div>

            {/* Right side - Auth & Profile */}
            <div className="flex items-center space-x-4">
              {user ? (
                <>
                  {/* User Profile Dropdown */}
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
                      <div className="absolute right-0 mt-2 w-56 bg-white dark:bg-gray-800 backdrop-blur-lg rounded-xl shadow-xl border border-white/20 dark:border-gray-700 py-2 z-50">
                        <div className="px-4 py-2 border-b border-gray-200/50 dark:border-gray-600/50">
                          <p className="text-sm font-medium text-gray-900 dark:text-white">{user.email}</p>
                          <p className="text-xs text-gray-500 dark:text-gray-400">Free Plan</p>
                        </div>
                        
                        <button
                          onClick={() => handleProfileAction('profile')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          <User className="w-4 h-4 mr-3" />
                          My Profile
                        </button>
                        
                        <button
                          onClick={() => handleProfileAction('saved')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          <Heart className="w-4 h-4 mr-3" />
                          Saved Jobs
                        </button>
                        
                        <button
                          onClick={() => handleProfileAction('applications')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          <FileText className="w-4 h-4 mr-3" />
                          Applications
                        </button>
                        
                        <button
                          onClick={() => handleProfileAction('settings')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                        >
                          <Settings className="w-4 h-4 mr-3" />
                          Settings
                        </button>
                        
                        <div className="border-t border-gray-200/50 dark:border-gray-600/50 mt-2 pt-2">
                          <button
                            onClick={() => handleProfileAction('logout')}
                            className="flex items-center w-full px-4 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors"
                          >
                            <LogOut className="w-4 h-4 mr-3" />
                            Sign Out
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </>
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
                    onClick={() => navigate('/register')}
                    className="text-white/90 hover:text-white font-medium px-4 py-2 transition-colors"
                  >
                    Create Profile
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
                  setShowMobileMenu(!showMobileMenu);
                }}
                className="md:hidden text-white p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                {showMobileMenu ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
              </button>
            </div>
          </div>
        </div>

        {/* Mobile menu */}
        {showMobileMenu && (
          <div className="md:hidden">
            <div className="px-2 pt-2 pb-3 space-y-1 sm:px-3 bg-slate-800/90 backdrop-blur-lg border-t border-white/10">
              {navigation.map((item) => (
                <Link
                  key={item.name}
                  to={item.href}
                  className="text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 hover:bg-white/10"
                  onClick={() => setShowMobileMenu(false)}
                >
                  {item.name}
                </Link>
              ))}
              
              {!user && (
                <div className="pt-4 pb-3 border-t border-gray-600/50">
                  <button
                    onClick={() => {
                      setShowAuthModal(true);
                      setShowMobileMenu(false);
                    }}
                    className="w-full text-left text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 hover:bg-white/10"
                  >
                    Sign In
                  </button>
                  <button
                    onClick={() => {
                      navigate('/register');
                      setShowMobileMenu(false);
                    }}
                    className="w-full text-left text-gray-300 hover:text-white block px-3 py-2 rounded-md text-base font-medium transition-colors duration-200 hover:bg-white/10"
                  >
                    Create Profile
                  </button>
                  <button
                    onClick={() => {
                      setShowAuthModal(true);
                      setShowMobileMenu(false);
                    }}
                    className="w-full mt-2 bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white font-medium px-3 py-2 rounded-lg transition-all duration-200 shadow-lg"
                  >
                    Get Started
                  </button>
                </div>
              )}
            </div>
          </div>
        )}
      </nav>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      )}
    </header>
  );
};

export default Header; 