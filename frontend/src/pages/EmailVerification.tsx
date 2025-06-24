import React, { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { CheckCircle, AlertCircle, Mail, RefreshCw } from 'lucide-react';
import { onboardingService } from '../services/onboardingService';

const EmailVerification: React.FC = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [status, setStatus] = useState<'loading' | 'success' | 'error' | 'expired'>('loading');
  const [message, setMessage] = useState('');
  const [userId, setUserId] = useState<string>('');

  useEffect(() => {
    const verifyEmail = async () => {
      const token = searchParams.get('token');
      
      if (!token) {
        setStatus('error');
        setMessage('Doğrulama token\'ı bulunamadı');
        return;
      }

      try {
        const result = await onboardingService.verifyEmail(token);
        setStatus('success');
        setMessage(result.message);
        setUserId(result.user_id || '');
        
        // 3 saniye sonra şifre belirleme sayfasına yönlendir
        setTimeout(() => {
          navigate(`/onboarding/set-password?token=${token}`);
        }, 3000);
        
      } catch (error) {
        setStatus('error');
        setMessage(error instanceof Error ? error.message : 'Email doğrulama başarısız');
      }
    };

    verifyEmail();
  }, [searchParams, navigate]);

  const handleContinue = () => {
    const token = searchParams.get('token');
    if (token) {
      navigate(`/onboarding/set-password?token=${token}`);
    }
  };

  const handleResendEmail = () => {
    // Bu fonksiyon email'i tekrar gönderecek
    window.location.href = '/';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          {/* Header */}
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Email Doğrulama
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Email adresinizi doğruluyoruz...
            </p>
          </div>

          {/* Status Content */}
          <div className="text-center">
            {status === 'loading' && (
              <div className="space-y-4">
                <RefreshCw className="w-12 h-12 text-orange-500 animate-spin mx-auto" />
                <p className="text-gray-600 dark:text-gray-400">
                  Email doğrulanıyor, lütfen bekleyin...
                </p>
              </div>
            )}

            {status === 'success' && (
              <div className="space-y-4">
                <CheckCircle className="w-12 h-12 text-green-500 mx-auto" />
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-green-700 dark:text-green-400">
                    Email Başarıyla Doğrulandı! 🎉
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {message}
                  </p>
                  <p className="text-sm text-gray-500 dark:text-gray-500">
                    3 saniye içinde şifre belirleme sayfasına yönlendirileceksiniz...
                  </p>
                </div>
                <button
                  onClick={handleContinue}
                  className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium"
                >
                  Şifre Belirlemek İçin Devam Et
                </button>
              </div>
            )}

            {status === 'error' && (
              <div className="space-y-4">
                <AlertCircle className="w-12 h-12 text-red-500 mx-auto" />
                <div className="space-y-2">
                  <h3 className="text-lg font-semibold text-red-700 dark:text-red-400">
                    Doğrulama Başarısız
                  </h3>
                  <p className="text-gray-600 dark:text-gray-400">
                    {message}
                  </p>
                </div>
                <div className="space-y-3">
                  <button
                    onClick={handleResendEmail}
                    className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium"
                  >
                    Yeni Doğrulama Emaili Gönder
                  </button>
                  <button
                    onClick={() => navigate('/')}
                    className="w-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 px-4 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
                  >
                    Ana Sayfaya Dön
                  </button>
                </div>
              </div>
            )}
          </div>

          {/* Footer */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
            <p className="text-xs text-gray-500 dark:text-gray-400 text-center">
              Email doğrulama sorunu yaşıyorsanız, spam klasörünüzü kontrol edin veya{' '}
              <button 
                onClick={handleResendEmail}
                className="text-orange-600 hover:text-orange-500 underline"
              >
                yeni bir doğrulama emaili
              </button>
              {' '}isteyin.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default EmailVerification; 