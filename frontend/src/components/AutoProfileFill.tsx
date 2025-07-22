import React, { useState, useEffect } from 'react';
import { 
  User, 
  FileText, 
  Linkedin, 
  CheckCircle, 
  AlertCircle, 
  Loader, 
  Edit3, 
  Save, 
  X,
  Download,
  Upload,
  ExternalLink,
  Sparkles
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface ProfileData {
  name?: string;
  email?: string;
  phone?: string;
  location?: string;
  title?: string;
  summary?: string;
  skills?: string[];
  experience?: any[];
  education?: any[];
  languages?: string[];
  certifications?: string[];
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
}

interface AutoProfileFillProps {
  onProfileUpdate: (profileData: ProfileData) => Promise<void>;
  currentProfile?: ProfileData;
  className?: string;
}

const AutoProfileFill: React.FC<AutoProfileFillProps> = ({
  onProfileUpdate,
  currentProfile = {},
  className = ''
}) => {
  const [isLoading, setIsLoading] = useState(false);
  const [extractedData, setExtractedData] = useState<ProfileData | null>(null);
  const [showPreview, setShowPreview] = useState(false);
  const [selectedFields, setSelectedFields] = useState<Set<string>>(new Set());
  const [isEditing, setIsEditing] = useState(false);

  // Available profile fields
  const profileFields = [
    { key: 'name', label: 'Full Name', icon: User, required: true },
    { key: 'email', label: 'Email', icon: User, required: true },
    { key: 'phone', label: 'Phone', icon: User, required: false },
    { key: 'location', label: 'Location', icon: User, required: false },
    { key: 'title', label: 'Job Title', icon: User, required: false },
    { key: 'summary', label: 'Professional Summary', icon: FileText, required: false },
    { key: 'skills', label: 'Skills', icon: Sparkles, required: false },
    { key: 'experience', label: 'Work Experience', icon: FileText, required: false },
    { key: 'education', label: 'Education', icon: FileText, required: false },
    { key: 'languages', label: 'Languages', icon: User, required: false },
    { key: 'certifications', label: 'Certifications', icon: FileText, required: false },
    { key: 'linkedin_url', label: 'LinkedIn URL', icon: Linkedin, required: false },
    { key: 'github_url', label: 'GitHub URL', icon: ExternalLink, required: false },
    { key: 'portfolio_url', label: 'Portfolio URL', icon: ExternalLink, required: false }
  ];

  // Extract profile from CV
  const extractFromCV = async () => {
    try {
      setIsLoading(true);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/auto-fill/extract-from-existing-cv`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to extract profile from CV');
      }
      
      const result = await response.json();
      setExtractedData(result.data);
      setShowPreview(true);
      toast.success('Profile data extracted from CV successfully!');
      
    } catch (error: any) {
      console.error('Error extracting from CV:', error);
      toast.error(error.message || 'Failed to extract from CV');
    } finally {
      setIsLoading(false);
    }
  };

  // Import from LinkedIn
  const importFromLinkedIn = async () => {
    try {
      setIsLoading(true);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/auto-fill/linkedin`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });
      
      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Failed to import from LinkedIn');
      }
      
      const result = await response.json();
      setExtractedData(result.data);
      setShowPreview(true);
      toast.success('Profile data imported from LinkedIn successfully!');
      
    } catch (error: any) {
      console.error('Error importing from LinkedIn:', error);
      toast.error(error.message || 'Failed to import from LinkedIn');
    } finally {
      setIsLoading(false);
    }
  };

  // Handle field selection
  const toggleField = (fieldKey: string) => {
    const newSelected = new Set(selectedFields);
    if (newSelected.has(fieldKey)) {
      newSelected.delete(fieldKey);
    } else {
      newSelected.add(fieldKey);
    }
    setSelectedFields(newSelected);
  };

  // Select all fields
  const selectAllFields = () => {
    const allFields = profileFields.map(field => field.key);
    setSelectedFields(new Set(allFields));
  };

  // Deselect all fields
  const deselectAllFields = () => {
    setSelectedFields(new Set());
  };

  // Apply selected fields to profile
  const applySelectedFields = async () => {
    if (selectedFields.size === 0) {
      toast.error('Please select at least one field to apply');
      return;
    }

    if (!extractedData) {
      toast.error('No extracted data available');
      return;
    }

    try {
      setIsLoading(true);
      
      // Create profile data with only selected fields
      const profileData: ProfileData = {};
      selectedFields.forEach(fieldKey => {
        if (extractedData[fieldKey as keyof ProfileData] !== undefined) {
          (profileData as any)[fieldKey] = extractedData[fieldKey as keyof ProfileData];
        }
      });

      await onProfileUpdate(profileData);
      setShowPreview(false);
      setSelectedFields(new Set());
      toast.success('Profile updated successfully!');
      
    } catch (error: any) {
      console.error('Error updating profile:', error);
      toast.error(error.message || 'Failed to update profile');
    } finally {
      setIsLoading(false);
    }
  };

  // Get field value for display
  const getFieldValue = (fieldKey: string) => {
    if (!extractedData) return '';
    
    const value = extractedData[fieldKey as keyof ProfileData];
    if (Array.isArray(value)) {
      return value.join(', ');
    }
    return value || '';
  };

  // Check if field has data
  const hasFieldData = (fieldKey: string) => {
    if (!extractedData) return false;
    const value = extractedData[fieldKey as keyof ProfileData];
    return value !== undefined && value !== null && value !== '';
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Auto Profile Fill</h3>
          <p className="text-sm text-gray-600">
            Automatically fill your profile from CV or LinkedIn
          </p>
        </div>
      </div>

      {/* Import Options */}
      {!showPreview && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* CV Import */}
          <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-blue-100 rounded-lg mr-3">
                <FileText className="text-blue-600" size={20} />
              </div>
              <div>
                <h4 className="font-medium text-blue-900">Extract from CV</h4>
                <p className="text-sm text-blue-700">Upload your CV to extract profile information</p>
              </div>
            </div>
            
            <button
              onClick={extractFromCV}
              disabled={isLoading}
              className={`w-full inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors ${
                isLoading
                  ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} />
                  Extracting...
                </>
              ) : (
                <>
                  <Upload className="mr-2" size={16} />
                  Extract from CV
                </>
              )}
            </button>
          </div>

          {/* LinkedIn Import */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-6">
            <div className="flex items-center mb-4">
              <div className="p-2 bg-indigo-100 rounded-lg mr-3">
                <Linkedin className="text-indigo-600" size={20} />
              </div>
              <div>
                <h4 className="font-medium text-indigo-900">Import from LinkedIn</h4>
                <p className="text-sm text-indigo-700">Connect your LinkedIn account to import profile data</p>
              </div>
            </div>
            
            <button
              onClick={importFromLinkedIn}
              disabled={isLoading}
              className={`w-full inline-flex items-center justify-center px-4 py-2 rounded-lg font-medium transition-colors ${
                isLoading
                  ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                  : 'bg-indigo-600 text-white hover:bg-indigo-700'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} />
                  Importing...
                </>
              ) : (
                <>
                  <ExternalLink className="mr-2" size={16} />
                  Import from LinkedIn
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* Data Preview */}
      {showPreview && extractedData && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="flex items-center justify-between mb-6">
            <div>
              <h4 className="text-lg font-medium text-gray-900">Extracted Profile Data</h4>
              <p className="text-sm text-gray-600">Select the fields you want to apply to your profile</p>
            </div>
            <div className="flex items-center space-x-2">
              <button
                onClick={selectAllFields}
                className="text-sm text-blue-600 hover:text-blue-800"
              >
                Select All
              </button>
              <span className="text-gray-300">|</span>
              <button
                onClick={deselectAllFields}
                className="text-sm text-gray-600 hover:text-gray-800"
              >
                Clear All
              </button>
            </div>
          </div>

          {/* Field Selection */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-6">
            {profileFields.map(field => {
              const hasData = hasFieldData(field.key);
              const isSelected = selectedFields.has(field.key);
              const Icon = field.icon;

              return (
                <div
                  key={field.key}
                  className={`border rounded-lg p-4 cursor-pointer transition-all ${
                    hasData
                      ? isSelected
                        ? 'border-blue-500 bg-blue-50'
                        : 'border-gray-200 hover:border-gray-300'
                      : 'border-gray-100 bg-gray-50 opacity-50 cursor-not-allowed'
                  }`}
                  onClick={() => hasData && toggleField(field.key)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <Icon size={16} className="text-gray-500 mr-2" />
                      <span className="font-medium text-gray-900">{field.label}</span>
                      {field.required && <span className="text-red-500 ml-1">*</span>}
                    </div>
                    {hasData && (
                      <div className="flex items-center space-x-2">
                        {isSelected ? (
                          <CheckCircle className="text-blue-600" size={16} />
                        ) : (
                          <div className="w-4 h-4 border-2 border-gray-300 rounded"></div>
                        )}
                      </div>
                    )}
                  </div>
                  
                  {hasData && (
                    <div className="text-sm text-gray-600">
                      <div className="truncate" title={getFieldValue(field.key)}>
                        {getFieldValue(field.key)}
                      </div>
                    </div>
                  )}
                  
                  {!hasData && (
                    <div className="text-sm text-gray-400">
                      No data available
                    </div>
                  )}
                </div>
              );
            })}
          </div>

          {/* Action Buttons */}
          <div className="flex items-center justify-between pt-4 border-t border-gray-200">
            <button
              onClick={() => setShowPreview(false)}
              className="inline-flex items-center px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              <X className="mr-2" size={16} />
              Cancel
            </button>
            
            <div className="flex items-center space-x-3">
              <span className="text-sm text-gray-600">
                {selectedFields.size} field{selectedFields.size !== 1 ? 's' : ''} selected
              </span>
              <button
                onClick={applySelectedFields}
                disabled={selectedFields.size === 0 || isLoading}
                className={`inline-flex items-center px-6 py-2 rounded-lg font-medium transition-colors ${
                  selectedFields.size === 0 || isLoading
                    ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                    : 'bg-green-600 text-white hover:bg-green-700'
                }`}
              >
                {isLoading ? (
                  <>
                    <Loader className="animate-spin mr-2" size={16} />
                    Applying...
                  </>
                ) : (
                  <>
                    <Save className="mr-2" size={16} />
                    Apply Selected Fields
                  </>
                )}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <Sparkles className="text-blue-600 mt-0.5 mr-3" size={16} />
          <div>
            <h4 className="font-medium text-blue-900 mb-1">💡 Tips for Best Results</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Use a well-formatted CV in PDF or DOCX format</li>
              <li>• Ensure your LinkedIn profile is up-to-date and public</li>
              <li>• Review extracted data before applying to your profile</li>
              <li>• You can manually edit any field after auto-filling</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutoProfileFill; 