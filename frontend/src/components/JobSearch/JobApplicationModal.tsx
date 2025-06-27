import React, { useState, useEffect } from 'react';
import { X, ExternalLink, Upload, User, Mail, Phone, FileText, Briefcase, Globe, CheckCircle, AlertCircle } from '../icons/EmojiIcons';
import { Job } from '../../types/job';
import { jobService } from '../../services/jobService';

interface JobApplicationModalProps {
  job: Job;
  onClose: () => void;
  onSubmit: (applicationData: ApplicationData) => void;
}

interface ApplicationData {
  jobId: string;
  applicationType: 'external' | 'direct' | 'auto';
  personalInfo: {
    fullName: string;
    email: string;
    phone: string;
    location: string;
  };
  documents: {
    resume: File | null;
    coverLetter: string;
    portfolio?: string;
  };
  answers: Record<string, string>;
  applicationMethod: 'redirect' | 'scraped_form' | 'automated';
}

interface ApplicationFormField {
  id: string;
  label: string;
  type: 'text' | 'email' | 'phone' | 'textarea' | 'select' | 'file' | 'checkbox';
  required: boolean;
  placeholder?: string;
  options?: string[];
  maxLength?: number;
}

const JobApplicationModal: React.FC<JobApplicationModalProps> = ({ job, onClose, onSubmit }) => {
  const [step, setStep] = useState<'method' | 'form' | 'review' | 'submitting'>('method');
  const [applicationMethod, setApplicationMethod] = useState<'external' | 'direct' | 'auto'>('external');
  const [scrapedFields, setScrapedFields] = useState<ApplicationFormField[]>([]);
  const [isScrapingForm, setIsScrapingForm] = useState(false);
  const [scrapingError, setScrapingError] = useState<string | null>(null);
  
  const [applicationData, setApplicationData] = useState<ApplicationData>({
    jobId: job.id,
    applicationType: 'external',
    personalInfo: {
      fullName: '',
      email: '',
      phone: '',
      location: ''
    },
    documents: {
      resume: null,
      coverLetter: '',
      portfolio: ''
    },
    answers: {},
    applicationMethod: 'redirect'
  });

  const [userProfile, setUserProfile] = useState<any>(null);
  const [autoFillAvailable, setAutoFillAvailable] = useState(false);

  useEffect(() => {
    // Load user profile for auto-fill
    loadUserProfile();
  }, []);

  const loadUserProfile = async () => {
    try {
      // Get user profile from onboarding/auth context
      const profile = await jobService.getUserProfile();
      setUserProfile(profile);
      
      // Check if profile is complete enough for auto-fill
      const hasRequiredFields = profile?.name && profile?.email && profile?.resume_url;
      setAutoFillAvailable(hasRequiredFields);
      
      if (hasRequiredFields) {
        setApplicationData(prev => ({
          ...prev,
          personalInfo: {
            fullName: profile.name || '',
            email: profile.email || '',
            phone: profile.phone || '',
            location: profile.location || ''
          }
        }));
      }
    } catch (error) {
      console.error('Error loading user profile:', error);
    }
  };

  const handleMethodSelection = async (method: 'external' | 'direct' | 'auto') => {
    setApplicationMethod(method);
    setApplicationData(prev => ({ 
      ...prev, 
      applicationType: method,
      applicationMethod: method === 'external' ? 'redirect' : 
                        method === 'direct' ? 'scraped_form' : 'automated'
    }));

    if (method === 'external') {
      // v1: Direct redirect to external site
      handleExternalRedirect();
    } else if (method === 'direct') {
      // v2: Scrape application form from target site
      await scrapeApplicationForm();
    } else if (method === 'auto') {
      // v3: Auto-fill and submit (if available)
      setStep('review');
    }
  };

  const handleExternalRedirect = () => {
    // v1 Implementation: Redirect to external job site
    const applicationUrl = job.applyUrl || job.sourceUrl;
    
    if (applicationUrl) {
      // Track the application attempt
      jobService.trackJobInteraction(job.id, 'external_redirect');
      
      // Open in new tab
      window.open(applicationUrl, '_blank');
      
      // Close modal after redirect
      setTimeout(() => {
        onClose();
      }, 1000);
    } else {
      // Fallback to Google search for application
      const searchQuery = `${job.title} ${job.company} job application site:${extractDomainFromUrl(job.sourceUrl)}`;
      const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(searchQuery)}`;
      window.open(searchUrl, '_blank');
      onClose();
    }
  };

  const scrapeApplicationForm = async () => {
    // v2 Implementation: Scrape application form fields
    setIsScrapingForm(true);
    setScrapingError(null);
    
    try {
      // Call backend API to scrape the application form
      const response = await jobService.scrapeJobApplicationForm(job.id, job.applyUrl || job.sourceUrl);
      
      if (response.success) {
        setScrapedFields(response.fields || []);
        setStep('form');
      } else {
        throw new Error(response.error || 'Failed to scrape form');
      }
    } catch (error) {
      console.error('Error scraping form:', error);
      setScrapingError('Unable to load application form. Redirecting to external site...');
      
      // Fallback to external redirect
      setTimeout(() => {
        handleExternalRedirect();
      }, 3000);
    } finally {
      setIsScrapingForm(false);
    }
  };

  const autoFillForm = () => {
    if (!userProfile) return;

    const autoFilledAnswers: Record<string, string> = {};
    
    scrapedFields.forEach(field => {
      const fieldLabel = field.label.toLowerCase();
      
      // Auto-fill based on field label patterns
      if (fieldLabel.includes('name') || fieldLabel.includes('full name')) {
        autoFilledAnswers[field.id] = userProfile.name || '';
      } else if (fieldLabel.includes('email')) {
        autoFilledAnswers[field.id] = userProfile.email || '';
      } else if (fieldLabel.includes('phone')) {
        autoFilledAnswers[field.id] = userProfile.phone || '';
      } else if (fieldLabel.includes('location') || fieldLabel.includes('address')) {
        autoFilledAnswers[field.id] = userProfile.location || '';
      } else if (fieldLabel.includes('experience')) {
        autoFilledAnswers[field.id] = userProfile.experience_years?.toString() || '';
      } else if (fieldLabel.includes('skill')) {
        autoFilledAnswers[field.id] = userProfile.skills?.join(', ') || '';
      } else if (fieldLabel.includes('cover letter') || fieldLabel.includes('why')) {
        autoFilledAnswers[field.id] = generateCoverLetter(job, userProfile);
      }
    });

    setApplicationData(prev => ({
      ...prev,
      answers: { ...prev.answers, ...autoFilledAnswers }
    }));
  };

  const generateCoverLetter = (job: Job, profile: any): string => {
    return `Dear Hiring Manager,

I am excited to apply for the ${job.title} position at ${job.company}. With ${profile.experience_years || 'several'} years of experience in ${profile.skills?.slice(0, 3).join(', ') || 'software development'}, I believe I would be a great fit for this role.

My background in ${profile.title || 'technology'} and expertise with ${profile.skills?.slice(0, 2).join(' and ') || 'modern technologies'} aligns well with the requirements outlined in your job posting. I am particularly drawn to ${job.company}'s mission and would love to contribute to your team.

Thank you for considering my application. I look forward to discussing how I can contribute to your team.

Best regards,
${profile.name || 'Applicant'}`;
  };

  const handleFormSubmit = async () => {
    setStep('submitting');
    
    try {
      if (applicationMethod === 'auto') {
        // v3: Automated submission
        const result = await jobService.submitAutomatedApplication(job.id, applicationData);
        if (result.success) {
          onSubmit(applicationData);
        } else {
          throw new Error(result.error || 'Automated submission failed');
        }
      } else {
        // v2: Manual form submission via backend
        const result = await jobService.submitScrapedFormApplication(job.id, applicationData);
        if (result.success) {
          onSubmit(applicationData);
        } else {
          throw new Error(result.error || 'Form submission failed');
        }
      }
    } catch (error) {
      console.error('Error submitting application:', error);
      // Show error and allow retry or fallback to external
      alert('Application submission failed. Please try applying directly on the company website.');
      handleExternalRedirect();
    }
  };

  const extractDomainFromUrl = (url?: string): string => {
    if (!url) return '';
    try {
      return new URL(url).hostname;
    } catch {
      return '';
    }
  };

  const renderMethodSelection = () => (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Apply to {job.title}</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="h-6 w-6" />
        </button>
      </div>

      <div className="mb-6">
        <div className="bg-gray-50 rounded-lg p-4 mb-4">
          <h3 className="font-medium text-gray-900 mb-2">{job.title}</h3>
          <p className="text-sm text-gray-600">{typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'} • {job.location}</p>
        </div>
      </div>

      <div className="space-y-4">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Choose Application Method</h3>

        {/* External Application (v1) */}
        <div 
          onClick={() => handleMethodSelection('external')}
          className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ExternalLink className="h-5 w-5 text-blue-600" />
              <div>
                <h4 className="font-medium text-gray-900">Apply on Company Website</h4>
                <p className="text-sm text-gray-600">Redirect to the original job posting (Recommended)</p>
              </div>
            </div>
            <div className="text-xs bg-green-100 text-green-800 px-2 py-1 rounded-full">Fast</div>
          </div>
        </div>

        {/* Direct Application (v2) */}
        <div 
          onClick={() => handleMethodSelection('direct')}
          className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
        >
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <FileText className="h-5 w-5 text-purple-600" />
              <div>
                <h4 className="font-medium text-gray-900">Apply Through Platform</h4>
                <p className="text-sm text-gray-600">Fill application form here (Beta)</p>
              </div>
            </div>
            <div className="text-xs bg-yellow-100 text-yellow-800 px-2 py-1 rounded-full">Beta</div>
          </div>
        </div>

        {/* Auto Application (v3) */}
        {autoFillAvailable && (
          <div 
            onClick={() => handleMethodSelection('auto')}
            className="border border-gray-200 rounded-lg p-4 cursor-pointer hover:border-blue-500 hover:bg-blue-50 transition-colors"
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <Briefcase className="h-5 w-5 text-green-600" />
                <div>
                  <h4 className="font-medium text-gray-900">One-Click Application</h4>
                  <p className="text-sm text-gray-600">Auto-fill with your profile (Premium)</p>
                </div>
              </div>
              <div className="text-xs bg-purple-100 text-purple-800 px-2 py-1 rounded-full">Premium</div>
            </div>
          </div>
        )}
      </div>

      {!autoFillAvailable && (
        <div className="mt-6 p-4 bg-blue-50 rounded-lg">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-blue-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900">Complete Your Profile</h4>
              <p className="text-sm text-blue-700">
                Complete your profile with CV and contact information to enable one-click applications.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  const renderApplicationForm = () => (
    <div className="p-6 max-h-[70vh] overflow-y-auto">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Application Form</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="h-6 w-6" />
        </button>
      </div>

      {isScrapingForm ? (
        <div className="text-center py-12">
          <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
          <p className="text-gray-600">Loading application form...</p>
        </div>
      ) : scrapingError ? (
        <div className="text-center py-12">
          <AlertCircle className="h-12 w-12 text-red-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">Unable to Load Form</h3>
          <p className="text-gray-600 mb-4">{scrapingError}</p>
        </div>
      ) : (
        <>
          <div className="mb-6">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Application Details</h3>
              {userProfile && (
                <button
                  onClick={autoFillForm}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                >
                  <User className="h-4 w-4" />
                  Auto-Fill
                </button>
              )}
            </div>

            <div className="space-y-4">
              {scrapedFields.map((field) => (
                <div key={field.id}>
                  <label htmlFor={field.id} className="block text-sm font-medium text-gray-700 mb-2">
                    {field.label}
                    {field.required && <span className="text-red-500 ml-1">*</span>}
                  </label>
                  
                  {field.type === 'textarea' ? (
                    <textarea id={field.id} value={applicationData.answers[field.id] || ''}
                      onChange={(e) => setApplicationData(prev => ({
                        ...prev,
                        answers: { ...prev.answers, [field.id]: e.target.value }
                      }))}
                      placeholder={field.placeholder}
                      rows={4}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      maxLength={field.maxLength}
                    />
                  ) : field.type === 'select' ? (
                    <select id={field.id} value={applicationData.answers[field.id] || ''}
                      onChange={(e) => setApplicationData(prev => ({
                        ...prev,
                        answers: { ...prev.answers, [field.id]: e.target.value }
                      }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">Select an option</option>
                      {field.options?.map(option => (
                        <option key={option} value={option}>{option}</option>
                      ))}
                    </select>
                  ) : field.type === 'file' ? (
                    <input id={field.id} type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={(e) => {
                        const file = e.target.files?.[0];
                        if (file) {
                          setApplicationData(prev => ({
                            ...prev,
                            documents: { ...prev.documents, resume: file }
                          }));
                        }
                      }}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    />
                  ) : (
                    <input id={field.id} type={field.type}
                      value={applicationData.answers[field.id] || ''}
                      onChange={(e) => setApplicationData(prev => ({
                        ...prev,
                        answers: { ...prev.answers, [field.id]: e.target.value }
                      }))}
                      placeholder={field.placeholder}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      maxLength={field.maxLength}
                    />
                  )}
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-3">
            <button
              onClick={() => setStep('method')}
              className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
            >
              Back
            </button>
            <button
              onClick={() => setStep('review')}
              className="flex-1 px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
            >
              Review Application
            </button>
          </div>
        </>
      )}
    </div>
  );

  const renderReview = () => (
    <div className="p-6">
      <div className="flex items-center justify-between mb-6">
        <h2 className="text-xl font-semibold text-gray-900">Review Application</h2>
        <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
          <X className="h-6 w-6" />
        </button>
      </div>

      <div className="space-y-6">
        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Job Details</h3>
          <p className="text-sm text-gray-600">{job.title} at {typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}</p>
          <p className="text-sm text-gray-600">{job.location}</p>
        </div>

        <div className="bg-gray-50 rounded-lg p-4">
          <h3 className="font-medium text-gray-900 mb-2">Personal Information</h3>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-gray-500">Name:</span>
              <p className="text-gray-900">{applicationData.personalInfo.fullName}</p>
            </div>
            <div>
              <span className="text-gray-500">Email:</span>
              <p className="text-gray-900">{applicationData.personalInfo.email}</p>
            </div>
          </div>
        </div>

        <div className="flex gap-3">
          <button
            onClick={() => setStep(applicationMethod === 'external' ? 'method' : 'form')}
            className="px-6 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors"
          >
            Back
          </button>
          <button
            onClick={handleFormSubmit}
            className="flex-1 px-6 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors flex items-center justify-center gap-2"
          >
            <CheckCircle className="h-4 w-4" />
            Submit Application
          </button>
        </div>
      </div>
    </div>
  );

  const renderSubmitting = () => (
    <div className="p-6 text-center">
      <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
      <h3 className="text-lg font-medium text-gray-900 mb-2">Submitting Application</h3>
      <p className="text-gray-600">Please wait while we submit your application...</p>
    </div>
  );

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-2xl w-full mx-4">
        {step === 'method' && renderMethodSelection()}
        {step === 'form' && renderApplicationForm()}
        {step === 'review' && renderReview()}
        {step === 'submitting' && renderSubmitting()}
      </div>
    </div>
  );
};

export default JobApplicationModal; 