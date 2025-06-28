import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { MapPin, 
  Briefcase, 
  Star, 
  DollarSign, 
  Settings, 
  Bell,
  X,
  Clock,
  CheckCircle,
  Globe,
  Mail } from '../components/icons/EmojiIcons';
import { notificationService } from '../services/notificationService';
import { API_BASE_URL } from '../utils/apiConfig';

interface LocationResult {
  display_name: string;
  lat: string;
  lon: string;
  place_id: string;
}

interface Skill {
  id: string;
  name: string;
}

interface JobTitle {
  id: string;
  title: string;
  category: string;
}

interface ExperienceLevel {
  value: string;
  label: string;
  minYears: number;
  maxYears: number | null;
}

const OnboardingCompleteProfile: React.FC = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const [userId, setUserId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');

  // Location states
  const [locationInput, setLocationInput] = useState('');
  const [locationSuggestions, setLocationSuggestions] = useState<LocationResult[]>([]);
  const [selectedLocation, setSelectedLocation] = useState<LocationResult | null>(null);
  const [gettingLocation, setGettingLocation] = useState(false);
  
  // Job title states
  const [jobTitleInput, setJobTitleInput] = useState('');
  const [jobTitleSuggestions, setJobTitleSuggestions] = useState<JobTitle[]>([]);
  const [selectedJobTitles, setSelectedJobTitles] = useState<JobTitle[]>([]);
  const [showJobTitleDropdown, setShowJobTitleDropdown] = useState(false);

  // Experience states
  const [experienceLevel, setExperienceLevel] = useState<string[]>([]);

  // Skills states
  const [skillInput, setSkillInput] = useState('');
  const [skillSuggestions, setSkillSuggestions] = useState<Skill[]>([]);
  const [selectedSkills, setSelectedSkills] = useState<Skill[]>([]);
  const [showSkillDropdown, setShowSkillDropdown] = useState(false);

  // Salary range state
  const [salaryRange, setSalaryRange] = useState<string[]>([]);

  // Work type states
  const [workTypes, setWorkTypes] = useState<string[]>(['Remote Jobs']);

  // Notification states
  const [emailNotifications, setEmailNotifications] = useState(false);
  const [sendNotifications, setSendNotifications] = useState(false);
  const [notificationPermission, setNotificationPermission] = useState<'default' | 'granted' | 'denied'>('default');

  // Refs
  const locationTimeoutRef = useRef<NodeJS.Timeout>();
  const jobTitleTimeoutRef = useRef<NodeJS.Timeout>();
  const skillTimeoutRef = useRef<NodeJS.Timeout>();

  const experienceLevels: ExperienceLevel[] = [
    { value: 'entry', label: 'Entry Level (0-2 years)', minYears: 0, maxYears: 2 },
    { value: 'mid', label: 'Mid Level (2-4 years)', minYears: 2, maxYears: 4 },
    { value: 'senior', label: 'Senior Level (4-6 years)', minYears: 4, maxYears: 6 },
    { value: 'lead', label: 'Lead/Principal (6-10 years)', minYears: 6, maxYears: 10 },
    { value: 'executive', label: 'Executive (10+ years)', minYears: 10, maxYears: null }
  ];

  const salaryRanges = [
    '$0 - $30k',
    '$30k - $70k', 
    '$70k - $120k',
    '$120k - $180k',
    '$180k - $240k',
    '$240k+'
  ];

  const workTypeOptions = [
    'Remote Jobs',
    'Hybrid Jobs', 
    'Office Jobs'
  ];

  useEffect(() => {
    const stateUserId = location.state?.userId;
    if (stateUserId) {
      setUserId(stateUserId);
    } else {
      navigate('/');
    }

    // Check notification permission
    if ('Notification' in window) {
      setNotificationPermission(Notification.permission);
    }
  }, [location, navigate]);

  // Location autocomplete
  const searchLocations = async (query: string) => {
    if (query.length < 3) {
      setLocationSuggestions([]);
      return;
    }

    try {
      const response = await fetch(
        `https://nominatim.openstreetmap.org/search?format=json&q=${encodeURIComponent(query)}&limit=5&addressdetails=1`
      );
      const data = await response.json();
      setLocationSuggestions(data);
    } catch (error) {
      console.error('Location search error:', error);
    }
  };

  const handleLocationInput = (value: string) => {
    setLocationInput(value);
    setSelectedLocation(null);
    
    if (locationTimeoutRef.current) {
      clearTimeout(locationTimeoutRef.current);
    }
    
    locationTimeoutRef.current = setTimeout(() => {
      searchLocations(value);
    }, 300);
  };

  const getCurrentLocation = async () => {
    if (!navigator.geolocation) {
      setError('Geolocation is not supported by this browser.');
      return;
    }

    setGettingLocation(true);
    
    navigator.geolocation.getCurrentPosition(
      async (position) => {
        const { latitude, longitude } = position.coords;
        
        try {
          // Reverse geocoding to get location name
          const response = await fetch(
            `https://nominatim.openstreetmap.org/reverse?format=json&lat=${latitude}&lon=${longitude}&addressdetails=1`
          );
          const data = await response.json();
          
          if (data && data.display_name) {
            setLocationInput(data.display_name);
            setSelectedLocation({
              place_id: data.place_id?.toString() || '',
              display_name: data.display_name,
              lat: latitude.toString(),
              lon: longitude.toString()
            });
          }
        } catch (error) {
          console.error('Reverse geocoding error:', error);
          setError('Failed to get location details');
        } finally {
          setGettingLocation(false);
        }
      },
      (error) => {
        console.error('Geolocation error:', error);
        setError('Failed to get your location. Please check location permissions.');
        setGettingLocation(false);
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  };

  // Job title autocomplete
  const searchJobTitles = async (query: string) => {
    if (query.length < 2) {
      setJobTitleSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/v1/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=10`);
      
      if (!response.ok) {
        throw new Error('API not available');
      }
      
      const data = await response.json();
      // Ensure proper format for job title suggestions
      const formattedSuggestions = data.map((item: any, index: number) => ({
        id: item.id || `api-${index}`,
        title: item.title,
        category: item.category || 'Technology'
      }));
      setJobTitleSuggestions(formattedSuggestions.slice(0, 10));
    } catch (error) {
      console.error('Job titles search error:', error);
      // Fallback with common job titles
      const commonJobTitles = [
        'Software Engineer', 'Frontend Developer', 'Backend Developer', 'Full Stack Developer',
        'DevOps Engineer', 'Data Scientist', 'Product Manager', 'UX Designer', 'UI Designer',
        'Marketing Manager', 'Sales Representative', 'Business Analyst', 'Project Manager'
      ].filter(title => title.toLowerCase().includes(query.toLowerCase()))
       .map((title, index) => ({ id: `common-${index}`, title, category: 'Technology' }));
      
      setJobTitleSuggestions(commonJobTitles);
    }
  };

  const handleJobTitleInput = (value: string) => {
    setJobTitleInput(value);
    setShowJobTitleDropdown(true);
    
    if (jobTitleTimeoutRef.current) {
      clearTimeout(jobTitleTimeoutRef.current);
    }
    
    jobTitleTimeoutRef.current = setTimeout(() => {
      searchJobTitles(value);
    }, 300);
  };

  const addJobTitle = (jobTitle: JobTitle) => {
    if (selectedJobTitles.find(jt => jt.id === jobTitle.id || jt.title.toLowerCase() === jobTitle.title.toLowerCase())) return;
    
    setSelectedJobTitles([...selectedJobTitles, jobTitle]);
    setJobTitleInput('');
    setJobTitleSuggestions([]);
    setShowJobTitleDropdown(false);
  };

  const removeJobTitle = (jobTitleId: string) => {
    setSelectedJobTitles(selectedJobTitles.filter(jt => jt.id !== jobTitleId));
  };

  // Skills autocomplete
  const searchSkills = async (query: string) => {
    if (query.length < 2) {
      setSkillSuggestions([]);
      return;
    }

    try {
      const response = await fetch(`${API_BASE_URL}/v1/jobs/skills/search?q=${encodeURIComponent(query)}`);
      
      if (!response.ok) {
        throw new Error('API not available');
      }
      
      const data = await response.json();
      setSkillSuggestions(data.slice(0, 10));
    } catch (error) {
      console.error('Skills search error:', error);
      // Fallback with common skills
      const commonSkills = [
        'JavaScript', 'React', 'Node.js', 'Python', 'TypeScript', 'HTML', 'CSS',
        'Java', 'C++', 'SQL', 'Git', 'Docker', 'AWS', 'MongoDB', 'PostgreSQL',
        'Vue.js', 'Angular', 'Django', 'Flask', 'Spring', 'Laravel', 'Ruby on Rails',
        'Go', 'Rust', 'Kotlin', 'Swift', 'React Native', 'Flutter', 'TensorFlow'
      ].filter(skill => skill.toLowerCase().includes(query.toLowerCase()))
       .map((skill, index) => ({ id: `common-${index}`, name: skill }));
      
      setSkillSuggestions(commonSkills);
    }
  };

  const handleSkillInput = (value: string) => {
    setSkillInput(value);
    setShowSkillDropdown(true);
    
    if (skillTimeoutRef.current) {
      clearTimeout(skillTimeoutRef.current);
    }
    
    skillTimeoutRef.current = setTimeout(() => {
      searchSkills(value);
    }, 300);
  };

  const addSkill = (skill: Skill) => {
    if (selectedSkills.length >= 30) {
      setError('Maximum 30 skills allowed');
      return;
    }
    
    if (selectedSkills.find(s => s.id === skill.id || s.name.toLowerCase() === skill.name.toLowerCase())) return;
    
    setSelectedSkills([...selectedSkills, skill]);
    setSkillInput('');
    setSkillSuggestions([]);
    setShowSkillDropdown(false);
    setError('');
  };

  const removeSkill = (skillId: string) => {
    setSelectedSkills(selectedSkills.filter(s => s.id !== skillId));
  };

  // Experience level handlers
  const toggleExperienceLevel = (level: string, includeBelow: boolean = false) => {
    if (includeBelow) {
      const levelIndex = experienceLevels.findIndex(el => el.value === level);
      const levelsToInclude = experienceLevels.slice(0, levelIndex + 1).map(el => el.value);
      setExperienceLevel(levelsToInclude);
    } else {
      if (experienceLevel.includes(level)) {
        setExperienceLevel(experienceLevel.filter(el => el !== level));
      } else {
        setExperienceLevel([...experienceLevel, level]);
      }
    }
  };

  // Salary range handlers
  const toggleSalaryRange = (range: string) => {
    if (salaryRange.includes(range)) {
      setSalaryRange(salaryRange.filter(sr => sr !== range));
    } else {
      setSalaryRange([...salaryRange, range]);
    }
  };

  // Work type handlers
  const toggleWorkType = (type: string) => {
    if (workTypes.includes(type)) {
      setWorkTypes(workTypes.filter(wt => wt !== type));
    } else {
      setWorkTypes([...workTypes, type]);
    }
  };

  // Notification handlers
  const handleNotificationToggle = async (enabled: boolean) => {
    if (enabled && notificationPermission !== 'granted') {
      const granted = await notificationService.requestPermission();
      if (granted) {
        setNotificationPermission('granted');
        setSendNotifications(true);
      } else {
        setNotificationPermission('denied');
        setSendNotifications(false);
      }
    } else {
      setSendNotifications(enabled);
    }
  };

  const handleComplete = async () => {
    if (selectedJobTitles.length === 0) {
      setError('Please select at least one job title');
      return;
    }

    if (experienceLevel.length === 0) {
      setError('Please select at least one experience level');
      return;
    }

    if (selectedSkills.length === 0) {
      setError('Please add at least one skill');
      return;
    }

    if (salaryRange.length === 0) {
      setError('Please select at least one salary range');
      return;
    }

    if (workTypes.length === 0) {
      setError('Please select at least one work type');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const profileData = {
        location: selectedLocation?.display_name || locationInput,
        job_titles: selectedJobTitles.map(jt => jt.title),
        experience_levels: experienceLevel,
        skills: selectedSkills.map(s => s.name),
        salary_ranges: salaryRange,
        work_types: workTypes,
        email_notifications: emailNotifications,
        browser_notifications: sendNotifications
      };

      // Save preferences to localStorage
      localStorage.setItem('userPreferences', JSON.stringify(profileData));

      // Save to backend
      const response = await fetch(`${API_BASE_URL}/v1/onboarding/complete-profile`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${localStorage.getItem('auth_token')}`
        },
        body: JSON.stringify({
          user_id: userId,
          ...profileData
        })
      });

      if (!response.ok) {
        throw new Error('Failed to save profile');
      }

      setSuccess('Profile completed successfully!');

      // Start job checking if notifications enabled
      if (sendNotifications) {
        notificationService.startPeriodicJobCheck(30); // Check every 30 minutes
      }

      // Navigate to search results with preferences
      setTimeout(() => {
        navigate('/jobs/search', { 
          state: { 
            searchParams: {
              job_title: selectedJobTitles.map(jt => jt.title).join(','),
              location: selectedLocation?.display_name || locationInput,
              experience_level: experienceLevel.join(','),
              work_type: workTypes.join(','),
              salary_range: salaryRange.join(',')
            }
          }
        });
      }, 2000);

    } catch (error: any) {
      setError(error.message || 'Failed to complete profile');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-orange-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 py-8 px-4">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-8">
          <div className="text-center mb-8">
            <div className="w-20 h-20 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-full flex items-center justify-center mx-auto mb-4">
              <CheckCircle className="w-10 h-10 text-white" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
              Complete Your Profile
            </h1>
            <p className="text-gray-600 dark:text-gray-400">
              Tell us about yourself to get personalized job recommendations
            </p>
          </div>

          {error && (
            <div className="mb-6 p-4 bg-red-100 border border-red-200 rounded-lg text-red-700">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-6 p-4 bg-green-100 border border-green-200 rounded-lg text-green-700">
              {success}
            </div>
          )}

          <div className="space-y-8">
            {/* Location with geolocation */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <MapPin className="w-4 h-4 inline mr-2" />
                Location
              </label>
              <div className="relative">
                <div className="flex">
                  <input
                    type="text"
                    value={locationInput}
                    onChange={(e) => handleLocationInput(e.target.value)}
                    className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-l-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                    placeholder="Enter your location or use GPS"
                  />
                  <button
                    type="button"
                    onClick={getCurrentLocation}
                    disabled={gettingLocation}
                    aria-label="Use GPS"
                    className="px-4 py-2 bg-orange-500 text-white rounded-r-lg hover:bg-orange-600 disabled:opacity-50 disabled:cursor-not-allowed flex items-center"
                  >
                    {gettingLocation ? (
                      <div className="animate-spin w-4 h-4 border-2 border-white border-t-transparent rounded-full"></div>
                    ) : (
                      <Globe className="w-4 h-4" />
                    )}
                  </button>
                </div>
                
                {/* Location suggestions */}
                {locationSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {locationSuggestions.map((location) => (
                      <button
                        key={location.place_id}
                        onClick={() => {
                          setSelectedLocation(location);
                          setLocationInput(location.display_name);
                          setLocationSuggestions([]);
                        }}
                        className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                      >
                        {location.display_name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            {/* Job Titles */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Briefcase className="w-4 h-4 inline mr-2" />
                Current/Desired Job Titles (multiple selection allowed)
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={jobTitleInput}
                  onChange={(e) => handleJobTitleInput(e.target.value)}
                  onFocus={() => setShowJobTitleDropdown(true)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Search and select job titles"
                />
                
                {/* Job title suggestions */}
                {showJobTitleDropdown && jobTitleSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {jobTitleSuggestions.map((jobTitle) => (
                      <button
                        key={jobTitle.id}
                        onClick={() => addJobTitle(jobTitle)}
                        className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                      >
                        <div className="font-medium">{jobTitle.title}</div>
                        <div className="text-xs text-gray-500">{jobTitle.category}</div>
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Selected job titles */}
              {selectedJobTitles.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {selectedJobTitles.map((jobTitle) => (
                    <span
                      key={jobTitle.id}
                      className="inline-flex items-center px-3 py-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 rounded-full text-sm"
                    >
                      {jobTitle.title}
                      <button
                        onClick={() => removeJobTitle(jobTitle.id)}
                        className="ml-2 text-orange-600 hover:text-orange-800"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
            </div>

            {/* Experience Level */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Star className="w-4 h-4 inline mr-2" />
                Experience Level
              </label>
              <div className="space-y-2">
                {experienceLevels.map((level) => (
                  <div key={level.value} className="flex items-center group">
                    <input
                      type="checkbox"
                      id={level.value}
                      checked={experienceLevel.includes(level.value)}
                      onChange={(e) => toggleExperienceLevel(level.value)}
                      className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                    />
                    <label
                      htmlFor={level.value}
                      className="ml-3 text-sm text-gray-700 dark:text-gray-300 cursor-pointer flex-1"
                    >
                      {level.label}
                    </label>
                    
                    {/* "and below" checkbox - appears on hover */}
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity">
                      <input
                        type="checkbox"
                        id={`${level.value}-below`}
                        checked={false}
                        onChange={() => toggleExperienceLevel(level.value, true)}
                        className="h-3 w-3 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                      />
                      <label
                        htmlFor={`${level.value}-below`}
                        className="ml-1 text-xs text-gray-500 cursor-pointer"
                      >
                        and below
                      </label>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Skills */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Settings className="w-4 h-4 inline mr-2" />
                Skills (max 30, searchable)
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={skillInput}
                  onChange={(e) => handleSkillInput(e.target.value)}
                  onFocus={() => setShowSkillDropdown(true)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  placeholder="Search and add skills"
                />
                
                {/* Skill suggestions */}
                {showSkillDropdown && skillSuggestions.length > 0 && (
                  <div className="absolute z-10 w-full mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-48 overflow-y-auto">
                    {skillSuggestions.map((skill) => (
                      <button
                        key={skill.id}
                        onClick={() => addSkill(skill)}
                        className="w-full text-left px-4 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 text-sm"
                      >
                        {skill.name}
                      </button>
                    ))}
                  </div>
                )}
              </div>
              
              {/* Selected skills */}
              {selectedSkills.length > 0 && (
                <div className="mt-2 flex flex-wrap gap-2">
                  {selectedSkills.map((skill) => (
                    <span
                      key={skill.id}
                      className="inline-flex items-center px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
                    >
                      {skill.name}
                      <button
                        onClick={() => removeSkill(skill.id)}
                        className="ml-2 text-blue-600 hover:text-blue-800"
                      >
                        <X className="w-3 h-3" />
                      </button>
                    </span>
                  ))}
                </div>
              )}
              
              {selectedSkills.length > 0 && (
                <div className="mt-1 text-xs text-gray-500">
                  {selectedSkills.length}/30 skills selected
                </div>
              )}
            </div>

            {/* Salary Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <DollarSign className="w-4 h-4 inline mr-2" />
                Salary Range
              </label>
              <div className="grid grid-cols-2 md:grid-cols-3 gap-2">
                {salaryRanges.map((range) => (
                  <label
                    key={range}
                    className="flex items-center cursor-pointer p-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <input
                      type="checkbox"
                      checked={salaryRange.includes(range)}
                      onChange={() => toggleSalaryRange(range)}
                      className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                    />
                    <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                      {range}
                    </span>
                  </label>
                ))}
              </div>
            </div>

            {/* Work Type */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                <Clock className="w-4 h-4 inline mr-2" />
                Work Type
              </label>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
                {workTypeOptions.map((type) => (
                  <label
                    key={type}
                    className="flex items-center cursor-pointer p-4 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700"
                  >
                    <input
                      type="checkbox"
                      checked={workTypes.includes(type)}
                      onChange={() => toggleWorkType(type)}
                      className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                    />
                    <span className="ml-3 text-sm font-medium text-gray-700 dark:text-gray-300">
                      {type}
                    </span>
                  </label>
                ))}
              </div>
              <p className="mt-2 text-xs text-gray-500">
                Remote Jobs is selected by default. You can select multiple options.
              </p>
            </div>

            {/* Notification Preferences */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">
                <Bell className="w-4 h-4 inline mr-2" />
                Notification Preferences
              </label>
              <div className="space-y-3">
                {/* Email notifications */}
                <label className="flex items-center cursor-pointer p-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                  <input
                    type="checkbox"
                    checked={emailNotifications}
                    onChange={(e) => setEmailNotifications(e.target.checked)}
                    className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                  />
                  <Mail className="w-4 h-4 ml-3 mr-2 text-gray-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Email notifications for new jobs
                  </span>
                </label>

                {/* Browser notifications */}
                <label className="flex items-center cursor-pointer p-3 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700">
                  <input
                    type="checkbox"
                    checked={sendNotifications}
                    onChange={(e) => handleNotificationToggle(e.target.checked)}
                    className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                  />
                  <Bell className="w-4 h-4 ml-3 mr-2 text-gray-500" />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Send notifications for new jobs
                  </span>
                </label>
              </div>
            </div>
          </div>

          {/* Complete Button */}
          <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-600">
            <button
              onClick={handleComplete}
              disabled={loading}
              className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-4 px-6 rounded-lg font-medium text-lg hover:from-orange-600 hover:to-yellow-600 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <div className="flex items-center justify-center">
                  <div className="animate-spin w-5 h-5 border-2 border-white border-t-transparent rounded-full mr-2"></div>
                  Completing Profile...
                </div>
              ) : (
                'Complete Profile & Find Jobs'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default OnboardingCompleteProfile; 