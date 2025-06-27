import React, { useState } from 'react';
import { User, 
  MapPin, 
  Briefcase, 
  Star, 
  CheckCircle, 
  ArrowRight, 
  ArrowLeft,
  Bell,
  Target,
  Zap } from './icons/EmojiIcons';

interface OnboardingProps {
  isOpen: boolean;
  onClose: () => void;
  onComplete: () => void;
}

interface UserProfile {
  fullName: string;
  email: string;
  location: string;
  jobTitle: string;
  experience: string;
  skills: string[];
  preferences: {
    jobTypes: string[];
    salaryRange: string;
    remoteOnly: boolean;
    notifications: boolean;
  };
}

const Onboarding: React.FC<OnboardingProps> = ({ isOpen, onClose, onComplete }) => {
  const [currentStep, setCurrentStep] = useState(1);
  const [profile, setProfile] = useState<UserProfile>({
    fullName: '',
    email: '',
    location: '',
    jobTitle: '',
    experience: '',
    skills: [],
    preferences: {
      jobTypes: [],
      salaryRange: '',
      remoteOnly: true,
      notifications: true
    }
  });

  const totalSteps = 5;

  const skillOptions = [
    'React', 'Vue.js', 'Angular', 'Node.js', 'Python', 'Java', 'JavaScript', 'TypeScript',
    'AWS', 'Docker', 'Kubernetes', 'MongoDB', 'PostgreSQL', 'GraphQL', 'REST APIs',
    'Machine Learning', 'Data Science', 'UI/UX Design', 'Product Management', 'DevOps'
  ];

  const jobTypeOptions = [
    { value: 'full-time', label: 'Full-time' },
    { value: 'part-time', label: 'Part-time' },
    { value: 'contract', label: 'Contract' },
    { value: 'freelance', label: 'Freelance' }
  ];

  const experienceOptions = [
    { value: 'entry', label: 'Entry Level (0-2 years)' },
    { value: 'mid', label: 'Mid Level (2-5 years)' },
    { value: 'senior', label: 'Senior Level (5+ years)' },
    { value: 'lead', label: 'Lead/Principal' },
    { value: 'executive', label: 'Executive' }
  ];

  const salaryRanges = [
    { value: '0-50k', label: '$0 - $50k' },
    { value: '50k-80k', label: '$50k - $80k' },
    { value: '80k-120k', label: '$80k - $120k' },
    { value: '120k-150k', label: '$120k - $150k' },
    { value: '150k+', label: '$150k+' }
  ];

  const handleNext = () => {
    if (currentStep < totalSteps) {
      setCurrentStep(currentStep + 1);
    } else {
      handleComplete();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const handleComplete = () => {
    // Save profile data
    localStorage.setItem('userProfile', JSON.stringify(profile));
    localStorage.setItem('onboardingCompleted', 'true');
    onComplete();
  };

  const handleSkillToggle = (skill: string) => {
    setProfile(prev => ({
      ...prev,
      skills: prev.skills.includes(skill)
        ? prev.skills.filter(s => s !== skill)
        : [...prev.skills, skill]
    }));
  };

  const handleJobTypeToggle = (jobType: string) => {
    setProfile(prev => ({
      ...prev,
      preferences: {
        ...prev.preferences,
        jobTypes: prev.preferences.jobTypes.includes(jobType)
          ? prev.preferences.jobTypes.filter(t => t !== jobType)
          : [...prev.preferences.jobTypes, jobType]
      }
    }));
  };

  if (!isOpen) return null;

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <div className="text-center">
            <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-6">
              <Zap className="w-10 h-10 text-white" />
            </div>
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Welcome to Buzz2Remote! 🎉</h2>
            <p className="text-lg text-gray-600 mb-8 max-w-md mx-auto">
              Let's set up your profile to find the perfect remote opportunities tailored just for you.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
              <div className="text-center">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Target className="w-6 h-6 text-blue-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">AI-Powered Matching</h3>
                <p className="text-sm text-gray-600">Get personalized job recommendations</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <CheckCircle className="w-6 h-6 text-green-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">One-Click Apply</h3>
                <p className="text-sm text-gray-600">Apply instantly with your saved profile</p>
              </div>
              <div className="text-center">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mx-auto mb-3">
                  <Bell className="w-6 h-6 text-purple-600" />
                </div>
                <h3 className="font-semibold text-gray-900 mb-2">Smart Alerts</h3>
                <p className="text-sm text-gray-600">Never miss your dream job</p>
              </div>
            </div>
          </div>
        );

      case 2:
        return (
          <div>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <User className="w-8 h-8 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Tell us about yourself</h2>
              <p className="text-gray-600">Basic information to get started</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label htmlFor="fullName" className="block text-sm font-medium text-gray-700 mb-2">Full Name</label>
                <input
                  id="fullName"
                  type="text"
                  value={profile.fullName}
                  onChange={(e) => setProfile(prev => ({ ...prev, fullName: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your full name"
                />
              </div>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">Email Address</label>
                <input
                  id="email"
                  type="email"
                  value={profile.email}
                  onChange={(e) => setProfile(prev => ({ ...prev, email: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="Enter your email address"
                />
              </div>
              
              <div>
                <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-2">Location</label>
                <div className="relative">
                  <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                  <input
                    id="location"
                    type="text"
                    value={profile.location}
                    onChange={(e) => setProfile(prev => ({ ...prev, location: e.target.value }))}
                    className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    placeholder="e.g. San Francisco, CA or Remote"
                  />
                </div>
              </div>
            </div>
          </div>
        );

      case 3:
        return (
          <div>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Briefcase className="w-8 h-8 text-green-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Your professional background</h2>
              <p className="text-gray-600">Help us understand your experience level</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label htmlFor="jobTitle" className="block text-sm font-medium text-gray-700 mb-2">Current/Desired Job Title</label>
                <input
                  id="jobTitle"
                  type="text"
                  value={profile.jobTitle}
                  onChange={(e) => setProfile(prev => ({ ...prev, jobTitle: e.target.value }))}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  placeholder="e.g. Frontend Developer, Product Manager"
                />
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Experience Level</label>
                <div className="grid grid-cols-1 gap-3">
                  {experienceOptions.map(option => (
                    <label key={option.value} className="flex items-center cursor-pointer">
                      <input
                        id={`experience-${option.value}`}
                        type="radio"
                        name="experience"
                        value={option.value}
                        checked={profile.experience === option.value}
                        onChange={(e) => setProfile(prev => ({ ...prev, experience: e.target.value }))}
                        className="mr-3 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">{option.label}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          </div>
        );

      case 4:
        return (
          <div>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Star className="w-8 h-8 text-purple-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Your skills & expertise</h2>
              <p className="text-gray-600">Select the skills you have experience with</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-4">
                  Skills (Select all that apply)
                </label>
                <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                  {skillOptions.map(skill => (
                    <button
                      key={skill}
                      onClick={() => handleSkillToggle(skill)}
                      className={`px-4 py-2 rounded-lg border text-sm font-medium transition-colors ${
                        profile.skills.includes(skill)
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-blue-500'
                      }`}
                    >
                      {skill}
                    </button>
                  ))}
                </div>
                <p className="text-sm text-gray-500 mt-3">
                  Selected: {profile.skills.length} skills
                </p>
              </div>
            </div>
          </div>
        );

      case 5:
        return (
          <div>
            <div className="text-center mb-8">
              <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <Target className="w-8 h-8 text-orange-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Job preferences</h2>
              <p className="text-gray-600">Set your job search preferences</p>
            </div>
            
            <div className="space-y-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Job Types</label>
                <div className="grid grid-cols-2 gap-3">
                  {jobTypeOptions.map(option => (
                    <button
                      key={option.value}
                      onClick={() => handleJobTypeToggle(option.value)}
                      className={`px-4 py-3 rounded-lg border text-sm font-medium transition-colors ${
                        profile.preferences.jobTypes.includes(option.value)
                          ? 'bg-blue-600 text-white border-blue-600'
                          : 'bg-white text-gray-700 border-gray-300 hover:border-blue-500'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-3">Salary Range</label>
                <div className="grid grid-cols-1 gap-2">
                  {salaryRanges.map(range => (
                    <label key={range.value} className="flex items-center cursor-pointer">
                      <input
                        id={`salary-${range.value}`}
                        type="radio"
                        name="salaryRange"
                        value={range.value}
                        checked={profile.preferences.salaryRange === range.value}
                        onChange={(e) => setProfile(prev => ({
                          ...prev,
                          preferences: { ...prev.preferences, salaryRange: e.target.value }
                        }))}
                        className="mr-3 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-gray-700">{range.label}</span>
                    </label>
                  ))}
                </div>
              </div>
              
              <div className="space-y-4">
                <label className="flex items-center cursor-pointer">
                  <input
                    id="remoteOnly"
                    type="checkbox"
                    checked={profile.preferences.remoteOnly}
                    onChange={(e) => setProfile(prev => ({
                      ...prev,
                      preferences: { ...prev.preferences, remoteOnly: e.target.checked }
                    }))}
                    className="mr-3 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-700">Remote jobs only</span>
                </label>
                
                <label className="flex items-center cursor-pointer">
                  <input
                    id="notifications"
                    type="checkbox"
                    checked={profile.preferences.notifications}
                    onChange={(e) => setProfile(prev => ({
                      ...prev,
                      preferences: { ...prev.preferences, notifications: e.target.checked }
                    }))}
                    className="mr-3 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-gray-700">Email notifications for new jobs</span>
                </label>
              </div>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="px-8 py-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Step {currentStep} of {totalSteps}
              </div>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 text-2xl"
            >
              ×
            </button>
          </div>
          
          {/* Progress Bar */}
          <div className="mt-4">
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-orange-500 to-yellow-500 h-2 rounded-full transition-all duration-300"
                style={{ width: `${(currentStep / totalSteps) * 100}%` }}
              ></div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="px-8 py-8">
          {renderStep()}
        </div>

        {/* Footer */}
        <div className="px-8 py-6 border-t border-gray-200 flex items-center justify-between">
          <button
            onClick={handlePrevious}
            disabled={currentStep === 1}
            className="flex items-center space-x-2 px-6 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          >
            <ArrowLeft className="w-4 h-4" />
            <span>Previous</span>
          </button>
          
          <div className="flex space-x-2">
            {[...Array(totalSteps)].map((_, i) => (
              <div
                key={i}
                className={`w-2 h-2 rounded-full ${
                  i + 1 <= currentStep ? 'bg-blue-600' : 'bg-gray-300'
                }`}
              />
            ))}
          </div>
          
          <button
            onClick={handleNext}
            className="flex items-center space-x-2 bg-gradient-to-r from-orange-500 to-yellow-500 text-white px-6 py-3 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-medium"
          >
            <span>{currentStep === totalSteps ? 'Complete Setup' : 'Next'}</span>
            <ArrowRight className="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>
  );
};

export default Onboarding; 