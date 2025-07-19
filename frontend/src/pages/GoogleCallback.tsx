import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getApiUrl } from '../utils/apiConfig';

const GoogleCallback: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [loading, setLoading] = React.useState(true);
  const [error, setError] = React.useState<string | null>(null);

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

        // Store user data
        const userData = {
          id: data.user_id,
          email: data.email,
          name: data.name,
          auth_provider: 'google'
        };
        localStorage.setItem('user_data', JSON.stringify(userData));

        // Redirect to home page
        navigate('/', { replace: true });
        window.location.reload();

      } catch (error) {
        console.error('Google callback error:', error);
        setError(error instanceof Error ? error.message : 'Google authentication failed');
        setLoading(false);
      }
    };

    handleGoogleCallback();
  }, [searchParams, navigate]);

  if (error) {
    return (
      <div className="flex items-center justify-center min-h-screen bg-gray-50">
        <div className="text-center">
          <div className="text-red-600 mb-4">
            <svg className="w-12 h-12 mx-auto" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
            </svg>
          </div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Authentication Error</h2>
          <p className="text-gray-600 mb-4">{error}</p>
          <button
            onClick={() => navigate('/')}
            className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
          >
            Return to Home
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Authenticating with Google...</p>
      </div>
    </div>
  );
};

export default GoogleCallback; 