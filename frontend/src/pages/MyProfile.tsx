import React, { useState, useEffect, useCallback } from 'react';
import { User, Mail, MapPin, Briefcase, Settings, Edit3, Save, X, Camera } from 'lucide-react';
import Header from '../components/Header';
import { useAuth } from '../contexts/AuthContext';

interface UserProfile {
  id: string;
  name: string;
  email: string;
  location?: string;
  bio?: string;
  job_titles?: string[];
  skills?: string[];
  experience_level?: string;
  work_preferences?: string[];
  salary_expectations?: string;
  created_at?: string;
  profile_picture?: string;
}

interface UserStats {
  applications_count: number;
  saved_jobs_count: number;
  profile_views: number;
  last_active: string;
}

const MyProfile: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [profile, setProfile] = useState<UserProfile | null>(null);
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);
  const [editing, setEditing] = useState(false);
  const [editForm, setEditForm] = useState<Partial<UserProfile>>({});

  const loadUserProfile = useCallback(async () => {
    try {
      // For now, use user data from auth context and localStorage preferences
      const preferences = JSON.parse(localStorage.getItem('userPreferences') || '{}');
      
      const profileData: UserProfile = {
        id: user?.id || 'demo-user',
        name: user?.name || 'User',
        email: user?.email || 'user@example.com',
        location: preferences.location || '',
        bio: preferences.bio || 'Professional seeking remote opportunities in technology.',
        job_titles: preferences.job_titles || ['Software Developer'],
        skills: preferences.skills || ['JavaScript', 'React', 'Node.js'],
        experience_level: preferences.experience_levels?.[0] || 'Mid Level',
        work_preferences: preferences.work_types || ['Remote'],
        salary_expectations: preferences.salary_ranges?.[0] || '$60,000 - $80,000',
        created_at: user?.created_at || new Date().toISOString(),
        profile_picture: user?.profile_picture || user?.profilePicture || null
      };
      
      setProfile(profileData);
      setEditForm(profileData);
    } catch (error) {
      console.error('Error loading profile:', error);
    }
  }, [user]);

  const loadUserStats = useCallback(async () => {
    try {
      // Mock stats - in production this would come from API
      const savedJobs = JSON.parse(localStorage.getItem('savedJobs') || '[]');
      const applications = JSON.parse(localStorage.getItem('myApplications') || '[]');
      
      setStats({
        applications_count: applications.length,
        saved_jobs_count: savedJobs.length,
        profile_views: Math.floor(Math.random() * 50) + 10, // Mock data
        last_active: new Date().toISOString()
      });
    } catch (error) {
      console.error('Error loading stats:', error);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadUserProfile();
      loadUserStats();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user, loadUserProfile, loadUserStats]);

  const handleSaveProfile = async () => {
    try {
      // Save to localStorage (in production, this would be saved to backend)
      const preferences = {
        location: editForm.location,
        bio: editForm.bio,
        job_titles: editForm.job_titles,
        skills: editForm.skills,
        experience_levels: editForm.experience_level ? [editForm.experience_level] : [],
        work_types: editForm.work_preferences,
        salary_ranges: editForm.salary_expectations ? [editForm.salary_expectations] : []
      };
      
      localStorage.setItem('userPreferences', JSON.stringify(preferences));
      
      // Update profile state
      setProfile(prev => prev ? { ...prev, ...editForm } : null);
      setEditing(false);
      
      // TODO: Save to backend API
      console.log('Profile updated:', editForm);
    } catch (error) {
      console.error('Error saving profile:', error);
    }
  };

  const handleCancelEdit = () => {
    setEditForm(profile || {});
    setEditing(false);
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="max-w-md mx-auto">
            <User className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Please Login</h1>
            <p className="text-gray-600 dark:text-gray-300">You need to be logged in to view your profile.</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading your profile...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      <Header />
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        {/* Profile Header */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6 mb-6">
          <div className="flex items-start justify-between mb-6">
            <div className="flex items-center gap-6">
              {/* Profile Picture */}
              <div className="relative">
                <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-2xl shadow-lg">
                  {profile?.name?.charAt(0)?.toUpperCase() || 'U'}
                </div>
                <button className="absolute bottom-0 right-0 p-1 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors">
                  <Camera className="w-3 h-3" />
                </button>
              </div>
              
              {/* Basic Info */}
              <div>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-1">
                  {profile?.name}
                </h1>
                <p className="text-gray-600 dark:text-gray-300 flex items-center gap-2 mb-2">
                  <Mail className="w-4 h-4" />
                  {profile?.email}
                </p>
                {profile?.location && (
                  <p className="text-gray-600 dark:text-gray-300 flex items-center gap-2">
                    <MapPin className="w-4 h-4" />
                    {profile.location}
                  </p>
                )}
              </div>
            </div>
            
            {/* Edit Button */}
            <div className="flex gap-2">
              {editing ? (
                <>
                  <button
                    onClick={handleSaveProfile}
                    className="px-4 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md flex items-center gap-2 transition-colors"
                  >
                    <Save className="w-4 h-4" />
                    Save
                  </button>
                  <button
                    onClick={handleCancelEdit}
                    className="px-4 py-2 bg-gray-600 hover:bg-gray-700 text-white rounded-md flex items-center gap-2 transition-colors"
                  >
                    <X className="w-4 h-4" />
                    Cancel
                  </button>
                </>
              ) : (
                <button
                  onClick={() => setEditing(true)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md flex items-center gap-2 transition-colors"
                >
                  <Edit3 className="w-4 h-4" />
                  Edit Profile
                </button>
              )}
            </div>
          </div>
          
          {/* Bio */}
          <div>
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">About</h3>
            {editing ? (
              <textarea
                value={editForm.bio || ''}
                onChange={(e) => setEditForm({...editForm, bio: e.target.value})}
                className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                rows={3}
                placeholder="Tell us about yourself..."
              />
            ) : (
              <p className="text-gray-600 dark:text-gray-300">
                {profile?.bio || 'No bio added yet.'}
              </p>
            )}
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Stats */}
          <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6">
            <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
              <Settings className="w-5 h-5" />
              Activity Stats
            </h2>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Applications</span>
                <span className="font-semibold text-gray-900 dark:text-white">{stats?.applications_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Saved Jobs</span>
                <span className="font-semibold text-gray-900 dark:text-white">{stats?.saved_jobs_count || 0}</span>
              </div>
              <div className="flex justify-between items-center">
                <span className="text-gray-600 dark:text-gray-300">Profile Views</span>
                <span className="font-semibold text-gray-900 dark:text-white">{stats?.profile_views || 0}</span>
              </div>
              <div className="pt-2 border-t border-gray-200 dark:border-slate-600">
                <span className="text-sm text-gray-500 dark:text-gray-400">
                  Member since {profile?.created_at ? new Date(profile.created_at).toLocaleDateString() : 'N/A'}
                </span>
              </div>
            </div>
          </div>

          {/* Professional Info */}
          <div className="lg:col-span-2 space-y-6">
            {/* Job Preferences */}
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <Briefcase className="w-5 h-5" />
                Professional Information
              </h2>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                {/* Job Titles */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Job Titles
                  </label>
                  {editing ? (
                    <input
                      type="text"
                      value={editForm.job_titles?.join(', ') || ''}
                      onChange={(e) => setEditForm({...editForm, job_titles: e.target.value.split(', ').filter(t => t.trim())})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Software Developer, Frontend Engineer"
                    />
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {profile?.job_titles?.map((title, index) => (
                        <span key={index} className="px-3 py-1 bg-blue-100 dark:bg-blue-900/30 text-blue-800 dark:text-blue-300 rounded-full text-sm">
                          {title}
                        </span>
                      )) || <span className="text-gray-500 dark:text-gray-400">No job titles added</span>}
                    </div>
                  )}
                </div>

                {/* Experience Level */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Experience Level
                  </label>
                  {editing ? (
                    <select
                      value={editForm.experience_level || ''}
                      onChange={(e) => setEditForm({...editForm, experience_level: e.target.value})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select Level</option>
                      <option value="Entry Level">Entry Level</option>
                      <option value="Mid Level">Mid Level</option>
                      <option value="Senior Level">Senior Level</option>
                      <option value="Lead/Principal">Lead/Principal</option>
                      <option value="Executive">Executive</option>
                    </select>
                  ) : (
                    <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 rounded-full text-sm">
                      {profile?.experience_level || 'Not specified'}
                    </span>
                  )}
                </div>

                {/* Work Preferences */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Work Preferences
                  </label>
                  {editing ? (
                    <input
                      type="text"
                      value={editForm.work_preferences?.join(', ') || ''}
                      onChange={(e) => setEditForm({...editForm, work_preferences: e.target.value.split(', ').filter(p => p.trim())})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Remote, Hybrid, On-site"
                    />
                  ) : (
                    <div className="flex flex-wrap gap-2">
                      {profile?.work_preferences?.map((pref, index) => (
                        <span key={index} className="px-3 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-800 dark:text-purple-300 rounded-full text-sm">
                          {pref}
                        </span>
                      )) || <span className="text-gray-500 dark:text-gray-400">No preferences set</span>}
                    </div>
                  )}
                </div>

                {/* Salary Expectations */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Salary Expectations
                  </label>
                  {editing ? (
                    <input
                      type="text"
                      value={editForm.salary_expectations || ''}
                      onChange={(e) => setEditForm({...editForm, salary_expectations: e.target.value})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="$60,000 - $80,000"
                    />
                  ) : (
                    <span className="px-3 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-800 dark:text-yellow-300 rounded-full text-sm">
                      {profile?.salary_expectations || 'Not specified'}
                    </span>
                  )}
                </div>
              </div>
            </div>

            {/* Skills */}
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Skills</h2>
              {editing ? (
                <textarea
                  value={editForm.skills?.join(', ') || ''}
                  onChange={(e) => setEditForm({...editForm, skills: e.target.value.split(', ').filter(s => s.trim())})}
                  className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  rows={3}
                  placeholder="JavaScript, React, Node.js, Python, etc."
                />
              ) : (
                <div className="flex flex-wrap gap-2">
                  {profile?.skills?.map((skill, index) => (
                    <span key={index} className="px-3 py-1 bg-gray-100 dark:bg-slate-700 text-gray-800 dark:text-gray-300 rounded-full text-sm border dark:border-slate-600">
                      {skill}
                    </span>
                  )) || <span className="text-gray-500 dark:text-gray-400">No skills added</span>}
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default MyProfile; 