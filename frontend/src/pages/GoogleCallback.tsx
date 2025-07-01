import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getApiUrl } from '../utils/apiConfig';

const GoogleCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const handleGoogleCallback = async () => {
      try {
        const code = searchParams.get('code');
        const error = searchParams.get('error');

        if (error) {
          throw new Error('Google authentication cancelled or failed');
        }

        if (!code) {
          throw new Error('No authorization code received from Google');
        }

        console.log('🔑 Processing Google callback...');
        const API_BASE_URL = await getApiUrl();

        const response = await fetch(`${API_BASE_URL}/auth/google/callback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code }),
        });

        if (!response.ok) {
          const errorData = await response.json();
          throw new Error(errorData.detail || 'Google authentication failed');
        }

        const data = await response.json();
        console.log('✅ Google authentication successful:', data);

        // Store authentication data
        if (data.access_token) {
          localStorage.setItem('auth_token', data.access_token);
          localStorage.setItem('token_type', data.token_type || 'bearer');
          localStorage.setItem('userToken', data.access_token);
        }

        if (data.user) {
          localStorage.setItem('user_data', JSON.stringify(data.user));
        }

        // Redirect to home page
        navigate('/', { replace: true });
        window.location.reload();

      } catch (error: any) {
        console.error('❌ Google callback error:', error);
        setError(error.message || 'Authentication failed');
        setLoading(false);
      }
    };

    handleGoogleCallback();
  }, [searchParams, navigate]);

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4 animate-pulse">
            <span className="text-2xl">🐝</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Completing Google Sign In...
          </h2>
          <p className="text-gray-600 dark:text-gray-400">
            Please wait while we authenticate your account
          </p>
          <div className="mt-4 flex justify-center">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-500"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center">
        <div className="text-center max-w-md mx-auto px-4">
          <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <span className="text-2xl text-red-500">❌</span>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
            Authentication Failed
          </h2>
          <p className="text-gray-600 dark:text-gray-400 mb-6">
            {error}
          </p>
          <button
            onClick={() => navigate('/login')}
            className="bg-gradient-to-r from-orange-500 to-yellow-500 text-white px-6 py-3 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  return null;
};

export default GoogleCallback; 