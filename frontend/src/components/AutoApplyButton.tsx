import React, { useState } from 'react';
import { Zap, Loader, CheckCircle2, AlertCircle } from './icons/EmojiIcons';
import { getApiUrl } from '../utils/apiConfig';

interface AutoApplyButtonProps {
  jobUrl: string;
  jobId: string;
  onApplied?: (applicationId: string) => void;
  className?: string;
  size?: 'sm' | 'md' | 'lg';
}

const AutoApplyButton: React.FC<AutoApplyButtonProps> = ({
  jobUrl,
  jobId,
  onApplied,
  className = '',
  size = 'md'
}) => {
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [showPreview, setShowPreview] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [previewData, setPreviewData] = useState<any>(null);
  const [error, setError] = useState<string>('');
  const [success, setSuccess] = useState(false);

  // Size configurations
  const sizeConfig = {
    sm: {
      button: 'px-3 py-1.5 text-xs',
      icon: 'w-3 h-3',
      text: 'text-xs'
    },
    md: {
      button: 'px-4 py-2 text-sm',
      icon: 'w-4 h-4',
      text: 'text-sm'
    },
    lg: {
      button: 'px-6 py-3 text-base',
      icon: 'w-5 h-5',
      text: 'text-base'
    }
  };

  const config = sizeConfig[size];

  const analyzeForm = async () => {
    setIsAnalyzing(true);
    setError('');
    
    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('Please login to use Auto Apply');
      }

      const response = await fetch(`${apiUrl}/auto-apply/analyze-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_url: jobUrl
        })
      });

      if (!response.ok) {
        throw new Error('Failed to analyze job form');
      }

      const result = await response.json();
      setAnalysisResult(result);

      if (result.auto_apply_supported) {
        // Get preview of generated responses
        await getPreview();
      } else {
        setError('Auto Apply is not supported for this job posting. The form is too complex or not detected.');
      }

    } catch (err: any) {
      setError(err.message || 'Failed to analyze job form');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getPreview = async () => {
    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiUrl}/auto-apply/preview-responses`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_url: jobUrl
        })
      });

      if (!response.ok) {
        throw new Error('Failed to generate preview');
      }

      const preview = await response.json();
      setPreviewData(preview);
      setShowPreview(true);

    } catch (err: any) {
      setError(err.message || 'Failed to generate preview');
    }
  };

  const performAutoApply = async () => {
    setIsApplying(true);
    setError('');

    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      const response = await fetch(`${apiUrl}/auto-apply/auto-apply`, {
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
        throw new Error('Auto Apply failed');
      }

      const result = await response.json();
      
      if (result.success) {
        setSuccess(true);
        setShowPreview(false);
        if (onApplied && result.application_id) {
          onApplied(result.application_id);
        }
      } else {
        throw new Error(result.message || 'Auto Apply failed');
      }

    } catch (err: any) {
      setError(err.message || 'Auto Apply failed');
    } finally {
      setIsApplying(false);
    }
  };

  // If already successfully applied
  if (success) {
    return (
      <div className={`flex items-center gap-2 ${config.text} text-green-600 ${className}`}>
        <CheckCircle2 className={config.icon} />
        Auto Applied
      </div>
    );
  }

  // Initial state - show Auto Apply button
  if (!analysisResult && !showPreview) {
    return (
      <button
        onClick={analyzeForm}
        disabled={isAnalyzing}
        className={`bg-purple-600 hover:bg-purple-700 text-white rounded-lg transition-colors font-medium flex items-center gap-2 disabled:bg-purple-400 disabled:cursor-not-allowed ${config.button} ${className}`}
      >
        {isAnalyzing ? (
          <>
            <Loader className={`${config.icon} animate-spin`} />
            Analyzing...
          </>
        ) : (
          <>
            <Zap className={config.icon} />
            Auto Apply
          </>
        )}
      </button>
    );
  }

  // Show error if any
  if (error) {
    return (
      <div className="space-y-2">
        <div className={`flex items-center gap-2 ${config.text} text-red-600`}>
          <AlertCircle className={config.icon} />
          <span>Auto Apply Failed</span>
        </div>
        <div className="text-xs text-red-500">{error}</div>
        <button
          onClick={() => {
            setError('');
            setAnalysisResult(null);
            setShowPreview(false);
          }}
          className={`text-purple-600 hover:text-purple-700 ${config.text} underline`}
        >
          Try Again
        </button>
      </div>
    );
  }

  // Show preview modal/popup
  if (showPreview && previewData) {
    return (
      <div className="relative">
        {/* The button that triggers the modal is outside, this is just the modal content */}
        <div className="absolute top-full left-0 mt-2 w-80 bg-white border border-gray-200 rounded-lg shadow-lg p-4 z-50">
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <h4 className="font-medium text-gray-900">Auto Apply Preview</h4>
              <button
                onClick={() => setShowPreview(false)}
                className="text-gray-400 hover:text-gray-600"
              >
                ✕
              </button>
            </div>
    
            <div className="text-sm text-gray-600">
              <div className="flex justify-between mb-2">
                <span>Form fields detected:</span>
                <span className="font-medium">{previewData.total_fields}</span>
              </div>
              <div className="flex justify-between mb-2">
                <span>Auto-fillable fields:</span>
                <span className="font-medium text-green-600">{previewData.fields_with_responses}</span>
              </div>
              <div className="flex justify-between">
                <span>Profile completeness:</span>
                <span className="font-medium">{previewData.user_profile_completeness?.overall_percentage}%</span>
              </div>
            </div>
    
            {previewData.user_profile_completeness?.ready_for_auto_apply ? (
              <div className="text-sm text-green-600 bg-green-50 p-2 rounded">
                ✓ Your profile is ready for Auto Apply
              </div>
            ) : (
              <div className="text-sm text-yellow-600 bg-yellow-50 p-2 rounded">
                ⚠ Complete your profile for better Auto Apply results
              </div>
            )}
    
            <div className="space-y-2">
              <h5 className="text-sm font-medium text-gray-700">Sample responses:</h5>
              <div className="max-h-32 overflow-y-auto space-y-1">
                {previewData.field_previews?.slice(0, 3).map((field: any, index: number) => (
                  <div key={index} className="text-xs bg-gray-50 p-2 rounded">
                    <div className="font-medium text-gray-700">{field.field_label || field.field_name}</div>
                    <div className="text-gray-600 truncate">{field.generated_value || 'Will be auto-filled'}</div>
                  </div>
                ))}
              </div>
            </div>
    
            <div className="flex gap-2 pt-2 border-t">
              <button
                onClick={performAutoApply}
                disabled={isApplying}
                className="flex-1 bg-purple-600 hover:bg-purple-700 text-white px-3 py-2 rounded text-sm font-medium disabled:bg-purple-400"
              >
                {isApplying ? 'Applying...' : 'Confirm Auto Apply'}
              </button>
              <button
                onClick={() => {
                  setShowPreview(false);
                  setAnalysisResult(null); // Reset analysis on cancel
                }}
                className="px-3 py-2 border border-gray-300 rounded text-sm hover:bg-gray-50"
              >
                Cancel
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return null;
};

export default AutoApplyButton; 