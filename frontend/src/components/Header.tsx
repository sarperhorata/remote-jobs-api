import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import AuthModal from './AuthModal';
import { Menu, X, User, LogOut, Settings, Heart, FileText, Search as SearchIcon } from 'lucide-react';

const Header: React.FC = () => {
  const { user, logout } = useAuth();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showProfileDropdown, setShowProfileDropdown] = useState(false);
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
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

  const navigation = [
    { name: 'Jobs', href: '/jobs' },
    { name: 'Companies', href: '/companies' },
    { name: 'About', href: '/about' },
    { name: 'Contact', href: '/contact' },
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
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 flex items-center justify-center shadow-lg group-hover:scale-105 transition-transform duration-200">
                    <span className="text-white font-bold text-lg animate-pulse">🐝</span>
                  </div>
                  <div className="absolute -inset-1 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-xl blur opacity-20 group-hover:opacity-40 transition-opacity duration-200"></div>
                </div>
                <div className="flex flex-col">
                  <span className="font-bold text-lg bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                    Buzz2Remote
                  </span>
                  <span className="text-xs text-white/70 -mt-1">Find Remote Jobs 🚀</span>
                </div>
              </Link>

              {/* Desktop Navigation */}
              <div className="hidden md:flex items-center space-x-8">
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
                {user ? (
                  /* User Menu */
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
                      <div className="absolute right-0 mt-2 w-56 bg-white/95 backdrop-blur-lg rounded-xl shadow-xl border border-white/20 py-2 z-50">
                        <div className="px-4 py-2 border-b border-gray-200/50">
                          <p className="text-sm font-medium text-gray-900">{user.email}</p>
                          <p className="text-xs text-gray-500">Free Plan</p>
                        </div>
                        
                        <button
                          onClick={() => handleProfileAction('profile')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <User className="w-4 h-4 mr-3" />
                          My Profile
                        </button>
                        
                        <button
                          onClick={() => handleProfileAction('saved')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <Heart className="w-4 h-4 mr-3" />
                          Saved Jobs
                        </button>
                        
                        <button
                          onClick={() => handleProfileAction('applications')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <FileText className="w-4 h-4 mr-3" />
                          Applications
                        </button>
                        
                        <button
                          onClick={() => handleProfileAction('settings')}
                          className="flex items-center w-full px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 transition-colors"
                        >
                          <Settings className="w-4 h-4 mr-3" />
                          Settings
                        </button>
                        
                        <div className="border-t border-gray-200/50 mt-2 pt-2">
                          <button
                            onClick={() => handleProfileAction('logout')}
                            className="flex items-center w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 transition-colors"
                          >
                            <LogOut className="w-4 h-4 mr-3" />
                            Sign Out
                          </button>
                        </div>
                      </div>
                    )}
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
                    className="block text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition-all duration-200 font-medium"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    {item.name}
                  </Link>
                ))}
                
                {!user && (
                  <div className="border-t border-white/20 pt-3 mt-3">
                    <button
                      onClick={() => {
                        setShowAuthModal(true);
                        setIsMobileMenuOpen(false);
                      }}
                      className="block w-full text-left text-white/90 hover:text-white hover:bg-white/10 px-3 py-2 rounded-lg transition-all duration-200 font-medium"
                    >
                      Sign In
                    </button>
                    <button
                      onClick={() => {
                        setShowAuthModal(true);
                        setIsMobileMenuOpen(false);
                      }}
                      className="block w-full mt-2 bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-white font-medium px-3 py-2 rounded-lg transition-all duration-200"
                    >
                      Get Started
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
        </nav>
      </header>

      {/* Auth Modal */}
      {showAuthModal && (
        <AuthModal 
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)} 
        />
      )}
    </>
  );
};

export default Header; 