import React, { useState, useEffect, useRef } from 'react';
import { useLocation, useNavigate, useSearchParams, Link } from 'react-router-dom';
import {
  MapPin,
  DollarSign,
  Briefcase,
  Filter,
  Search,
  Bookmark,
  BookmarkPlus,
  ExternalLink,
  ChevronDown,
  Calendar,
  Building,
  Globe
} from 'lucide-react';
import Header from '../components/Header';

// Interface definitions
interface JobTitle {
  title: string;
  count: number;
}

interface Job {
  id?: string;
  _id?: string;
  title: string;
  company: string | { name: string; logo?: string };
  company_logo?: string;
  location?: string;
  salary?: string;
  description?: string;
  job_type?: string;
  work_type?: string;
  posted_date?: string;
  isRemote?: boolean;
  required_skills?: string[];
  url?: string;
  category?: string;
  seniority_level?: string;
}

interface Filters {
  workType: string;
  jobType: string;
  salaryRange: string;
  location: string;
  experience: string;
  postedAge: string;
  sortBy: string;
  jobTitles: string;
}

const JobSearchResults: React.FC = () => {
  const [searchParams] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const hasFetched = useRef(false);

  // State management
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);

  // Saved and applied jobs state
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  const [appliedJobs, setAppliedJobs] = useState<Set<string>>(new Set());

  // Filter state
  const [filters, setFilters] = useState<Filters>({
    workType: searchParams.get('work_type') || '',
    jobType: searchParams.get('job_type') || '',
    salaryRange: searchParams.get('salary_range') || '',
    location: searchParams.get('location') || '',
    experience: searchParams.get('experience') || '',
    postedAge: searchParams.get('posted_age') || '30DAYS',
    sortBy: searchParams.get('sort_by') || 'newest',
    jobTitles: searchParams.get('job_titles') || ''
  });

  const [searchQuery, setSearchQuery] = useState(searchParams.get('q') || '');

  // Fetch jobs function
  const fetchJobs = async (page = 1) => {
    if (hasFetched.current && page === 1) return;
    
    setLoading(true);
    setError(null);

    try {
      const queryParams = new URLSearchParams({
        q: searchQuery,
        page: page.toString(),
        limit: '20',
        sort_by: filters.sortBy,
        ...(filters.workType && { work_type: filters.workType }),
        ...(filters.jobType && { job_type: filters.jobType }),
        ...(filters.location && { location: filters.location }),
        ...(filters.experience && { experience: filters.experience }),
        ...(filters.postedAge && { posted_age: filters.postedAge }),
        ...(filters.jobTitles && { job_titles: filters.jobTitles }),
        ...(filters.salaryRange && { salary_range: filters.salaryRange })
      });

      console.log('🔍 Fetching jobs with params:', queryParams.toString());
      
      const response = await fetch(`http://localhost:8001/api/v1/jobs/search?${queryParams}`);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch jobs: ${response.status} ${response.statusText}`);
      }

      const data = await response.json();
      console.log('✅ Jobs fetched successfully:', data);

      setJobs(data.jobs || []);
      setTotalJobs(data.total || 0);
      setCurrentPage(page);
      hasFetched.current = true;
    } catch (error: any) {
      console.error('❌ Error fetching jobs:', error);
      setError(error.message || 'Failed to load jobs');
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  // Filter change handler
  const handleFilterChange = (newFilters: Partial<Filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
    hasFetched.current = false;
  };

  // Apply filters (re-fetch jobs)
  useEffect(() => {
    fetchJobs(1);
  }, [filters, searchQuery]);

  // Job interaction handlers
  const handleSaveJob = (jobId: string) => {
    setSavedJobs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
      } else {
        newSet.add(jobId);
      }
      return newSet;
    });
  };

  const handleApplyJob = (jobId: string) => {
    setAppliedJobs(prev => {
      const newSet = new Set(prev);
      newSet.add(jobId);
      return newSet;
    });
  };

  const clearAllFilters = () => {
    setFilters({
      workType: '',
      jobType: '',
      salaryRange: '',
      location: '',
      experience: '',
      postedAge: '30DAYS',
      sortBy: 'newest',
      jobTitles: ''
    });
    setSearchQuery('');
    hasFetched.current = false;
  };

  const formatSalary = (salary: string | undefined): string => {
    if (!salary) return '';
    return salary.includes('$') ? salary : `$${salary}`;
  };

  const formatDate = (dateString: string | undefined): string => {
    if (!dateString) return 'Recently posted';
    
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffTime = Math.abs(now.getTime() - date.getTime());
      const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
      
      if (diffDays === 1) return '1 day ago';
      if (diffDays < 30) return `${diffDays} days ago`;
      if (diffDays < 365) return `${Math.floor(diffDays / 30)} months ago`;
      return `${Math.floor(diffDays / 365)} years ago`;
    } catch {
      return 'Recently posted';
    }
  };

  const getJobTypeColor = (type: string | undefined): string => {
    switch (type?.toLowerCase()) {
      case 'full-time': case 'full time': return 'bg-green-100 text-green-700 border-green-200';
      case 'part-time': case 'part time': return 'bg-blue-100 text-blue-700 border-blue-200';
      case 'contract': return 'bg-orange-100 text-orange-700 border-orange-200';
      case 'freelance': return 'bg-purple-100 text-purple-700 border-purple-200';
      case 'internship': return 'bg-pink-100 text-pink-700 border-pink-200';
      default: return 'bg-gray-100 text-gray-700 border-gray-200';
    }
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Add Homepage Header */}
      <Header />

      {/* Page Header */}
      <div className="bg-white border-b border-gray-200 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
                🐝 <span className="bg-gradient-to-r from-yellow-500 to-orange-500 bg-clip-text text-transparent">
                  Buzz2Remote
                </span>
              </h1>
              <div className="flex items-center gap-6 mt-2 text-gray-600">
                <span className="flex items-center gap-2">
                  <Briefcase className="w-4 h-4" />
                  {loading ? 'Searching...' : `${totalJobs.toLocaleString()} jobs found`}
                </span>
                {searchQuery && (
                  <span className="flex items-center gap-2">
                    <Search className="w-4 h-4" />
                    Results for "{searchQuery}"
                  </span>
                )}
              </div>
            </div>

            {/* Action Controls */}
            <div className="flex items-center gap-4">
              <button
                onClick={clearAllFilters}
                className="text-sm text-yellow-600 hover:text-yellow-700 font-medium"
              >
                Clear All
              </button>
              
              {/* Sort Dropdown */}
              <div className="relative">
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange({ sortBy: e.target.value })}
                  className="appearance-none bg-white border border-gray-300 rounded-lg px-4 py-2 pr-10 text-sm font-medium text-gray-700 hover:border-gray-400 focus:ring-2 focus:ring-yellow-500 focus:border-yellow-500"
                >
                  <option value="newest">Most Recent</option>
                  <option value="relevance">Most Relevant</option>
                  <option value="salary">Highest Salary</option>
                </select>
                <ChevronDown className="absolute right-3 top-2.5 w-4 h-4 text-gray-400 pointer-events-none" />
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="flex gap-8">
          {/* Left Sidebar Filters */}
          <div className="w-80 flex-shrink-0">
            <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 sticky top-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 flex items-center gap-2">
                  <Filter className="w-5 h-5 text-yellow-500" />
                  Filters
                </h3>
              </div>

              <div className="space-y-6">
                {/* Work Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-3">Work Type</label>
                  <div className="space-y-2">
                    {['Remote', 'Hybrid', 'On-site'].map((type) => (
                      <label key={type} className="flex items-center">
                        <input
                          type="radio"
                          name="workType"
                          value={type}
                          checked={filters.workType === type}
                          onChange={(e) => handleFilterChange({ workType: e.target.value })}
                          className="w-4 h-4 text-yellow-600 border-gray-300 focus:ring-yellow-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Job Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-3">Job Type</label>
                  <div className="space-y-2">
                    {['Full-time', 'Part-time', 'Contract', 'Freelance', 'Internship'].map((type) => (
                      <label key={type} className="flex items-center">
                        <input
                          type="radio"
                          name="jobType"
                          value={type}
                          checked={filters.jobType === type}
                          onChange={(e) => handleFilterChange({ jobType: e.target.value })}
                          className="w-4 h-4 text-yellow-600 border-gray-300 focus:ring-yellow-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Posted Date */}
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-3">Posted Date</label>
                  <select
                    value={filters.postedAge}
                    onChange={(e) => handleFilterChange({ postedAge: e.target.value })}
                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-yellow-500 focus:border-yellow-500"
                  >
                    <option value="1DAY">Last 24 hours</option>
                    <option value="3DAYS">Last 3 days</option>
                    <option value="7DAYS">Last week</option>
                    <option value="30DAYS">Last month</option>
                    <option value="90DAYS">Last 3 months</option>
                  </select>
                </div>

                {/* Experience Level */}
                <div>
                  <label className="block text-sm font-medium text-gray-900 mb-3">Experience Level</label>
                  <div className="space-y-2">
                    {['Entry level', 'Mid level', 'Senior level', 'Lead', 'Manager'].map((level) => (
                      <label key={level} className="flex items-center">
                        <input
                          type="radio"
                          name="experience"
                          value={level}
                          checked={filters.experience === level}
                          onChange={(e) => handleFilterChange({ experience: e.target.value })}
                          className="w-4 h-4 text-yellow-600 border-gray-300 focus:ring-yellow-500"
                        />
                        <span className="ml-2 text-sm text-gray-700">{level}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Side Job Results */}
          <div className="flex-1">
            {loading ? (
              <div className="flex items-center justify-center py-12">
                <div className="text-center">
                  <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-yellow-600 mx-auto mb-4"></div>
                  <p className="text-gray-600">Finding the perfect jobs for you...</p>
                </div>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-red-500 mb-4">
                  <ExternalLink className="w-12 h-12 mx-auto mb-2" />
                  <p className="text-lg font-medium">Oops! Something went wrong</p>
                  <p className="text-sm text-gray-600 mt-1">{error}</p>
                </div>
                <button
                  onClick={() => fetchJobs(1)}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Search className="w-12 h-12 mx-auto mb-2" />
                  <p className="text-lg font-medium text-gray-900">No jobs found</p>
                  <p className="text-sm text-gray-600 mt-1">Try adjusting your filters or search terms</p>
                </div>
                <button
                  onClick={clearAllFilters}
                  className="px-4 py-2 bg-yellow-600 text-white rounded-lg hover:bg-yellow-700 transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              <div className="grid gap-6 grid-cols-1">
                {jobs.map((job) => (
                  <div 
                    key={job.id || job._id} 
                    className="bg-white rounded-xl shadow-sm border border-gray-200 hover:shadow-md transition-all duration-200 p-6 group"
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        {/* Company Logo & Info */}
                        <div className="flex items-center gap-4 mb-4">
                          <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center text-lg font-bold text-yellow-600 flex-shrink-0">
                            {job.company_logo || (typeof job.company === 'string' ? job.company[0]?.toUpperCase() : '🏢')}
                          </div>
                          <div>
                            <h3 className="text-lg font-semibold text-gray-900 group-hover:text-yellow-600 transition-colors cursor-pointer">
                              {job.title}
                            </h3>
                            <p className="text-gray-600 flex items-center gap-1">
                              <Building className="w-4 h-4" />
                              {typeof job.company === 'string' ? job.company : job.company?.name}
                            </p>
                          </div>
                        </div>

                        {/* Job Details */}
                        <div className="flex flex-wrap items-center gap-4 mb-4 text-sm text-gray-600">
                          {job.location && (
                            <span className="flex items-center gap-1">
                              <MapPin className="w-4 h-4" />
                              {job.location}
                            </span>
                          )}
                          {job.isRemote && (
                            <span className="flex items-center gap-1 text-green-600">
                              <Globe className="w-4 h-4" />
                              Remote
                            </span>
                          )}
                          {job.salary && (
                            <span className="flex items-center gap-1">
                              <DollarSign className="w-4 h-4" />
                              {formatSalary(job.salary)}
                            </span>
                          )}
                          <span className="flex items-center gap-1">
                            <Calendar className="w-4 h-4" />
                            {formatDate(job.posted_date)}
                          </span>
                        </div>

                        {/* Job Tags */}
                        <div className="flex flex-wrap gap-2 mb-4">
                          {job.job_type && (
                            <span className={`px-3 py-1 rounded-full text-xs font-medium border ${getJobTypeColor(job.job_type)}`}>
                              {job.job_type}
                            </span>
                          )}
                          {job.work_type && (
                            <span className="px-3 py-1 bg-blue-50 text-blue-700 rounded-full text-xs font-medium border border-blue-200">
                              {job.work_type}
                            </span>
                          )}
                          {job.required_skills?.slice(0, 3).map((skill, index) => (
                            <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 rounded text-xs">
                              {skill}
                            </span>
                          ))}
                        </div>

                        {/* Job Description Preview */}
                        {job.description && (
                          <p className="text-gray-600 text-sm line-clamp-2 mb-4">
                            {job.description.length > 150 
                              ? `${job.description.substring(0, 150)}...` 
                              : job.description
                            }
                          </p>
                        )}
                      </div>

                      {/* Actions */}
                      <div className="flex flex-col gap-2 ml-4">
                        <button
                          onClick={() => handleSaveJob(job.id || job._id || '')}
                          className={`p-2 rounded-lg border transition-colors ${
                            savedJobs.has(job.id || job._id || '')
                              ? 'bg-yellow-50 border-yellow-300 text-yellow-600'
                              : 'bg-white border-gray-300 text-gray-400 hover:text-yellow-600 hover:border-yellow-300'
                          }`}
                        >
                          {savedJobs.has(job.id || job._id || '') ? <Bookmark className="w-4 h-4" /> : <BookmarkPlus className="w-4 h-4" />}
                        </button>
                        
                        <button
                          onClick={() => handleApplyJob(job.id || job._id || '')}
                          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                            appliedJobs.has(job.id || job._id || '')
                              ? 'bg-green-100 text-green-700 border border-green-200'
                              : 'bg-yellow-600 text-white hover:bg-yellow-700'
                          }`}
                          disabled={appliedJobs.has(job.id || job._id || '')}
                        >
                          {appliedJobs.has(job.id || job._id || '') ? 'Applied' : 'Apply Now'}
                        </button>
                        
                        {job.url && (
                          <a
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="p-2 rounded-lg border border-gray-300 text-gray-400 hover:text-gray-600 transition-colors"
                          >
                            <ExternalLink className="w-4 h-4" />
                          </a>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {/* Pagination */}
            {jobs.length > 0 && totalJobs > 20 && (
              <div className="mt-8 flex items-center justify-center">
                <div className="flex items-center gap-2">
                  <button
                    onClick={() => fetchJobs(currentPage - 1)}
                    disabled={currentPage === 1}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Previous
                  </button>
                  
                  <span className="px-4 py-2 text-sm text-gray-700">
                    Page {currentPage} of {Math.ceil(totalJobs / 20)}
                  </span>
                  
                  <button
                    onClick={() => fetchJobs(currentPage + 1)}
                    disabled={currentPage >= Math.ceil(totalJobs / 20)}
                    className="px-4 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobSearchResults; 