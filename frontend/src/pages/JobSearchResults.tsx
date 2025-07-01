import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { useLocation, useNavigate, useSearchParams } from 'react-router-dom';
import { 
  X, EyeOff, Heart, ChevronDown, Check
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { Job } from '../types/job';
import Layout from '../components/Layout';
import AuthModal from '../components/AuthModal';
import JobCard from '../components/JobCard/JobCard';
import SearchFilters from '../components/JobSearch/SearchFilters';

interface Filters {
  workTypes: string[];
  jobTypes: string[];
  experiences: string[];
  postedAge: string;
  sortBy: string;
  salaryRange: string;
  location: string;
  company: string;
  page: number;
  limit: number;
}

// Custom Multi-Select Dropdown Component
interface MultiSelectProps {
  label: string;
  options: { value: string; label: string }[];
  selectedValues: string[];
  onChange: (values: string[]) => void;
  placeholder?: string;
}

const MultiSelectDropdown: React.FC<MultiSelectProps> = ({
  label,
  options,
  selectedValues,
  onChange,
  placeholder = "Select options"
}) => {
  const [isOpen, setIsOpen] = useState(false);

  const toggleOption = (value: string) => {
    if (selectedValues.includes(value)) {
      onChange(selectedValues.filter(v => v !== value));
    } else {
      onChange([...selectedValues, value]);
    }
  };

  const displayText = selectedValues.length === 0 
    ? placeholder 
    : selectedValues.length === options.length 
      ? "All Selected" 
      : `${selectedValues.length} selected`;

  return (
    <div className="relative">
      <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{label}</label>
      <div className="relative">
        <button
          type="button"
          onClick={() => setIsOpen(!isOpen)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500 appearance-none text-left flex items-center justify-between transition-colors duration-200"
        >
          <span className={selectedValues.length === 0 ? "text-gray-500" : ""}>{displayText}</span>
          <ChevronDown className={`w-4 h-4 text-gray-400 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
        </button>
        
        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-lg shadow-xl max-h-60 overflow-y-auto">
            {options.map((option) => (
              <label key={option.value} className="flex items-center px-3 py-2 hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
                <input
                  type="checkbox"
                  checked={selectedValues.includes(option.value)}
                  onChange={() => toggleOption(option.value)}
                  className="h-3 w-3 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded mr-2"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">{option.label}</span>
              </label>
            ))}
          </div>
        )}
      </div>
      
      {/* Click outside to close */}
      {isOpen && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setIsOpen(false)}
        />
      )}
    </div>
  );
};

// Company/Location Autocomplete Input Component
interface AutocompleteInputProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder: string;
  type: 'company' | 'location';
}

const AutocompleteInput: React.FC<AutocompleteInputProps> = ({
  label,
  value,
  onChange,
  placeholder,
  type
}) => {
  const [suggestions, setSuggestions] = useState<string[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);

  const fetchSuggestions = useCallback(async (query: string) => {
    if (!query.trim() || query.length < 2) {
      setSuggestions([]);
      setShowSuggestions(false);
      return;
    }

    setIsLoading(true);
    try {
      const baseUrl = await import('../utils/apiConfig').then(m => m.getApiUrl());
      const endpoint = type === 'company' ? 'companies/search' : 'locations/search';
      const response = await fetch(`${baseUrl}/${endpoint}?q=${encodeURIComponent(query)}&limit=5`);
      
      if (response.ok) {
        const data = await response.json();
        setSuggestions(data.map((item: any) => item.name || item));
        setShowSuggestions(true);
      } else {
        setSuggestions([]);
        setShowSuggestions(false);
      }
    } catch (error) {
      console.error(`Error fetching ${type} suggestions:`, error);
      setSuggestions([]);
      setShowSuggestions(false);
    } finally {
      setIsLoading(false);
    }
  }, [type]);

  useEffect(() => {
    const timeoutId = setTimeout(() => {
      fetchSuggestions(value);
    }, 300);

    return () => clearTimeout(timeoutId);
  }, [value, fetchSuggestions]);

  return (
    <div className="relative">
      <label className="block text-xs font-medium text-gray-700 dark:text-gray-300 mb-1">{label}</label>
      <div className="relative">
        <input
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onFocus={() => setShowSuggestions(suggestions.length > 0)}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500 pr-8"
        />
        {isLoading && (
          <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
            <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
          </div>
        )}
      </div>
      
      {showSuggestions && (
        <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 rounded-lg shadow-xl max-h-60 overflow-y-auto">
          {suggestions.length > 0 ? (
            suggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => {
                  onChange(suggestion);
                  setShowSuggestions(false);
                }}
                className="w-full px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 text-sm text-gray-700 dark:text-gray-300"
              >
                {suggestion}
              </button>
            ))
          ) : value.length > 2 && !isLoading && (
            <div className="px-3 py-2 text-sm text-gray-500 dark:text-gray-400 text-center">
              No results found for "{value}"
            </div>
          )}
        </div>
      )}
      
      {/* Click outside to close */}
      {showSuggestions && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowSuggestions(false)}
        />
      )}
    </div>
  );
};

export default function JobSearchResults() {
  const location = useLocation();
  const { isAuthenticated, user } = useAuth();
  
  // State management
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadingMore, setLoadingMore] = useState(false);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  
  // Job status tracking
  const [favoriteJobs, setFavoriteJobs] = useState(new Set<string>());
  const [hiddenJobs, setHiddenJobs] = useState(new Set<string>());
  const [appliedJobs, setAppliedJobs] = useState(new Set<string>());
  
  // Filters
  const [filters, setFilters] = useState<Filters>({
    workTypes: [],
    jobTypes: [],
    experiences: [],
    postedAge: '30DAYS',
    sortBy: 'relevance',
    salaryRange: '',
    location: '',
    company: '',
    page: 1,
    limit: 5,
  });
  
  const [showHiddenJobs, setShowHiddenJobs] = useState(false);

  const fetchJobs = async (page = 1, append = false) => {
    append ? setLoadingMore(true) : setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        q: searchQuery,
        page: page.toString(),
        limit: '5000',
        sort_by: filters.sortBy,
        posted_age: filters.postedAge,
        ...(filters.workTypes.length > 0 && { work_type: filters.workTypes.join(',') }),
        ...(filters.jobTypes.length > 0 && { job_type: filters.jobTypes.join(',') }),
        ...(filters.experiences.length > 0 && { experience: filters.experiences.join(',') }),
        ...(filters.salaryRange && { salary_range: filters.salaryRange }),
        ...(filters.location && { location: filters.location }),
        ...(filters.company && { company: filters.company }),
      });

      const response = await fetch(`${await import('../utils/apiConfig').then(m => m.getApiUrl())}/jobs/search?${queryParams}`);
      const data = await response.json();
      
      const newJobs = data.jobs || [];
      
      if (append) {
        setJobs(prev => [...prev, ...newJobs]);
        setCurrentPage(page);
      } else {
        setJobs(newJobs);
        setCurrentPage(1);
      }
      
      setTotalJobs(data.total || 0);
      setHasMore(newJobs.length === 5000); // Assume no more if less than limit
    } catch (e: any) {
      console.error(e.message);
      if (!append) {
        setJobs([]);
        setTotalJobs(0);
      }
    } finally {
      setLoading(false);
      setLoadingMore(false);
    }
  };

  // Infinite scroll handler
  const loadMore = () => {
    if (!loadingMore && hasMore) {
      fetchJobs(currentPage + 1, true);
    }
  };

  // Scroll event listener for infinite scroll
  useEffect(() => {
    const handleScroll = () => {
      if (window.innerHeight + document.documentElement.scrollTop >= document.documentElement.offsetHeight - 1000) {
        loadMore();
      }
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, [loadingMore, hasMore, currentPage]); // eslint-disable-line react-hooks/exhaustive-deps

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setSearchQuery(params.get('q') || '');
    fetchJobs();
  }, [location.search, filters]); // eslint-disable-line react-hooks/exhaustive-deps
  
  const handleFiltersChange = useCallback((newFilters: Partial<Filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: newFilters.page || 1 }));
  }, []);

  // Remove filter helper (commented as not currently used in UI)
  // const removeFilter = (filterKey: keyof Filters) => {
  //   if (filterKey === 'workTypes' || filterKey === 'jobTypes' || filterKey === 'experiences') {
  //     setFilters(prev => ({ ...prev, [filterKey]: [] }));
  //   } else {
  //     setFilters(prev => ({ ...prev, [filterKey]: '' }));
  //   }
  // };
  
  // Job action handlers
  const toggleFavorite = (jobId: string) => {
    if (!isAuthenticated) {
      setIsAuthModalOpen(true);
      toast.error("Please login to save favorites");
      return;
    }
    setFavoriteJobs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
        toast.success("Removed from favorites");
      } else {
        newSet.add(jobId);
        toast.success("Added to favorites");
      }
      return newSet;
    });
  };
  
  const markAsApplied = (jobId: string) => {
    if (!isAuthenticated) {
      setIsAuthModalOpen(true);
      toast.error("Please login to track applications");
      return;
    }
    setAppliedJobs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
        toast.success("Removed from applied");
      } else {
        newSet.add(jobId);
        toast.success("Marked as applied");
      }
      return newSet;
    });
  };

  // Hide/reveal job functions
  const handleJobHide = (jobId: string) => {
    setHiddenJobs(prev => {
      const newHidden = new Set(prev);
      newHidden.add(jobId);
      return newHidden;
    });
    
    // Update total count for display
    setTotalJobs(prev => prev - 1);
    toast.success('Job hidden successfully');
  };

  const handleJobReveal = (jobId: string) => {
    setHiddenJobs(prev => {
      const newHidden = new Set(prev);
      newHidden.delete(jobId);
      return newHidden;
    });
    
    // Update total count for display
    setTotalJobs(prev => prev + 1);
    toast.success('Job revealed successfully');
  };

  // Calculate visible jobs count
  const visibleJobsCount = useMemo(() => {
    return jobs.filter(job => !hiddenJobs.has(job._id || job.id || '')).length;
  }, [jobs, hiddenJobs]);

  // Calculate actual displayed total (excluding hidden jobs)
  const displayedTotal = useMemo(() => {
    return totalJobs - hiddenJobs.size;
  }, [totalJobs, hiddenJobs]);

  return (
    <Layout>
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />

      {/* Main Content */}
      <div className="flex-1 relative">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          <div className="flex flex-col xl:flex-row gap-8 min-h-[600px]">
            {/* Filters Sidebar */}
            <div className="xl:w-80 flex-shrink-0">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 p-6 sticky top-24 max-h-[calc(100vh-8rem)] overflow-y-auto">
                <SearchFilters 
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                  availableCompanies={availableCompanies}
                  availableLocations={availableLocations}
                />
              </div>
            </div>

            {/* Job Listings - Equal width and height */}
            <div className="xl:flex-1 min-w-0">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 min-h-[600px] flex flex-col">
                {/* Header */}
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
                    <div>
                      <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                        Job Search Results
                      </h1>
                      <p className="text-gray-600 dark:text-gray-400 mt-1">
                        Found {displayedTotal} jobs matching your criteria
                        {hiddenJobs.size > 0 && (
                          <span className="text-sm text-gray-500 ml-2">
                            ({hiddenJobs.size} hidden)
                          </span>
                        )}
                      </p>
                    </div>
                    
                    {/* Sort Options */}
                    <div className="flex items-center gap-3">
                      <label className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        Sort by:
                      </label>
                      <select 
                        value={filters.sortBy}
                        onChange={(e) => handleFiltersChange({ sortBy: e.target.value })}
                        className="border border-gray-300 dark:border-gray-600 rounded-lg px-3 py-2 bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="newest">Newest First</option>
                        <option value="relevance">Most Relevant</option>
                        <option value="oldest">Oldest First</option>
                      </select>
                    </div>
                  </div>
                </div>

                {/* Job Cards Container */}
                <div className="flex-1 p-6">
                  {loading ? (
                    <div className="grid gap-4">
                      {[...Array(8)].map((_, i) => (
                        <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-4 animate-pulse">
                          <div className="flex justify-between items-start mb-3">
                            <div className="flex-1">
                              <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-2"></div>
                              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
                              <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                            </div>
                            <div className="h-8 w-20 bg-gray-200 dark:bg-gray-700 rounded"></div>
                          </div>
                          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-full mb-2"></div>
                          <div className="h-3 bg-gray-200 dark:bg-gray-700 rounded w-2/3"></div>
                        </div>
                      ))}
                    </div>
                  ) : jobs.length > 0 ? (
                    <div className="space-y-4">
                      {jobs
                        .filter(job => !hiddenJobs.has(job._id || job.id || ''))
                        .map((job, index) => (
                          <JobCard
                            key={job._id || job.id || index}
                            job={job}
                            isHidden={false}
                            onHide={() => handleJobHide(job._id || job.id || `job-${index}`)}
                            onReveal={() => handleJobReveal(job._id || job.id || `job-${index}`)}
                          />
                        ))}
                    </div>
                  ) : (
                    <div className="flex-1 flex items-center justify-center">
                      <div className="text-center">
                        <div className="text-gray-400 dark:text-gray-500 mb-4">
                          <svg className="mx-auto h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                          </svg>
                        </div>
                        <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No jobs found</h3>
                        <p className="text-gray-500 dark:text-gray-400">
                          Try adjusting your search criteria or filters.
                        </p>
                      </div>
                    </div>
                  )}
                </div>

                {/* Pagination */}
                {totalJobs > 0 && (
                  <div className="border-t border-gray-200 dark:border-gray-700 p-6">
                    <div className="flex items-center justify-between">
                      <div className="text-sm text-gray-700 dark:text-gray-300">
                        Showing {Math.max(1, ((filters.page - 1) * filters.limit) + 1)} to {Math.min(filters.page * filters.limit, displayedTotal)} of {displayedTotal} results
                        {hiddenJobs.size > 0 && (
                          <span className="text-gray-500 ml-2">({hiddenJobs.size} jobs hidden)</span>
                        )}
                      </div>
                      
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => handleFiltersChange({...filters, page: Math.max(1, filters.page - 1)})}
                          disabled={filters.page <= 1}
                          className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                          Previous
                        </button>
                        
                        <div className="flex items-center space-x-1">
                          {Array.from({ length: Math.min(5, Math.ceil(totalJobs / filters.limit)) }, (_, i) => {
                            const pageNum = i + 1;
                            return (
                              <button
                                key={pageNum}
                                onClick={() => handleFiltersChange({...filters, page: pageNum})}
                                className={`px-3 py-2 text-sm rounded-lg ${
                                  filters.page === pageNum
                                    ? 'bg-blue-600 text-white'
                                    : 'border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white'
                                }`}
                              >
                                {pageNum}
                              </button>
                            );
                          })}
                        </div>
                        
                        <button
                          onClick={() => handleFiltersChange({...filters, page: Math.min(Math.ceil(totalJobs / filters.limit), filters.page + 1)})}
                          disabled={filters.page >= Math.ceil(totalJobs / filters.limit)}
                          className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 bg-white dark:bg-gray-800 text-gray-900 dark:text-white"
                        >
                          Next
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
} 