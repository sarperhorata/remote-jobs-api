import React, { useState, useEffect, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  MapPin, 
  Filter,
  Grid3X3,
  List,
  Search,
  ExternalLink
} from 'lucide-react';
import JobCard from '../components/JobCard/JobCard';
import { Job } from '../types/job';
import { getApiUrl } from '../utils/apiConfig';

interface SearchFilters {
  jobTitle: string;
  location: string;
  experienceLevel: string[];
  workType: string[];
  salaryRange: string[];
  skills: string[];
  sortBy: 'newest' | 'salary' | 'relevance';
}

const JobSearchResults: React.FC = () => {
  const location = useLocation();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const [totalJobs, setTotalJobs] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>('grid');
  const [showFilters, setShowFilters] = useState(false);
  const [filters, setFilters] = useState<SearchFilters>({
    jobTitle: '',
    location: '',
    experienceLevel: [],
    workType: ['Remote Jobs'],
    salaryRange: [],
    skills: [],
    sortBy: 'newest'
  });

  const experienceLevels = [
    'Entry Level (0-2 years)',
    'Mid Level (2-4 years)', 
    'Senior Level (4-6 years)',
    'Lead/Principal (6-10 years)',
    'Executive (10+ years)'
  ];

  const workTypeOptions = [
    'Remote Jobs',
    'Hybrid Jobs',
    'Office Jobs'
  ];

  const salaryRanges = [
    '$0 - $30k',
    '$30k - $70k',
    '$70k - $120k', 
    '$120k - $180k',
    '$180k - $240k',
    '$240k+'
  ];

  const performSearch = useCallback(async (searchFilters: SearchFilters, page: number = 1) => {
    setLoading(true);
    setError('');

    try {
      const params = new URLSearchParams();
      
      // Use 'q' parameter for general search (supports both title and content search)
      if (searchFilters.jobTitle) params.append('q', searchFilters.jobTitle);
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
      
      params.append('page', page.toString());
      params.append('limit', '20');
      params.append('sort_by', searchFilters.sortBy);

      // Get dynamic API URL
      const apiUrl = await getApiUrl();
      const response = await fetch(`${apiUrl}/jobs/search?${params}`);
      
      if (!response.ok) {
        throw new Error('Failed to fetch jobs');
      }

      const data = await response.json();
      
      setJobs(data.jobs || []);
      setTotalJobs(data.total || 0);
      setCurrentPage(page);

      // Update URL without page reload - keep original URL structure
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
  }, [location.pathname]);

  useEffect(() => {
    // Parse URL parameters to support both /jobs and /jobs/search routes
    const searchParams = location.state?.searchParams || {};
    const urlParams = new URLSearchParams(location.search);
    
    const initialFilters: SearchFilters = {
      // Support both 'q' and 'job_title' for job title search
      jobTitle: searchParams.job_title || urlParams.get('q') || urlParams.get('job_title') || urlParams.get('position') || '',
      location: searchParams.location || urlParams.get('location') || '',
      experienceLevel: searchParams.experience_level ? searchParams.experience_level.split(',') : [],
      workType: searchParams.work_type ? searchParams.work_type.split(',') : ['Remote Jobs'],
      salaryRange: searchParams.salary_range ? searchParams.salary_range.split(',') : [],
      skills: searchParams.skills ? searchParams.skills.split(',') : [],
      sortBy: 'newest'
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
      workType: ['Remote Jobs'],
      salaryRange: [],
      skills: [],
      sortBy: 'newest'
    };
    setFilters(clearedFilters);
    performSearch(clearedFilters, 1);
  };

  const totalPages = Math.ceil(totalJobs / 20);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between gap-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Job Search Results
              </h1>
              <p className="text-gray-600 dark:text-gray-400 mt-1">
                {totalJobs > 0 ? (
                  <>Found {totalJobs.toLocaleString()} jobs matching your criteria</>
                ) : (
                  'No jobs found'
                )}
              </p>
            </div>
            
            <div className="flex items-center gap-3">
              {/* View Mode Toggle */}
              <div className="flex bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
                <button
                  onClick={() => setViewMode('grid')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'grid'
                      ? 'bg-white dark:bg-gray-600 text-orange-600 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  <Grid3X3 className="w-4 h-4" />
                </button>
                <button
                  onClick={() => setViewMode('list')}
                  className={`p-2 rounded-md transition-colors ${
                    viewMode === 'list'
                      ? 'bg-white dark:bg-gray-600 text-orange-600 shadow-sm'
                      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
                  }`}
                >
                  <List className="w-4 h-4" />
                </button>
              </div>

              {/* Filters Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="flex items-center gap-2 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
              >
                <Filter className="w-4 h-4" />
                Filters
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 py-6">
        <div className="flex gap-6">
          {/* Filters Sidebar */}
          <div className={`${showFilters ? 'block' : 'hidden'} lg:block w-full lg:w-80 flex-shrink-0`}>
            <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 sticky top-6">
              <div className="flex items-center justify-between mb-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h3>
                <button
                  onClick={clearAllFilters}
                  className="text-sm text-orange-600 hover:text-orange-700"
                >
                  Clear All
                </button>
              </div>

              <div className="space-y-6">
                {/* Job Title */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Job Title
                  </label>
                  <div className="relative">
                    <Search className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={filters.jobTitle}
                      onChange={(e) => handleFilterChange({ jobTitle: e.target.value })}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      placeholder="e.g. Frontend Developer"
                    />
                  </div>
                </div>

                {/* Location */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Location
                  </label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-3 w-4 h-4 text-gray-400" />
                    <input
                      type="text"
                      value={filters.location}
                      onChange={(e) => handleFilterChange({ location: e.target.value })}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                      placeholder="e.g. San Francisco, CA"
                    />
                  </div>
                </div>

                {/* Experience Level */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Experience Level
                  </label>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {experienceLevels.map((level) => (
                      <label key={level} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.experienceLevel.includes(level)}
                          onChange={() => 
                            toggleArrayFilter(
                              filters.experienceLevel, 
                              level, 
                              (newLevels) => handleFilterChange({ experienceLevel: newLevels })
                            )
                          }
                          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{level}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Work Type */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Work Type
                  </label>
                  <div className="space-y-2">
                    {workTypeOptions.map((type) => (
                      <label key={type} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.workType.includes(type)}
                          onChange={() => 
                            toggleArrayFilter(
                              filters.workType, 
                              type, 
                              (newTypes) => handleFilterChange({ workType: newTypes })
                            )
                          }
                          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{type}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Salary Range */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Salary Range
                  </label>
                  <div className="space-y-2 max-h-40 overflow-y-auto">
                    {salaryRanges.map((range) => (
                      <label key={range} className="flex items-center cursor-pointer">
                        <input
                          type="checkbox"
                          checked={filters.salaryRange.includes(range)}
                          onChange={() => 
                            toggleArrayFilter(
                              filters.salaryRange, 
                              range, 
                              (newRanges) => handleFilterChange({ salaryRange: newRanges })
                            )
                          }
                          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
                        />
                        <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">{range}</span>
                      </label>
                    ))}
                  </div>
                </div>

                {/* Sort By */}
                <div>
                  <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Sort By
                  </label>
                  <select
                    value={filters.sortBy}
                    onChange={(e) => handleFilterChange({ sortBy: e.target.value as 'newest' | 'salary' | 'relevance' })}
                    className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent dark:bg-gray-700 dark:text-white"
                  >
                    <option value="newest">Newest First</option>
                    <option value="relevance">Most Relevant</option>
                    <option value="salary">Highest Salary</option>
                  </select>
                </div>
              </div>
            </div>
          </div>

          {/* Results */}
          <div className="flex-1">
            {loading ? (
              <div className="flex justify-center items-center h-64">
                <div className="w-8 h-8 border-4 border-orange-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
            ) : error ? (
              <div className="text-center py-12">
                <div className="text-red-600 mb-4">
                  <ExternalLink className="w-12 h-12 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  Error Loading Jobs
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">{error}</p>
                <button
                  onClick={() => performSearch(filters, currentPage)}
                  className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
                >
                  Try Again
                </button>
              </div>
            ) : jobs.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 mb-4">
                  <Search className="w-12 h-12 mx-auto" />
                </div>
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No jobs found
                </h3>
                <p className="text-gray-600 dark:text-gray-400 mb-4">
                  Try adjusting your search criteria or clearing some filters
                </p>
                <button
                  onClick={clearAllFilters}
                  className="px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
                >
                  Clear Filters
                </button>
              </div>
            ) : (
              <>
                {/* Results Grid/List */}
                <div className={
                  viewMode === 'grid' 
                    ? 'grid gap-6 md:grid-cols-2 lg:grid-cols-1 xl:grid-cols-2' 
                    : 'space-y-4'
                }>
                  {jobs.map((job) => (
                    <JobCard key={job.id || job._id} job={job} />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="mt-8 flex justify-center">
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
                      >
                        Previous
                      </button>
                      
                      {/* Page numbers */}
                      {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                        const pageNum = Math.max(1, Math.min(totalPages - 4, currentPage - 2)) + i;
                        return (
                          <button
                            key={pageNum}
                            onClick={() => handlePageChange(pageNum)}
                            className={`px-3 py-2 border rounded-lg text-sm font-medium ${
                              pageNum === currentPage
                                ? 'border-orange-500 bg-orange-600 text-white'
                                : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700'
                            }`}
                          >
                            {pageNum}
                          </button>
                        );
                      })}
                      
                      <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50 disabled:cursor-not-allowed"
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