import React, { useState, useEffect } from 'react';
import { FileText, ExternalLink, MapPin, DollarSign, Calendar, Briefcase, Clock, CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import Header from '../components/Header';
import { useAuth } from '../contexts/AuthContext';

interface Application {
  id: string;
  job_id: string;
  job_title: string;
  company: string;
  company_logo?: string;
  location?: string;
  salary?: string;
  job_type?: string;
  work_type?: string;
  applied_at: string;
  status: 'pending' | 'reviewing' | 'interview' | 'rejected' | 'accepted';
  application_url?: string;
  notes?: string;
  next_step?: string;
  interview_date?: string;
}

const statusConfig = {
  pending: {
    icon: Clock,
    color: 'text-yellow-600 dark:text-yellow-400',
    bg: 'bg-yellow-50 dark:bg-yellow-900/30',
    label: 'Pending'
  },
  reviewing: {
    icon: AlertCircle,
    color: 'text-blue-600 dark:text-blue-400',
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    label: 'Under Review'
  },
  interview: {
    icon: Calendar,
    color: 'text-purple-600 dark:text-purple-400',
    bg: 'bg-purple-50 dark:bg-purple-900/30',
    label: 'Interview Scheduled'
  },
  rejected: {
    icon: XCircle,
    color: 'text-red-600 dark:text-red-400',
    bg: 'bg-red-50 dark:bg-red-900/30',
    label: 'Rejected'
  },
  accepted: {
    icon: CheckCircle,
    color: 'text-green-600 dark:text-green-400',
    bg: 'bg-green-50 dark:bg-green-900/30',
    label: 'Accepted'
  }
};

const MyApplications: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const [applications, setApplications] = useState<Application[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'date' | 'status' | 'company'>('date');

  useEffect(() => {
    if (isAuthenticated && user) {
      loadApplications();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  const loadApplications = async () => {
    try {
      setLoading(true);
      
      // Get applications from localStorage (in production, this would come from API)
      const savedApplications = JSON.parse(localStorage.getItem('myApplications') || '[]');
      
      // If no saved applications, create some mock data for demo
      if (savedApplications.length === 0) {
        const mockApplications: Application[] = [
          {
            id: '1',
            job_id: 'job-1',
            job_title: 'Senior React Developer',
            company: 'TechCorp Inc.',
            location: 'Remote',
            salary: '$80,000 - $120,000',
            job_type: 'Full-time',
            work_type: 'Remote',
            applied_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
            status: 'reviewing',
            application_url: 'https://example.com/application/1',
            notes: 'Applied through company website. Submitted custom cover letter.',
            next_step: 'Waiting for initial screening call'
          },
          {
            id: '2',
            job_id: 'job-2',
            job_title: 'Frontend Engineer',
            company: 'StartupXYZ',
            location: 'San Francisco, CA',
            salary: '$90,000 - $130,000',
            job_type: 'Full-time',
            work_type: 'Hybrid',
            applied_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(), // 5 days ago
            status: 'interview',
            interview_date: new Date(Date.now() + 3 * 24 * 60 * 60 * 1000).toISOString(), // 3 days from now
            application_url: 'https://example.com/application/2',
            notes: 'Recruiter reached out on LinkedIn. Technical interview scheduled.',
            next_step: 'Technical interview with engineering team'
          },
          {
            id: '3',
            job_id: 'job-3',
            job_title: 'Full Stack Developer',
            company: 'RemoteFirst Ltd.',
            location: 'Remote',
            salary: '$70,000 - $100,000',
            job_type: 'Full-time',
            work_type: 'Remote',
            applied_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(), // 10 days ago
            status: 'rejected',
            application_url: 'https://example.com/application/3',
            notes: 'Applied via job board. Received automated rejection email.',
            next_step: 'Look for similar positions'
          }
        ];
        
        setApplications(mockApplications);
        localStorage.setItem('myApplications', JSON.stringify(mockApplications));
      } else {
        setApplications(savedApplications);
      }
    } catch (error) {
      console.error('Error loading applications:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredApplications = applications.filter(app => {
    if (filter === 'all') return true;
    return app.status === filter;
  });

  const sortedApplications = [...filteredApplications].sort((a, b) => {
    switch (sortBy) {
      case 'date':
        return new Date(b.applied_at).getTime() - new Date(a.applied_at).getTime();
      case 'status':
        return a.status.localeCompare(b.status);
      case 'company':
        return a.company.localeCompare(b.company);
      default:
        return 0;
    }
  });

  const getStatusIcon = (status: Application['status']) => {
    const config = statusConfig[status];
    const Icon = config.icon;
    return <Icon className={`w-4 h-4 ${config.color}`} />;
  };

  const getStatusBadge = (status: Application['status']) => {
    const config = statusConfig[status];
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 rounded-full text-xs font-medium ${config.bg} ${config.color}`}>
        {getStatusIcon(status)}
        {config.label}
      </span>
    );
  };

  const getApplicationStats = () => {
    const stats = {
      total: applications.length,
      pending: applications.filter(app => app.status === 'pending').length,
      reviewing: applications.filter(app => app.status === 'reviewing').length,
      interview: applications.filter(app => app.status === 'interview').length,
      accepted: applications.filter(app => app.status === 'accepted').length,
      rejected: applications.filter(app => app.status === 'rejected').length,
    };
    return stats;
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="max-w-md mx-auto">
            <FileText className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Please Login</h1>
            <p className="text-gray-600 dark:text-gray-300">You need to be logged in to view your applications.</p>
          </div>
        </div>
      </div>
    );
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Loading your applications...</p>
        </div>
      </div>
    );
  }

  const stats = getApplicationStats();

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-slate-900">
      <Header />
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <FileText className="w-8 h-8 text-blue-500" />
            My Applications
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            Track your job applications and their status
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-6 gap-4 mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Total</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.pending}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Pending</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.reviewing}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Review</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">{stats.interview}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Interview</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.accepted}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Accepted</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.rejected}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Rejected</div>
          </div>
        </div>

        {/* Filters and Sort */}
        <div className="bg-white dark:bg-slate-800 rounded-lg border border-gray-200 dark:border-slate-600 p-4 mb-6">
          <div className="flex flex-col sm:flex-row gap-4 justify-between items-start sm:items-center">
            <div className="flex flex-wrap gap-2">
              <button
                onClick={() => setFilter('all')}
                className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                  filter === 'all' 
                    ? 'bg-blue-600 text-white' 
                    : 'bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-slate-600'
                }`}
              >
                All ({stats.total})
              </button>
              {Object.entries(statusConfig).map(([status, config]) => (
                <button
                  key={status}
                  onClick={() => setFilter(status)}
                  className={`px-3 py-1 rounded-full text-sm font-medium transition-colors ${
                    filter === status 
                      ? 'bg-blue-600 text-white' 
                      : `${config.bg} ${config.color} hover:opacity-80`
                  }`}
                >
                  {config.label} ({stats[status as keyof typeof stats]})
                </button>
              ))}
            </div>
            
            <div className="flex items-center gap-2">
              <label className="text-sm text-gray-600 dark:text-gray-300">Sort by:</label>
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'date' | 'status' | 'company')}
                className="px-3 py-1 bg-gray-100 dark:bg-slate-700 border border-gray-300 dark:border-slate-600 rounded text-sm text-gray-700 dark:text-gray-300 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="date">Date Applied</option>
                <option value="status">Status</option>
                <option value="company">Company</option>
              </select>
            </div>
          </div>
        </div>

        {/* Applications List */}
        {sortedApplications.length > 0 ? (
          <div className="space-y-4">
            {sortedApplications.map((application) => (
              <div key={application.id} className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between mb-4">
                  <div className="flex-1">
                    <div className="flex items-start gap-4">
                      {/* Company Logo Placeholder */}
                      <div className="w-12 h-12 rounded-lg bg-gray-100 dark:bg-slate-700 flex items-center justify-center flex-shrink-0">
                        <div className="w-12 h-12 rounded-lg bg-gray-200 dark:bg-slate-600 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm font-semibold">
                          {application.company.charAt(0)}
                        </div>
                      </div>
                      
                      <div className="flex-1">
                        <div className="flex items-start justify-between gap-4">
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                              {application.job_title}
                            </h3>
                            <p className="text-gray-600 dark:text-gray-300 mb-2">{application.company}</p>
                            
                            {/* Job Details */}
                            <div className="flex flex-wrap gap-2 mb-3">
                              {application.location && (
                                <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                                  <MapPin className="w-3 h-3" />
                                  {application.location}
                                </span>
                              )}
                              {application.job_type && (
                                <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                                  <Briefcase className="w-3 h-3" />
                                  {application.job_type}
                                </span>
                              )}
                              {application.work_type && (
                                <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full">
                                  🏠 {application.work_type}
                                </span>
                              )}
                              {application.salary && (
                                <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs rounded-full">
                                  <DollarSign className="w-3 h-3" />
                                  {application.salary}
                                </span>
                              )}
                            </div>
                          </div>
                          
                          <div className="flex flex-col items-end gap-2">
                            {getStatusBadge(application.status)}
                            <span className="text-xs text-gray-500 dark:text-gray-400">
                              Applied {new Date(application.applied_at).toLocaleDateString()}
                            </span>
                          </div>
                        </div>
                        
                        {/* Additional Info */}
                        {application.interview_date && (
                          <div className="mt-3 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg">
                            <div className="flex items-center gap-2 text-purple-700 dark:text-purple-300">
                              <Calendar className="w-4 h-4" />
                              <span className="text-sm font-medium">
                                Interview: {new Date(application.interview_date).toLocaleDateString()} at{' '}
                                {new Date(application.interview_date).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                              </span>
                            </div>
                          </div>
                        )}
                        
                        {application.notes && (
                          <div className="mt-3">
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                              <strong>Notes:</strong> {application.notes}
                            </p>
                          </div>
                        )}
                        
                        {application.next_step && (
                          <div className="mt-2">
                            <p className="text-sm text-gray-600 dark:text-gray-300">
                              <strong>Next Step:</strong> {application.next_step}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Action Button */}
                  <div className="ml-4">
                    {application.application_url && (
                      <a
                        href={application.application_url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="p-2 text-gray-400 dark:text-gray-500 hover:text-blue-500 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-full transition-colors"
                        title="View Application"
                      >
                        <ExternalLink className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <FileText className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              {filter === 'all' ? 'No Applications Yet' : `No ${statusConfig[filter as keyof typeof statusConfig]?.label} Applications`}
            </h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">
              {filter === 'all' 
                ? 'Start applying to jobs to see them here.' 
                : `You don't have any applications with ${statusConfig[filter as keyof typeof statusConfig]?.label.toLowerCase()} status.`
              }
            </p>
            <a 
              href="/jobs/search" 
              className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Browse Jobs
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default MyApplications; 