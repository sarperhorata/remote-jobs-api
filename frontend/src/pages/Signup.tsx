import React, { useState } from 'react';
import { useNavigate, Link, useLocation } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

interface LocationState {
  from?: {
    pathname: string;
  };
}

const Signup: React.FC = () => {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [error, setError] = useState('');
  const [emailError, setEmailError] = useState('');
  const [passwordHints, setPasswordHints] = useState({
    length: false,
    upper: false,
    lower: false,
    digit: false,
    special: false,
  });
  const [isLoading, setIsLoading] = useState(false);
  const { signup } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  
  // Get the previous location, or default to dashboard
  const locationState = location.state as LocationState;
  const from = locationState?.from?.pathname || '/dashboard';
  
  const isValidEmail = (value: string) => {
    // RFC5322-basics, pragmatic
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
    return re.test(value.trim());
  };

  const evaluatePassword = (value: string) => {
    setPasswordHints({
      length: value.length >= 8,
      upper: /[A-Z]/.test(value),
      lower: /[a-z]/.test(value),
      digit: /\d/.test(value),
      special: /[!@#$%^&*(),.?":{}|<>]/.test(value),
    });
  };

  const canSubmit = () => {
    const allRequiredRules = passwordHints.length && passwordHints.upper && passwordHints.lower && passwordHints.digit;
    return (
      isValidEmail(email) &&
      allRequiredRules &&
      password === confirmPassword &&
      name.trim().length > 0
    );
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    // Form validation
    if (!isValidEmail(email)) {
      setEmailError('Please enter a valid email like user@example.com');
      return;
    }
    setEmailError('');

    // Password rules (mirror backend)
    if (password.length < 8 || !/[A-Z]/.test(password) || !/[a-z]/.test(password) || !/\d/.test(password)) {
      return setError('Password must be at least 8 chars and include uppercase, lowercase and a digit');
    }

    if (password !== confirmPassword) {
      return setError('Passwords do not match');
    }
    
    setError('');
    setIsLoading(true);
    
    try {
      await signup(name, email, password);
      // Redirect to the page they tried to visit or to dashboard
      navigate(from, { replace: true });
    } catch (err) {
      setError('Failed to create an account');
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex min-h-screen bg-gray-50">
      <div className="m-auto w-full max-w-md p-8 space-y-8 bg-white rounded-lg shadow-md">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Create your account
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Or{' '}
            <Link to="/auth/login" className="font-medium text-primary hover:text-primary-dark">
              sign in to your account
            </Link>
          </p>
        </div>
        
        {error && (
          <div className="p-4 mb-4 text-sm text-red-700 bg-red-100 rounded-lg" role="alert">
            {error}
          </div>
        )}
        
        <form className="mt-8 space-y-6" onSubmit={handleSubmit}>
          <div className="rounded-md shadow-sm space-y-3">
            <div>
              <label htmlFor="name" className="sr-only">
                Full name
              </label>
              <input
                id="name"
                name="name"
                type="text"
                autoComplete="name"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                placeholder="Full name"
                value={name}
                onChange={(e) => setName(e.target.value)}
              />
            </div>
            <div>
              <label htmlFor="email-address" className="sr-only">
                Email address
              </label>
              <input
                id="email-address"
                name="email"
                type="email"
                autoComplete="email"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                placeholder="Email address"
                value={email}
                onChange={(e) => {
                  setEmail(e.target.value);
                  if (emailError) setEmailError('');
                }}
              />
              {emailError && (
                <p className="mt-1 text-xs text-red-600">{emailError}</p>
              )}
            </div>
            <div>
              <label htmlFor="password" className="sr-only">
                Password
              </label>
              <input
                id="password"
                name="password"
                type="password"
                autoComplete="new-password"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                placeholder="Password"
                value={password}
                onChange={(e) => {
                  const v = e.target.value;
                  setPassword(v);
                  evaluatePassword(v);
                }}
              />
              {/* Password rules checklist (backend-aligned) */}
              <ul className="mt-2 space-y-1 text-xs">
                <li className={passwordHints.length ? 'text-green-600' : 'text-gray-500'}>
                  • At least 8 characters
                </li>
                <li className={passwordHints.upper ? 'text-green-600' : 'text-gray-500'}>
                  • Contains an uppercase letter (A-Z)
                </li>
                <li className={passwordHints.lower ? 'text-green-600' : 'text-gray-500'}>
                  • Contains a lowercase letter (a-z)
                </li>
                <li className={passwordHints.digit ? 'text-green-600' : 'text-gray-500'}>
                  • Contains a digit (0-9)
                </li>
                <li className={passwordHints.special ? 'text-emerald-600' : 'text-gray-400'}>
                  • Special character (optional)
                </li>
              </ul>
            </div>
            <div>
              <label htmlFor="confirm-password" className="sr-only">
                Confirm Password
              </label>
              <input
                id="confirm-password"
                name="confirm-password"
                type="password"
                autoComplete="new-password"
                required
                className="appearance-none relative block w-full px-3 py-2 border border-gray-300 placeholder-gray-500 text-gray-900 rounded-md focus:outline-none focus:ring-primary focus:border-primary focus:z-10 sm:text-sm"
                placeholder="Confirm Password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
              />
            </div>
          </div>

          <div>
            <button
              type="submit"
              disabled={isLoading || !canSubmit()}
              className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-primary hover:bg-primary-dark focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary"
            >
              {isLoading ? 'Creating account...' : 'Sign up'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default Signup; 