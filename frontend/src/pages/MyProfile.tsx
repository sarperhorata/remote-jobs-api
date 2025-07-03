import React, { useState, useEffect, useCallback } from 'react';
import { 
  User, Edit3, Save, X, MapPin, Mail, Briefcase, Settings, 
  Download, Camera, Plus, Calendar, GraduationCap,
  Linkedin, Github, Twitter, Globe
} from 'lucide-react';
import Header from '../components/Header';
import { useAuth } from '../contexts/AuthContext';
// import { toast } from 'react-hot-toast';

// Temporary toast replacement
const toast = {
  success: (message: string) => console.log('✅', message),
  error: (message: string) => console.error('❌', message)
};

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
  
  // Social Media Links
  linkedin_url?: string;
  github_url?: string;
  twitter_url?: string;
  instagram_url?: string;
  facebook_url?: string;
  youtube_url?: string;
  personal_website?: string;
  
  // Professional Info (for LinkedIn import)
  work_experience?: WorkExperience[];
  education?: Education[];
  certificates?: Certificate[];
}

interface WorkExperience {
  title: string;
  company: string;
  location?: string;
  start_date: string;
  end_date?: string;
  current: boolean;
  description?: string;
}

interface Education {
  degree: string;
  institution: string;
  field_of_study?: string;
  start_date: string;
  end_date?: string;
  current: boolean;
  gpa?: string;
}

interface Certificate {
  name: string;
  issuer: string;
  issue_date: string;
  expiry_date?: string;
  credential_url?: string;
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
  const [importingLinkedIn, setImportingLinkedIn] = useState(false);

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
        profile_picture: user?.profile_picture || user?.profilePicture || null,
        
        // Social Media Links
        linkedin_url: preferences.linkedin_url || '',
        github_url: preferences.github_url || '',
        twitter_url: preferences.twitter_url || '',
        instagram_url: preferences.instagram_url || '',
        facebook_url: preferences.facebook_url || '',
        youtube_url: preferences.youtube_url || '',
        personal_website: preferences.personal_website || '',
        
        // Professional Info (for LinkedIn import)
        work_experience: preferences.work_experience || [],
        education: preferences.education || [],
        certificates: preferences.certificates || []
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
        salary_ranges: editForm.salary_expectations ? [editForm.salary_expectations] : [],
        linkedin_url: editForm.linkedin_url,
        github_url: editForm.github_url,
        twitter_url: editForm.twitter_url,
        instagram_url: editForm.instagram_url,
        facebook_url: editForm.facebook_url,
        youtube_url: editForm.youtube_url,
        personal_website: editForm.personal_website,
        work_experience: editForm.work_experience,
        education: editForm.education,
        certificates: editForm.certificates
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

  // LinkedIn Import Handler with OAuth
  const handleLinkedInImport = async () => {
    try {
      setImportingLinkedIn(true);
      
      // LinkedIn OAuth URL
      const linkedInAuthUrl = `https://www.linkedin.com/oauth/v2/authorization?` +
        `response_type=code&` +
        `client_id=${process.env.REACT_APP_LINKEDIN_CLIENT_ID}&` +
        `redirect_uri=${encodeURIComponent(window.location.origin + '/auth/linkedin/callback')}&` +
        `scope=r_liteprofile%20r_emailaddress&` +
        `state=${Math.random().toString(36).substring(7)}`;
      
      // Store current user email for verification
      localStorage.setItem('linkedin_auth_email', user?.email || '');
      
      // Open LinkedIn OAuth in popup
      const popup = window.open(
        linkedInAuthUrl,
        'linkedinAuth',
        'width=600,height=600,scrollbars=yes,resizable=yes'
      );
      
      // Listen for popup to close and handle the result
      const checkClosed = setInterval(() => {
        if (popup?.closed) {
          clearInterval(checkClosed);
          setImportingLinkedIn(false);
          
          // Check if we received LinkedIn data
          const linkedInData = localStorage.getItem('linkedin_profile_data');
          if (linkedInData) {
            const profileData = JSON.parse(linkedInData);
            
            // Verify email matches
            if (profileData.email === user?.email) {
              // Update profile with LinkedIn data
              const updatedProfile = {
                ...profile,
                name: profileData.name || profile.name,
                profile_picture: profileData.picture || profile.profile_picture,
                linkedin_url: profileData.profileUrl || profile.linkedin_url,
                bio: profileData.summary || profile.bio,
                location: profileData.location || profile.location,
                work_experience: [
                  ...profile.work_experience,
                  ...profileData.experience.map((exp: any) => ({
                    title: exp.title,
                    company: exp.company,
                    location: exp.location || '',
                    start_date: exp.startDate,
                    end_date: exp.endDate,
                    current: exp.isCurrent || false,
                    description: exp.description || ''
                  }))
                ],
                education: [
                  ...profile.education,
                  ...profileData.education.map((edu: any) => ({
                    institution: edu.schoolName,
                    degree: edu.degreeName,
                    field_of_study: edu.fieldOfStudy || '',
                    start_date: edu.startDate,
                    end_date: edu.endDate,
                    current: edu.isCurrent || false,
                    gpa: ''
                  }))
                ]
              };
              
              setProfile(updatedProfile);
              setEditForm(updatedProfile);
              
              // Clean up
              localStorage.removeItem('linkedin_profile_data');
              localStorage.removeItem('linkedin_auth_email');
              
              toast.success('LinkedIn profile imported successfully!');
            } else {
              toast.error('LinkedIn email does not match your account email.');
            }
          }
        }
      }, 1000);
      
    } catch (error) {
      console.error('LinkedIn import error:', error);
      setImportingLinkedIn(false);
      toast.error('Failed to import LinkedIn profile. Please try again.');
    }
  };

