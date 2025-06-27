import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { Mail, CheckCircle } from '../components/icons/EmojiIcons';

const CheckEmail: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();

  const email = location.state?.email || '';
  const message = location.state?.message || 'Doğrulama emaili gönderildi';

  if (!email) {
    navigate('/');
    return null;
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-md w-full">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <Mail className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              Email Adresinizi Kontrol Edin
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Kayıt işleminizi tamamlamak için size email gönderdik
            </p>
          </div>

          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg p-4 mb-6">
            <div className="flex items-center space-x-3">
              <CheckCircle className="w-5 h-5 text-green-600 dark:text-green-400 flex-shrink-0" />
              <div>
                <p className="text-green-800 dark:text-green-200 font-medium">
                  Email Gönderildi!
                </p>
                <p className="text-green-700 dark:text-green-300 text-sm">
                  {message}
                </p>
              </div>
            </div>
          </div>

          <div className="text-center mb-6">
            <p className="text-gray-700 dark:text-gray-300 mb-2">
              Doğrulama linki şu adrese gönderildi:
            </p>
            <p className="text-orange-600 dark:text-orange-400 font-medium bg-orange-50 dark:bg-orange-900/20 px-3 py-2 rounded-lg">
              {email}
            </p>
          </div>

          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4 mb-6">
            <h3 className="font-medium text-blue-900 dark:text-blue-100 mb-2">
              📧 Sonraki Adımlar:
            </h3>
            <ol className="text-blue-800 dark:text-blue-200 text-sm space-y-1 list-decimal list-inside">
              <li>Email kutunuzu kontrol edin</li>
              <li>Doğrulama linkine tıklayın</li>
              <li>Şifrenizi belirleyin</li>
              <li>Profilinizi oluşturun</li>
            </ol>
          </div>

          <button
            onClick={() => navigate('/')}
            className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium"
          >
            Ana Sayfaya Dön
          </button>
        </div>
      </div>
    </div>
  );
};

export default CheckEmail; 