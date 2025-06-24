import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { User, Upload, CheckCircle, AlertCircle, Linkedin, FileText, Edit } from 'lucide-react';
import { onboardingService } from '../services/onboardingService';

const ProfileSetup: React.FC = () => {
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
      // UserId yoksa ana sayfaya yönlendir
      navigate('/');
    }
  }, [location, navigate]);

  const handleLinkedInConnect = async () => {
    setLoading(true);
    setError('');
    
    try {
      const { auth_url } = await onboardingService.getLinkedInAuthUrl();
      // LinkedIn auth URL'ini yeni pencerede aç
      window.location.href = auth_url;
    } catch (error) {
      setError(error instanceof Error ? error.message : 'LinkedIn bağlantısı başarısız');
    } finally {
      setLoading(false);
    }
  };

  const handleFileSelect = (file: File) => {
    // File validation
    const allowedTypes = ['application/pdf', 'application/msword', 
                         'application/vnd.openxmlformats-officedocument.wordprocessingml.document'];
    
    if (!allowedTypes.includes(file.type)) {
      setError('Sadece PDF, DOC ve DOCX dosyaları kabul edilir');
      return;
    }

    if (file.size > 5 * 1024 * 1024) { // 5MB
      setError('Dosya boyutu 5MB\'dan küçük olmalıdır');
      return;
    }

    setSelectedFile(file);
    setError('');
  };

  const handleFileDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setDragActive(false);
    
    const file = e.dataTransfer.files[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleFileInput = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      handleFileSelect(file);
    }
  };

  const handleCVUpload = async () => {
    if (!selectedFile || !userId) return;

    setLoading(true);
    setError('');

    try {
      const result = await onboardingService.uploadCV(userId, selectedFile);
      setSuccess(result.message);
      
      // CV yüklendikten sonra profil tamamlama sayfasına geç
      setTimeout(() => {
        navigate('/onboarding/complete-profile', { 
          state: { userId, hasCV: true }
        });
      }, 2000);
      
    } catch (error) {
      setError(error instanceof Error ? error.message : 'CV yükleme başarısız');
    } finally {
      setLoading(false);
    }
  };

  const handleManualProfileSubmit = () => {
    // Validation
    if (!manualProfile.name.trim()) {
      setError('İsim alanı zorunludur');
      return;
    }

    // Manuel profil bilgileriyle devam et
    navigate('/onboarding/complete-profile', { 
      state: { 
        userId, 
        manualProfile,
        hasManualProfile: true 
      }
    });
  };

  const handleSkip = () => {
    // Profil kurulumunu atla ve doğrudan tamamlama sayfasına git
    navigate('/onboarding/complete-profile', { 
      state: { userId, skipped: true }
    });
  };

  if (step === 'choice') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="max-w-4xl w-full">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            {/* Header */}
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

            {/* Profile Options */}
            <div className="grid md:grid-cols-3 gap-6 mb-8">
              {/* LinkedIn Option */}
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
                  <div className="space-y-2">
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      <span>Hızlı ve güvenli</span>
                    </div>
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      <span>Otomatik bilgi alma</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* CV Upload Option */}
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
                  <div className="space-y-2">
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      <span>PDF, DOC, DOCX</span>
                    </div>
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      <span>Maks. 5MB</span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Manual Option */}
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
                  <div className="space-y-2">
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      <span>Tam kontrol</span>
                    </div>
                    <div className="flex items-center text-green-600 text-sm">
                      <CheckCircle className="w-4 h-4 mr-2" />
                      <span>Özelleştirilebilir</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            {/* Skip Option */}
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
  }

  if (step === 'linkedin') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-blue-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Linkedin className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                LinkedIn ile Bağlan
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                LinkedIn hesabınızı bağlayarak profil bilgilerinizi otomatik olarak alabilirsiniz
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg">
                {error}
              </div>
            )}

            <div className="space-y-4">
              <button
                onClick={handleLinkedInConnect}
                disabled={loading}
                className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg transition-colors font-medium disabled:opacity-50 flex items-center justify-center space-x-2"
              >
                <Linkedin className="w-5 h-5" />
                <span>{loading ? 'Bağlanıyor...' : 'LinkedIn ile Bağlan'}</span>
              </button>

              <button
                onClick={() => setStep('choice')}
                className="w-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 px-4 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
              >
                Geri Dön
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'cv') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-green-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <FileText className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                CV Yükle
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                CV dosyanızı yükleyerek profil bilgilerinizi otomatik olarak oluşturalım
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg">
                {error}
              </div>
            )}

            {success && (
              <div className="mb-6 p-4 text-sm text-green-700 bg-green-100 border border-green-200 rounded-lg">
                {success}
              </div>
            )}

            {/* File Upload Area */}
            <div
              className={`border-2 border-dashed rounded-lg p-6 text-center transition-colors ${
                dragActive 
                  ? 'border-orange-400 bg-orange-50 dark:bg-orange-900/20' 
                  : 'border-gray-300 dark:border-gray-600'
              }`}
              onDragEnter={() => setDragActive(true)}
              onDragLeave={() => setDragActive(false)}
              onDragOver={(e) => e.preventDefault()}
              onDrop={handleFileDrop}
            >
              <Upload className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              {selectedFile ? (
                <div className="space-y-2">
                  <p className="text-green-600 font-medium">✓ {selectedFile.name}</p>
                  <p className="text-sm text-gray-500">
                    {(selectedFile.size / 1024 / 1024).toFixed(2)} MB
                  </p>
                </div>
              ) : (
                <div className="space-y-2">
                  <p className="text-gray-600 dark:text-gray-400">
                    Dosyayı buraya sürükleyip bırakın veya
                  </p>
                  <label className="inline-block bg-orange-500 hover:bg-orange-600 text-white px-4 py-2 rounded cursor-pointer transition-colors">
                    Dosya Seç
                    <input
                      type="file"
                      className="hidden"
                      accept=".pdf,.doc,.docx"
                      onChange={handleFileInput}
                    />
                  </label>
                  <p className="text-xs text-gray-500">
                    PDF, DOC veya DOCX • Maks. 5MB
                  </p>
                </div>
              )}
            </div>

            <div className="mt-6 space-y-3">
              {selectedFile && (
                <button
                  onClick={handleCVUpload}
                  disabled={loading}
                  className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium disabled:opacity-50"
                >
                  {loading ? 'Yükleniyor...' : 'CV\'yi Yükle ve Devam Et'}
                </button>
              )}

              <button
                onClick={() => setStep('choice')}
                className="w-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 px-4 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
              >
                Geri Dön
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  if (step === 'manual') {
    return (
      <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 flex items-center justify-center p-4">
        <div className="max-w-md w-full">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-purple-600 rounded-full flex items-center justify-center mx-auto mb-4">
                <Edit className="w-8 h-8 text-white" />
              </div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                Manuel Profil Girişi
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Profil bilgilerinizi kendiniz girerek özelleştirin
              </p>
            </div>

            {error && (
              <div className="mb-6 p-4 text-sm text-red-700 bg-red-100 border border-red-200 rounded-lg">
                {error}
              </div>
            )}

            <form onSubmit={(e) => { e.preventDefault(); handleManualProfileSubmit(); }} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Ad Soyad *
                </label>
                <input
                  type="text"
                  required
                  value={manualProfile.name}
                  onChange={(e) => setManualProfile({...manualProfile, name: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Adınız ve soyadınız"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Kısa Açıklama
                </label>
                <textarea
                  value={manualProfile.bio}
                  onChange={(e) => setManualProfile({...manualProfile, bio: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Kendinizi kısaca tanıtın"
                  rows={3}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Konum
                </label>
                <input
                  type="text"
                  value={manualProfile.location}
                  onChange={(e) => setManualProfile({...manualProfile, location: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Şehir, Ülke"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Yetenekler
                </label>
                <input
                  type="text"
                  value={manualProfile.skills}
                  onChange={(e) => setManualProfile({...manualProfile, skills: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="React, Node.js, Python (virgülle ayırın)"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Deneyim (Yıl)
                </label>
                <input
                  type="number"
                  min="0"
                  max="50"
                  value={manualProfile.experience_years}
                  onChange={(e) => setManualProfile({...manualProfile, experience_years: e.target.value})}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="0"
                />
              </div>

              <div className="space-y-3 pt-4">
                <button
                  type="submit"
                  className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-3 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium"
                >
                  Profili Oluştur ve Devam Et
                </button>

                <button
                  type="button"
                  onClick={() => setStep('choice')}
                  className="w-full bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 py-3 px-4 rounded-lg hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors font-medium"
                >
                  Geri Dön
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default ProfileSetup; 