  // Add work experience
  const addWorkExperience = () => {
    const newExperience: WorkExperience = {
      title: '',
      company: '',
      location: '',
      start_date: '',
      end_date: '',
      current: false,
      description: ''
    };

    setEditForm(prev => ({
      ...prev,
      work_experience: [...(prev.work_experience || []), newExperience]
    }));
  };

  // Update work experience
  const updateWorkExperience = (index: number, field: keyof WorkExperience, value: any) => {
    const experiences = editForm.work_experience || [];
    const updatedExperiences = [...experiences];
    updatedExperiences[index] = { ...updatedExperiences[index], [field]: value };
    setEditForm({ ...editForm, work_experience: updatedExperiences });
  };

  // Remove work experience
  const removeWorkExperience = (index: number) => {
    const experiences = editForm.work_experience || [];
    const updatedExperiences = experiences.filter((_, i) => i !== index);
    setEditForm({ ...editForm, work_experience: updatedExperiences });
  };

  // Add education
  const addEducation = () => {
    const newEducation: Education = {
      institution: '',
      degree: '',
      field_of_study: '',
      start_date: '',
      end_date: '',
      current: false,
      gpa: ''
    };

    setEditForm(prev => ({
      ...prev,
      education: [...(prev.education || []), newEducation]
    }));
  };

  // Update education
  const updateEducation = (index: number, field: keyof Education, value: string | boolean) => {
    setEditForm(prev => ({
      ...prev,
      education: prev.education?.map((edu, i) => 
        i === index ? { ...edu, [field]: value } : edu
      ) || []
    }));
  };

  // Remove education
  const removeEducation = (index: number) => {
    setEditForm(prev => ({
      ...prev,
      education: prev.education?.filter((_, i) => i !== index) || []
    }));
  };

