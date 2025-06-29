import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { 
  X, EyeOff, Heart, ChevronDown, Check
} from 'lucide-react';
import toast from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { Job } from '../types/job';
import Layout from '../components/Layout';
import AuthModal from '../components/AuthModal';

interface Filters {
  workTypes: string[];
  jobTypes: string[];
  experiences: string[];
  postedAge: string;
  sortBy: string;
  salaryRange: string;
  location: string;
  company: string;
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
  });
  
  const [showHiddenJobs, setShowHiddenJobs] = useState(false);

  const fetchJobs = async (page = 1, append = false) => {
    append ? setLoadingMore(true) : setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        q: searchQuery,
        page: page.toString(),
        limit: '20',
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
      setHasMore(newJobs.length === 20); // Assume no more if less than limit
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
  
  const handleFilterChange = (newFilters: Partial<Filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

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

  const hideJob = (jobId: string) => {
    setHiddenJobs(prev => new Set(prev).add(jobId));
    toast.success("Job hidden");
  };
  
  const filteredJobs = useMemo(() => {
    if (showHiddenJobs) return jobs;
    return jobs.filter(job => !hiddenJobs.has(job._id || job.id));
  }, [jobs, hiddenJobs, showHiddenJobs]);

  return (
    <Layout>
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />

      <div className="max-w-7xl mx-auto px-4 py-6">
        {/* Compact Filter Bar */}
        <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-4 mb-6 transition-colors duration-200">
          {/* First Row - Main Filters */}
          <div className="grid grid-cols-1 md:grid-cols-5 gap-4 mb-4">
            {/* Work Type Multi-Select */}
            <MultiSelectDropdown
              label="Work Type"
              options={[
                { value: "remote", label: "Remote" },
                { value: "hybrid", label: "Hybrid" },
                { value: "on-site", label: "On-site" }
              ]}
              selectedValues={filters.workTypes}
              onChange={(values) => handleFilterChange({ workTypes: values })}
              placeholder="All Types"
            />

            {/* Job Type Multi-Select */}
            <MultiSelectDropdown
              label="Job Type"
              options={[
                { value: "full-time", label: "Full-time" },
                { value: "part-time", label: "Part-time" },
                { value: "contract", label: "Contract" },
                { value: "freelance", label: "Freelance" }
              ]}
              selectedValues={filters.jobTypes}
              onChange={(values) => handleFilterChange({ jobTypes: values })}
              placeholder="All Types"
            />

            {/* Experience Multi-Select */}
            <MultiSelectDropdown
              label="Experience"
              options={[
                { value: "entry", label: "Entry (0-2y)" },
                { value: "mid", label: "Mid (3-5y)" },
                { value: "senior", label: "Senior (6y+)" },
                { value: "lead", label: "Lead/Manager" }
              ]}
              selectedValues={filters.experiences}
              onChange={(values) => handleFilterChange({ experiences: values })}
              placeholder="All Levels"
            />

            {/* Post Time Dropdown */}
            <div className="relative">
              <label className="block text-xs font-medium text-gray-700 dark:text-slate-300 mb-1">Post Time</label>
              <div className="relative">
                <select
                  value={filters.postedAge}
                  onChange={(e) => handleFilterChange({ postedAge: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500 appearance-none transition-colors duration-200"
                >
                  <option value="1DAY">24 hours</option>
                  <option value="3DAYS">3 days</option>
                  <option value="7DAYS">1 week</option>
                  <option value="30DAYS">1 month</option>
                </select>
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-slate-400 pointer-events-none" />
              </div>
            </div>

            {/* Salary Dropdown */}
            <div className="relative">
              <label className="block text-xs font-medium text-gray-700 dark:text-slate-300 mb-1">Salary</label>
              <div className="relative">
                <select
                  value={filters.salaryRange}
                  onChange={(e) => handleFilterChange({ salaryRange: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-slate-100 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500 appearance-none transition-colors duration-200"
                >
                  <option value="">Any</option>
                  <option value="0-36000">$0-36K</option>
                  <option value="36000-72000">$36K-72K</option>
                  <option value="72000-108000">$72K-108K</option>
                  <option value="108000-144000">$108K-144K</option>
                  <option value="144000-180000">$144K-180K</option>
                  <option value="180000+">$180K+</option>
                </select>
                <ChevronDown className="absolute right-2 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400 dark:text-slate-400 pointer-events-none" />
              </div>
            </div>
          </div>

          {/* Second Row - Location, Company, Clear All */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            {/* Location Autocomplete */}
            <AutocompleteInput
              label="Location"
              value={filters.location}
              onChange={(value) => handleFilterChange({ location: value })}
              placeholder="City, Country..."
              type="location"
            />

            {/* Company Autocomplete */}
            <AutocompleteInput
              label="Company"
              value={filters.company}
              onChange={(value) => handleFilterChange({ company: value })}
              placeholder="Company name..."
              type="company"
            />

            {/* Clear All + Show Hidden */}
            <div className="flex gap-2">
              <button
                onClick={() => setFilters({
                  workTypes: [],
                  jobTypes: [],
                  experiences: [],
                  postedAge: '30DAYS',
                  sortBy: 'relevance',
                  salaryRange: '',
                  location: '',
                  company: '',
                })}
                className="flex-1 px-4 py-2 text-sm text-gray-600 dark:text-slate-300 bg-gray-100 dark:bg-slate-700 hover:bg-gray-200 dark:hover:bg-slate-600 rounded-lg transition-colors duration-200"
              >
                Clear All
              </button>
              <label className="flex items-center text-sm">
                <input
                  type="checkbox"
                  checked={showHiddenJobs}
                  onChange={(e) => setShowHiddenJobs(e.target.checked)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-slate-600 rounded dark:bg-slate-700 mr-2"
                />
                <span className="text-gray-700 dark:text-slate-300 whitespace-nowrap">Show Hidden</span>
              </label>
            </div>
          </div>
        </div>

        {/* Results Header and Sort */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-6">
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              {loading ? 'Searching...' : `${totalJobs.toLocaleString()} jobs found${searchQuery ? ` for "${searchQuery}"` : ''}`}
            </h1>
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600 dark:text-gray-400">Sort by:</span>
              <select
                value={filters.sortBy}
                onChange={(e) => handleFilterChange({ sortBy: e.target.value })}
                className="px-3 py-1.5 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="relevance">Most Relevant</option>
                <option value="newest">Newest First</option>
                <option value="oldest">Oldest First</option>
              </select>
            </div>
          </div>
        </div>

        {/* Active Filters Tags */}
        {(filters.workTypes.length > 0 || filters.jobTypes.length > 0 || filters.experiences.length > 0 || filters.location || filters.company || filters.salaryRange) && (
          <div className="flex flex-wrap gap-2 items-center mb-4">
            <span className="text-sm text-gray-600 dark:text-gray-400">Active filters:</span>
            {filters.workTypes.map(type => (
              <span key={`work-${type}`} className="flex items-center gap-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs font-medium px-2.5 py-1 rounded-full">
                {type}
                <button onClick={() => handleFilterChange({ workTypes: filters.workTypes.filter(t => t !== type) })} className="ml-1 hover:text-blue-900 dark:hover:text-blue-100">
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            {filters.jobTypes.map(type => (
              <span key={`job-${type}`} className="flex items-center gap-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs font-medium px-2.5 py-1 rounded-full">
                {type}
                <button onClick={() => handleFilterChange({ jobTypes: filters.jobTypes.filter(t => t !== type) })} className="ml-1 hover:text-green-900 dark:hover:text-green-100">
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            {filters.experiences.map(exp => (
              <span key={`exp-${exp}`} className="flex items-center gap-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 text-xs font-medium px-2.5 py-1 rounded-full">
                {exp}
                <button onClick={() => handleFilterChange({ experiences: filters.experiences.filter(e => e !== exp) })} className="ml-1 hover:text-purple-900 dark:hover:text-purple-100">
                  <X className="w-3 h-3" />
                </button>
              </span>
            ))}
            {filters.location && (
              <span className="flex items-center gap-1 bg-orange-100 dark:bg-orange-900 text-orange-800 dark:text-orange-200 text-xs font-medium px-2.5 py-1 rounded-full">
                📍 {filters.location}
                <button onClick={() => handleFilterChange({ location: '' })} className="ml-1 hover:text-orange-900 dark:hover:text-orange-100">
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.company && (
              <span className="flex items-center gap-1 bg-indigo-100 dark:bg-indigo-900 text-indigo-800 dark:text-indigo-200 text-xs font-medium px-2.5 py-1 rounded-full">
                🏢 {filters.company}
                <button onClick={() => handleFilterChange({ company: '' })} className="ml-1 hover:text-indigo-900 dark:hover:text-indigo-100">
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
            {filters.salaryRange && (
              <span className="flex items-center gap-1 bg-yellow-100 dark:bg-yellow-900 text-yellow-800 dark:text-yellow-200 text-xs font-medium px-2.5 py-1 rounded-full">
                💰 {filters.salaryRange}
                <button onClick={() => handleFilterChange({ salaryRange: '' })} className="ml-1 hover:text-yellow-900 dark:hover:text-yellow-100">
                  <X className="w-3 h-3" />
                </button>
              </span>
            )}
          </div>
        )}

        {/* Job Listings - Full Width */}
        <div className="w-full">
          {loading ? (
            <div className="grid gap-4">
              {[...Array(8)].map((_, i) => (
                <div key={i} className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 animate-pulse">
                  <div className="flex justify-between items-start mb-4">
                    <div className="flex-1">
                      <div className="h-5 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mb-3"></div>
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2 mb-2"></div>
                      <div className="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/3"></div>
                    </div>
                    <div className="flex gap-2">
                      <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                      <div className="w-8 h-8 bg-gray-200 dark:bg-gray-700 rounded-full"></div>
                    </div>
                  </div>
                  <div className="flex gap-2 mb-3">
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-full w-16"></div>
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-full w-20"></div>
                    <div className="h-6 bg-gray-200 dark:bg-gray-700 rounded-full w-14"></div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="grid gap-4">
              {filteredJobs.map((job) => (
                <div
                  key={job._id || job.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 hover:shadow-lg hover:border-blue-200 dark:hover:border-blue-700 transition-all duration-200 cursor-pointer"
                >
                  <div className="flex justify-between items-start mb-3">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1 truncate">
                        {job.url && isAuthenticated ? (
                          <a 
                            href={job.url} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors cursor-pointer"
                          >
                            {job.title}
                          </a>
                        ) : (
                          <span 
                            className={`${job.url && !isAuthenticated ? 'cursor-pointer hover:text-blue-600 dark:hover:text-blue-400' : ''}`}
                            onClick={() => {
                              if (job.url && !isAuthenticated) {
                                setIsAuthModalOpen(true);
                                toast.error("Please login to apply for jobs", { duration: 5000 });
                              }
                            }}
                          >
                            {job.title}
                          </span>
                        )}
                      </h3>
                      <div className="flex items-center text-sm text-gray-600 dark:text-gray-400 mb-2">
                        <span className="font-medium">{typeof job.company === 'object' ? job.company.name : job.company}</span>
                        {job.location && (
                          <>
                            <span className="mx-2">•</span>
                            <span>{job.location}</span>
                          </>
                        )}
                      </div>
                    </div>
                    <div className="flex items-center gap-3 ml-4">
                      <button
                        onClick={() => markAsApplied(job._id || job.id)}
                        className={`p-3 rounded-full transition-colors ${
                          appliedJobs.has(job._id || job.id)
                            ? 'text-green-500 hover:text-green-600 bg-green-50 dark:bg-green-900/20'
                            : 'text-gray-400 hover:text-green-500 hover:bg-green-50 dark:hover:bg-green-900/20'
                        }`}
                        title={appliedJobs.has(job._id || job.id) ? 'Applied' : 'Mark as applied'}
                      >
                        <Check className="w-8 h-8" />
                      </button>
                      <button
                        onClick={() => toggleFavorite(job._id || job.id)}
                        className={`p-3 rounded-full transition-colors ${
                          favoriteJobs.has(job._id || job.id)
                            ? 'text-red-500 hover:text-red-600 bg-red-50 dark:bg-red-900/20'
                            : 'text-gray-400 hover:text-red-500 hover:bg-red-50 dark:hover:bg-red-900/20'
                        }`}
                        title={favoriteJobs.has(job._id || job.id) ? 'Remove from favorites' : 'Add to favorites'}
                      >
                        <Heart className="w-8 h-8" fill={favoriteJobs.has(job._id || job.id) ? 'currentColor' : 'none'} />
                      </button>
                      <button
                        onClick={() => hideJob(job._id || job.id)}
                        className={`p-3 rounded-full transition-colors ${
                          hiddenJobs.has(job._id || job.id)
                            ? 'text-gray-600 hover:text-gray-700 bg-gray-100 dark:bg-gray-700'
                            : 'text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700'
                        }`}
                        title="Hide this job"
                      >
                        <EyeOff className="w-8 h-8" />
                      </button>
                    </div>
                  </div>

                  {/* Job Tags */}
                  <div className="flex flex-wrap gap-2 mb-3">
                    {job.location && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                        {job.location}
                      </span>
                    )}
                    {job.job_type && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                        {job.job_type}
                      </span>
                    )}
                    {job.isRemote && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800">
                        Remote
                      </span>
                    )}
                    {job.salary_range && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
                        {job.salary_range}
                      </span>
                    )}
                    {job.experienceLevel && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-indigo-100 text-indigo-800">
                        {job.experienceLevel}
                      </span>
                    )}
                    {job.source && user?.email === 'admin@buzz2remote.com' && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-gray-100 text-gray-800">
                        {job.source}
                      </span>
                    )}
                    {job.created_at && (
                      <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-orange-100 text-orange-800">
                        {new Date(job.created_at).toLocaleDateString()}
                      </span>
                    )}
                  </div>

                  {/* Skills */}
                  {job.skills && job.skills.length > 0 && (
                    <div className="mb-3">
                      <div className="flex flex-wrap gap-1">
                        {job.skills.slice(0, 6).map((skill, index) => (
                          <span
                            key={index}
                            className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-50 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-200 dark:border-gray-600"
                          >
                            {skill}
                          </span>
                        ))}
                        {job.skills.length > 6 && (
                          <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-50 dark:bg-gray-700 text-gray-500 dark:text-gray-400">
                            +{job.skills.length - 6} more
                          </span>
                        )}
                      </div>
                    </div>
                  )}

                  {/* Description */}
                  {job.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                      {job.description.replace(/<[^>]*>/g, '').substring(0, 150)}...
                    </p>
                  )}

                  {/* Source info for admin only */}
                  {job.source && user?.email === 'admin@buzz2remote.com' && (
                    <div className="flex justify-end">
                      <div className="text-xs text-gray-500 dark:text-gray-400">
                        via {job.source}
                      </div>
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
          
          {/* Infinite Scroll Loading Indicator */}
          {loadingMore && (
            <div className="flex justify-center py-8">
              <div className="flex items-center gap-2">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
                <span className="text-gray-600 dark:text-gray-400">Loading more jobs...</span>
              </div>
            </div>
          )}
          
          {/* End of results message */}
          {!loading && !loadingMore && !hasMore && jobs.length > 0 && (
            <div className="text-center py-8">
              <p className="text-gray-600 dark:text-gray-400">You've seen all available jobs!</p>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
} 