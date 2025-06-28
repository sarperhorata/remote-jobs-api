import React, { useState, useEffect, useCallback } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import AutoApplyButton from '../components/AutoApplyButton';
import { Job } from '../types/job';
import { getApiUrl } from '../utils/apiConfig';
import { 
  MapPin, Filter, Grid3X3, List, Search, ExternalLink, Building2, 
  Clock, Bookmark, BookmarkPlus, CheckCircle2, Briefcase, Eye, 
  Users, TrendingUp, X 
} from '../components/icons/EmojiIcons';

interface SearchFilters {
  jobTitle: string;
  location: string;
  experienceLevel: string[];
  workType: string[];
  salaryRange: string[];
  skills: string[];
  sortBy: 'newest' | 'salary' | 'relevance';
  postedAge: string;
  companySize: string[];
  negativeKeywords: string;
}

const JobSearchResults: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('list');
  const [showFilters, setShowFilters] = useState(false);
  const [appliedJobs, setAppliedJobs] = useState<Set<string>>(new Set());
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  const [selectedJobTitles, setSelectedJobTitles] = useState<string[]>([]);
  
  const [filters, setFilters] = useState<SearchFilters>({
    jobTitle: '',
    location: '',
    experienceLevel: [],
    workType: ['Remote'],
    salaryRange: [],
    skills: [],
    sortBy: 'newest',
    postedAge: '30DAYS',
    companySize: [],
    negativeKeywords: ''
  });

  const experienceLevels = [
    'Entry Level (0-2 years)',
    'Mid Level (2-4 years)', 
    'Senior Level (4-6 years)',
    'Lead/Principal (6-10 years)',
    'Executive (10+ years)'
  ];

  const workTypeOptions = [
    { value: 'Remote', label: 'Remote', icon: '🌍', color: 'bg-green-100 text-green-800' },
    { value: 'Hybrid', label: 'Hybrid', icon: '🏢', color: 'bg-blue-100 text-blue-800' },
    { value: 'Onsite', label: 'On-site', icon: '🏙️', color: 'bg-gray-100 text-gray-800' }
  ];

  const salaryRanges = [
    '$0 - $30k',
    '$30k - $70k',
    '$70k - $120k', 
    '$120k - $180k',
    '$180k - $240k',
    '$240k+'
  ];

  const postedAgeOptions = [
    { value: '1DAY', label: 'Last 24 hours' },
    { value: '3DAYS', label: 'Last 3 days' },
    { value: '7DAYS', label: 'Last week' },
    { value: '30DAYS', label: 'Last month' },
    { value: 'ALL', label: 'Any time' }
  ];

  // Load user applied jobs from localStorage
  useEffect(() => {
    const applied = localStorage.getItem('appliedJobs');
    const saved = localStorage.getItem('savedJobs');
    if (applied) {
      setAppliedJobs(new Set(JSON.parse(applied)));
    }
    if (saved) {
      setSavedJobs(new Set(JSON.parse(saved)));
    }
  }, []);

  const performSearch = useCallback(async (searchFilters: SearchFilters, page: number = 1) => {
    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams();
      
      // Handle multi-search from URL or filters
      const urlParams = new URLSearchParams(location.search);
      const isMultiSearch = urlParams.get('multi_search') === 'true';
      const jobTitles = urlParams.get('job_titles');
      
      if (isMultiSearch && jobTitles) {
        // Multi-position search
        const titleArray = jobTitles.split(',');
        setSelectedJobTitles(titleArray);
        params.append('q', titleArray.join(' OR '));
        params.append('job_titles', jobTitles);
      } else if (searchFilters.jobTitle) {
        params.append('q', searchFilters.jobTitle);
      }
      
      if (searchFilters.location) params.append('location', searchFilters.location);
      if (searchFilters.experienceLevel.length > 0) {
        params.append('experience_level', searchFilters.experienceLevel.join(','));
      }
      if (searchFilters.workType.length > 0) {
        params.append('work_type', searchFilters.workType.join(','));
      }
      if (searchFilters.salaryRange.length > 0) {
        params.append('salary_range', searchFilters.salaryRange.join(','));
      }
      if (searchFilters.skills.length > 0) {
        params.append('skills', searchFilters.skills.join(','));
      }
      if (searchFilters.postedAge !== 'ALL') {
        params.append('posted_age', searchFilters.postedAge);
      }
      if (searchFilters.companySize.length > 0) {
        params.append('company_size', searchFilters.companySize.join(','));
      }
      if (searchFilters.negativeKeywords) {
        params.append('negative_keywords', searchFilters.negativeKeywords);
      }
      
      params.append('page', page.toString());
      params.append('limit', '20');
      params.append('sort_by', searchFilters.sortBy);

      const apiUrl = await getApiUrl();
      const response = await fetch(`${apiUrl}/jobs/search?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch jobs');
      }

      const data = await response.json();
      
      setJobs(data.jobs || []);
      setTotalJobs(data.total || 0);
      setCurrentPage(page);

      // Update URL without page reload
      const currentPath = location.pathname;
      const newUrl = `${currentPath}?${params}`;
      window.history.replaceState({}, '', newUrl);

    } catch (error: any) {
      setError(error.message || 'Failed to search jobs');
      setJobs([]);
      setTotalJobs(0);
    } finally {
      setLoading(false);
    }
  }, [location.pathname, location.search]);

  useEffect(() => {
    const searchParams = location.state?.searchParams || {};
    const urlParams = new URLSearchParams(location.search);
    
    const initialFilters: SearchFilters = {
      jobTitle: searchParams.job_title || urlParams.get('q') || urlParams.get('job_title') || urlParams.get('position') || '',
      location: searchParams.location || urlParams.get('location') || '',
      experienceLevel: searchParams.experience_level ? searchParams.experience_level.split(',') : [],
      workType: searchParams.work_type ? searchParams.work_type.split(',') : ['Remote'],
      salaryRange: searchParams.salary_range ? searchParams.salary_range.split(',') : [],
      skills: searchParams.skills ? searchParams.skills.split(',') : [],
      sortBy: 'newest',
      postedAge: urlParams.get('posted_age') || '30DAYS',
      companySize: searchParams.company_size ? searchParams.company_size.split(',') : [],
      negativeKeywords: urlParams.get('negative_keywords') || ''
    };

    setFilters(initialFilters);
    performSearch(initialFilters, 1);
  }, [location, performSearch]);

  const handleFilterChange = (newFilters: Partial<SearchFilters>) => {
    const updatedFilters = { ...filters, ...newFilters };
    setFilters(updatedFilters);
    performSearch(updatedFilters, 1);
  };

  const handlePageChange = (page: number) => {
    performSearch(filters, page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const toggleArrayFilter = (array: string[], value: string, setter: (newArray: string[]) => void) => {
    if (array.includes(value)) {
      setter(array.filter(item => item !== value));
    } else {
      setter([...array, value]);
    }
  };

  const clearAllFilters = () => {
    const clearedFilters: SearchFilters = {
      jobTitle: '',
      location: '',
      experienceLevel: [],
      workType: ['Remote'],
      salaryRange: [],
      skills: [],
      sortBy: 'newest',
      postedAge: '30DAYS',
      companySize: [],
      negativeKeywords: ''
    };
    setFilters(clearedFilters);
    setSelectedJobTitles([]);
    performSearch(clearedFilters, 1);
  };

  const handleApplyJob = (jobId: string) => {
    const newAppliedJobs = new Set([...appliedJobs, jobId]);
    setAppliedJobs(newAppliedJobs);
    localStorage.setItem('appliedJobs', JSON.stringify([...newAppliedJobs]));
  };

  const handleSaveJob = (jobId: string) => {
    const newSavedJobs = savedJobs.has(jobId) 
      ? new Set([...savedJobs].filter(id => id !== jobId))
      : new Set([...savedJobs, jobId]);
    
    setSavedJobs(newSavedJobs);
    localStorage.setItem('savedJobs', JSON.stringify([...newSavedJobs]));
  };

  const removeJobTitle = (titleToRemove: string) => {
    const updatedTitles = selectedJobTitles.filter(title => title !== titleToRemove);
    setSelectedJobTitles(updatedTitles);
    
    if (updatedTitles.length === 0) {
      // Clear search if no titles left
      clearAllFilters();
    } else {
      // Update search with remaining titles
      const updatedFilters = {
        ...filters,
        jobTitle: updatedTitles.join(' OR ')
      };
      setFilters(updatedFilters);
      performSearch(updatedFilters, 1);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) return 'Just posted';
    if (diffInHours < 24) return `${diffInHours}h ago`;
    const diffInDays = Math.floor(diffInHours / 24);
    if (diffInDays < 7) return `${diffInDays}d ago`;
    return `${Math.floor(diffInDays / 7)}w ago`;
  };

  const totalPages = Math.ceil(totalJobs / 20);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-50 via-blue-50/30 to-purple-50/20">
      {/* Header - Modern Enhanced Style */}
      <div className="bg-white/80 backdrop-blur-md border-b border-gray-200/50 shadow-lg">
        <div className="max-w-7xl mx-auto px-4 py-8">
          {/* Multi-search indicators */}
          {selectedJobTitles.length > 0 && (
            <div className="mb-4">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-sm font-medium text-gray-700">
                  Searching for {selectedJobTitles.length} job title{selectedJobTitles.length > 1 ? 's' : ''}:
                </h3>
                <button
                  onClick={clearAllFilters}
                  className="text-xs text-red-600 hover:text-red-700"
                >
                  Clear all
                </button>
              </div>
              <div className="flex flex-wrap gap-2">
                {selectedJobTitles.map((title, index) => (
                  <div
                    key={index}
                    className="flex items-center bg-blue-100 text-blue-800 text-sm px-3 py-1 rounded-full"
                  >
                    <span className="truncate max-w-40">{title}</span>
                    <button
                      onClick={() => removeJobTitle(title)}
                      className="ml-2 text-blue-600 hover:text-blue-800"
                    >
                      <X className="w-3 h-3" />
                    </button>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-4xl font-bold bg-gradient-to-r from-blue-600 via-purple-600 to-blue-800 bg-clip-text text-transparent">
                Remote Jobs
              </h1>
              <p className="text-lg text-gray-600 mt-2 mb-4">Discover your next remote opportunity from top companies worldwide</p>
              <div className="flex items-center gap-6 mt-4">
                <div className="flex items-center gap-2 bg-blue-50 px-4 py-2 rounded-full">
                  <Briefcase className="w-5 h-5 text-blue-600" />
                  <span className="text-blue-800 font-semibold">
                    {loading ? 'Searching...' : `${totalJobs.toLocaleString()} jobs`}
                  </span>
                </div>
                <div className="flex items-center gap-2 bg-green-50 px-4 py-2 rounded-full">
                  <CheckCircle2 className="w-5 h-5 text-green-600" />
                  <span className="text-green-800 font-semibold">{appliedJobs.size} applied</span>
                </div>
                <div className="flex items-center gap-2 bg-yellow-50 px-4 py-2 rounded-full">
                  <Bookmark className="w-5 h-5 text-yellow-600" />
                  <span className="text-yellow-800 font-semibold">{savedJobs.size} saved</span>
                </div>
              </div>
            </div>
            
            <div className="flex items-center gap-4">
              {/* Sort Options */}
              <div className="relative">
                <select
                  value={filters.sortBy}
                  onChange={(e) => handleFilterChange({ sortBy: e.target.value as any })}
                  className="px-4 py-3 bg-white border border-gray-200 rounded-xl text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:border-transparent shadow-sm hover:shadow-md transition-all appearance-none cursor-pointer min-w-[140px]"
                >
                  <option value="newest">🕒 Most Recent</option>
                  <option value="relevance">🎯 Most Relevant</option>
                  <option value="salary">💰 Highest Salary</option>
                </select>
                <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
                  <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
                  </svg>
                </div>
              </div>

              {/* View Mode Toggle */}
              <div className="flex bg-gray-100 rounded-xl p-1 shadow-sm">
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-3 rounded-lg transition-all duration-200 ${
                    viewMode === 'list'
                      ? 'bg-white text-blue-600 shadow-md scale-105'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                  title="List View"
                >
                  <List className="w-5 h-5" />
                </button>
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-3 rounded-lg transition-all duration-200 ${
                    viewMode === 'grid'
                      ? 'bg-white text-blue-600 shadow-md scale-105'
                      : 'text-gray-500 hover:text-gray-700 hover:bg-gray-50'
                  }`}
                  title="Grid View"
                >
                  <Grid3X3 className="w-5 h-5" />
                </button>
              </div>

              {/* Filters Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-700 hover:to-purple-700 text-white rounded-xl font-medium transition-all duration-200 shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                <Filter className="w-5 h-5" />
                <span>Filters</span>
                {Object.values(filters).some(val => 
                  Array.isArray(val) ? val.length > 0 : val && val !== 'newest' && val !== '30DAYS'
                ) && (
                  <span className="bg-white/20 text-xs px-2 py-1 rounded-full">
                    Active
                  </span>
                )}
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* Filters Sidebar - JobsFromSpace Style */}
          <div className={`${showFilters ? 'block' : 'hidden'} lg:block w-full lg:w-80 flex-shrink-0`}>
            <div className="bg-white/70 backdrop-blur-md rounded-2xl shadow-xl border border-gray-200/50 p-6 sticky top-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-bold text-gray-900 flex items-center gap-2">
                  <Filter className="w-5 h-5 text-blue-600" />
                  Filters
                </h3>
                <button
                  onClick={clearAllFilters}
                  className="text-sm text-red-600 hover:text-red-700 font-medium px-3 py-1 rounded-full hover:bg-red-50 transition-all"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-6">
                {/* Job Title */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Job Title
                  </label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={filters.jobTitle}
                      onChange={(e) => handleFilterChange({ jobTitle: e.target.value })}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g. Frontend Developer"
                    />
                  </div>
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Location
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={filters.location}
                      onChange={(e) => handleFilterChange({ location: e.target.value })}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="e.g. San Francisco, CA"
                    />
                  </div>
                </div>

                {/* Work Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Work Type
                  </label>
                  <div className="space-y-2">
                    {workTypeOptions.map((type) => (
                      <label key={type.value} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.workType.includes(type.value)}
                          onChange={() => toggleArrayFilter(
                            filters.workType,
                            type.value,
                            (newArray) => handleFilterChange({ workType: newArray })
                          )}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="ml-3 flex items-center gap-2">
                          <span className={`px-2 py-1 text-xs rounded-full ${type.color}`}>
                            {type.icon} {type.label}
                          </span>
                        </span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Experience Level */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Experience Level
                  </label>
                  <div className="space-y-2">
                    {experienceLevels.map((level) => (
                      <label key={level} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.experienceLevel.includes(level)}
                          onChange={() => toggleArrayFilter(
                            filters.experienceLevel,
                            level,
                            (newArray) => handleFilterChange({ experienceLevel: newArray })
                          )}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="ml-3 text-sm text-gray-700">{level}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Salary Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-3">
                    Salary Range
                  </label>
                  <div className="space-y-2">
                    {salaryRanges.map((range) => (
                      <label key={range} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.salaryRange.includes(range)}
                          onChange={() => toggleArrayFilter(
                            filters.salaryRange,
                            range,
                            (newArray) => handleFilterChange({ salaryRange: newArray })
                          )}
                          className="w-4 h-4 text-blue-600 border-gray-300 rounded focus:ring-blue-500"
                        />
                        <span className="ml-3 text-sm text-gray-700">{range}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Posted Age */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Posted Date
                  </label>
                  <select
                    value={filters.postedAge}
                    onChange={(e) => handleFilterChange({ postedAge: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                  >
                    {postedAgeOptions.map((option) => (
                      <option key={option.value} value={option.value}>
                        {option.label}
                      </option>
                    ))}
                  </select>
                </div>

                {/* Negative Keywords */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    Exclude Keywords
                  </label>
                  <input
                    type="text"
                    value={filters.negativeKeywords}
                    onChange={(e) => handleFilterChange({ negativeKeywords: e.target.value })}
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500"
                    placeholder="e.g. sales, marketing"
                  />
                  <p className="text-xs text-gray-500 mt-1">
                    Jobs containing these keywords will be excluded
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="flex-1">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="w-8 h-8 border-4 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-red-600 mb-4">
                  <ExternalLink className="w-12 h-12 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  Error Loading Jobs
                </h3>
                <p className="text-gray-600 mb-4">{error}</p>
                <button
                  onClick={() => performSearch(filters, currentPage)}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Search className="w-12 h-12 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">
                  No jobs found
                </h3>
                <p className="text-gray-600 mb-4">
                  Try adjusting your search criteria or clearing some filters
                </p>
                <button
                  onClick={clearAllFilters}
                  className="px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-lg transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              <>
                {/* Results */}
                <div className={
                  viewMode === 'grid' 
                    ? 'grid gap-6 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2' 
                    : 'space-y-4'
                }>
                  {jobs.map((job) => (
                    <div key={job.id || job._id} className="group bg-white/80 backdrop-blur-sm rounded-2xl shadow-lg border border-gray-200/50 hover:shadow-2xl hover:border-blue-200 transition-all duration-300 p-6 transform hover:-translate-y-1">
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-start gap-4 flex-1">
                          <div className="w-14 h-14 bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl flex items-center justify-center text-xl shadow-md flex-shrink-0 group-hover:shadow-lg transition-all duration-300">
                            {job.company_logo || (typeof job.company === 'string' ? job.company[0]?.toUpperCase() : '🏢')}
                          </div>
                          <div className="flex-1 min-w-0">
                            <h3 className="text-xl font-bold text-gray-900 group-hover:text-blue-600 cursor-pointer mb-2 transition-colors duration-200">
                              {job.title}
                            </h3>
                            <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                              <div className="flex items-center gap-1">
                                <Building2 className="w-4 h-4" />
                                <span className="font-medium">{typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}</span>
                              </div>
                              {job.location && (
                                <div className="flex items-center gap-1">
                                  <MapPin className="w-4 h-4" />
                                  {job.location}
                                </div>
                              )}
                              <div className="flex items-center gap-1">
                                <Clock className="w-4 h-4" />
                                {formatTimeAgo(job.createdAt || job.created_at)}
                              </div>
                            </div>
                            
                            {/* Job Tags */}
                            <div className="flex flex-wrap gap-2 mb-4">
                              {job.isRemote && (
                                <span className="px-3 py-2 bg-gradient-to-r from-green-100 to-green-200 text-green-800 text-sm rounded-xl font-semibold shadow-sm border border-green-200/50">
                                  <span>🌍</span> <span>Remote</span>
                                </span>
                              )}
                              {job.job_type && (
                                <span className="px-3 py-2 bg-gradient-to-r from-blue-100 to-blue-200 text-blue-800 text-sm rounded-xl font-medium shadow-sm border border-blue-200/50">
                                  💼 {job.job_type}
                                </span>
                              )}
                              {job.salary && (
                                <span className="px-3 py-2 bg-gradient-to-r from-yellow-100 to-amber-200 text-yellow-800 text-sm rounded-xl font-semibold shadow-sm border border-yellow-200/50">
                                  {typeof job.salary === 'string' 
                                    ? `💰 ${job.salary}` 
                                    : `💰 ${job.salary.currency || '$'}${job.salary.min ? `${job.salary.min.toLocaleString()}` : ''}${job.salary.max ? ` - ${job.salary.max.toLocaleString()}` : ''}`
                                  }
                                </span>
                              )}
                              {job.skills && job.skills.slice(0, 3).map((skill, index) => (
                                <span key={index} className="px-3 py-2 bg-gradient-to-r from-gray-100 to-gray-200 text-gray-700 text-sm rounded-xl border border-gray-200/50 hover:shadow-sm transition-shadow">
                                  {skill}
                                </span>
                              ))}
                              {job.skills && job.skills.length > 3 && (
                                <span className="px-3 py-2 bg-gradient-to-r from-purple-100 to-purple-200 text-purple-700 text-sm rounded-xl font-medium border border-purple-200/50">
                                  +{job.skills.length - 3} more
                                </span>
                              )}
                            </div>

                            {/* Job Description Preview */}
                            {job.description && (
                              <p className="text-sm text-gray-600 line-clamp-2 mb-4">
                                {job.description.length > 150 
                                  ? `${job.description.substring(0, 150)}...`
                                  : job.description
                                }
                              </p>
                            )}
                          </div>
                        </div>

                        {/* Actions */}
                        <div className="flex flex-col items-end gap-2 flex-shrink-0 ml-4">
                          <button
                            onClick={() => handleSaveJob(job.id || job._id)}
                            className={`p-3 rounded-xl transition-all duration-200 shadow-md hover:shadow-lg transform hover:scale-105 ${
                              savedJobs.has(job.id || job._id)
                                ? 'bg-gradient-to-r from-yellow-100 to-amber-100 text-yellow-600 border border-yellow-200'
                                : 'bg-gradient-to-r from-gray-100 to-gray-200 text-gray-500 hover:from-yellow-100 hover:to-amber-100 hover:text-yellow-600 border border-gray-200'
                            }`}
                            title={savedJobs.has(job.id || job._id) ? 'Remove from saved' : 'Save job'}
                          >
                            {savedJobs.has(job.id || job._id) ? (
                              <Bookmark className="w-5 h-5 fill-current" />
                            ) : (
                              <BookmarkPlus className="w-5 h-5" />
                            )}
                          </button>
                          
                          {appliedJobs.has(job.id || job._id) ? (
                            <div className="flex items-center gap-1 text-green-600 font-medium text-sm">
                              <CheckCircle2 className="w-4 h-4" />
                              Applied
                            </div>
                          ) : (
                            <div className="flex flex-col gap-2">
                              <div className="flex gap-3">
                                <button
                                  onClick={() => navigate(`/jobs/${job.id || job._id}`)}
                                  className="px-4 py-3 text-blue-600 border-2 border-blue-600 rounded-xl hover:bg-blue-50 transition-all text-sm font-semibold hover:shadow-lg transform hover:scale-105"
                                >
                                  👁️ Details
                                </button>
                                <button
                                  onClick={() => handleApplyJob(job.id || job._id)}
                                  className="px-5 py-3 bg-gradient-to-r from-blue-600 to-purple-600 text-white rounded-xl hover:from-blue-700 hover:to-purple-700 transition-all text-sm font-semibold flex items-center gap-2 shadow-lg hover:shadow-xl transform hover:scale-105"
                                >
                                  <ExternalLink className="w-4 h-4" />
                                  Apply Now
                                </button>
                              </div>
                              
                              {/* Auto Apply Button */}
                              {(job.applyUrl || job.applicationUrl) && (
                                <AutoApplyButton
                                  jobUrl={job.applyUrl || job.applicationUrl || '#'}
                                  jobId={job.id || job._id}
                                  onApplied={(applicationId) => handleApplyJob(job.id || job._id)}
                                  size="sm"
                                  className="w-full"
                                />
                              )}
                            </div>
                          )}
                        </div>
                      </div>

                      {/* Job Stats */}
                      <div className="flex items-center justify-between pt-4 border-t border-gray-100 text-xs text-gray-500">
                        <div className="flex items-center gap-4">
                          {job.applicantCount && (
                            <span className="flex items-center gap-1">
                              <Users className="w-3 h-3" />
                              {job.applicantCount} applicants
                            </span>
                          )}
                          {job.views_count && (
                            <span className="flex items-center gap-1">
                              <Eye className="w-3 h-3" />
                              {job.views_count} views
                            </span>
                          )}
                        </div>
                        <div className="flex items-center gap-1">
                          <TrendingUp className="w-3 h-3" />
                          High match
                        </div>
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="mt-8 flex justify-center">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
                        return (
                          <button
                            key={pageNum}
                            onClick={() => handlePageChange(pageNum)}
                            className={`px-3 py-2 border rounded-lg text-sm font-medium ${
                              pageNum === currentPage
                                ? 'border-blue-500 bg-blue-600 text-white'
                                : 'border-gray-300 text-gray-700 bg-white hover:bg-gray-50'
                            }`}
                          >
                            {pageNum}
                          </button>
                        );
                      })}
                      
                      <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="px-3 py-2 border border-gray-300 rounded-lg text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobSearchResults; 