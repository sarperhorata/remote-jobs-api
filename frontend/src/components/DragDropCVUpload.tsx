import React, { useState, useRef, useCallback } from 'react';
import { Upload, FileText, X, CheckCircle, AlertCircle, Loader, Download } from 'lucide-react';
import { toast } from 'react-hot-toast';

interface DragDropCVUploadProps {
  onFileUpload: (file: File) => Promise<void>;
  onFileRemove?: () => void;
  currentCVUrl?: string;
  isUploading?: boolean;
  maxFileSize?: number; // in MB
  acceptedFileTypes?: string[];
  className?: string;
}

const DragDropCVUpload: React.FC<DragDropCVUploadProps> = ({
  onFileUpload,
  onFileRemove,
  currentCVUrl,
  isUploading = false,
  maxFileSize = 5,
  acceptedFileTypes = ['.pdf', '.doc', '.docx'],
  className = ''
}) => {
  const [isDragOver, setIsDragOver] = useState(false);
  const [dragCounter, setDragCounter] = useState(0);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [validationError, setValidationError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  // File validation
  const validateFile = useCallback((file: File): string | null => {
    // Check file type
    const fileExtension = '.' + file.name.split('.').pop()?.toLowerCase();
    if (!acceptedFileTypes.includes(fileExtension)) {
      return `File type not supported. Please upload: ${acceptedFileTypes.join(', ')}`;
    }

    // Check file size
    if (file.size > maxFileSize * 1024 * 1024) {
      return `File size must be less than ${maxFileSize}MB`;
    }

    return null;
  }, [acceptedFileTypes, maxFileSize]);

  // Handle file selection
  const handleFileSelect = useCallback(async (file: File) => {
    setValidationError(null);
    setSelectedFile(file);

    const error = validateFile(file);
    if (error) {
      setValidationError(error);
      toast.error(error);
      return;
    }

    try {
      setUploadProgress(0);
      await onFileUpload(file);
      setUploadProgress(100);
      toast.success('CV uploaded successfully!');
    } catch (error: any) {
      setValidationError(error.message || 'Upload failed');
      toast.error(error.message || 'Upload failed');
    }
  }, [onFileUpload, validateFile]);

  // Drag and drop handlers
  const handleDragEnter = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(prev => prev + 1);
    setIsDragOver(true);
  }, []);

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setDragCounter(prev => prev - 1);
    if (dragCounter <= 1) {
      setIsDragOver(false);
    }
  }, [dragCounter]);

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
  }, []);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setIsDragOver(false);
    setDragCounter(0);

    const files = Array.from(e.dataTransfer.files);
    if (files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // File input change handler
  const handleFileInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const files = e.target.files;
    if (files && files.length > 0) {
      handleFileSelect(files[0]);
    }
  }, [handleFileSelect]);

  // Remove current CV
  const handleRemoveCurrentCV = useCallback(() => {
    if (onFileRemove) {
      onFileRemove();
      toast.success('Current CV removed');
    }
  }, [onFileRemove]);

  // Format file size
  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Current CV Display */}
      {currentCVUrl && (
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <CheckCircle className="text-green-600" size={20} />
              <div>
                <h4 className="font-medium text-green-900">Current CV</h4>
                <p className="text-sm text-green-700">Your CV is uploaded and ready</p>
              </div>
            </div>
            <div className="flex items-center space-x-2">
              <a
                href={currentCVUrl}
                target="_blank"
                rel="noopener noreferrer"
                className="text-green-600 hover:text-green-800 flex items-center gap-1 text-sm"
              >
                <Download size={16} />
                View
              </a>
              {onFileRemove && (
                <button
                  onClick={handleRemoveCurrentCV}
                  className="text-red-600 hover:text-red-800 flex items-center gap-1 text-sm"
                >
                  <X size={16} />
                  Remove
                </button>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Drag & Drop Zone */}
      <div
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-all duration-200 ${
          isDragOver
            ? 'border-blue-400 bg-blue-50 scale-105'
            : 'border-gray-300 hover:border-gray-400 hover:bg-gray-50'
        } ${isUploading ? 'opacity-50 pointer-events-none' : ''}`}
        onDragEnter={handleDragEnter}
        onDragLeave={handleDragLeave}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        {/* Upload Progress Overlay */}
        {isUploading && (
          <div className="absolute inset-0 bg-white bg-opacity-90 rounded-lg flex items-center justify-center">
            <div className="text-center">
              <Loader className="animate-spin mx-auto mb-2" size={24} />
              <p className="text-sm text-gray-600">Processing your CV...</p>
              <div className="w-48 bg-gray-200 rounded-full h-2 mt-2">
                <div
                  className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                  style={{ width: `${uploadProgress}%` }}
                  role="progressbar"
                  aria-valuenow={uploadProgress}
                  aria-valuemin={0}
                  aria-valuemax={100}
                ></div>
              </div>
            </div>
          </div>
        )}

        {/* Drag & Drop Content */}
        <div className="space-y-4">
          <div className="flex justify-center">
            <div className={`p-4 rounded-full ${
              isDragOver ? 'bg-blue-100' : 'bg-gray-100'
            }`}>
              <Upload 
                size={32} 
                className={isDragOver ? 'text-blue-600' : 'text-gray-400'} 
              />
            </div>
          </div>

          <div>
            <h3 className="text-lg font-medium text-gray-900 mb-2">
              {isDragOver ? 'Drop your CV here' : 'Upload your CV'}
            </h3>
            <p className="text-gray-600 mb-4">
              Drag and drop your CV file here, or click to browse
            </p>

            {/* File Input */}
            <input
              ref={fileInputRef}
              type="file"
              accept={acceptedFileTypes.join(',')}
              onChange={handleFileInputChange}
              className="hidden"
              disabled={isUploading}
            />

            <button
              onClick={() => fileInputRef.current?.click()}
              disabled={isUploading}
              className={`inline-flex items-center px-4 py-2 rounded-lg font-medium transition-colors ${
                isUploading
                  ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                  : 'bg-blue-600 text-white hover:bg-blue-700'
              }`}
            >
              <FileText size={16} className="mr-2" />
              Choose File
            </button>
          </div>

          {/* File Info */}
          {selectedFile && !isUploading && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
              <div className="flex items-center justify-between">
                <div className="flex items-center space-x-2">
                  <FileText className="text-blue-600" size={16} />
                  <div className="text-left">
                    <p className="text-sm font-medium text-blue-900">{selectedFile.name}</p>
                    <p className="text-xs text-blue-700">{formatFileSize(selectedFile.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => setSelectedFile(null)}
                  className="text-blue-600 hover:text-blue-800"
                >
                  <X size={16} />
                </button>
              </div>
            </div>
          )}

          {/* Validation Error */}
          {validationError && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-3">
              <div className="flex items-center space-x-2">
                <AlertCircle className="text-red-600" size={16} />
                <p className="text-sm text-red-700">{validationError}</p>
              </div>
            </div>
          )}

          {/* Supported Formats */}
          <div className="text-xs text-gray-500">
            <p>Supported formats: {acceptedFileTypes.join(', ')}</p>
            <p>Maximum file size: {maxFileSize}MB</p>
          </div>
        </div>
      </div>

      {/* Upload Tips */}
      <div className="bg-gray-50 rounded-lg p-4">
        <h4 className="font-medium text-gray-900 mb-2">💡 Upload Tips</h4>
        <ul className="text-sm text-gray-600 space-y-1">
          <li>• Use PDF format for best compatibility</li>
          <li>• Ensure your CV is up-to-date and well-formatted</li>
          <li>• Include relevant keywords for better job matching</li>
          <li>• Keep file size under {maxFileSize}MB for faster upload</li>
        </ul>
      </div>
    </div>
  );
};

export default DragDropCVUpload; 