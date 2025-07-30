import React, { useState, useEffect } from 'react';
import { jobService } from '../services/AllServices';
import { useAuth } from '../contexts/AuthContext';
import { User, Heart, FileText, Upload, ExternalLink, CheckCircle, AlertCircle, Loader } from 'lucide-react';
import { toast } from 'react-hot-toast';
import DragDropCVUpload from '../components/DragDropCVUpload';
import AICVAnalysis from '../components/AICVAnalysis';
import SkillsExtraction from '../components/SkillsExtraction';
import AutoProfileFill from '../components/AutoProfileFill';
import CoverLetterManager from '../components/CoverLetterManager';

interface ApplicationHistory {
  applications: any[];
  savedJobs: any[];
}

interface ParsedCVData {
  name: string;
  email: string;
  phone: string;
  location: string;
  summary: string;
  skills: string[];
  experience: any[];
  education: any[];
  languages: string[];
  certifications: string[];
}

interface Skill {
  id: string;
  name: string;
  category?: string;
  confidence?: number;
  source: 'cv' | 'manual' | 'ai';
}

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [applicationHistory, setApplicationHistory] = useState<ApplicationHistory>({ applications: [], savedJobs: [] });
  const [isLoading, setIsLoading] = useState(true);
  const [isUploading, setIsUploading] = useState(false);
  const [parsedData, setParsedData] = useState<ParsedCVData | null>(null);
  const [showParsedData, setShowParsedData] = useState(false);
  const [userSkills, setUserSkills] = useState<Skill[]>([]);
  const [isExtractingSkills, setIsExtractingSkills] = useState(false);

  useEffect(() => {
    const fetchApplicationHistory = async () => {
      if (!user?.id) return;
      
      try {
        setIsLoading(true);
        const data = await jobService.getMyApplications();
        setApplicationHistory(data || { applications: [], savedJobs: [] });
      } catch (error) {
        console.error('Error fetching application history:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchApplicationHistory();
  }, [user?.id]);

  const handleCvUpload = async (file: File) => {
    setCvFile(file);
    await uploadAndParseCV(file);
  };

  const uploadAndParseCV = async (file: File) => {
    try {
      setIsUploading(true);
      
      const formData = new FormData();
      formData.append('file', file);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/upload-cv`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
        body: formData,
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to upload CV');
      }
      
      const result = await response.json();
      
      if (result.success) {
        setParsedData(result.data.parsed_data);
        setShowParsedData(true);
        toast.success('CV uploaded and parsed successfully!');
        
        // Automatically extract skills from the uploaded CV
        setTimeout(() => {
          extractSkillsFromCV();
        }, 1000);
        
        // Update user context with new data
        // You might want to refresh the user data here
        window.location.reload(); // Simple refresh for now
      } else {
        throw new Error(result.message || 'Failed to parse CV');
      }
      
    } catch (error: any) {
      console.error('Error uploading CV:', error);
      toast.error(error.message || 'Failed to upload CV');
    } finally {
      setIsUploading(false);
    }
  };

  const handleLinkedInImport = async () => {
    if (linkedinUrl) {
      console.log('Importing LinkedIn profile:', linkedinUrl);
    }
  };

  const handleLinkedInCVFetch = async () => {
    try {
      setIsUploading(true);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/auth/linkedin/fetch-cv`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to fetch LinkedIn CV');
      }
      
      const result = await response.json();
      
      toast.success(`CV imported successfully! Found ${result.cv_data.experience_count} experiences, ${result.cv_data.education_count} education entries, and ${result.cv_data.skills_count} skills.`);
      
      // Refresh the page to show updated data
      window.location.reload();
      
    } catch (error: any) {
      console.error('Error fetching LinkedIn CV:', error);
      toast.error(error.message || 'Failed to fetch LinkedIn CV');
    } finally {
      setIsUploading(false);
    }
  };

  const applyParsedData = () => {
    if (!parsedData) return;
    
    // Here you would typically update the user profile with parsed data
    // For now, we'll just show a success message
    toast.success('Profile updated with CV data!');
    setShowParsedData(false);
  };

  const handleRemoveCurrentCV = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/cv`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        toast.success('CV removed successfully');
        // Refresh user data or update local state
        window.location.reload();
      } else {
        throw new Error('Failed to remove CV');
      }
    } catch (error: any) {
      console.error('Error removing CV:', error);
      toast.error(error.message || 'Failed to remove CV');
    }
  };

  // Skills extraction functions
  const extractSkillsFromCV = async () => {
    try {
      setIsExtractingSkills(true);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/skills/extract-from-cv`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to extract skills');
      }
      
      const result = await response.json();
      
      if (result.success) {
        // Convert extracted skills to Skill interface format
        const extractedSkills: Skill[] = result.data.skills.map((skill: any, index: number) => ({
          id: skill.id || `skill-${index}`,
          name: skill.name,
          category: skill.category,
          confidence: skill.confidence,
          source: skill.source || 'cv'
        }));
        
        setUserSkills(extractedSkills);
        toast.success(`Successfully extracted ${extractedSkills.length} skills from your CV!`);
      } else {
        throw new Error(result.message || 'Failed to extract skills');
      }
      
    } catch (error: any) {
      console.error('Error extracting skills:', error);
      toast.error(error.message || 'Failed to extract skills');
    } finally {
      setIsExtractingSkills(false);
    }
  };

  const updateUserSkills = async (skills: Skill[]) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/skills/update-skills`, {
        method: 'PUT',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          skills: skills.map(skill => skill.name),
          extracted_skills: skills
        }),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update skills');
      }
      
      const result = await response.json();
      
      if (result.success) {
        setUserSkills(skills);
        toast.success('Skills updated successfully!');
      } else {
        throw new Error(result.message || 'Failed to update skills');
      }
      
    } catch (error: any) {
      console.error('Error updating skills:', error);
      toast.error(error.message || 'Failed to update skills');
    }
  };

  const loadUserSkills = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/skills/user-skills`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (response.ok) {
        const result = await response.json();
        const skills: Skill[] = result.extracted_skills?.map((skill: any, index: number) => ({
          id: skill.id || `skill-${index}`,
          name: skill.name,
          category: skill.category,
          confidence: skill.confidence,
          source: skill.source || 'cv'
        })) || [];
        
        setUserSkills(skills);
      }
    } catch (error) {
      console.error('Error loading user skills:', error);
    }
  };

  // Load user skills on component mount
  useEffect(() => {
    if (user?.id) {
      loadUserSkills();
    }
  }, [user?.id]);

  // Handle profile auto-fill updates
  const handleProfileUpdate = async (profileData: any) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/auto-fill/apply`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(profileData),
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to update profile');
      }
      
      // Refresh the page to show updated data
      window.location.reload();
      
    } catch (error: any) {
      console.error('Error updating profile:', error);
      throw error;
    }
  };

  const menuItems = [
    {
      id: 'profile',
      label: 'My Profile',
      icon: User,
      description: 'Personal information & CV'
    },
    {
      id: 'saved',
      label: 'My Favorites',
      icon: Heart,
      description: 'Saved job opportunities'
    },
    {
      id: 'applications',
      label: 'My Applications',
      icon: FileText,
      description: 'Application history & status'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="flex gap-8">
          {/* Left Sidebar Menu */}
          <div className="w-80 bg-white rounded-lg shadow-md h-fit">
            {/* User Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                  {user?.name?.charAt(0) || 'U'}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{user?.name || 'User'}</h2>
                  <p className="text-gray-600">{user?.email}</p>
                  <p className="text-sm text-blue-600 font-medium">Product Manager</p>
                </div>
              </div>
            </div>

            {/* Navigation Menu */}
            <nav className="p-4">
              <ul className="space-y-2">
                {menuItems.map((item) => {
                  const IconComponent = item.icon;
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => setActiveTab(item.id)}
                        className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                          activeTab === item.id
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
                        }`}
                      >
                        <IconComponent 
                          size={20} 
                          className={activeTab === item.id ? 'text-blue-600' : 'text-gray-500'} 
                        />
                        <div>
                          <div className="font-medium">{item.label}</div>
                          <div className="text-sm text-gray-500">{item.description}</div>
                        </div>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </nav>

            {/* Stats Cards */}
            <div className="p-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-blue-50 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {applicationHistory?.applications?.length || 0}
                  </div>
                  <div className="text-xs text-blue-700">Applications</div>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {applicationHistory?.savedJobs?.length || 0}
                  </div>
                  <div className="text-xs text-purple-700">Saved Jobs</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Content Area */}
          <div className="flex-1 bg-white rounded-lg shadow-md">
            {/* Content Header */}
            <div className="p-6 border-b border-gray-200">
              <h1 className="text-2xl font-bold text-gray-900">
                {menuItems.find(item => item.id === activeTab)?.label}
              </h1>
              <p className="text-gray-600 mt-1">
                {menuItems.find(item => item.id === activeTab)?.description}
              </p>
            </div>

            {/* Content */}
            <div className="p-6">
              {activeTab === 'profile' && (
                <div className="space-y-8">
                  {/* Profile Summary Card */}
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-100">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Summary</h3>
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Full Name</label>
                        <p className="text-gray-900">{user?.profile?.name || user?.name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <p className="text-gray-900">{user?.profile?.email || user?.email}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Phone</label>
                        <p className="text-gray-900">{user?.profile?.phone || 'Not provided'}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Location</label>
                        <p className="text-gray-900">{user?.profile?.location || 'Not provided'}</p>
                      </div>
                    </div>
                  </div>

                  {/* CV Upload Section */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                      <Upload className="mr-2" size={20} />
                      CV / Resume
                    </h3>
                    
                    {/* LinkedIn CV Import */}
                    {user?.linkedin_connected && (
                      <div className="mb-6 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-4 border border-blue-200">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-blue-900 mb-1">LinkedIn CV Import</h4>
                            <p className="text-sm text-blue-700">
                              Import your experience, education, and skills directly from LinkedIn
                            </p>
                          </div>
                          <button
                            onClick={handleLinkedInCVFetch}
                            disabled={isUploading}
                            className={`px-4 py-2 rounded-lg flex items-center gap-2 transition ${
                              isUploading 
                                ? 'bg-gray-400 text-gray-600 cursor-not-allowed' 
                                : 'bg-blue-600 text-white hover:bg-blue-700'
                            }`}
                          >
                            {isUploading ? (
                              <>
                                <Loader className="animate-spin" size={16} />
                                Importing...
                              </>
                            ) : (
                              <>
                                <ExternalLink size={16} />
                                Import from LinkedIn
                              </>
                            )}
                          </button>
                        </div>
                      </div>
                    )}
                    
                    {/* Modern Drag & Drop CV Upload */}
                    <DragDropCVUpload
                      onFileUpload={handleCvUpload}
                      onFileRemove={handleRemoveCurrentCV}
                      currentCVUrl={user?.profile?.cvUrl}
                      isUploading={isUploading}
                      maxFileSize={5}
                      acceptedFileTypes={['.pdf', '.doc', '.docx']}
                    />
                  </div>

                  {/* Auto Profile Fill */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                      <User className="mr-2" size={20} />
                      Auto Profile Fill
                    </h3>
                    <AutoProfileFill
                      onProfileUpdate={handleProfileUpdate}
                      currentProfile={{
                        name: user?.profile?.name || user?.name,
                        email: user?.profile?.email || user?.email,
                        phone: user?.profile?.phone,
                        location: user?.profile?.location,
                        title: (user?.profile as any)?.title,
                        summary: (user?.profile as any)?.summary,
                        skills: user?.skills?.map((skill: any) => skill.name || skill) || [],
                        experience: user?.experience,
                        education: user?.education,
                        languages: (user?.profile as any)?.languages,
                        certifications: (user?.profile as any)?.certifications,
                        linkedin_url: (user?.profile as any)?.linkedin_url,
                        github_url: (user?.profile as any)?.github_url,
                        portfolio_url: (user?.profile as any)?.portfolio_url
                      }}
                      className="mt-4"
                    />
                  </div>

                  {/* Cover Letter Manager */}
                  <CoverLetterManager
                    className="mt-8"
                    onUpdate={() => {
                      // Refresh user data if needed
                      window.location.reload();
                    }}
                  />

                  {/* AI CV Analysis */}
                  <AICVAnalysis
                    cvUrl={user?.profile?.cvUrl}
                    className="mt-8"
                  />

                  {/* Parsed Data Preview */}
                  {showParsedData && parsedData && (
                    <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                      <div className="flex items-center justify-between mb-4">
                        <h3 className="text-lg font-semibold text-green-900 flex items-center">
                          <CheckCircle className="mr-2" size={20} />
                          CV Parsed Successfully!
                        </h3>
                        <button
                          onClick={() => setShowParsedData(false)}
                          className="text-green-600 hover:text-green-800"
                        >
                          ×
                        </button>
                      </div>
                      
                      <div className="space-y-4">
                        <div className="grid grid-cols-2 gap-4">
                          {parsedData.name && (
                            <div>
                              <label className="text-sm font-medium text-green-700">Name</label>
                              <p className="text-green-900">{parsedData.name}</p>
                            </div>
                          )}
                          {parsedData.email && (
                            <div>
                              <label className="text-sm font-medium text-green-700">Email</label>
                              <p className="text-green-900">{parsedData.email}</p>
                            </div>
                          )}
                          {parsedData.phone && (
                            <div>
                              <label className="text-sm font-medium text-green-700">Phone</label>
                              <p className="text-green-900">{parsedData.phone}</p>
                            </div>
                          )}
                          {parsedData.location && (
                            <div>
                              <label className="text-sm font-medium text-green-700">Location</label>
                              <p className="text-green-900">{parsedData.location}</p>
                            </div>
                          )}
                        </div>
                        
                        {parsedData.skills && parsedData.skills.length > 0 && (
                          <div>
                            <label className="text-sm font-medium text-green-700">Skills Found</label>
                            <div className="flex flex-wrap gap-2 mt-1">
                              {parsedData.skills.slice(0, 10).map((skill, index) => (
                                <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm">
                                  {skill}
                                </span>
                              ))}
                              {parsedData.skills.length > 10 && (
                                <span className="text-green-600 text-sm">
                                  +{parsedData.skills.length - 10} more
                                </span>
                              )}
                            </div>
                          </div>
                        )}
                        
                        <div className="flex gap-3 pt-4">
                          <button
                            onClick={applyParsedData}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition"
                          >
                            Apply to Profile
                          </button>
                          <button
                            onClick={() => setShowParsedData(false)}
                            className="bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition"
                          >
                            Dismiss
                          </button>
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Skills Extraction */}
                  <div>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-lg font-semibold flex items-center">
                        <span>Skills & Expertise</span>
                        {user?.cv_source === 'linkedin' && (
                          <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                            From LinkedIn
                          </span>
                        )}
                      </h3>
                      {/* Extract Skills Button */}
                      {user?.profile?.cvUrl && (
                        <button
                          onClick={extractSkillsFromCV}
                          disabled={isExtractingSkills}
                          className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            isExtractingSkills
                              ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                              : 'bg-green-600 text-white hover:bg-green-700'
                          }`}
                        >
                          {isExtractingSkills ? (
                            <>
                              <Loader className="animate-spin mr-2" size={16} />
                              Extracting...
                            </>
                          ) : (
                            <>
                              <CheckCircle className="mr-2" size={16} />
                              Extract Skills from CV
                            </>
                          )}
                        </button>
                      )}
                    </div>
                    <SkillsExtraction
                      skills={userSkills}
                      onSkillsUpdate={updateUserSkills}
                      isExtracting={isExtractingSkills}
                      className="mt-4"
                    />
                    {user?.linkedin_connected && (
                      <p className="text-sm mt-2">Connect your LinkedIn account to import your skills</p>
                    )}
                  </div>

                  {/* Experience */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center justify-between">
                      <span>Professional Experience</span>
                      {user?.cv_source === 'linkedin' && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                          From LinkedIn
                        </span>
                      )}
                    </h3>
                    <div className="space-y-6">
                      {user?.experience && user.experience.length > 0 ? (
                        user.experience.map((exp, index) => (
                          <div key={index} className="relative pl-8 pb-6">
                            <div className="absolute left-0 top-0 w-4 h-4 bg-blue-600 rounded-full"></div>
                            {index < (user.experience.length || 0) - 1 && (
                              <div className="absolute left-2 top-4 w-0.5 h-full bg-gray-300"></div>
                            )}
                            <div className="bg-gray-50 rounded-lg p-4">
                              <h4 className="font-semibold text-gray-900">{exp.title}</h4>
                              <p className="text-blue-600 font-medium">{exp.company}</p>
                              <p className="text-sm text-gray-600 mb-2">
                                {new Date(exp.startDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} -{' '}
                                {exp.endDate
                                  ? new Date(exp.endDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
                                  : 'Present'}
                              </p>
                              <p className="text-gray-700">{exp.description}</p>
                            </div>
                          </div>
                        ))
                      ) : user?.profile?.experience && user.profile.experience.length > 0 ? (
                        user.profile.experience.map((exp, index) => (
                          <div key={index} className="relative pl-8 pb-6">
                            <div className="absolute left-0 top-0 w-4 h-4 bg-blue-600 rounded-full"></div>
                            {index < (user.profile.experience.length || 0) - 1 && (
                              <div className="absolute left-2 top-4 w-0.5 h-full bg-gray-300"></div>
                            )}
                            <div className="bg-gray-50 rounded-lg p-4">
                              <h4 className="font-semibold text-gray-900">{exp.title}</h4>
                              <p className="text-blue-600 font-medium">{exp.company}</p>
                              <p className="text-sm text-gray-600 mb-2">
                                {new Date(exp.startDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} -{' '}
                                {exp.endDate
                                  ? new Date(exp.endDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
                                  : 'Present'}
                              </p>
                              <p className="text-gray-700">{exp.description}</p>
                            </div>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <p>No experience information available</p>
                          {user?.linkedin_connected && (
                            <p className="text-sm mt-2">Connect your LinkedIn account to import your experience</p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>

                  {/* Education */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center justify-between">
                      <span>Education</span>
                      {user?.cv_source === 'linkedin' && (
                        <span className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded-full">
                          From LinkedIn
                        </span>
                      )}
                    </h3>
                    <div className="space-y-4">
                      {user?.education && user.education.length > 0 ? (
                        user.education.map((edu, index) => (
                          <div key={index} className="bg-gray-50 rounded-lg p-4">
                            <h4 className="font-semibold text-gray-900">{edu.school}</h4>
                            <p className="text-blue-600 font-medium">
                              {edu.degree} {edu.field && `in ${edu.field}`}
                            </p>
                            <p className="text-sm text-gray-600">
                              {new Date(edu.startDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} -{' '}
                              {edu.endDate
                                ? new Date(edu.endDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
                                : 'Present'}
                            </p>
                          </div>
                        ))
                      ) : user?.profile?.education && user.profile.education.length > 0 ? (
                        user.profile.education.map((edu, index) => (
                          <div key={index} className="bg-gray-50 rounded-lg p-4">
                            <h4 className="font-semibold text-gray-900">{edu.school}</h4>
                            <p className="text-blue-600 font-medium">
                              {edu.degree} in {edu.field}
                            </p>
                            <p className="text-sm text-gray-600">
                              {new Date(edu.startDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} -{' '}
                              {edu.endDate
                                ? new Date(edu.endDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
                                : 'Present'}
                            </p>
                          </div>
                        ))
                      ) : (
                        <div className="text-center py-8 text-gray-500">
                          <p>No education information available</p>
                          {user?.linkedin_connected && (
                            <p className="text-sm mt-2">Connect your LinkedIn account to import your education</p>
                          )}
                        </div>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'applications' && (
                <div>
                  <div className="space-y-4">
                    {applicationHistory?.applications?.length > 0 ? (
                      applicationHistory.applications.map((application, index) => (
                        <div
                          key={application.jobId || index}
                          className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md transition-all"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900 text-lg">
                                {application.job?.title || 'Job Title'}
                              </h3>
                              <p className="text-blue-600 font-medium">
                                {application.job?.company?.name || 'Company Name'}
                              </p>
                              <p className="text-gray-600 mt-1">
                                {application.job?.location || 'Location not specified'}
                              </p>
                            </div>
                            <div className="text-right">
                              <span
                                className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                                  application.status === 'applied'
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : application.status === 'interviewing'
                                    ? 'bg-blue-100 text-blue-800'
                                    : application.status === 'offered'
                                    ? 'bg-green-100 text-green-800'
                                    : application.status === 'rejected'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {application.status ? application.status.charAt(0).toUpperCase() + application.status.slice(1) : 'Pending'}
                              </span>
                              <div className="text-sm text-gray-500 mt-2">
                                Applied on{' '}
                                {application.appliedAt ? new Date(application.appliedAt).toLocaleDateString() : 'Recent'}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12">
                        <FileText size={48} className="mx-auto text-gray-400 mb-4" />
                        <p className="text-gray-500 text-lg">No applications yet</p>
                        <p className="text-gray-400">Start applying to jobs to see your application history here</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'saved' && (
                <div>
                  <div className="space-y-4">
                    {applicationHistory?.savedJobs?.length > 0 ? (
                      applicationHistory.savedJobs.map((job, index) => (
                        <div
                          key={job.id || index}
                          className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md transition-all"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900 text-lg">{job.title}</h3>
                              <p className="text-blue-600 font-medium">
                                {typeof job.company === 'string' ? job.company : (job.company?.name || job.companyName)}
                              </p>
                              <p className="text-gray-600 mt-1">{job.location || 'Remote'}</p>
                              {job.skills && (
                                <div className="mt-3 flex flex-wrap gap-2">
                                  {job.skills.slice(0, 5).map((skill: string, skillIndex: number) => (
                                    <span
                                      key={skillIndex}
                                      className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                  {job.skills.length > 5 && (
                                    <span className="text-gray-500 text-xs">
                                      +{job.skills.length - 5} more
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                            <div className="flex flex-col gap-2">
                              <button
                                className="text-red-600 hover:text-red-800 text-sm font-medium"
                                onClick={() => jobService.unsaveJob(user?.id!, job.id)}
                              >
                                Remove from Favorites
                              </button>
                              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                                View Job Details
                              </button>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12">
                        <Heart size={48} className="mx-auto text-gray-400 mb-4" />
                        <p className="text-gray-500 text-lg">No saved jobs yet</p>
                        <p className="text-gray-400">Save interesting job opportunities to review them later</p>
                      </div>
                    )}
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

export default Profile;
