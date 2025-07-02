import React, { useEffect } from 'react';

const LinkedInCallback: React.FC = () => {
  useEffect(() => {
    const handleLinkedInCallback = async () => {
      try {
        const urlParams = new URLSearchParams(window.location.search);
        const code = urlParams.get('code');
        const state = urlParams.get('state');
        const error = urlParams.get('error');

        if (error) {
          console.error('LinkedIn OAuth error:', error);
          window.close();
          return;
        }

        if (code) {
          // Exchange code for access token
          const tokenResponse = await fetch('/api/auth/linkedin/token', {
            method: 'POST',
            headers: {
              'Content-Type': 'application/json',
            },
            body: JSON.stringify({ code, state }),
          });

          if (tokenResponse.ok) {
            const tokenData = await tokenResponse.json();
            
            // Fetch LinkedIn profile data
            const profileResponse = await fetch('/api/auth/linkedin/profile', {
              method: 'GET',
              headers: {
                'Authorization': `Bearer ${tokenData.access_token}`,
              },
            });

            if (profileResponse.ok) {
              const profileData = await profileResponse.json();
              
              // Store profile data for parent window to pick up
              localStorage.setItem('linkedin_profile_data', JSON.stringify(profileData));
              
              // Close popup
              window.close();
            } else {
              throw new Error('Failed to fetch LinkedIn profile');
            }
          } else {
            throw new Error('Failed to exchange code for token');
          }
        }
      } catch (error) {
        console.error('LinkedIn callback error:', error);
        localStorage.setItem('linkedin_auth_error', 'Failed to authenticate with LinkedIn');
        window.close();
      }
    };

    handleLinkedInCallback();
  }, []);

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-50">
      <div className="text-center">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
        <p className="text-gray-600">Authenticating with LinkedIn...</p>
      </div>
    </div>
  );
};

export default LinkedInCallback; 