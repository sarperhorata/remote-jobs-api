import React, { useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { authService } from '../services/authService';

export const AuthCallback: React.FC = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  useEffect(() => {
    const handleCallback = async () => {
      try {
        const token = searchParams.get('token');
        const error = searchParams.get('error');
        
        if (error) {
          console.error('Auth error:', error);
          navigate('/auth/error', { state: { error } });
          return;
        }
        
        if (!token) {
          throw new Error('No token received');
        }
        
        // Handle the callback
        await authService.handleGoogleCallback(token);
        
        // Redirect to home page
        navigate('/');
        
      } catch (error) {
        console.error('Callback error:', error);
        navigate('/auth/error', { state: { error: 'Authentication failed' } });
      }
    };
    
    handleCallback();
  }, [searchParams, navigate]);
  
  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-50">
      <div className="max-w-md w-full space-y-8">
        <div>
          <h2 className="mt-6 text-center text-3xl font-extrabold text-gray-900">
            Completing authentication...
          </h2>
          <p className="mt-2 text-center text-sm text-gray-600">
            Please wait while we complete your sign in
          </p>
        </div>
      </div>
    </div>
  );
}; 