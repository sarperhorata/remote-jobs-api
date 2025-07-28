import React, { useState, useEffect } from 'react';
import { 
  FileText, 
  Upload, 
  Edit3, 
  Save, 
  Trash2, 
  Download, 
  Loader,
  AlertCircle,
  CheckCircle,
  X
} from 'lucide-react';
import { toast } from 'react-hot-toast';

interface CoverLetterData {
  text?: string;
  file?: {
    url: string;
    filename: string;
    uploaded_at: string;
  };
}

interface CoverLetterManagerProps {
  className?: string;
  onUpdate?: () => void;
}

const CoverLetterManager: React.FC<CoverLetterManagerProps> = ({
  className = '',
  onUpdate
}) => {
  const [coverLetterData, setCoverLetterData] = useState<CoverLetterData | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isEditing, setIsEditing] = useState(false);
  const [textContent, setTextContent] = useState('');
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [uploadMode, setUploadMode] = useState<'text' | 'file'>('text');

  // Load cover letter data
  const loadCoverLetter = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/cover-letter`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const result = await response.json();
        setCoverLetterData(result.data);
        setTextContent(result.data.text || '');
      }
    } catch (error) {
      console.error('Error loading cover letter:', error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    loadCoverLetter();
  }, []);

  // Handle file selection
  const handleFileSelect = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      const allowedTypes = ['.pdf', '.doc', '.docx', '.txt'];
      const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
      
      if (!allowedTypes.includes(fileExtension)) {
        toast.error('Please select a valid file type (PDF, DOC, DOCX, or TXT)');
        return;
      }
      
      if (file.size > 5 * 1024 * 1024) { // 5MB limit
        toast.error('File size must be less than 5MB');
        return;
      }
      
      setSelectedFile(file);
    }
  };

  // Save cover letter
  const handleSave = async () => {
    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      
      if (uploadMode === 'file' && selectedFile) {
        const formData = new FormData();
        formData.append('file', selectedFile);
        
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/cover-letter`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
          body: formData,
        });

        if (response.ok) {
          toast.success('Cover letter file uploaded successfully!');
          setSelectedFile(null);
          setIsEditing(false);
          loadCoverLetter();
          onUpdate?.();
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to upload cover letter');
        }
      } else if (uploadMode === 'text' && textContent.trim()) {
        const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/cover-letter`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({ cover_letter_text: textContent }),
        });

        if (response.ok) {
          toast.success('Cover letter text saved successfully!');
          setIsEditing(false);
          loadCoverLetter();
          onUpdate?.();
        } else {
          const error = await response.json();
          throw new Error(error.detail || 'Failed to save cover letter');
        }
      } else {
        toast.error('Please provide content to save');
        return;
      }
    } catch (error: any) {
      console.error('Error saving cover letter:', error);
      toast.error(error.message || 'Failed to save cover letter');
    } finally {
      setIsLoading(false);
    }
  };

  // Delete cover letter
  const handleDelete = async () => {
    if (!window.confirm('Are you sure you want to delete your cover letter?')) {
      return;
    }

    try {
      setIsLoading(true);
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/profile/cover-letter`, {
        method: 'DELETE',
        headers: {
          'Authorization': `Bearer ${token}`,
        },
      });

      if (response.ok) {
        toast.success('Cover letter deleted successfully!');
        setCoverLetterData(null);
        setTextContent('');
        setSelectedFile(null);
        setIsEditing(false);
        onUpdate?.();
      } else {
        const error = await response.json();
        throw new Error(error.detail || 'Failed to delete cover letter');
      }
    } catch (error: any) {
      console.error('Error deleting cover letter:', error);
      toast.error(error.message || 'Failed to delete cover letter');
    } finally {
      setIsLoading(false);
    }
  };

  // Download cover letter file
  const handleDownload = () => {
    if (coverLetterData?.file?.url) {
      window.open(coverLetterData.file.url, '_blank');
    }
  };

  return (
    <div className={`space-y-6 ${className}`}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 flex items-center">
            <FileText className="mr-2" size={20} />
            Cover Letter
          </h3>
          <p className="text-sm text-gray-600">
            Upload a cover letter file or write one directly
          </p>
        </div>
        
        {coverLetterData && (coverLetterData.text || coverLetterData.file) && (
          <div className="flex items-center space-x-2">
            <button
              onClick={handleDelete}
              disabled={isLoading}
              className="inline-flex items-center px-3 py-2 text-sm text-red-600 hover:text-red-800 hover:bg-red-50 rounded-lg transition-colors"
            >
              <Trash2 size={16} className="mr-1" />
              Delete
            </button>
          </div>
        )}
      </div>

      {/* Loading State */}
      {isLoading && (
        <div className="flex items-center justify-center py-8">
          <Loader className="animate-spin text-blue-600" size={24} />
          <span className="ml-2 text-gray-600">Loading...</span>
        </div>
      )}

      {/* Existing Cover Letter Display */}
      {!isLoading && coverLetterData && (coverLetterData.text || coverLetterData.file) && !isEditing && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          {coverLetterData.file && (
            <div className="mb-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <FileText className="text-blue-600 mr-2" size={20} />
                  <span className="font-medium text-gray-900">{coverLetterData.file.filename}</span>
                </div>
                <button
                  onClick={handleDownload}
                  className="inline-flex items-center px-3 py-1 text-sm text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded transition-colors"
                >
                  <Download size={16} className="mr-1" />
                  Download
                </button>
              </div>
              <p className="text-sm text-gray-500 mt-1">
                Uploaded on {new Date(coverLetterData.file.uploaded_at).toLocaleDateString()}
              </p>
            </div>
          )}

          {coverLetterData.text && (
            <div className="mb-4">
              <h4 className="font-medium text-gray-900 mb-2">Cover Letter Text</h4>
              <div className="bg-gray-50 rounded-lg p-4 max-h-60 overflow-y-auto">
                <p className="text-gray-700 whitespace-pre-wrap">{coverLetterData.text}</p>
              </div>
            </div>
          )}

          <button
            onClick={() => setIsEditing(true)}
            className="inline-flex items-center px-4 py-2 text-sm font-medium text-blue-600 hover:text-blue-800 hover:bg-blue-50 rounded-lg transition-colors"
          >
            <Edit3 size={16} className="mr-2" />
            Edit Cover Letter
          </button>
        </div>
      )}

      {/* Edit Mode */}
      {isEditing && (
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <div className="mb-4">
            <div className="flex items-center space-x-4 mb-4">
              <button
                onClick={() => setUploadMode('text')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  uploadMode === 'text'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Write Text
              </button>
              <button
                onClick={() => setUploadMode('file')}
                className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  uploadMode === 'file'
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                }`}
              >
                Upload File
              </button>
            </div>
          </div>

          {uploadMode === 'text' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Cover Letter Text
                </label>
                <textarea
                  value={textContent}
                  onChange={(e) => setTextContent(e.target.value)}
                  rows={12}
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  placeholder="Write your cover letter here..."
                />
                <p className="text-sm text-gray-500 mt-1">
                  {textContent.length} characters
                </p>
              </div>
            </div>
          )}

          {uploadMode === 'file' && (
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Upload Cover Letter File
                </label>
                <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                  <Upload className="mx-auto text-gray-400 mb-2" size={32} />
                  <p className="text-sm text-gray-600 mb-2">
                    Drag and drop your cover letter file here, or click to browse
                  </p>
                  <input
                    type="file"
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={handleFileSelect}
                    className="hidden"
                    id="cover-letter-file"
                  />
                  <label
                    htmlFor="cover-letter-file"
                    className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 cursor-pointer transition-colors"
                  >
                    Choose File
                  </label>
                  <p className="text-xs text-gray-500 mt-2">
                    Supported formats: PDF, DOC, DOCX, TXT (max 5MB)
                  </p>
                </div>
                {selectedFile && (
                  <div className="mt-2 p-3 bg-green-50 border border-green-200 rounded-lg">
                    <div className="flex items-center">
                      <CheckCircle className="text-green-600 mr-2" size={16} />
                      <span className="text-sm text-green-800">{selectedFile.name}</span>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          <div className="flex items-center justify-end space-x-3 pt-4 border-t border-gray-200">
            <button
              onClick={() => {
                setIsEditing(false);
                setSelectedFile(null);
                setTextContent(coverLetterData?.text || '');
              }}
              className="px-4 py-2 text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 transition-colors"
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isLoading || (uploadMode === 'text' && !textContent.trim()) || (uploadMode === 'file' && !selectedFile)}
              className={`inline-flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                isLoading || (uploadMode === 'text' && !textContent.trim()) || (uploadMode === 'file' && !selectedFile)
                  ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              {isLoading ? (
                <>
                  <Loader className="animate-spin mr-2" size={16} />
                  Saving...
                </>
              ) : (
                <>
                  <Save className="mr-2" size={16} />
                  Save Cover Letter
                </>
              )}
            </button>
          </div>
        </div>
      )}

      {/* No Cover Letter State */}
      {!isLoading && !coverLetterData && !isEditing && (
        <div className="bg-gray-50 border border-gray-200 rounded-lg p-8 text-center">
          <FileText className="mx-auto text-gray-400 mb-4" size={48} />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No Cover Letter Yet</h3>
          <p className="text-gray-600 mb-4">
            Create a cover letter to make your job applications stand out
          </p>
          <button
            onClick={() => setIsEditing(true)}
            className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Edit3 className="mr-2" size={16} />
            Create Cover Letter
          </button>
        </div>
      )}

      {/* Tips */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start">
          <AlertCircle className="text-blue-600 mt-0.5 mr-3" size={16} />
          <div>
            <h4 className="font-medium text-blue-900 mb-1">💡 Cover Letter Tips</h4>
            <ul className="text-sm text-blue-700 space-y-1">
              <li>• Keep it concise and professional (1-2 pages)</li>
              <li>• Tailor it to the specific job and company</li>
              <li>• Highlight relevant experience and achievements</li>
              <li>• Show enthusiasm for the role and company</li>
              <li>• Proofread carefully before submitting</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CoverLetterManager; 