  // Handle profile image change
  const handleProfileImageChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setEditForm({...editForm, profile_picture: URL.createObjectURL(file)});
    }
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
                <div className="w-20 h-20 rounded-full bg-gradient-to-r from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold text-2xl shadow-lg overflow-hidden">
                  {editForm.profile_picture ? (
                    <img src={editForm.profile_picture} alt="Profile" className="w-full h-full object-cover" />
                  ) : profile?.profile_picture ? (
                    <img src={profile.profile_picture} alt="Profile" className="w-full h-full object-cover" />
                  ) : (
                    profile?.name?.charAt(0)?.toUpperCase() || 'U'
                  )}
                </div>
                {editing && (
                  <>
                    <input
                      type="file"
                      id="profile-picture-upload"
                      accept="image/*"
                      onChange={handleProfileImageChange}
                      className="hidden"
                    />
                    <label
                      htmlFor="profile-picture-upload"
                      className="absolute bottom-0 right-0 p-1 bg-blue-600 text-white rounded-full hover:bg-blue-700 transition-colors cursor-pointer"
                    >
                      <Camera className="w-3 h-3" />
                    </label>
                  </>
                )}
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

            {/* Social Media Links */}
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Social Links</h2>
                {!editing && profile?.linkedin_url && (
                  <button
                    onClick={handleLinkedInImport}
                    disabled={importingLinkedIn}
                    className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm rounded-md flex items-center gap-2 transition-colors disabled:opacity-50"
                  >
                    {importingLinkedIn ? (
                      <>
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                        Importing...
                      </>
                    ) : (
                      <>
                        <Download className="w-4 h-4" />
                        Import from LinkedIn
                      </>
                    )}
                  </button>
                )}
              </div>
              
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {/* LinkedIn */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Linkedin className="w-4 h-4" />
                    LinkedIn
                  </label>
                  {editing ? (
                    <input
                      type="url"
                      value={editForm.linkedin_url || ''}
                      onChange={(e) => setEditForm({...editForm, linkedin_url: e.target.value})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://linkedin.com/in/yourprofile"
                    />
                  ) : (
                    profile?.linkedin_url ? (
                      <a href={profile.linkedin_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                        {profile.linkedin_url}
                      </a>
                    ) : <span className="text-gray-500 dark:text-gray-400">Not connected</span>
                  )}
                </div>
                
                {/* GitHub */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Github className="w-4 h-4" />
                    GitHub
                  </label>
                  {editing ? (
                    <input
                      type="url"
                      value={editForm.github_url || ''}
                      onChange={(e) => setEditForm({...editForm, github_url: e.target.value})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://github.com/yourusername"
                    />
                  ) : (
                    profile?.github_url ? (
                      <a href={profile.github_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                        {profile.github_url}
                      </a>
                    ) : <span className="text-gray-500 dark:text-gray-400">Not connected</span>
                  )}
                </div>
                
                {/* Twitter */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Twitter className="w-4 h-4" />
                    Twitter/X
                  </label>
                  {editing ? (
                    <input
                      type="url"
                      value={editForm.twitter_url || ''}
                      onChange={(e) => setEditForm({...editForm, twitter_url: e.target.value})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://twitter.com/yourhandle"
                    />
                  ) : (
                    profile?.twitter_url ? (
                      <a href={profile.twitter_url} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                        {profile.twitter_url}
                      </a>
                    ) : <span className="text-gray-500 dark:text-gray-400">Not connected</span>
                  )}
                </div>
                
                {/* Personal Website */}
                <div>
                  <label className="flex items-center gap-2 text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    <Globe className="w-4 h-4" />
                    Personal Website
                  </label>
                  {editing ? (
                    <input
                      type="url"
                      value={editForm.personal_website || ''}
                      onChange={(e) => setEditForm({...editForm, personal_website: e.target.value})}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="https://yourwebsite.com"
                    />
                  ) : (
                    profile?.personal_website ? (
                      <a href={profile.personal_website} target="_blank" rel="noopener noreferrer" className="text-blue-600 dark:text-blue-400 hover:underline">
                        {profile.personal_website}
                      </a>
                    ) : <span className="text-gray-500 dark:text-gray-400">Not added</span>
                  )}
                </div>
              </div>
            </div>

            {/* Work Experience */}
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <Briefcase className="w-5 h-5" />
                  Work Experience
                </h2>
                {editing && (
                  <button
                    type="button"
                    onClick={addWorkExperience}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-1 text-sm"
                  >
                    <Plus className="w-4 h-4" />
                    Add Experience
                  </button>
                )}
              </div>
              
              {editing ? (
                <div className="space-y-4">
                  {editForm.work_experience?.map((exp, index) => (
                    <div key={index} className="border border-gray-200 dark:border-slate-600 rounded-lg p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input
                          type="text"
                          value={exp.title}
                          onChange={(e) => updateWorkExperience(index, 'title', e.target.value)}
                          placeholder="Job Title"
                          className="w-full p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                        />
                        <input
                          type="text"
                          value={exp.company}
                          onChange={(e) => updateWorkExperience(index, 'company', e.target.value)}
                          placeholder="Company"
                          className="w-full p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                        />
                        <input
                          type="text"
                          value={exp.location}
                          onChange={(e) => updateWorkExperience(index, 'location', e.target.value)}
                          placeholder="Location"
                          className="w-full p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                        />
                        <div className="flex gap-2">
                          <input
                            type="month"
                            value={exp.start_date}
                            onChange={(e) => updateWorkExperience(index, 'start_date', e.target.value)}
                            placeholder="Start Date"
                            className="flex-1 p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                          />
                          {!exp.current && (
                            <input
                              type="month"
                              value={exp.end_date || ''}
                              onChange={(e) => updateWorkExperience(index, 'end_date', e.target.value)}
                              placeholder="End Date"
                              className="flex-1 p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                            />
                          )}
                        </div>
                      </div>
                      <div className="mt-2 flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={exp.current}
                            onChange={(e) => updateWorkExperience(index, 'current', e.target.checked)}
                            className="rounded"
                          />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Currently working here</span>
                        </label>
                        <button
                          type="button"
                          onClick={() => removeWorkExperience(index)}
                          className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                      <textarea
                        value={exp.description || ''}
                        onChange={(e) => updateWorkExperience(index, 'description', e.target.value)}
                        placeholder="Description (optional)"
                        className="w-full mt-2 p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                        rows={2}
                      />
                    </div>
                  ))}
                  {(!editForm.work_experience || editForm.work_experience.length === 0) && (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                      No work experience added yet. Click "Add Experience" to start.
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {profile?.work_experience?.map((exp, index) => (
                    <div key={index} className="border-l-2 border-blue-500 pl-4">
                      <h4 className="font-medium text-gray-900 dark:text-white">{exp.title}</h4>
                      <p className="text-gray-600 dark:text-gray-300 flex items-center gap-2">
                        <Briefcase className="w-4 h-4" />
                        {exp.company} {exp.location && `• ${exp.location}`}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {exp.start_date} - {exp.current ? 'Present' : exp.end_date}
                      </p>
                      {exp.description && (
                        <p className="mt-2 text-gray-600 dark:text-gray-300">{exp.description}</p>
                      )}
                    </div>
                  )) || <p className="text-gray-500 dark:text-gray-400">No work experience added</p>}
                </div>
              )}
            </div>

            {/* Education */}
            <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white flex items-center gap-2">
                  <GraduationCap className="w-5 h-5" />
                  Education
                </h2>
                {editing && (
                  <button
                    type="button"
                    onClick={addEducation}
                    className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 flex items-center gap-1 text-sm"
                  >
                    <Plus className="w-4 h-4" />
                    Add Education
                  </button>
                )}
              </div>
              
              {editing ? (
                <div className="space-y-4">
                  {editForm.education?.map((edu, index) => (
                    <div key={index} className="border border-gray-200 dark:border-slate-600 rounded-lg p-4">
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <input
                          type="text"
                          value={edu.institution}
                          onChange={(e) => updateEducation(index, 'institution', e.target.value)}
                          placeholder="Institution"
                          className="w-full p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                        />
                        <input
                          type="text"
                          value={edu.degree}
                          onChange={(e) => updateEducation(index, 'degree', e.target.value)}
                          placeholder="Degree"
                          className="w-full p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                        />
                        <input
                          type="text"
                          value={edu.field_of_study}
                          onChange={(e) => updateEducation(index, 'field_of_study', e.target.value)}
                          placeholder="Field of Study"
                          className="w-full p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                        />
                        <div className="flex gap-2">
                          <input
                            type="month"
                            value={edu.start_date}
                            onChange={(e) => updateEducation(index, 'start_date', e.target.value)}
                            placeholder="Start Date"
                            className="flex-1 p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                          />
                          {!edu.current && (
                            <input
                              type="month"
                              value={edu.end_date || ''}
                              onChange={(e) => updateEducation(index, 'end_date', e.target.value)}
                              placeholder="End Date"
                              className="flex-1 p-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg"
                            />
                          )}
                        </div>
                      </div>
                      <div className="mt-2 flex items-center justify-between">
                        <label className="flex items-center gap-2">
                          <input
                            type="checkbox"
                            checked={edu.current}
                            onChange={(e) => updateEducation(index, 'current', e.target.checked)}
                            className="rounded"
                          />
                          <span className="text-sm text-gray-700 dark:text-gray-300">Currently studying here</span>
                        </label>
                        <button
                          type="button"
                          onClick={() => removeEducation(index)}
                          className="text-red-600 dark:text-red-400 hover:text-red-700 dark:hover:text-red-300"
                        >
                          <X className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  ))}
                  {(!editForm.education || editForm.education.length === 0) && (
                    <p className="text-gray-500 dark:text-gray-400 text-center py-4">
                      No education added yet. Click "Add Education" to start.
                    </p>
                  )}
                </div>
              ) : (
                <div className="space-y-4">
                  {profile?.education?.map((edu, index) => (
                    <div key={index} className="border-l-2 border-green-500 pl-4">
                      <h4 className="font-medium text-gray-900 dark:text-white">{edu.degree}</h4>
                      <p className="text-gray-600 dark:text-gray-300">
                        {edu.field_of_study && `${edu.field_of_study} • `}{edu.institution}
                      </p>
                      <p className="text-sm text-gray-500 dark:text-gray-400 flex items-center gap-2">
                        <Calendar className="w-4 h-4" />
                        {edu.start_date} - {edu.current ? 'Present' : edu.end_date}
                      </p>
                    </div>
                  )) || <p className="text-gray-500 dark:text-gray-400">No education added</p>}
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