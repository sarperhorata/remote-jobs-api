import React, { useState, useEffect } from 'react';
import { Search, Filter, MapPin, Clock, DollarSign, Building2, ExternalLink, BookmarkPlus, Bookmark } from '../icons/EmojiIcons';
import { Job } from '../../types/job';
import { jobService } from '../../services/jobService';
import JobApplicationModal from './JobApplicationModal';

interface JobSearchFilters {
  location: string;
  jobType: string;
  experienceLevel: string;
  salaryRange: string;
  company: string;
  remote: boolean;
  datePosted: string;
}

interface JobSearchProps {
  onJobSelect?: (job: Job) => void;
}

const JobSearch: React.FC<JobSearchProps> = ({ onJobSelect }) => {
  const [searchQuery, setSearchQuery] = useState('');
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [showFilters, setShowFilters] = useState(false);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());

  const [filters, setFilters] = useState<JobSearchFilters>({
    location: '',
    jobType: '',
    experienceLevel: '',
    salaryRange: '',
    company: '',
    remote: false,
    datePosted: ''
  });

  const jobTypes = ['Full-time', 'Part-time', 'Contract', 'Freelance', 'Internship'];
  const experienceLevels = ['Entry Level', 'Mid Level', 'Senior Level', 'Lead', 'Executive'];
  const salaryRanges = ['0-50k', '50k-100k', '100k-150k', '150k-200k', '200k+'];
  const datePostedOptions = ['Last 24 hours', 'Last 3 days', 'Last week', 'Last month'];

  useEffect(() => {
    searchJobs();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [jobs, filters, searchQuery]);

  const searchJobs = async () => {
    setLoading(true);
    try {
      const response = await jobService.searchJobs({
        q: searchQuery,
        location: filters.location,
        limit: 50
      });
      setJobs(response.jobs || []);
    } catch (error) {
      console.error('Error searching jobs:', error);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const applyFilters = () => {
    let filtered = jobs.filter(job => {
      // Search query filter
      if (searchQuery && !job.title.toLowerCase().includes(searchQuery.toLowerCase()) &&
          !((typeof job.company === 'string' ? job.company : job.company?.name) || 'Unknown').toLowerCase().includes(searchQuery.toLowerCase()) &&
          !job.description.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }

      // Location filter
      if (filters.location && !job.location.toLowerCase().includes(filters.location.toLowerCase())) {
        return false;
      }

      // Job type filter
      if (filters.jobType && job.jobType !== filters.jobType) {
        return false;
      }

      // Experience level filter
      if (filters.experienceLevel && job.experienceLevel !== filters.experienceLevel) {
        return false;
      }

      // Company filter
      if (filters.company && !((typeof job.company === 'string' ? job.company : job.company?.name) || 'Unknown').toLowerCase().includes(filters.company.toLowerCase())) {
        return false;
      }

      // Remote filter
      if (filters.remote && !job.isRemote) {
        return false;
      }

      // Date posted filter
      if (filters.datePosted) {
        const jobDate = new Date(job.createdAt);
        const now = new Date();
        const daysDiff = Math.floor((now.getTime() - jobDate.getTime()) / (1000 * 60 * 60 * 24));

        switch (filters.datePosted) {
          case 'Last 24 hours':
            if (daysDiff > 1) return false;
            break;
          case 'Last 3 days':
            if (daysDiff > 3) return false;
            break;
          case 'Last week':
            if (daysDiff > 7) return false;
            break;
          case 'Last month':
            if (daysDiff > 30) return false;
            break;
        }
      }

      return true;
    });

    setFilteredJobs(filtered);
  };

  const handleApply = (job: Job) => {
    setSelectedJob(job);
    setShowApplicationModal(true);
  };

  const handleExternalApply = (job: Job) => {
    // v1: Redirect to external job site
    if (job.applyUrl) {
      window.open(job.applyUrl, '_blank');
    } else if (job.sourceUrl) {
      window.open(job.sourceUrl, '_blank');
    } else {
      // Fallback to company website or job board
      const searchUrl = `https://www.google.com/search?q=${encodeURIComponent(job.title + ' ' + job.company + ' job application')}`;
      window.open(searchUrl, '_blank');
    }

    // Track application attempt
    trackJobApplication(job, 'external_redirect');
  };

  const toggleSaveJob = (jobId: string) => {
    const newSavedJobs = new Set(savedJobs);
    if (newSavedJobs.has(jobId)) {
      newSavedJobs.delete(jobId);
    } else {
      newSavedJobs.add(jobId);
    }
    setSavedJobs(newSavedJobs);
    
    // TODO: Persist to backend
    localStorage.setItem('savedJobs', JSON.stringify([...newSavedJobs]));
  };

  const trackJobApplication = (job: Job, type: 'external_redirect' | 'direct_apply') => {
    // Analytics tracking
    console.log('Job application tracked:', { job: job.id, type });
    
    // TODO: Send to analytics service
    jobService.trackJobInteraction(job.id, type);
  };

  const resetFilters = () => {
    setFilters({
      location: '',
      jobType: '',
      experienceLevel: '',
      salaryRange: '',
      company: '',
      remote: false,
      datePosted: ''
    });
  };

  const formatSalary = (salary: any) => {
    if (!salary) return null;
    if (typeof salary === 'string') return salary;
    if (salary.min && salary.max) {
      return `$${salary.min.toLocaleString()} - $${salary.max.toLocaleString()}`;
    }
    if (salary.min) return `$${salary.min.toLocaleString()}+`;
    return null;
  };

  return (
    <div className="job-search-container">
      {/* Search Header */}
      <div className="search-header bg-white rounded-lg shadow-sm p-6 mb-6">
        <div className="flex flex-col lg:flex-row gap-4">
          {/* Search Input */}
          <div className="flex-1 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Job title, company, or keywords..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && searchJobs()}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Location Filter */}
          <div className="relative lg:w-64">
            <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
            <input
              type="text"
              placeholder="Location"
              value={filters.location}
              onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Search & Filter Buttons */}
          <div className="flex gap-2">
            <button
              onClick={searchJobs}
              disabled={loading}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
            >
              {loading ? (
                <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
              ) : (
                <Search className="h-5 w-5" />
              )}
              Search
            </button>
            
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="px-4 py-3 border border-gray-300 rounded-lg hover:bg-gray-50 flex items-center gap-2"
            >
              <Filter className="h-5 w-5" />
              Filters
            </button>
          </div>
        </div>

        {/* Advanced Filters */}
        {showFilters && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              {/* Job Type */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Job Type</label>
                <select
                  value={filters.jobType}
                  onChange={(e) => setFilters(prev => ({ ...prev, jobType: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Types</option>
                  {jobTypes.map(type => (
                    <option key={type} value={type}>{type}</option>
                  ))}
                </select>
              </div>

              {/* Experience Level */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Experience</label>
                <select
                  value={filters.experienceLevel}
                  onChange={(e) => setFilters(prev => ({ ...prev, experienceLevel: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">All Levels</option>
                  {experienceLevels.map(level => (
                    <option key={level} value={level}>{level}</option>
                  ))}
                </select>
              </div>

              {/* Date Posted */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">Date Posted</label>
                <select
                  value={filters.datePosted}
                  onChange={(e) => setFilters(prev => ({ ...prev, datePosted: e.target.value }))}
                  className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                >
                  <option value="">Any Time</option>
                  {datePostedOptions.map(option => (
                    <option key={option} value={option}>{option}</option>
                  ))}
                </select>
              </div>

              {/* Remote Work */}
              <div>
                <label className="flex items-center pt-6">
                  <input
                    type="checkbox"
                    checked={filters.remote}
                    onChange={(e) => setFilters(prev => ({ ...prev, remote: e.target.checked }))}
                    className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  <span className="ml-2 text-sm text-gray-700">Remote Only</span>
                </label>
              </div>
            </div>

            <div className="mt-4 flex gap-2">
              <button
                onClick={resetFilters}
                className="px-4 py-2 text-gray-600 border border-gray-300 rounded-lg hover:bg-gray-50"
              >
                Clear Filters
              </button>
              <span className="text-sm text-gray-500 py-2">
                {filteredJobs.length} jobs found
              </span>
            </div>
          </div>
        )}
      </div>

      {/* Job Results */}
      <div className="job-results">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-600">Searching jobs...</p>
          </div>
        ) : filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <Search className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">Try adjusting your search terms or filters</p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredJobs.map((job) => (
              <div key={job.id} className="job-card bg-white rounded-lg shadow-sm p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    {/* Job Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {job.title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600">
                          <div className="flex items-center gap-1">
                            <Building2 className="h-4 w-4" />
                            {typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}
                          </div>
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            {job.location}
                            {job.isRemote && <span className="text-green-600 font-medium">• Remote</span>}
                          </div>
                          {formatSalary(job.salary) && (
                            <div className="flex items-center gap-1">
                              <DollarSign className="h-4 w-4" />
                              {formatSalary(job.salary)}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Save Job Button */}
                      <button
                        onClick={() => toggleSaveJob(job.id)}
                        className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                        title={savedJobs.has(job.id) ? 'Remove from saved' : 'Save job'}
                      >
                        {savedJobs.has(job.id) ? (
                          <Bookmark className="h-5 w-5 text-blue-600 fill-current" />
                        ) : (
                          <BookmarkPlus className="h-5 w-5 text-gray-400" />
                        )}
                      </button>
                    </div>

                    {/* Job Details */}
                    <div className="mb-4">
                      <p className="text-gray-700 line-clamp-3">
                        {job.description.length > 200 
                          ? job.description.substring(0, 200) + '...'
                          : job.description
                        }
                      </p>
                    </div>

                    {/* Job Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.jobType && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                          {job.jobType}
                        </span>
                      )}
                      {job.experienceLevel && (
                        <span className="px-2 py-1 bg-green-100 text-green-800 text-xs rounded-full">
                          {job.experienceLevel}
                        </span>
                      )}
                      {job.skills?.slice(0, 3).map((skill, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                          {skill}
                        </span>
                      ))}
                      {job.skills && job.skills.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{job.skills.length - 3} more
                        </span>
                      )}
                    </div>

                    {/* Job Footer */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        <div className="flex items-center gap-1">
                          <Clock className="h-4 w-4" />
                          {new Date(job.createdAt).toLocaleDateString()}
                        </div>
                        {job.applicantCount && (
                          <span>{job.applicantCount} applicants</span>
                        )}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-2">
                        <button
                          onClick={() => {
                            setSelectedJob(job);
                            onJobSelect?.(job);
                          }}
                          className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors"
                        >
                          View Details
                        </button>
                        
                        <button
                          onClick={() => handleExternalApply(job)}
                          className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
                        >
                          <ExternalLink className="h-4 w-4" />
                          Apply Now
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Application Modal */}
      {showApplicationModal && selectedJob && (
        <JobApplicationModal
          job={selectedJob}
          onClose={() => {
            setShowApplicationModal(false);
            setSelectedJob(null);
          }}
          onSubmit={(applicationData) => {
            console.log('Application submitted:', applicationData);
            setShowApplicationModal(false);
            setSelectedJob(null);
          }}
        />
      )}
    </div>
  );
};

export default JobSearch; 