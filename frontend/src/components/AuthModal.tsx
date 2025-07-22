import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getApiUrl } from '../utils/apiConfig';
import { X, Eye, EyeOff, Check, ExternalLink } from 'lucide-react';

interface AuthModalProps {
  isOpen: boolean;
  onClose: () => void;
  defaultTab?: 'login' | 'register';
}

interface PasswordRequirement {
  text: string;
  isValid: boolean;
}

const AuthModal: React.FC<AuthModalProps> = ({ isOpen, onClose, defaultTab = 'login' }) => {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'login' | 'register'>(defaultTab);
  const [showPassword, setShowPassword] = useState(false);
  
  // Login form state
  const [loginEmail, setLoginEmail] = useState('');
  const [loginPassword, setLoginPassword] = useState('');
  const [loginRememberMe, setLoginRememberMe] = useState(false);
  const [loginLoading, setLoginLoading] = useState(false);
  const [loginError, setLoginError] = useState<string | null>(null);
  
  // Register form state
  const [registerEmail, setRegisterEmail] = useState('');
  const [registerFullName, setRegisterFullName] = useState('');
  const [registerPassword, setRegisterPassword] = useState('');
  const [agreedToTerms, setAgreedToTerms] = useState(false);
  const [registerLoading, setRegisterLoading] = useState(false);
  const [registerError, setRegisterError] = useState<string | null>(null);
  const [registerSuccess, setRegisterSuccess] = useState<string | null>(null);

  // Password validation - updated requirements
  const getPasswordRequirements = (password: string): PasswordRequirement[] => {
    return [
      {
        text: "At least 8 characters",
        isValid: password.length >= 8
      },
      {
        text: "At least 1 number",
        isValid: /\d/.test(password)
      },
      {
        text: "At least 1 uppercase letter",
        isValid: /[A-Z]/.test(password)
      }
    ];
  };

  const passwordRequirements = getPasswordRequirements(registerPassword);
  const isPasswordValid = passwordRequirements.every(req => req.isValid);

  if (!isOpen) return null;

  const handleGoogleLogin = async () => {
    try {
      // Create Google OAuth URL directly
      const googleClientId = '655034019922-pq66mk4ah4tou451gauikvvgeflv6ual.apps.googleusercontent.com';
      const redirectUri = window.location.origin + '/auth/google/callback';
      
      const googleAuthUrl = `https://accounts.google.com/o/oauth2/v2/auth?` +
        `client_id=${googleClientId}&` +
        `redirect_uri=${encodeURIComponent(redirectUri)}&` +
        `response_type=code&` +
        `scope=email%20profile&` +
        `access_type=offline&` +
        `prompt=consent`;
      
      window.location.href = googleAuthUrl;
    } catch (error) {
      console.error('Google auth error:', error);
      setLoginError('Google authentication failed. Please try again.');
    }
  };

  const handleLinkedInLogin = async () => {
    try {
      console.log('🔗 Attempting LinkedIn login...');
      const API_BASE_URL = await getApiUrl();
      
      const response = await fetch(`${API_BASE_URL}/auth/linkedin/auth-url`);
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'LinkedIn authentication failed');
      }
      
      const data = await response.json();
      console.log('✅ LinkedIn auth URL received:', data.auth_url);
      
      // LinkedIn OAuth URL'sine yönlendir
      window.location.href = data.auth_url;
    } catch (error) {
      console.error('LinkedIn auth error:', error);
      setLoginError('LinkedIn authentication failed. Please try again.');
    }
  };

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoginLoading(true);
    setLoginError(null);
    
    try {
      // Basic validations
      if (!loginEmail || !loginPassword) {
        throw new Error('Please fill in all fields');
      }
      
      console.log('🔑 Attempting login with API...');
      const API_BASE_URL = await getApiUrl();
      
      const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({
          username: loginEmail,
          password: loginPassword
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        if (response.status === 401) {
          throw new Error('Invalid email or password');
        } else if (response.status === 403) {
          throw new Error('Email not verified. Please check your email and verify your account.');
        }
        throw new Error(errorData.detail || 'Login failed');
      }
      
      const data = await response.json();
      console.log('✅ Login successful:', data);
      
      // Store authentication data
      if (data.access_token) {
        localStorage.setItem('auth_token', data.access_token);
        localStorage.setItem('token_type', data.token_type || 'bearer');
        localStorage.setItem('userToken', data.access_token); // Compatibility
        
        // Fetch user data
        try {
          const userResponse = await fetch(`${API_BASE_URL}/auth/me`, {
            headers: {
              'Authorization': `Bearer ${data.access_token}`,
            },
          });
          
          if (userResponse.ok) {
            const userData = await userResponse.json();
            localStorage.setItem('user_data', JSON.stringify(userData));
          }
        } catch (userError) {
          console.error('Failed to fetch user data:', userError);
        }
      }
      
      onClose();
      window.location.reload();
      
    } catch (error: any) {
      console.error('❌ Login failed:', error);
      setLoginError(error.message || 'Login failed. Please try again.');
    } finally {
      setLoginLoading(false);
    }
  };

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();
    setRegisterLoading(true);
    setRegisterError(null);
    setRegisterSuccess(null);
    
    try {
      // Basic validations
      if (!registerEmail || !registerFullName || !registerPassword) {
        throw new Error('Please fill in all required fields');
      }
      
      if (!isPasswordValid) {
        throw new Error('Password must meet all requirements');
      }
      
      if (!agreedToTerms) {
        throw new Error('Please agree to the Terms of Service');
      }
      
      console.log('🔑 Attempting registration with API...');
      const API_BASE_URL = await getApiUrl();
      
      const response = await fetch(`${API_BASE_URL}/auth/register`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: registerEmail,
          name: registerFullName,
          password: registerPassword
        })
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        if (errorData.detail && Array.isArray(errorData.detail)) {
          // Pydantic validation errors
          const errorMessage = errorData.detail.map((err: any) => err.msg).join(', ');
          throw new Error(errorMessage);
        }
        throw new Error(errorData.detail || 'Registration failed');
      }
      
      const data = await response.json();
      console.log('✅ Registration successful:', data);
      
      setRegisterSuccess('Registration successful! Please check your email to login');
      setTimeout(() => {
        onClose();
        window.location.reload();
      }, 30000); // 30 seconds display
      
    } catch (error: any) {
      console.error('❌ Registration failed:', error);
      setRegisterError(error.message || 'Registration failed. Please try again.');
    } finally {
      setRegisterLoading(false);
    }
  };



  return (
    <>
      <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-2xl w-full max-w-md max-h-[90vh] overflow-y-auto">
          {/* Header */}
          <div className="flex justify-between items-center p-6 border-b border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center">
                <span className="text-2xl">🐝</span>
              </div>
              <h2 className="text-xl font-bold text-gray-900 dark:text-white">Buzz2Remote</h2>
            </div>
            <button 
              onClick={onClose} 
              className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-2xl font-light"
            >
              ×
            </button>
          </div>

          {/* Tabs */}
          <div className="flex border-b border-gray-200 dark:border-gray-700">
            <button
              onClick={() => setActiveTab('login')}
              className={`flex-1 py-4 px-6 text-sm font-medium text-center border-b-2 transition-colors ${
                activeTab === 'login'
                  ? 'border-orange-500 text-orange-600 dark:text-orange-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
                Sign In
              </button>
            <button
              onClick={() => setActiveTab('register')}
              className={`flex-1 py-4 px-6 text-sm font-medium text-center border-b-2 transition-colors ${
                activeTab === 'register'
                  ? 'border-orange-500 text-orange-600 dark:text-orange-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200'
              }`}
            >
              Create Account
            </button>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'login' ? (
              /* Login Form */
              <form onSubmit={handleLogin} className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Welcome back!
                </h3>
                
                {loginError && (
                  <div className="p-3 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg">
                    {loginError}
                  </div>
                )}

                <div>
                  <label htmlFor="loginEmail" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email Address
                  </label>
                  <input
                    type="email" required value={loginEmail}
                    onChange={(e) => setLoginEmail(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="your@email.com"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <label htmlFor="loginPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300">
                      Password
                    </label>
                    <button 
                      type="button" 
                      onClick={() => {
                        onClose();
                        navigate('/forgot-password');
                      }}
                      className="text-xs text-orange-600 hover:text-orange-500 underline"
                    >
                      Forgot Password?
                    </button>
                  </div>
                  <div className="relative">
                    <input
                      id="loginPassword"
                      type={showPassword ? 'text' : 'password'} 
                      required 
                      value={loginPassword}
                      onChange={(e) => setLoginPassword(e.target.value)}
                      className="w-full px-3 py-2 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      placeholder="Your password"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 focus:outline-none"
                    >
                      <div className="w-4 h-4 flex items-center justify-center">
                        {showPassword ? <EyeOff /> : <Eye />}
                      </div>
                    </button>
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={loginRememberMe}
                    onChange={(e) => setLoginRememberMe(e.target.checked)}
                    className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-600 dark:text-gray-400">Remember me</span>
                </div>

                <button
                  type="submit"
                  disabled={loginLoading}
                  className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {loginLoading ? 'Signing in...' : 'Sign In'}
                </button>

                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300 dark:border-gray-600" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white dark:bg-gray-800 text-gray-500">Or continue with</span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  className="w-full flex items-center justify-center space-x-2 bg-white border border-gray-300 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  <span>Sign in with Google</span>
                </button>

                <button
                  type="button"
                  onClick={handleLinkedInLogin}
                  className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition-colors font-medium"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  <span>Sign in with LinkedIn</span>
                </button>
              </form>
            ) : (
              /* Register Form */
              <form onSubmit={handleRegister} className="space-y-4">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  Create Account
                </h3>
                
                {registerError && (
                  <div className="p-3 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg">
                    {registerError}
                  </div>
                )}

                {registerSuccess && (
                  <div className="p-3 text-sm text-green-700 bg-green-100 border border-green-200 rounded-lg">
                    {registerSuccess}
                  </div>
                )}

                <div>
                  <label htmlFor="registerEmail" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Email Address
                  </label>
                  <input
                    id="registerEmail" 
                    type="email" 
                    required 
                    value={registerEmail}
                    onChange={(e) => setRegisterEmail(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="your@email.com"
                  />
                </div>

                <div>
                  <label htmlFor="registerFullName" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                    Full Name
                  </label>
                  <input
                    id="registerFullName" 
                    type="text" 
                    required 
                    value={registerFullName}
                    onChange={(e) => setRegisterFullName(e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="John Doe"
                  />
                </div>

                <div className="grid grid-cols-1 gap-4">
                  {/* Password Field */}
                  <div>
                    <label htmlFor="registerPassword" className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                      Password
                    </label>
                    <div className="relative">
                      <input
                        id="registerPassword"
                        type={showPassword ? 'text' : 'password'}
                        required
                        value={registerPassword}
                        onChange={(e) => setRegisterPassword(e.target.value)}
                        className="w-full px-3 py-2 pr-20 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                        placeholder="Create a strong password"
                      />
                      
                      {/* Password Policy Icon */}
                      {registerPassword.length > 0 && (
                        <div className="absolute right-12 top-2.5">
                          <div className="group cursor-help">
                            <div className="w-4 h-4 flex items-center justify-center">
                              {isPasswordValid ? (
                                <span className="text-green-500">
                                  <Check />
                                </span>
                              ) : (
                                <span className="text-red-500">
                                  <X />
                                </span>
                              )}
                            </div>
                            <div className="absolute z-50 right-0 mt-2 w-64 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                              <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                Password Requirements:
                              </div>
                              <div className="space-y-1">
                                {passwordRequirements.map((requirement, index) => (
                                  <div key={index} className="flex items-center space-x-2">
                                    <div className="w-3 h-3 flex items-center justify-center">
                                      {requirement.isValid ? (
                                        <span className="text-green-500"><Check /></span>
                                      ) : (
                                        <span className="text-red-500"><X /></span>
                                      )}
                                    </div>
                                    <span className={`text-xs ${
                                      requirement.isValid ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'
                                    }`}>
                                      {requirement.text}
                                    </span>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>
                        </div>
                      )}
                      
                      {/* Show/Hide Password Button */}
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute right-3 top-2.5 text-gray-400 hover:text-gray-600"
                      >
                        <div className="w-4 h-4 flex items-center justify-center">
                          {showPassword ? <EyeOff /> : <Eye />}
                        </div>
                      </button>
                    </div>
                  </div>
                </div>

                <div className="flex items-start">
                  <input
                    id="agreedToTerms"
                    type="checkbox"
                    required
                    checked={agreedToTerms}
                    onChange={(e) => setAgreedToTerms(e.target.checked)}
                    className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded mt-1"
                  />
                  <label htmlFor="agreedToTerms" className="ml-2 text-sm text-gray-600 dark:text-gray-400">
                    I agree to the{' '}
                    <a 
                      href="/terms-conditions" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-orange-600 hover:text-orange-500 underline inline-flex items-center gap-1"
                    >
                      Terms of Service
                      <ExternalLink className="w-3 h-3" />
                    </a>
                    {' '}and{' '}
                    <a 
                      href="/privacy-policy" 
                      target="_blank" 
                      rel="noopener noreferrer"
                      className="text-orange-600 hover:text-orange-500 underline inline-flex items-center gap-1"
                    >
                      Privacy Policy
                      <ExternalLink className="w-3 h-3" />
                    </a>
                  </label>
                </div>

                <button
                  type="submit"
                  disabled={registerLoading || !isPasswordValid || !agreedToTerms}
                  className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  {registerLoading ? 'Creating Account...' : 'Create Account'}
                </button>

                <div className="relative my-6">
                  <div className="absolute inset-0 flex items-center">
                    <div className="w-full border-t border-gray-300 dark:border-gray-600" />
                  </div>
                  <div className="relative flex justify-center text-sm">
                    <span className="px-2 bg-white dark:bg-gray-800 text-gray-500">Or continue with</span>
                  </div>
                </div>

                <button
                  type="button"
                  onClick={handleGoogleLogin}
                  className="w-full flex items-center justify-center space-x-2 bg-white border border-gray-300 text-gray-700 py-3 px-4 rounded-lg hover:bg-gray-50 transition-colors font-medium"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24">
                    <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                    <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                    <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                    <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                  </svg>
                  <span>Sign up with Google</span>
                </button>

                <button
                  type="button"
                  onClick={handleLinkedInLogin}
                  className="w-full flex items-center justify-center space-x-2 bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition-colors font-medium"
                >
                  <svg className="w-5 h-5" viewBox="0 0 24 24" fill="currentColor">
                    <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                  </svg>
                  <span>Sign up with LinkedIn</span>
                </button>
              </form>
            )}
          </div>
        </div>
      </div>

    </>
  );
};

export default AuthModal; 