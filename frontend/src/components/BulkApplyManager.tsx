import React, { useState, useEffect } from 'react';
import { Zap, Users, FileText, Clock, CheckCircle, AlertCircle, BarChart3 } from './icons/EmojiIcons';
import BulkJobSelector from './BulkJobSelector';
import AutoFormFiller from './AutoFormFiller';
import BulkApplyQueue from './BulkApplyQueue';
import { getApiUrl } from '../utils/apiConfig';

interface Job {
  _id: string;
  id: string;
  title: string;
  company: {
    name: string;
    logo?: string;
  };
  location: string;
  job_type: string;
  salary_min?: number;
  salary_max?: number;
  url: string;
  is_active: boolean;
  created_at: string;
}

interface BulkApplyManagerProps {
  className?: string;
}

const BulkApplyManager: React.FC<BulkApplyManagerProps> = ({ className = '' }) => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJobs, setSelectedJobs] = useState<Job[]>([]);
  const [currentStep, setCurrentStep] = useState<'select' | 'configure' | 'queue' | 'complete'>('select');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string>('');
  const [stats, setStats] = useState({
    totalApplied: 0,
    successful: 0,
    failed: 0,
    skipped: 0
  });

  // Load available jobs
  useEffect(() => {
    loadJobs();
  }, []);

  const loadJobs = async () => {
    setIsLoading(true);
    setError('');

    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Authentication required');
      }

      const response = await fetch(`${apiUrl}/jobs`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (!response.ok) {
        throw new Error('Failed to load jobs');
      }

      const jobsData = await response.json();
      setJobs(jobsData);
    } catch (err: any) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  // Handle job selection change
  const handleSelectionChange = (selected: Job[]) => {
    setSelectedJobs(selected);
  };

  // Handle bulk apply
  const handleBulkApply = (appliedJobs: Job[]) => {
    setStats(prev => ({
      ...prev,
      totalApplied: prev.totalApplied + appliedJobs.length
    }));
    setCurrentStep('queue');
  };

  // Handle job completion
  const handleJobComplete = (jobId: string, result: any) => {
    setStats(prev => ({
      ...prev,
      successful: prev.successful + 1
    }));
  };

  // Handle job error
  const handleJobError = (jobId: string, error: string) => {
    setStats(prev => ({
      ...prev,
      failed: prev.failed + 1
    }));
  };

  // Handle queue completion
  const handleQueueComplete = () => {
    setCurrentStep('complete');
  };

  // Reset to selection step
  const resetToSelection = () => {
    setCurrentStep('select');
    setSelectedJobs([]);
    setStats({
      totalApplied: 0,
      successful: 0,
      failed: 0,
      skipped: 0
    });
  };

  // Convert selected jobs to queue format
  const getQueueJobs = () => {
    return selectedJobs.map(job => ({
      id: job._id,
      jobId: job._id,
      title: job.title,
      company: job.company.name,
      url: job.url,
      status: 'pending' as const,
      priority: 0,
      retryCount: 0,
      maxRetries: 3,
      createdAt: new Date()
    }));
  };

  // Render step content
  const renderStepContent = () => {
    switch (currentStep) {
      case 'select':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Bulk Job Application</h2>
              <p className="text-gray-600">
                Select multiple jobs and apply to them automatically with our intelligent form filling system.
              </p>
            </div>

            {isLoading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-purple-600 mx-auto"></div>
                <p className="mt-2 text-gray-600">Loading available jobs...</p>
              </div>
            ) : error ? (
              <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                <div className="flex items-center gap-2 text-red-800">
                  <AlertCircle className="w-5 h-5" />
                  <span className="font-medium">Error</span>
                </div>
                <p className="text-sm text-red-600 mt-1">{error}</p>
                <button
                  onClick={loadJobs}
                  className="mt-2 text-red-600 hover:text-red-800 text-sm underline"
                >
                  Try Again
                </button>
              </div>
            ) : (
              <BulkJobSelector
                jobs={jobs}
                onSelectionChange={handleSelectionChange}
                onBulkApply={handleBulkApply}
              />
            )}
          </div>
        );

      case 'configure':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Configure Auto Apply</h2>
              <p className="text-gray-600">
                Review and configure your auto apply settings for {selectedJobs.length} selected jobs.
              </p>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <FileText className="w-5 h-5" />
                  Form Filling Configuration
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Configure how the system should fill out application forms automatically.
                </p>
                {/* Form filler configuration would go here */}
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Auto-fill personal info</span>
                    <span className="text-sm text-green-600">✓ Enabled</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Generate cover letters</span>
                    <span className="text-sm text-green-600">✓ Enabled</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Skip complex forms</span>
                    <span className="text-sm text-green-600">✓ Enabled</span>
                  </div>
                </div>
              </div>

              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <h3 className="text-lg font-medium text-gray-900 mb-4 flex items-center gap-2">
                  <Clock className="w-5 h-5" />
                  Queue Settings
                </h3>
                <p className="text-sm text-gray-600 mb-4">
                  Configure how jobs should be processed in the queue.
                </p>
                <div className="space-y-3">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Max concurrent jobs</span>
                    <span className="text-sm text-gray-600">1</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Delay between jobs</span>
                    <span className="text-sm text-gray-600">3 seconds</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Max retries</span>
                    <span className="text-sm text-gray-600">3</span>
                  </div>
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-700">Rate limit</span>
                    <span className="text-sm text-gray-600">20/min</span>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4">
              <button
                onClick={() => setCurrentStep('select')}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Back to Selection
              </button>
              <button
                onClick={() => setCurrentStep('queue')}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Start Bulk Apply
              </button>
            </div>
          </div>
        );

      case 'queue':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Processing Applications</h2>
              <p className="text-gray-600">
                Your applications are being processed automatically. You can monitor the progress below.
              </p>
            </div>

            <BulkApplyQueue
              jobs={getQueueJobs()}
              onJobComplete={handleJobComplete}
              onJobError={handleJobError}
              onQueueComplete={handleQueueComplete}
            />
          </div>
        );

      case 'complete':
        return (
          <div className="space-y-6">
            <div className="text-center">
              <h2 className="text-2xl font-bold text-gray-900 mb-2">Bulk Apply Complete!</h2>
              <p className="text-gray-600">
                Your bulk application process has finished. Here's a summary of the results.
              </p>
            </div>

            <div className="bg-white border border-gray-200 rounded-lg p-6">
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center">
                  <div className="text-2xl font-bold text-purple-600">{stats.totalApplied}</div>
                  <div className="text-sm text-gray-600">Total Applied</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-green-600">{stats.successful}</div>
                  <div className="text-sm text-gray-600">Successful</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-red-600">{stats.failed}</div>
                  <div className="text-sm text-gray-600">Failed</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl font-bold text-yellow-600">{stats.skipped}</div>
                  <div className="text-sm text-gray-600">Skipped</div>
                </div>
              </div>

              <div className="mt-6 pt-6 border-t border-gray-200">
                <h3 className="text-lg font-medium text-gray-900 mb-3">What's Next?</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <p>• Check your email for application confirmations</p>
                  <p>• Monitor your application status in the dashboard</p>
                  <p>• Follow up with companies after a few days</p>
                  <p>• Review and improve your profile for better results</p>
                </div>
              </div>
            </div>

            <div className="flex items-center justify-center gap-4">
              <button
                onClick={resetToSelection}
                className="px-6 py-2 bg-purple-600 text-white rounded-lg hover:bg-purple-700"
              >
                Apply to More Jobs
              </button>
              <button
                onClick={() => window.location.href = '/dashboard'}
                className="px-6 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Go to Dashboard
              </button>
            </div>
          </div>
        );

      default:
        return null;
    }
  };

  // Render step indicator
  const renderStepIndicator = () => {
    const steps = [
      { key: 'select', label: 'Select Jobs', icon: Users },
      { key: 'configure', label: 'Configure', icon: FileText },
      { key: 'queue', label: 'Processing', icon: Clock },
      { key: 'complete', label: 'Complete', icon: CheckCircle }
    ];

    return (
      <div className="flex items-center justify-center mb-8">
        <div className="flex items-center space-x-4">
          {steps.map((step, index) => {
            const Icon = step.icon;
            const isActive = currentStep === step.key;
            const isCompleted = steps.findIndex(s => s.key === currentStep) > index;

            return (
              <div key={step.key} className="flex items-center">
                <div className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                  isActive 
                    ? 'border-purple-600 bg-purple-600 text-white' 
                    : isCompleted 
                    ? 'border-green-600 bg-green-600 text-white'
                    : 'border-gray-300 bg-white text-gray-400'
                }`}>
                  <Icon className="w-5 h-5" />
                </div>
                <span className={`ml-2 text-sm font-medium ${
                  isActive ? 'text-purple-600' : isCompleted ? 'text-green-600' : 'text-gray-400'
                }`}>
                  {step.label}
                </span>
                {index < steps.length - 1 && (
                  <div className={`w-8 h-0.5 mx-4 ${
                    isCompleted ? 'bg-green-600' : 'bg-gray-300'
                  }`} />
                )}
              </div>
            );
          })}
        </div>
      </div>
    );
  };

  return (
    <div className={`max-w-6xl mx-auto px-4 py-8 ${className}`}>
      {renderStepIndicator()}
      {renderStepContent()}
    </div>
  );
};

export default BulkApplyManager; 