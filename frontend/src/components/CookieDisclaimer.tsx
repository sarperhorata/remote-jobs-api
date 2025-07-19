import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { X, Cookie, Settings } from '../components/icons/EmojiIcons';

interface CookiePreferences {
  essential: boolean;
  performance: boolean;
  functionality: boolean;
  marketing: boolean;
}

const CookieDisclaimer: React.FC = () => {
  const [isVisible, setIsVisible] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [preferences, setPreferences] = useState<CookiePreferences>({
    essential: true, // Always true, cannot be disabled
    performance: false,
    functionality: false,
    marketing: false
  });

  useEffect(() => {
    // Check if user has already made a choice
    const cookieConsent = localStorage.getItem('cookieConsent');
    if (!cookieConsent) {
      setIsVisible(true);
    }
  }, []);

  const handleAcceptAll = () => {
    const allPreferences = {
      essential: true,
      performance: true,
      functionality: true,
      marketing: true
    };
    setPreferences(allPreferences);
    localStorage.setItem('cookieConsent', JSON.stringify(allPreferences));
    setIsVisible(false);
  };

  const handleAcceptEssential = () => {
    const essentialOnly = {
      essential: true,
      performance: false,
      functionality: false,
      marketing: false
    };
    setPreferences(essentialOnly);
    localStorage.setItem('cookieConsent', JSON.stringify(essentialOnly));
    setIsVisible(false);
  };

  const handleSavePreferences = () => {
    localStorage.setItem('cookieConsent', JSON.stringify(preferences));
    setShowSettings(false);
    setIsVisible(false);
  };

  const handlePreferenceChange = (type: keyof CookiePreferences) => {
    if (type === 'essential') return; // Essential cookies cannot be disabled
    setPreferences(prev => ({
      ...prev,
      [type]: !prev[type]
    }));
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-0 left-0 right-0 z-50 bg-white border-t border-gray-200 shadow-lg">
      <div className="container mx-auto px-4 py-4">
        {!showSettings ? (
          // Main cookie banner
          <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
            <div className="flex items-start gap-3 flex-1">
              <Cookie className="w-6 h-6 text-blue-600 mt-1 flex-shrink-0" />
              <div className="flex-1">
                <h3 className="font-semibold text-gray-900 mb-1">
                  We use cookies to enhance your experience
                </h3>
                <p className="text-sm text-gray-600 mb-3">
                  We use cookies to analyze site traffic, personalize content, and provide social media features. 
                  By continuing to use our site, you consent to our use of cookies.
                </p>
                <div className="flex flex-wrap gap-2">
                  <Link 
                    to="/cookie-policy" 
                    className="text-sm text-blue-600 hover:text-blue-700 underline"
                  >
                    Learn more
                  </Link>
                  <button
                    onClick={() => setShowSettings(true)}
                    className="text-sm text-gray-600 hover:text-gray-800 flex items-center gap-1"
                  >
                    <Settings className="w-4 h-4" />
                    Customize
                  </button>
                </div>
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2 flex-shrink-0">
              <button
                onClick={handleAcceptEssential}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Essential Only
              </button>
              <button
                onClick={handleAcceptAll}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                Accept All
              </button>
            </div>
          </div>
        ) : (
          // Cookie settings
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="font-semibold text-gray-900 flex items-center gap-2">
                <Settings className="w-5 h-5" />
                Cookie Preferences
              </h3>
              <button
                onClick={() => setShowSettings(false)}
                className="text-gray-500 hover:text-gray-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>
            
            <div className="space-y-3">
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Essential Cookies</h4>
                  <p className="text-sm text-gray-600">Required for basic website functionality</p>
                </div>
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={preferences.essential}
                    disabled
                    className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                  />
                  <span className="ml-2 text-xs text-gray-500">Always active</span>
                </div>
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Performance Cookies</h4>
                  <p className="text-sm text-gray-600">Help us understand how visitors use our website</p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.performance}
                  onChange={() => handlePreferenceChange('performance')}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Functionality Cookies</h4>
                  <p className="text-sm text-gray-600">Remember your preferences and settings</p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.functionality}
                  onChange={() => handlePreferenceChange('functionality')}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
              
              <div className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div>
                  <h4 className="font-medium text-gray-900">Marketing Cookies</h4>
                  <p className="text-sm text-gray-600">Used to deliver relevant advertisements</p>
                </div>
                <input
                  type="checkbox"
                  checked={preferences.marketing}
                  onChange={() => handlePreferenceChange('marketing')}
                  className="w-4 h-4 text-blue-600 bg-gray-100 border-gray-300 rounded focus:ring-blue-500"
                />
              </div>
            </div>
            
            <div className="flex flex-col sm:flex-row gap-2 pt-2">
              <button
                onClick={handleSavePreferences}
                className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-lg transition-colors"
              >
                Save Preferences
              </button>
              <button
                onClick={() => setShowSettings(false)}
                className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-100 hover:bg-gray-200 rounded-lg transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CookieDisclaimer; 