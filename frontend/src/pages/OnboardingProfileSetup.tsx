import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { User, Upload, CheckCircle, Linkedin, FileText, Edit } from 'lucide-react';
import { onboardingService } from '../services/onboardingService';

const OnboardingProfileSetup: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [userId, setUserId] = useState<string>('');
  const [step, setStep] = useState<'choice' | 'linkedin' | 'cv' | 'manual'>('choice');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // CV Upload states
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [dragActive, setDragActive] = useState(false);

  // Manual profile states
  const [manualProfile, setManualProfile] = useState({
    name: '',
    bio: '',
    location: '',
    skills: '',
    experience_years: '',
  });

  useEffect(() => {
    const stateUserId = location.state?.userId;
    if (stateUserId) {
      setUserId(stateUserId);
    } else {
      navigate('/');
    }
  }, [location, navigate]);

  const handleLinkedInConnect = async () => {
    setLoading(true);
    setError('');
    
    try {
      const { auth_url } = await onboardingService.getLinkedInAuthUrl();
      window.location.href = auth_url;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'LinkedIn bağlantısı başarısız');
    } finally {
      setLoading(false);
    }
  };

  const handleSkip = () => {
    navigate('/onboarding/complete-profile', { 
      state: { userId, skipped: true }
    });
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
      <div className="max-w-4xl w-full">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-16 h-16 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <User className="w-8 h-8 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Profilinizi Oluşturun
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              İş başvurularınızı hızlandırmak için profilinizi nasıl oluşturmak istersiniz?
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg">
              {error}
            </div>
          )}

          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="border-2 border-gray-200 dark:border-gray-600 rounded-xl p-6 hover:border-orange-300 dark:hover:border-orange-500 transition-colors cursor-pointer group"
                 onClick={() => setStep('linkedin')}>
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <Linkedin className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  LinkedIn ile Bağlan
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  LinkedIn profilinizi bağlayarak bilgilerinizi otomatik olarak alın
                </p>
              </div>
            </div>

            <div className="border-2 border-gray-200 dark:border-gray-600 rounded-xl p-6 hover:border-orange-300 dark:hover:border-orange-500 transition-colors cursor-pointer group"
                 onClick={() => setStep('cv')}>
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <FileText className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  CV Yükle
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  CV dosyanızı yükleyerek bilgilerinizi otomatik olarak işletelim
                </p>
              </div>
            </div>

            <div className="border-2 border-gray-200 dark:border-gray-600 rounded-xl p-6 hover:border-orange-300 dark:hover:border-orange-500 transition-colors cursor-pointer group"
                 onClick={() => setStep('manual')}>
              <div className="text-center space-y-4">
                <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto group-hover:scale-110 transition-transform">
                  <Edit className="w-8 h-8 text-white" />
                </div>
                <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                  Manuel Giriş
                </h3>
                <p className="text-gray-600 dark:text-gray-400 text-sm">
                  Profil bilgilerinizi kendiniz girerek özelleştirin
                </p>
              </div>
            </div>
          </div>

          <div className="text-center">
            <button
              onClick={handleSkip}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 underline"
            >
              Şimdilik atla, daha sonra tamamla
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingProfileSetup; 