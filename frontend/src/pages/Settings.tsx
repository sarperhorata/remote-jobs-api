import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  ArrowLeft, 
  User, 
  Bell, 
  Shield, 
  Palette, 
  Globe, 
  Mail, 
  Smartphone,
  Eye,
  EyeOff,
  Save,
  Trash2,
  Download,
  Upload,
  Key,
  CreditCard,
  HelpCircle,
  Info,
  Sun,
  Moon,
  Check,
  X
} from 'lucide-react';
import { useAuth } from '../contexts/AuthContext';
import { useTheme } from '../contexts/ThemeContext';

interface PasswordRequirement {
  text: string;
  isValid: boolean;
}

const Settings: React.FC = () => {
  const navigate = useNavigate();
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  
  // Form states
  const [profileData, setProfileData] = useState({
    firstName: user?.firstName || '',
    lastName: user?.lastName || '',
    email: user?.email || '',
    phone: user?.phone || '',
    location: user?.location || '',
    bio: user?.bio || ''
  });

  const [notificationSettings, setNotificationSettings] = useState({
    emailNotifications: true,
    pushNotifications: true,
    jobAlerts: true,
    applicationUpdates: true,
    marketingEmails: false,
    weeklyDigest: true
  });

  const [privacySettings, setPrivacySettings] = useState<{
    profileVisibility: string;
    showEmail: boolean;
    showPhone: boolean;
    allowSearch: boolean;
    dataSharing: boolean;
  }>({
    profileVisibility: 'public',
    showEmail: false,
    showPhone: false,
    allowSearch: true,
    dataSharing: false
  });

  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const [showPassword, setShowPassword] = useState({
    current: false,
    new: false,
    confirm: false
  });

  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('profile');

  // Password validation
  const getPasswordRequirements = (password: string): PasswordRequirement[] => {
    return [
      {
        text: 'At least 8 characters long',
        isValid: password.length >= 8
      },
      {
        text: 'Contains at least one uppercase letter',
        isValid: /[A-Z]/.test(password)
      },
      {
        text: 'Contains at least one lowercase letter',
        isValid: /[a-z]/.test(password)
      },
      {
        text: 'Contains at least one number',
        isValid: /\d/.test(password)
      },
      {
        text: 'Contains at least one special character',
        isValid: /[!@#$%^&*(),.?":{}|<>]/.test(password)
      }
    ];
  };

  const isNewPasswordValid = (password: string): boolean => {
    const requirements = getPasswordRequirements(password);
    return requirements.every(req => req.isValid);
  };

  const newPasswordRequirements = getPasswordRequirements(passwordData.newPassword);

  const tabs = [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'privacy', name: 'Privacy', icon: Shield },
    { id: 'appearance', name: 'Appearance', icon: Palette },
    { id: 'security', name: 'Security', icon: Key },
    { id: 'account', name: 'Account', icon: CreditCard }
  ];

  const handleProfileSave = async () => {
    setIsLoading(true);
    try {
      // API call to update profile
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      console.log('Profile updated:', profileData);
    } catch (error) {
      console.error('Error updating profile:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handlePasswordChange = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      alert('New passwords do not match');
      return;
    }
    
    setIsLoading(true);
    try {
      // API call to change password
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call
      setPasswordData({ currentPassword: '', newPassword: '', confirmPassword: '' });
      console.log('Password changed successfully');
    } catch (error) {
      console.error('Error changing password:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteAccount = () => {
    if (window.confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
      // API call to delete account
      logout();
      navigate('/');
    }
  };

  const exportData = () => {
    const data = {
      profile: profileData,
      settings: {
        notifications: notificationSettings,
        privacy: privacySettings
      },
      exportDate: new Date().toISOString()
    };
    
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `buzz2remote-data-${new Date().toISOString().split('T')[0]}.json`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      {/* Header */}
      <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200/50 dark:border-gray-700/50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 text-gray-600 dark:text-gray-300 hover:text-gray-900 dark:hover:text-white hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5" />
              </button>
              <div>
                <h1 className="text-xl font-bold text-gray-900 dark:text-white">Settings</h1>
                <p className="text-sm text-gray-500 dark:text-gray-400">Manage your account preferences</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Sidebar */}
          <div className="lg:col-span-1">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-6">
              <nav className="space-y-2">
                {tabs.map((tab) => {
                  const Icon = tab.icon;
                  return (
                    <button
                      key={tab.id}
                      onClick={() => setActiveTab(tab.id)}
                      className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-all duration-200 ${
                        activeTab === tab.id
                          ? 'bg-gradient-to-r from-blue-500 to-purple-500 text-white shadow-lg'
                          : 'text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700/50'
                      }`}
                    >
                      <Icon className="w-5 h-5" />
                      <span className="font-medium">{tab.name}</span>
                    </button>
                  );
                })}
              </nav>
            </div>
          </div>

          {/* Main Content */}
          <div className="lg:col-span-3">
            <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-xl shadow-lg border border-gray-200/50 dark:border-gray-700/50 p-8">
              
              {/* Profile Settings */}
              {activeTab === 'profile' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Profile Settings</h2>
                    <p className="text-gray-600 dark:text-gray-400">Update your personal information</p>
                  </div>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        First Name
                      </label>
                      <input
                        type="text"
                        value={profileData.firstName}
                        onChange={(e) => setProfileData({...profileData, firstName: e.target.value})}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Last Name
                      </label>
                      <input
                        type="text"
                        value={profileData.lastName}
                        onChange={(e) => setProfileData({...profileData, lastName: e.target.value})}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        value={profileData.email}
                        onChange={(e) => setProfileData({...profileData, email: e.target.value})}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    
                    <div>
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Phone
                      </label>
                      <input
                        type="tel"
                        value={profileData.phone}
                        onChange={(e) => setProfileData({...profileData, phone: e.target.value})}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Location
                      </label>
                      <input
                        type="text"
                        value={profileData.location}
                        onChange={(e) => setProfileData({...profileData, location: e.target.value})}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      />
                    </div>
                    
                    <div className="md:col-span-2">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Bio
                      </label>
                      <textarea
                        value={profileData.bio}
                        onChange={(e) => setProfileData({...profileData, bio: e.target.value})}
                        rows={4}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                        placeholder="Tell us about yourself..."
                      />
                    </div>
                  </div>
                  
                  <div className="flex justify-end">
                    <button
                      onClick={handleProfileSave}
                      disabled={isLoading}
                      className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
                    >
                      <Save className="w-4 h-4" />
                      <span>{isLoading ? 'Saving...' : 'Save Changes'}</span>
                    </button>
                  </div>
                </div>
              )}

              {/* Notification Settings */}
              {activeTab === 'notifications' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Notification Preferences</h2>
                    <p className="text-gray-600 dark:text-gray-400">Choose how you want to be notified</p>
                  </div>
                  
                  <div className="space-y-4">
                    {Object.entries(notificationSettings).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Bell className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                          <div>
                            <h3 className="font-medium text-gray-900 dark:text-white">
                              {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              Receive notifications about {key.toLowerCase().replace(/([A-Z])/g, ' $1')}
                            </p>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={value}
                            onChange={(e) => setNotificationSettings({...notificationSettings, [key]: e.target.checked})}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Privacy Settings */}
              {activeTab === 'privacy' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Privacy Settings</h2>
                    <p className="text-gray-600 dark:text-gray-400">Control your privacy and data sharing</p>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                        Profile Visibility
                      </label>
                      <select
                        value={privacySettings.profileVisibility}
                        onChange={(e) => setPrivacySettings({...privacySettings, profileVisibility: e.target.value})}
                        className="w-full px-4 py-3 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                      >
                        <option value="public">Public</option>
                        <option value="private">Private</option>
                        <option value="friends">Friends Only</option>
                      </select>
                    </div>
                    
                    {Object.entries(privacySettings).filter(([key]) => key !== 'profileVisibility').map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                        <div className="flex items-center space-x-3">
                          <Shield className="w-5 h-5 text-gray-600 dark:text-gray-400" />
                          <div>
                            <h3 className="font-medium text-gray-900 dark:text-white">
                              {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}
                            </h3>
                            <p className="text-sm text-gray-500 dark:text-gray-400">
                              {key === 'showEmail' ? 'Show email address to other users' :
                               key === 'showPhone' ? 'Show phone number to other users' :
                               key === 'allowSearch' ? 'Allow others to find your profile' :
                               'Share data with third-party services'}
                            </p>
                          </div>
                        </div>
                        <label className="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            checked={typeof value === 'boolean' ? value : false}
                            onChange={(e) => setPrivacySettings({...privacySettings, [key]: e.target.checked})}
                            className="sr-only peer"
                          />
                          <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
                        </label>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Appearance Settings */}
              {activeTab === 'appearance' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Appearance</h2>
                    <p className="text-gray-600 dark:text-gray-400">Customize your app appearance</p>
                  </div>
                  
                  <div className="p-6 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-3">
                        <Palette className="w-6 h-6 text-gray-600 dark:text-gray-400" />
                        <div>
                          <h3 className="font-medium text-gray-900 dark:text-white">Theme</h3>
                          <p className="text-sm text-gray-500 dark:text-gray-400">
                            Switch between light and dark mode
                          </p>
                        </div>
                      </div>
                      <button
                        onClick={toggleTheme}
                        className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-4 py-2 rounded-lg font-medium transition-all duration-200"
                      >
                        {theme === 'dark' ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
                        <span>{theme === 'dark' ? 'Light Mode' : 'Dark Mode'}</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}

              {/* Security Settings */}
              {activeTab === 'security' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Security</h2>
                    <p className="text-gray-600 dark:text-gray-400">Manage your account security</p>
                  </div>
                  
                  <div className="space-y-6">
                    <div className="p-6 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Change Password</h3>
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Current Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPassword.current ? "text" : "password"}
                              value={passwordData.currentPassword}
                              onChange={(e) => setPasswordData({...passwordData, currentPassword: e.target.value})}
                              className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword({...showPassword, current: !showPassword.current})}
                              className="absolute inset-y-0 right-0 pr-3 flex items-center"
                            >
                              {showPassword.current ? <EyeOff className="w-5 h-5 text-gray-400" /> : <Eye className="w-5 h-5 text-gray-400" />}
                            </button>
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            New Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPassword.new ? "text" : "password"}
                              value={passwordData.newPassword}
                              onChange={(e) => setPasswordData({...passwordData, newPassword: e.target.value})}
                              className="w-full px-4 py-3 pr-20 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                            
                            {/* Password Policy Icon */}
                            {passwordData.newPassword.length > 0 && (
                              <div className="absolute right-12 top-1/2 transform -translate-y-1/2">
                                <div className="group cursor-help">
                                  <div className="w-4 h-4 flex items-center justify-center">
                                    {isNewPasswordValid(passwordData.newPassword) ? (
                                      <span className="text-green-500">
                                        <Check />
                                      </span>
                                    ) : (
                                      <span className="text-red-500">
                                        <X />
                                      </span>
                                    )}
                                  </div>
                                  <div className="absolute z-50 right-0 mt-2 w-64 p-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-lg opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none">
                                    <div className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                                      Password Requirements:
                                    </div>
                                    <div className="space-y-1">
                                      {newPasswordRequirements.map((requirement, index) => (
                                        <div key={index} className="flex items-center space-x-2">
                                          <div className="w-3 h-3 flex items-center justify-center">
                                            {requirement.isValid ? (
                                              <span className="text-green-500"><Check /></span>
                                            ) : (
                                              <span className="text-red-500"><X /></span>
                                            )}
                                          </div>
                                          <span className={`text-xs ${
                                            requirement.isValid ? 'text-green-700 dark:text-green-400' : 'text-red-700 dark:text-red-400'
                                          }`}>
                                            {requirement.text}
                                          </span>
                                        </div>
                                      ))}
                                    </div>
                                  </div>
                                </div>
                              </div>
                            )}
                            
                            {/* Show/Hide Password Button */}
                            <button
                              type="button"
                              onClick={() => setShowPassword({...showPassword, new: !showPassword.new})}
                              className="absolute inset-y-0 right-0 pr-3 flex items-center"
                            >
                              {showPassword.new ? <EyeOff className="w-5 h-5 text-gray-400" /> : <Eye className="w-5 h-5 text-gray-400" />}
                            </button>
                          </div>
                        </div>
                        
                        <div>
                          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                            Confirm New Password
                          </label>
                          <div className="relative">
                            <input
                              type={showPassword.confirm ? "text" : "password"}
                              value={passwordData.confirmPassword}
                              onChange={(e) => setPasswordData({...passwordData, confirmPassword: e.target.value})}
                              className="w-full px-4 py-3 pr-12 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                            />
                            <button
                              type="button"
                              onClick={() => setShowPassword({...showPassword, confirm: !showPassword.confirm})}
                              className="absolute inset-y-0 right-0 pr-3 flex items-center"
                            >
                              {showPassword.confirm ? <EyeOff className="w-5 h-5 text-gray-400" /> : <Eye className="w-5 h-5 text-gray-400" />}
                            </button>
                          </div>
                        </div>
                        
                        <button
                          onClick={handlePasswordChange}
                          disabled={isLoading || !passwordData.currentPassword || !passwordData.newPassword || !passwordData.confirmPassword}
                          className="w-full bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white px-6 py-3 rounded-lg font-medium transition-all duration-200 shadow-lg hover:shadow-xl disabled:opacity-50"
                        >
                          {isLoading ? 'Changing Password...' : 'Change Password'}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Account Settings */}
              {activeTab === 'account' && (
                <div className="space-y-6">
                  <div>
                    <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Account Management</h2>
                    <p className="text-gray-600 dark:text-gray-400">Manage your account data and preferences</p>
                  </div>
                  
                  <div className="space-y-4">
                    <div className="p-6 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                      <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-4">Data Export</h3>
                      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
                        Download a copy of your data including profile information, settings, and preferences.
                      </p>
                      <button
                        onClick={exportData}
                        className="flex items-center space-x-2 bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                      >
                        <Download className="w-4 h-4" />
                        <span>Export Data</span>
                      </button>
                    </div>
                    
                    <div className="p-6 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
                      <h3 className="text-lg font-medium text-red-900 dark:text-red-100 mb-4">Danger Zone</h3>
                      <p className="text-sm text-red-700 dark:text-red-300 mb-4">
                        Once you delete your account, there is no going back. Please be certain.
                      </p>
                      <button
                        onClick={handleDeleteAccount}
                        className="flex items-center space-x-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span>Delete Account</span>
                      </button>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings; 