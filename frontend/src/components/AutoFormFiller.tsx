import React, { useState, useEffect } from 'react';
import { FileText, User, Briefcase, Mail, Phone, MapPin, Calendar, CheckCircle, AlertCircle, Loader } from './icons/EmojiIcons';
import { getApiUrl } from '../utils/apiConfig';

interface UserProfile {
  personal_info: {
    first_name: string;
    last_name: string;
    email: string;
    phone: string;
    location: string;
    linkedin_url?: string;
    portfolio_url?: string;
  };
  experience: Array<{
    title: string;
    company: string;
    start_date: string;
    end_date?: string;
    description: string;
  }>;
  education: Array<{
    degree: string;
    institution: string;
    graduation_year: string;
    gpa?: string;
  }>;
  skills: string[];
  resume_text: string;
}

interface FormField {
  id: string;
  name: string;
  type: string;
  label: string;
  required: boolean;
  value?: string;
  options?: string[];
  placeholder?: string;
}

interface AutoFormFillerProps {
  jobUrl: string;
  jobId: string;
  onFormFilled: (filledData: any) => void;
  onError: (error: string) => void;
  className?: string;
}

const AutoFormFiller: React.FC<AutoFormFillerProps> = ({
  jobUrl,
  jobId,
  onFormFilled,
  onError,
  className = ''
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isFilling, setIsFilling] = useState(false);
  const [userProfile, setUserProfile] = useState<UserProfile | null>(null);
  const [formFields, setFormFields] = useState<FormField[]>([]);
  const [filledData, setFilledData] = useState<any>({});
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState(false);

  // Load user profile on component mount
  useEffect(() => {
    loadUserProfile();
  }, []);

  // Load user profile from API
  const loadUserProfile = async () => {
    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${apiUrl}/user/profile`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load user profile');
      }

      const profile = await response.json();
      setUserProfile(profile);
    } catch (err: any) {
      setError(err.message);
      onError(err.message);
    }
  };

  // Analyze job form
  const analyzeForm = async () => {
    setIsAnalyzing(true);
    setError('');

    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${apiUrl}/auto-apply/analyze-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_url: jobUrl,
          job_id: jobId
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze job form');
      }

      const result = await response.json();
      setAnalysisResult(result);

      if (result.form_fields) {
        setFormFields(result.form_fields);
      }

    } catch (err: any) {
      setError(err.message);
      onError(err.message);
    } finally {
      setIsAnalyzing(false);
    }
  };

  // Generate form fill data based on user profile
  const generateFormData = () => {
    if (!userProfile || !formFields.length) return {};

    const data: any = {};

    formFields.forEach(field => {
      const fieldName = field.name.toLowerCase();
      const fieldLabel = field.label.toLowerCase();

      // Personal Information
      if (fieldName.includes('first') || fieldLabel.includes('first name')) {
        data[field.name] = userProfile.personal_info.first_name;
      } else if (fieldName.includes('last') || fieldLabel.includes('last name')) {
        data[field.name] = userProfile.personal_info.last_name;
      } else if (fieldName.includes('email') || fieldLabel.includes('email')) {
        data[field.name] = userProfile.personal_info.email;
      } else if (fieldName.includes('phone') || fieldLabel.includes('phone')) {
        data[field.name] = userProfile.personal_info.phone;
      } else if (fieldName.includes('location') || fieldLabel.includes('location') || fieldLabel.includes('address')) {
        data[field.name] = userProfile.personal_info.location;
      } else if (fieldName.includes('linkedin') || fieldLabel.includes('linkedin')) {
        data[field.name] = userProfile.personal_info.linkedin_url || '';
      } else if (fieldName.includes('portfolio') || fieldLabel.includes('portfolio')) {
        data[field.name] = userProfile.personal_info.portfolio_url || '';
      }
      // Experience
      else if (fieldName.includes('experience') || fieldLabel.includes('experience')) {
        if (userProfile.experience.length > 0) {
          const latestExp = userProfile.experience[0];
          data[field.name] = `${latestExp.title} at ${latestExp.company}`;
        }
      } else if (fieldName.includes('company') || fieldLabel.includes('company')) {
        if (userProfile.experience.length > 0) {
          data[field.name] = userProfile.experience[0].company;
        }
      } else if (fieldName.includes('title') || fieldLabel.includes('title') || fieldLabel.includes('position')) {
        if (userProfile.experience.length > 0) {
          data[field.name] = userProfile.experience[0].title;
        }
      }
      // Education
      else if (fieldName.includes('education') || fieldLabel.includes('education')) {
        if (userProfile.education.length > 0) {
          const latestEdu = userProfile.education[0];
          data[field.name] = `${latestEdu.degree} from ${latestEdu.institution}`;
        }
      } else if (fieldName.includes('degree') || fieldLabel.includes('degree')) {
        if (userProfile.education.length > 0) {
          data[field.name] = userProfile.education[0].degree;
        }
      } else if (fieldName.includes('university') || fieldName.includes('college') || fieldLabel.includes('university') || fieldLabel.includes('college')) {
        if (userProfile.education.length > 0) {
          data[field.name] = userProfile.education[0].institution;
        }
      }
      // Skills
      else if (fieldName.includes('skill') || fieldLabel.includes('skill')) {
        data[field.name] = userProfile.skills.slice(0, 5).join(', ');
      }
      // Cover Letter
      else if (fieldName.includes('cover') || fieldName.includes('letter') || fieldLabel.includes('cover letter')) {
        data[field.name] = generateCoverLetter();
      }
      // Resume
      else if (fieldName.includes('resume') || fieldLabel.includes('resume')) {
        data[field.name] = userProfile.resume_text;
      }
      // Default empty value
      else {
        data[field.name] = '';
      }
    });

    return data;
  };

  // Generate cover letter based on job and user profile
  const generateCoverLetter = () => {
    if (!userProfile) return '';

    const latestExp = userProfile.experience[0];
    const skills = userProfile.skills.slice(0, 3).join(', ');

    return `Dear Hiring Manager,

I am writing to express my interest in this position. With my background in ${latestExp?.title || 'software development'} and experience at ${latestExp?.company || 'various companies'}, I believe I would be a valuable addition to your team.

My key skills include ${skills}, and I am passionate about delivering high-quality solutions. I am excited about the opportunity to contribute to your organization and would welcome the chance to discuss how my experience aligns with your needs.

Thank you for considering my application.

Best regards,
${userProfile.personal_info.first_name} ${userProfile.personal_info.last_name}`;
  };

  // Fill form with generated data
  const fillForm = async () => {
    setIsFilling(true);
    setError('');

    try {
      const formData = generateFormData();
      setFilledData(formData);

      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${apiUrl}/auto-apply/fill-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_url: jobUrl,
          job_id: jobId,
          form_data: formData
        })
      });

      if (!response.ok) {
        throw new Error('Failed to fill form');
      }

      const result = await response.json();
      
      if (result.success) {
        setSuccess(true);
        onFormFilled(formData);
      } else {
        throw new Error(result.message || 'Form filling failed');
      }

    } catch (err: any) {
      setError(err.message);
      onError(err.message);
    } finally {
      setIsFilling(false);
    }
  };

  // Handle manual field value change
  const handleFieldChange = (fieldName: string, value: string) => {
    setFilledData(prev => ({
      ...prev,
      [fieldName]: value
    }));
  };

  // Submit form
  const submitForm = async () => {
    setIsFilling(true);
    setError('');

    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${apiUrl}/auto-apply/submit-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_url: jobUrl,
          job_id: jobId,
          form_data: filledData
        })
      });

      if (!response.ok) {
        throw new Error('Failed to submit form');
      }

      const result = await response.json();
      
      if (result.success) {
        setSuccess(true);
        onFormFilled(filledData);
      } else {
        throw new Error(result.message || 'Form submission failed');
      }

    } catch (err: any) {
      setError(err.message);
      onError(err.message);
    } finally {
      setIsFilling(false);
    }
  };

  // Reset form
  const resetForm = () => {
    setFilledData({});
    setFormFields([]);
    setAnalysisResult(null);
    setError('');
    setSuccess(false);
  };

  if (success) {
    return (
      <div className={`bg-green-50 border border-green-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-green-800">
          <CheckCircle className="w-5 h-5" />
          <span className="font-medium">Form filled successfully!</span>
        </div>
        <p className="text-sm text-green-600 mt-1">
          The application form has been automatically filled and submitted.
        </p>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-red-50 border border-red-200 rounded-lg p-4 ${className}`}>
        <div className="flex items-center gap-2 text-red-800">
          <AlertCircle className="w-5 h-5" />
          <span className="font-medium">Error</span>
        </div>
        <p className="text-sm text-red-600 mt-1">{error}</p>
        <button
          onClick={resetForm}
          className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
        >
          Try Again
        </button>
      </div>
    );
  }

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-medium text-gray-900">Auto Form Filler</h3>
        <div className="flex items-center gap-2">
          {!analysisResult && (
            <button
              onClick={analyzeForm}
              disabled={isAnalyzing}
              className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 disabled:bg-blue-400"
            >
              {isAnalyzing ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Analyzing...
                </>
              ) : (
                <>
                  <FileText className="w-4 h-4" />
                  Analyze Form
                </>
              )}
            </button>
          )}
        </div>
      </div>

      {/* Analysis Result */}
      {analysisResult && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
          <div className="flex items-center gap-2 text-blue-800 mb-2">
            <FileText className="w-4 h-4" />
            <span className="font-medium">Form Analysis Complete</span>
          </div>
          <div className="text-sm text-blue-700 space-y-1">
            <p>• {formFields.length} form fields detected</p>
            <p>• {formFields.filter(f => f.required).length} required fields</p>
            <p>• Profile completeness: {analysisResult.profile_completeness || 'Unknown'}%</p>
          </div>
        </div>
      )}

      {/* Form Fields */}
      {formFields.length > 0 && (
        <div className="space-y-4">
          <div className="flex items-center justify-between">
            <h4 className="font-medium text-gray-900">Form Fields</h4>
            <button
              onClick={fillForm}
              disabled={isFilling}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 disabled:bg-purple-400"
            >
              {isFilling ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Filling...
                </>
              ) : (
                <>
                  <User className="w-4 h-4" />
                  Auto Fill
                </>
              )}
            </button>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {formFields.map((field) => (
              <div key={field.id} className="space-y-2">
                <label className="block text-sm font-medium text-gray-700">
                  {field.label}
                  {field.required && <span className="text-red-500 ml-1">*</span>}
                </label>
                
                {field.type === 'textarea' ? (
                  <textarea
                    value={filledData[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500 resize-vertical"
                    rows={4}
                  />
                ) : field.type === 'select' ? (
                  <select
                    value={filledData[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  >
                    <option value="">Select {field.label.toLowerCase()}</option>
                    {field.options?.map((option) => (
                      <option key={option} value={option}>
                        {option}
                      </option>
                    ))}
                  </select>
                ) : (
                  <input
                    type={field.type}
                    value={filledData[field.name] || ''}
                    onChange={(e) => handleFieldChange(field.name, e.target.value)}
                    placeholder={field.placeholder || `Enter ${field.label.toLowerCase()}`}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                  />
                )}
              </div>
            ))}
          </div>

          {/* Submit Button */}
          {Object.keys(filledData).length > 0 && (
            <div className="flex items-center gap-2 pt-4 border-t">
              <button
                onClick={submitForm}
                disabled={isFilling}
                className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded-lg font-medium flex items-center gap-2 disabled:bg-green-400"
              >
                {isFilling ? (
                  <>
                    <Loader className="w-4 h-4 animate-spin" />
                    Submitting...
                  </>
                ) : (
                  <>
                    <CheckCircle className="w-4 h-4" />
                    Submit Application
                  </>
                )}
              </button>
              
              <button
                onClick={resetForm}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Reset
              </button>
            </div>
          )}
        </div>
      )}

      {/* Profile Status */}
      {userProfile && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-4">
          <h4 className="font-medium text-gray-900 mb-2">Profile Status</h4>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center gap-2">
              <User className="w-4 h-4 text-gray-500" />
              <span>Personal Info</span>
            </div>
            <div className="flex items-center gap-2">
              <Briefcase className="w-4 h-4 text-gray-500" />
              <span>{userProfile.experience.length} Experience</span>
            </div>
            <div className="flex items-center gap-2">
              <Mail className="w-4 h-4 text-gray-500" />
              <span>{userProfile.skills.length} Skills</span>
            </div>
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-gray-500" />
              <span>Resume Ready</span>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AutoFormFiller; 