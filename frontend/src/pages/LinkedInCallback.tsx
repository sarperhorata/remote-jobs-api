import React, { useEffect, useState } from 'react';

const LinkedInCallback: React.FC = () => {
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('Authenticating with LinkedIn...');

  useEffect(() => {
    const handleLinkedInCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');
        const errorDescription = urlParams.get('error_description');

        if (error) {
          console.error('LinkedIn OAuth error:', error, errorDescription);
          setStatus('error');
          setMessage(errorDescription || 'Authentication failed. Please try again.');
          
          // Store error for parent window
          localStorage.setItem('linkedin_auth_error', errorDescription || 'Authentication failed');
          
          // Close popup after 3 seconds
          setTimeout(() => window.close(), 3000);
          return;
        }

        if (!code) {
          setStatus('error');
          setMessage('No authorization code received. Please try again.');
          localStorage.setItem('linkedin_auth_error', 'No authorization code received');
          setTimeout(() => window.close(), 3000);
          return;
        }

        setMessage('Exchanging code for access token...');

        // Exchange code for access token
        const tokenResponse = await fetch('/api/auth/linkedin/token', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ code, state }),
        });

        if (!tokenResponse.ok) {
          const errorData = await tokenResponse.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to exchange code for token');
        }

        const tokenData = await tokenResponse.json();
        
        setMessage('Fetching LinkedIn profile data...');
        
        // Fetch LinkedIn profile data
        const profileResponse = await fetch('/api/auth/linkedin/profile', {
          method: 'GET',
          headers: {
            'Authorization': `Bearer ${tokenData.access_token}`,
          },
        });

        if (!profileResponse.ok) {
          const errorData = await profileResponse.json().catch(() => ({}));
          throw new Error(errorData.detail || 'Failed to fetch LinkedIn profile');
        }

        const profileData = await profileResponse.json();
        
        // Store profile data for parent window to pick up
        localStorage.setItem('linkedin_profile_data', JSON.stringify(profileData));
        
        setStatus('success');
        setMessage('Profile imported successfully! Closing window...');
        
        // Close popup after 2 seconds
        setTimeout(() => window.close(), 2000);
        
      } catch (error) {
        console.error('LinkedIn callback error:', error);
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'An unexpected error occurred');
        localStorage.setItem('linkedin_auth_error', error instanceof Error ? error.message : 'An unexpected error occurred');
        
        // Close popup after 5 seconds
        setTimeout(() => window.close(), 5000);
      }
    };

    handleLinkedInCallback();
  }, []);

  const getStatusIcon = () => {
    switch (status) {
      case 'loading':
        return (
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        );
      case 'success':
        return (
          <div className="w-12 h-12 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
            </svg>
          </div>
        );
      case 'error':
        return (
          <div className="w-12 h-12 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
            <svg className="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        );
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'loading':
        return 'text-blue-600';
      case 'success':
        return 'text-green-600';
      case 'error':
        return 'text-red-600';
    }
  };

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center max-w-md mx-auto p-6">
        {getStatusIcon()}
        <h2 className={`text-lg font-semibold mb-2 ${getStatusColor()}`}>
          {status === 'loading' && 'Authenticating...'}
          {status === 'success' && 'Success!'}
          {status === 'error' && 'Error'}
        </h2>
        <p className="text-gray-600 mb-4">{message}</p>
        
        {status === 'error' && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-3 mb-4">
            <p className="text-sm text-red-700">
              If this error persists, please try again or contact support.
            </p>
          </div>
        )}
        
        {status === 'success' && (
          <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4">
            <p className="text-sm text-green-700">
              Your LinkedIn profile has been successfully imported!
            </p>
          </div>
        )}
        
        <div className="text-xs text-gray-500">
          This window will close automatically...
        </div>
      </div>
    </div>
  );
};

export default LinkedInCallback; 