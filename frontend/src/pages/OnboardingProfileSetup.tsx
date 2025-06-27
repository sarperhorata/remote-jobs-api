import React from 'react';
import { useNavigate } from 'react-router-dom';
import { User } from '../components/icons/EmojiIcons';

const OnboardingProfileSetup: React.FC = () => {
  const navigate = useNavigate();

  const handleSkip = () => {
    navigate('/');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">
              Profilinizi Oluşturun
            </h1>
            <p className="text-gray-600">
              Profil oluşturma özelliği yakında eklenecek.
            </p>
          </div>

          <div className="text-center">
            <button
              onClick={handleSkip}
              className="bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-6 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium"
            >
              Ana Sayfaya Dön
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingProfileSetup;
