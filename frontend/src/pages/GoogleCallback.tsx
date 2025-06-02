import React, { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { getApiUrl } from '../utils/apiConfig';

const GoogleCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('');

  useEffect(() => {
    const handleCallback = async () => {
      const code = searchParams.get('code');
      const state = searchParams.get('state');
      const error = searchParams.get('error');

      if (error) {
        setStatus('error');
        setMessage('Authentication was cancelled or failed.');
        setTimeout(() => navigate('/'), 3000);
        return;
      }

      if (!code) {
        setStatus('error');
        setMessage('No authorization code received.');
        setTimeout(() => navigate('/'), 3000);
        return;
      }

      try {
        const API_BASE_URL = await getApiUrl();
        const response = await fetch(`${API_BASE_URL}/google/callback`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            code,
            state
          }),
        });

        const data = await response.json();

        if (response.ok) {
          setStatus('success');
          setMessage('Successfully authenticated! Redirecting...');
          // Store user data if needed
          if (data.user) {
            localStorage.setItem('user', JSON.stringify(data.user));
          }
          setTimeout(() => navigate('/'), 2000);
        } else {
          setStatus('error');
          setMessage(data.detail || 'Authentication failed.');
          setTimeout(() => navigate('/'), 3000);
        }
      } catch (error) {
        setStatus('error');
        setMessage('Network error occurred.');
        setTimeout(() => navigate('/'), 3000);
      }
    };

    handleCallback();
  }, [searchParams, navigate]);

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div className="text-center">
          {status === 'loading' && (
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          )}
          {status === 'success' && (
            <div className="text-green-600 text-2xl font-bold">✓</div>
          )}
          {status === 'error' && (
            <div className="text-red-600 text-2xl font-bold">✗</div>
          )}
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            {status === 'loading' && 'Processing...'}
            {status === 'success' && 'Success!'}
            {status === 'error' && 'Error'}
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            {message}
          </p>
        </div>
      </div>
    </div>
  );
};

export default GoogleCallback; 