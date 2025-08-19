import React, { useState, useEffect } from 'react';
import { CheckSquare, Square, ExternalLink, Trash2, Play, Pause, Settings } from './icons/EmojiIcons';
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

interface BulkJobSelectorProps {
  jobs: Job[];
  onSelectionChange: (selectedJobs: Job[]) => void;
  onBulkApply: (selectedJobs: Job[]) => void;
  className?: string;
}

const BulkJobSelector: React.FC<BulkJobSelectorProps> = ({
  jobs,
  onSelectionChange,
  onBulkApply,
  className = ''
}) => {
  const [selectedJobs, setSelectedJobs] = useState<Set<string>>(new Set());
  const [selectAll, setSelectAll] = useState(false);
  const [isBulkApplying, setIsBulkApplying] = useState(false);
  const [bulkApplyProgress, setBulkApplyProgress] = useState(0);
  const [bulkApplyStatus, setBulkApplyStatus] = useState<'idle' | 'running' | 'paused' | 'completed' | 'error'>('idle');
  const [showSettings, setShowSettings] = useState(false);
  const [settings, setSettings] = useState({
    delayBetweenApplications: 2000, // 2 seconds
    maxApplicationsPerSession: 10,
    openInNewTab: true,
    autoFillForms: true,
    skipComplexForms: true
  });

  // Update parent when selection changes
  useEffect(() => {
    const selectedJobObjects = jobs.filter(job => selectedJobs.has(job._id));
    onSelectionChange(selectedJobObjects);
  }, [selectedJobs, jobs, onSelectionChange]);

  // Handle select all
  const handleSelectAll = () => {
    if (selectAll) {
      setSelectedJobs(new Set());
      setSelectAll(false);
    } else {
      const allJobIds = new Set(jobs.map(job => job._id));
      setSelectedJobs(allJobIds);
      setSelectAll(true);
    }
  };

  // Handle individual job selection
  const handleJobSelection = (jobId: string) => {
    const newSelection = new Set(selectedJobs);
    if (newSelection.has(jobId)) {
      newSelection.delete(jobId);
    } else {
      newSelection.add(jobId);
    }
    setSelectedJobs(newSelection);
    setSelectAll(newSelection.size === jobs.length);
  };

  // Handle bulk apply
  const handleBulkApply = async () => {
    if (selectedJobs.size === 0) return;

    setIsBulkApplying(true);
    setBulkApplyStatus('running');
    setBulkApplyProgress(0);

    const selectedJobObjects = jobs.filter(job => selectedJobs.has(job._id));
    const maxJobs = Math.min(selectedJobObjects.length, settings.maxApplicationsPerSession);

    try {
      for (let i = 0; i < maxJobs; i++) {
        if (bulkApplyStatus === 'paused') {
          break;
        }

        const job = selectedJobObjects[i];
        setBulkApplyProgress(((i + 1) / maxJobs) * 100);

        // Open job in new tab if enabled
        if (settings.openInNewTab) {
          window.open(job.url, '_blank');
        }

        // Auto apply if enabled
        if (settings.autoFillForms) {
          await performAutoApply(job);
        }

        // Delay between applications
        if (i < maxJobs - 1) {
          await new Promise(resolve => setTimeout(resolve, settings.delayBetweenApplications));
        }
      }

      setBulkApplyStatus('completed');
      onBulkApply(selectedJobObjects.slice(0, maxJobs));
    } catch (error) {
      console.error('Bulk apply error:', error);
      setBulkApplyStatus('error');
    } finally {
      setIsBulkApplying(false);
    }
  };

  // Perform auto apply for a single job
  const performAutoApply = async (job: Job) => {
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
          job_url: job.url,
          job_id: job._id
        })
      });

      if (!response.ok) {
        if (settings.skipComplexForms) {
          console.log(`Skipping complex form for job: ${job.title}`);
          return;
        }
        throw new Error('Failed to analyze job form');
      }

      const result = await response.json();

      if (result.auto_apply_supported) {
        // Perform the actual auto apply
        const applyResponse = await fetch(`${apiUrl}/auto-apply/auto-apply`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
          },
          body: JSON.stringify({
            job_url: job.url,
            job_id: job._id
          })
        });

        if (!applyResponse.ok) {
          throw new Error('Auto apply failed');
        }
      }
    } catch (error) {
      console.error(`Auto apply failed for job ${job.title}:`, error);
      if (!settings.skipComplexForms) {
        throw error;
      }
    }
  };

  // Pause bulk apply
  const pauseBulkApply = () => {
    setBulkApplyStatus('paused');
  };

  // Resume bulk apply
  const resumeBulkApply = () => {
    setBulkApplyStatus('running');
    handleBulkApply();
  };

  // Reset bulk apply
  const resetBulkApply = () => {
    setBulkApplyStatus('idle');
    setBulkApplyProgress(0);
    setIsBulkApplying(false);
  };

  const selectedCount = selectedJobs.size;
  const isAnySelected = selectedCount > 0;

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Bulk Actions Header */}
      <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center gap-4">
          <label className="flex items-center gap-2 cursor-pointer">
            <input
              type="checkbox"
              checked={selectAll}
              onChange={handleSelectAll}
              className="sr-only"
            />
            {selectAll ? (
              <CheckSquare className="w-5 h-5 text-blue-600" />
            ) : (
              <Square className="w-5 h-5 text-gray-400" />
            )}
            <span className="font-medium">
              Select All ({jobs.length} jobs)
            </span>
          </label>
          
          {isAnySelected && (
            <span className="text-sm text-gray-600">
              {selectedCount} job{selectedCount !== 1 ? 's' : ''} selected
            </span>
          )}
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
            title="Bulk Apply Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {isAnySelected && (
            <button
              onClick={handleBulkApply}
              disabled={isBulkApplying}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 disabled:bg-purple-400 disabled:cursor-not-allowed"
            >
              <Play className="w-4 h-4" />
              Bulk Apply ({selectedCount})
            </button>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
          <h3 className="font-medium text-gray-900">Bulk Apply Settings</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delay between applications (ms)
              </label>
              <input
                type="number"
                value={settings.delayBetweenApplications}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  delayBetweenApplications: parseInt(e.target.value) || 2000
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="1000"
                max="10000"
                step="500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max applications per session
              </label>
              <input
                type="number"
                value={settings.maxApplicationsPerSession}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  maxApplicationsPerSession: parseInt(e.target.value) || 10
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="1"
                max="50"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.openInNewTab}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  openInNewTab: e.target.checked
                }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Open jobs in new tabs</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.autoFillForms}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  autoFillForms: e.target.checked
                }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Auto-fill application forms</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.skipComplexForms}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  skipComplexForms: e.target.checked
                }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Skip complex forms</span>
            </label>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {isBulkApplying && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Bulk Apply Progress
            </span>
            <span className="text-sm text-gray-600">
              {Math.round(bulkApplyProgress)}%
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${bulkApplyProgress}%` }}
            />
          </div>

          <div className="flex items-center gap-2 mt-3">
            {bulkApplyStatus === 'running' && (
              <button
                onClick={pauseBulkApply}
                className="bg-yellow-500 hover:bg-yellow-600 text-white px-3 py-1 rounded text-sm"
              >
                Pause
              </button>
            )}
            
            {bulkApplyStatus === 'paused' && (
              <button
                onClick={resumeBulkApply}
                className="bg-green-500 hover:bg-green-600 text-white px-3 py-1 rounded text-sm"
              >
                Resume
              </button>
            )}
            
            <button
              onClick={resetBulkApply}
              className="bg-gray-500 hover:bg-gray-600 text-white px-3 py-1 rounded text-sm"
            >
              Reset
            </button>
          </div>
        </div>
      )}

      {/* Job List */}
      <div className="space-y-2">
        {jobs.map((job) => (
          <div
            key={job._id}
            className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg hover:bg-gray-50"
          >
            <label className="flex items-center gap-3 cursor-pointer flex-1">
              <input
                type="checkbox"
                checked={selectedJobs.has(job._id)}
                onChange={() => handleJobSelection(job._id)}
                className="sr-only"
              />
              {selectedJobs.has(job._id) ? (
                <CheckSquare className="w-5 h-5 text-blue-600" />
              ) : (
                <Square className="w-5 h-5 text-gray-400" />
              )}
              
              <div className="flex-1">
                <h4 className="font-medium text-gray-900">{job.title}</h4>
                <p className="text-sm text-gray-600">{job.company.name} • {job.location}</p>
                <div className="flex items-center gap-2 mt-1">
                  <span className="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">
                    {job.job_type}
                  </span>
                  {job.salary_min && job.salary_max && (
                    <span className="text-xs text-gray-600">
                      ${job.salary_min.toLocaleString()} - ${job.salary_max.toLocaleString()}
                    </span>
                  )}
                </div>
              </div>
            </label>

            <div className="flex items-center gap-2">
              <button
                onClick={() => window.open(job.url, '_blank')}
                className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
                title="Open in new tab"
              >
                <ExternalLink className="w-4 h-4" />
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BulkJobSelector; 