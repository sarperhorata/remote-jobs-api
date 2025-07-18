import React, { useState, useEffect } from 'react';
import { Settings as SettingsIcon, User, Bell, Shield, Palette, Globe, Mail, Smartphone, Save, X } from 'lucide-react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';

interface UserSettings {
  notifications: {
    email: boolean;
    browser: boolean;
    job_alerts: boolean;
    application_updates: boolean;
    marketing: boolean;
  };
  privacy: {
    profile_visibility: 'public' | 'private';
    show_salary: boolean;
    show_applications: boolean;
  };
  preferences: {
    theme: 'light' | 'dark' | 'auto';
    language: string;
    timezone: string;
    currency: string;
  };
  account: {
    email: string;
    phone?: string;
    delete_account: boolean;
  };
}

const Settings: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [settings, setSettings] = useState<UserSettings>({
    notifications: {
      email: true,
      browser: true,
      job_alerts: true,
      application_updates: true,
      marketing: false,
    },
    privacy: {
      profile_visibility: 'public',
      show_salary: true,
      show_applications: false,
    },
    preferences: {
      theme: 'auto',
      language: 'en',
      timezone: 'UTC',
      currency: 'USD',
    },
    account: {
      email: user?.email || '',
      phone: '',
      delete_account: false,
    },
  });
  const [activeTab, setActiveTab] = useState('notifications');
  const [loading, setLoading] = useState(false);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    loadSettings();
  }, [user]);

  const loadSettings = () => {
    try {
      const savedSettings = localStorage.getItem('userSettings');
      if (savedSettings) {
        setSettings(JSON.parse(savedSettings));
      }
    } catch (error) {
      console.error('Error loading settings:', error);
    }
  };

  const handleSave = async () => {
    setLoading(true);
    try {
      // Save to localStorage
      localStorage.setItem('userSettings', JSON.stringify(settings));
      
      // TODO: Save to backend API
      console.log('Settings saved:', settings);
      
      setSaved(true);
      setTimeout(() => setSaved(false), 3000);
    } catch (error) {
      console.error('Error saving settings:', error);
    } finally {
      setLoading(false);
    }
  };

  const updateSettings = (section: keyof UserSettings, key: string, value: any) => {
    setSettings(prev => ({
      ...prev,
      [section]: {
        ...prev[section],
        [key]: value,
      },
    }));
  };

  const tabs = [
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'privacy', label: 'Privacy', icon: Shield },
    { id: 'preferences', label: 'Preferences', icon: Palette },
    { id: 'account', label: 'Account', icon: User },
  ];

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Please log in to access settings</h1>
            <p className="text-gray-600">You need to be authenticated to access this page.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      
      <div className="max-w-4xl mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">Settings</h1>
          <p className="text-gray-600">Manage your account preferences and privacy</p>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200">
          {/* Tab Navigation */}
          <div className="border-b border-gray-200">
            <nav className="flex space-x-8 px-6">
              {tabs.map((tab) => {
                const Icon = tab.icon;
                return (
                  <button
                    key={tab.id}
                    onClick={() => setActiveTab(tab.id)}
                    className={`flex items-center gap-2 py-4 px-1 border-b-2 font-medium text-sm ${
                      activeTab === tab.id
                        ? 'border-blue-500 text-blue-600'
                        : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                  >
                    <Icon className="w-4 h-4" />
                    {tab.label}
                  </button>
                );
              })}
            </nav>
          </div>

          {/* Tab Content */}
          <div className="p-6">
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900">Notification Preferences</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Email Notifications</h4>
                      <p className="text-sm text-gray-600">Receive notifications via email</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.email}
                        onChange={(e) => updateSettings('notifications', 'email', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Browser Notifications</h4>
                      <p className="text-sm text-gray-600">Receive notifications in your browser</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.browser}
                        onChange={(e) => updateSettings('notifications', 'browser', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Job Alerts</h4>
                      <p className="text-sm text-gray-600">Get notified about new job opportunities</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.job_alerts}
                        onChange={(e) => updateSettings('notifications', 'job_alerts', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Application Updates</h4>
                      <p className="text-sm text-gray-600">Receive updates about your job applications</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.application_updates}
                        onChange={(e) => updateSettings('notifications', 'application_updates', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Marketing Communications</h4>
                      <p className="text-sm text-gray-600">Receive promotional emails and updates</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.notifications.marketing}
                        onChange={(e) => updateSettings('notifications', 'marketing', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'privacy' && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900">Privacy Settings</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Profile Visibility
                    </label>
                    <select
                      value={settings.privacy.profile_visibility}
                      onChange={(e) => updateSettings('privacy', 'profile_visibility', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="public">Public</option>
                      <option value="private">Private</option>
                    </select>
                    <p className="text-sm text-gray-600 mt-1">
                      Control who can see your profile information
                    </p>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Show Salary Information</h4>
                      <p className="text-sm text-gray-600">Display salary information on your profile</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.privacy.show_salary}
                        onChange={(e) => updateSettings('privacy', 'show_salary', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>

                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="font-medium text-gray-900">Show Application History</h4>
                      <p className="text-sm text-gray-600">Display your job application history</p>
                    </div>
                    <label className="relative inline-flex items-center cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.privacy.show_applications}
                        onChange={(e) => updateSettings('privacy', 'show_applications', e.target.checked)}
                        className="sr-only peer"
                      />
                      <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                    </label>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'preferences' && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900">Preferences</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Theme
                    </label>
                    <select
                      value={settings.preferences.theme}
                      onChange={(e) => updateSettings('preferences', 'theme', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="light">Light</option>
                      <option value="dark">Dark</option>
                      <option value="auto">Auto</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Language
                    </label>
                    <select
                      value={settings.preferences.language}
                      onChange={(e) => updateSettings('preferences', 'language', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="en">English</option>
                      <option value="tr">Türkçe</option>
                      <option value="es">Español</option>
                      <option value="fr">Français</option>
                      <option value="de">Deutsch</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Timezone
                    </label>
                    <select
                      value={settings.preferences.timezone}
                      onChange={(e) => updateSettings('preferences', 'timezone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="UTC">UTC</option>
                      <option value="Europe/Istanbul">Europe/Istanbul</option>
                      <option value="America/New_York">America/New_York</option>
                      <option value="America/Los_Angeles">America/Los_Angeles</option>
                      <option value="Europe/London">Europe/London</option>
                      <option value="Europe/Paris">Europe/Paris</option>
                      <option value="Asia/Tokyo">Asia/Tokyo</option>
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Currency
                    </label>
                    <select
                      value={settings.preferences.currency}
                      onChange={(e) => updateSettings('preferences', 'currency', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="USD">USD ($)</option>
                      <option value="EUR">EUR (€)</option>
                      <option value="TRY">TRY (₺)</option>
                      <option value="GBP">GBP (£)</option>
                      <option value="JPY">JPY (¥)</option>
                    </select>
                  </div>
                </div>
              </div>
            )}

            {activeTab === 'account' && (
              <div className="space-y-6">
                <h3 className="text-lg font-medium text-gray-900">Account Information</h3>
                
                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Email Address
                    </label>
                    <input
                      type="email"
                      value={settings.account.email}
                      onChange={(e) => updateSettings('account', 'email', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter your email address"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Phone Number
                    </label>
                    <input
                      type="tel"
                      value={settings.account.phone}
                      onChange={(e) => updateSettings('account', 'phone', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Enter your phone number"
                    />
                  </div>

                  <div className="border-t pt-6">
                    <h4 className="text-lg font-medium text-red-600 mb-4">Danger Zone</h4>
                    <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                      <div className="flex items-center justify-between">
                        <div>
                          <h5 className="font-medium text-red-800">Delete Account</h5>
                          <p className="text-sm text-red-600 mt-1">
                            Once you delete your account, there is no going back. Please be certain.
                          </p>
                        </div>
                        <button
                          onClick={() => updateSettings('account', 'delete_account', true)}
                          className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500"
                        >
                          Delete Account
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Save Button */}
          <div className="border-t border-gray-200 px-6 py-4 bg-gray-50">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                {saved && (
                  <div className="flex items-center text-green-600">
                    <Save className="w-4 h-4 mr-1" />
                    <span className="text-sm font-medium">Settings saved successfully!</span>
                  </div>
                )}
              </div>
              <button
                onClick={handleSave}
                disabled={loading}
                className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
              >
                {loading ? (
                  <>
                    <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                    Saving...
                  </>
                ) : (
                  <>
                    <Save className="w-4 h-4 mr-2" />
                    Save Changes
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Settings; 