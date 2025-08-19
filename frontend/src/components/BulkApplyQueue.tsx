import React, { useState, useEffect, useRef } from 'react';
import { Clock, Play, Pause, Stop, CheckCircle, AlertCircle, Loader, Settings, BarChart3 } from './icons/EmojiIcons';
import { getApiUrl } from '../utils/apiConfig';

interface QueueJob {
  id: string;
  jobId: string;
  title: string;
  company: string;
  url: string;
  status: 'pending' | 'processing' | 'completed' | 'failed' | 'skipped';
  priority: number;
  retryCount: number;
  maxRetries: number;
  createdAt: Date;
  startedAt?: Date;
  completedAt?: Date;
  error?: string;
  result?: any;
}

interface QueueSettings {
  maxConcurrentJobs: number;
  delayBetweenJobs: number;
  maxRetries: number;
  rateLimitPerMinute: number;
  autoRetry: boolean;
  skipOnError: boolean;
}

interface BulkApplyQueueProps {
  jobs: QueueJob[];
  onJobComplete: (jobId: string, result: any) => void;
  onJobError: (jobId: string, error: string) => void;
  onQueueComplete: () => void;
  className?: string;
}

const BulkApplyQueue: React.FC<BulkApplyQueueProps> = ({
  jobs,
  onJobComplete,
  onJobError,
  onQueueComplete,
  className = ''
}) => {
  const [queue, setQueue] = useState<QueueJob[]>([]);
  const [isRunning, setIsRunning] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [currentJobIndex, setCurrentJobIndex] = useState(0);
  const [settings, setSettings] = useState<QueueSettings>({
    maxConcurrentJobs: 1,
    delayBetweenJobs: 3000,
    maxRetries: 3,
    rateLimitPerMinute: 20,
    autoRetry: true,
    skipOnError: false
  });
  const [showSettings, setShowSettings] = useState(false);
  const [stats, setStats] = useState({
    total: 0,
    completed: 0,
    failed: 0,
    skipped: 0,
    pending: 0,
    processing: 0
  });
  const [rateLimitTracker, setRateLimitTracker] = useState<Date[]>([]);
  
  const queueRef = useRef<NodeJS.Timeout | null>(null);
  const rateLimitRef = useRef<NodeJS.Timeout | null>(null);

  // Initialize queue with jobs
  useEffect(() => {
    const initialQueue = jobs.map((job, index) => ({
      ...job,
      priority: index,
      retryCount: 0,
      status: 'pending' as const,
      createdAt: new Date()
    }));
    setQueue(initialQueue);
    setStats({
      total: initialQueue.length,
      completed: 0,
      failed: 0,
      skipped: 0,
      pending: initialQueue.length,
      processing: 0
    });
  }, [jobs]);

  // Update stats when queue changes
  useEffect(() => {
    const newStats = {
      total: queue.length,
      completed: queue.filter(job => job.status === 'completed').length,
      failed: queue.filter(job => job.status === 'failed').length,
      skipped: queue.filter(job => job.status === 'skipped').length,
      pending: queue.filter(job => job.status === 'pending').length,
      processing: queue.filter(job => job.status === 'processing').length
    };
    setStats(newStats);
  }, [queue]);

  // Rate limiting cleanup
  useEffect(() => {
    return () => {
      if (rateLimitRef.current) {
        clearInterval(rateLimitRef.current);
      }
    };
  }, []);

  // Check rate limit
  const checkRateLimit = () => {
    const now = new Date();
    const oneMinuteAgo = new Date(now.getTime() - 60000);
    
    // Remove old entries
    const recentRequests = rateLimitTracker.filter(time => time > oneMinuteAgo);
    setRateLimitTracker(recentRequests);
    
    return recentRequests.length < settings.rateLimitPerMinute;
  };

  // Add to rate limit tracker
  const addToRateLimit = () => {
    setRateLimitTracker(prev => [...prev, new Date()]);
  };

  // Process a single job
  const processJob = async (job: QueueJob): Promise<void> => {
    // Check rate limit
    if (!checkRateLimit()) {
      console.log('Rate limit exceeded, skipping job:', job.title);
      updateJobStatus(job.id, 'skipped', 'Rate limit exceeded');
      return;
    }

    // Update job status to processing
    updateJobStatus(job.id, 'processing');
    addToRateLimit();

    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('token');

      if (!token) {
        throw new Error('Authentication required');
      }

      // Analyze form first
      const analyzeResponse = await fetch(`${apiUrl}/auto-apply/analyze-form`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_url: job.url,
          job_id: job.jobId
        })
      });

      if (!analyzeResponse.ok) {
        if (settings.skipOnError) {
          throw new Error('Form analysis failed - skipping');
        }
        throw new Error('Failed to analyze job form');
      }

      const analysisResult = await analyzeResponse.json();

      if (!analysisResult.auto_apply_supported) {
        updateJobStatus(job.id, 'skipped', 'Auto apply not supported');
        return;
      }

      // Perform auto apply
      const applyResponse = await fetch(`${apiUrl}/auto-apply/auto-apply`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({
          job_url: job.url,
          job_id: job.jobId
        })
      });

      if (!applyResponse.ok) {
        throw new Error('Auto apply failed');
      }

      const result = await applyResponse.json();
      
      if (result.success) {
        updateJobStatus(job.id, 'completed', undefined, result);
        onJobComplete(job.id, result);
      } else {
        throw new Error(result.message || 'Auto apply failed');
      }

    } catch (error: any) {
      console.error(`Job ${job.title} failed:`, error);
      
      if (job.retryCount < settings.maxRetries && settings.autoRetry) {
        // Retry the job
        const updatedJob = {
          ...job,
          retryCount: job.retryCount + 1,
          status: 'pending' as const
        };
        updateJobInQueue(updatedJob);
      } else {
        updateJobStatus(job.id, 'failed', error.message);
        onJobError(job.id, error.message);
      }
    }
  };

  // Update job status
  const updateJobStatus = (jobId: string, status: QueueJob['status'], error?: string, result?: any) => {
    setQueue(prev => prev.map(job => {
      if (job.id === jobId) {
        return {
          ...job,
          status,
          error,
          result,
          startedAt: status === 'processing' ? new Date() : job.startedAt,
          completedAt: ['completed', 'failed', 'skipped'].includes(status) ? new Date() : job.completedAt
        };
      }
      return job;
    }));
  };

  // Update job in queue
  const updateJobInQueue = (updatedJob: QueueJob) => {
    setQueue(prev => prev.map(job => job.id === updatedJob.id ? updatedJob : job));
  };

  // Process queue
  const processQueue = async () => {
    if (isPaused || !isRunning) return;

    const pendingJobs = queue.filter(job => job.status === 'pending');
    
    if (pendingJobs.length === 0) {
      // All jobs completed
      setIsRunning(false);
      onQueueComplete();
      return;
    }

    const jobsToProcess = pendingJobs.slice(0, settings.maxConcurrentJobs);
    
    // Process jobs concurrently
    const promises = jobsToProcess.map(job => processJob(job));
    
    try {
      await Promise.all(promises);
    } catch (error) {
      console.error('Error processing jobs:', error);
    }

    // Schedule next batch
    if (isRunning && !isPaused) {
      queueRef.current = setTimeout(() => {
        processQueue();
      }, settings.delayBetweenJobs);
    }
  };

  // Start queue
  const startQueue = () => {
    setIsRunning(true);
    setIsPaused(false);
    processQueue();
  };

  // Pause queue
  const pauseQueue = () => {
    setIsPaused(true);
    if (queueRef.current) {
      clearTimeout(queueRef.current);
    }
  };

  // Resume queue
  const resumeQueue = () => {
    setIsPaused(false);
    processQueue();
  };

  // Stop queue
  const stopQueue = () => {
    setIsRunning(false);
    setIsPaused(false);
    if (queueRef.current) {
      clearTimeout(queueRef.current);
    }
  };

  // Retry failed job
  const retryJob = (jobId: string) => {
    setQueue(prev => prev.map(job => {
      if (job.id === jobId && job.status === 'failed') {
        return {
          ...job,
          status: 'pending' as const,
          retryCount: 0,
          error: undefined,
          result: undefined
        };
      }
      return job;
    }));
  };

  // Clear completed jobs
  const clearCompleted = () => {
    setQueue(prev => prev.filter(job => 
      !['completed', 'failed', 'skipped'].includes(job.status)
    ));
  };

  // Get job status icon
  const getStatusIcon = (status: QueueJob['status']) => {
    switch (status) {
      case 'pending':
        return <Clock className="w-4 h-4 text-gray-400" />;
      case 'processing':
        return <Loader className="w-4 h-4 text-blue-600 animate-spin" />;
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-green-600" />;
      case 'failed':
        return <AlertCircle className="w-4 h-4 text-red-600" />;
      case 'skipped':
        return <AlertCircle className="w-4 h-4 text-yellow-600" />;
      default:
        return <Clock className="w-4 h-4 text-gray-400" />;
    }
  };

  // Get job status color
  const getStatusColor = (status: QueueJob['status']) => {
    switch (status) {
      case 'pending':
        return 'text-gray-600 bg-gray-100';
      case 'processing':
        return 'text-blue-600 bg-blue-100';
      case 'completed':
        return 'text-green-600 bg-green-100';
      case 'failed':
        return 'text-red-600 bg-red-100';
      case 'skipped':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  return (
    <div className={`space-y-4 ${className}`}>
      {/* Queue Header */}
      <div className="flex items-center justify-between bg-gray-50 p-4 rounded-lg">
        <div className="flex items-center gap-4">
          <h3 className="text-lg font-medium text-gray-900">Bulk Apply Queue</h3>
          <div className="flex items-center gap-2 text-sm text-gray-600">
            <BarChart3 className="w-4 h-4" />
            <span>{stats.completed}/{stats.total} completed</span>
          </div>
        </div>

        <div className="flex items-center gap-2">
          <button
            onClick={() => setShowSettings(!showSettings)}
            className="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
            title="Queue Settings"
          >
            <Settings className="w-4 h-4" />
          </button>

          {!isRunning && (
            <button
              onClick={startQueue}
              disabled={stats.pending === 0}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2 disabled:bg-green-400"
            >
              <Play className="w-4 h-4" />
              Start Queue
            </button>
          )}

          {isRunning && !isPaused && (
            <button
              onClick={pauseQueue}
              className="bg-yellow-600 hover:bg-yellow-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2"
            >
              <Pause className="w-4 h-4" />
              Pause
            </button>
          )}

          {isRunning && isPaused && (
            <button
              onClick={resumeQueue}
              className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2"
            >
              <Play className="w-4 h-4" />
              Resume
            </button>
          )}

          {isRunning && (
            <button
              onClick={stopQueue}
              className="bg-red-600 hover:bg-red-700 text-white px-4 py-2 rounded-lg font-medium flex items-center gap-2"
            >
              <Stop className="w-4 h-4" />
              Stop
            </button>
          )}
        </div>
      </div>

      {/* Settings Panel */}
      {showSettings && (
        <div className="bg-white border border-gray-200 rounded-lg p-4 space-y-4">
          <h4 className="font-medium text-gray-900">Queue Settings</h4>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max concurrent jobs
              </label>
              <input
                type="number"
                value={settings.maxConcurrentJobs}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  maxConcurrentJobs: parseInt(e.target.value) || 1
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="1"
                max="5"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Delay between jobs (ms)
              </label>
              <input
                type="number"
                value={settings.delayBetweenJobs}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  delayBetweenJobs: parseInt(e.target.value) || 3000
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="1000"
                max="10000"
                step="500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Max retries
              </label>
              <input
                type="number"
                value={settings.maxRetries}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  maxRetries: parseInt(e.target.value) || 3
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="0"
                max="10"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Rate limit (per minute)
              </label>
              <input
                type="number"
                value={settings.rateLimitPerMinute}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  rateLimitPerMinute: parseInt(e.target.value) || 20
                }))}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-purple-500"
                min="1"
                max="100"
              />
            </div>
          </div>

          <div className="space-y-2">
            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.autoRetry}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  autoRetry: e.target.checked
                }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Auto retry failed jobs</span>
            </label>

            <label className="flex items-center gap-2">
              <input
                type="checkbox"
                checked={settings.skipOnError}
                onChange={(e) => setSettings(prev => ({
                  ...prev,
                  skipOnError: e.target.checked
                }))}
                className="rounded border-gray-300 text-purple-600 focus:ring-purple-500"
              />
              <span className="text-sm text-gray-700">Skip jobs on error</span>
            </label>
          </div>
        </div>
      )}

      {/* Progress Bar */}
      {isRunning && (
        <div className="bg-white border border-gray-200 rounded-lg p-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Queue Progress
            </span>
            <span className="text-sm text-gray-600">
              {Math.round((stats.completed / stats.total) * 100)}%
            </span>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div
              className="bg-purple-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${(stats.completed / stats.total) * 100}%` }}
            />
          </div>

          <div className="flex items-center gap-4 mt-3 text-sm text-gray-600">
            <span>Completed: {stats.completed}</span>
            <span>Failed: {stats.failed}</span>
            <span>Skipped: {stats.skipped}</span>
            <span>Pending: {stats.pending}</span>
            <span>Processing: {stats.processing}</span>
          </div>
        </div>
      )}

      {/* Queue Actions */}
      <div className="flex items-center gap-2">
        <button
          onClick={clearCompleted}
          className="px-3 py-1 text-sm border border-gray-300 rounded text-gray-700 hover:bg-gray-50"
        >
          Clear Completed
        </button>
      </div>

      {/* Job List */}
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {queue.map((job) => (
          <div
            key={job.id}
            className="flex items-center gap-3 p-3 bg-white border border-gray-200 rounded-lg"
          >
            {getStatusIcon(job.status)}
            
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{job.title}</h4>
              <p className="text-sm text-gray-600">{job.company}</p>
              <div className="flex items-center gap-2 mt-1">
                <span className={`text-xs px-2 py-1 rounded ${getStatusColor(job.status)}`}>
                  {job.status}
                </span>
                {job.retryCount > 0 && (
                  <span className="text-xs text-gray-500">
                    Retries: {job.retryCount}/{settings.maxRetries}
                  </span>
                )}
              </div>
              {job.error && (
                <p className="text-xs text-red-600 mt-1">{job.error}</p>
              )}
            </div>

            <div className="flex items-center gap-2">
              {job.status === 'failed' && (
                <button
                  onClick={() => retryJob(job.id)}
                  className="px-2 py-1 text-xs bg-blue-600 text-white rounded hover:bg-blue-700"
                >
                  Retry
                </button>
              )}
              
              <button
                onClick={() => window.open(job.url, '_blank')}
                className="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded"
                title="Open job"
              >
                ↗
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default BulkApplyQueue; 