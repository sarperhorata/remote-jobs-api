import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import Layout from '../components/Layout';
import AuthModal from '../components/AuthModal';
import SearchFilters from '../components/JobSearch/SearchFilters';
import JobCard from '../components/JobCard/JobCard';
import { useAuth } from '../contexts/AuthContext';
import { Job } from '../types/job';
import { Filter, X, Save } from 'lucide-react';
import jobService from '../services/jobService';

interface Filters {
  query: string;
  location: string;
  jobType: string;
  workType: string;
  experience_level: string;
  salaryMin: string;
  salaryMax: string;
  company: string;
  postedWithin: string;
  experiences?: string[];
  postedAge?: string;
  salaryRange?: string;
  page?: number;
}

interface SavedSearch {
  id: string;
  name: string;
  filters: Omit<Filters, "page">;
  createdAt: string;
}

export default function JobSearchResults() {
  const location = useLocation();
  const { user } = useAuth();
  
  // States
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(() => 
    window.innerWidth >= 1024 ? 'grid' : 'list'
  );
  const [hiddenJobs, setHiddenJobs] = useState<Set<string>>(new Set());
  
  // Job status tracking
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  
  // Save Search States
  const [searchName, setSearchName] = useState('');
  
  // Saved searches
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);
  const [showSaveDialog, setShowSaveDialog] = useState(false);
  const [showSavedSearches, setShowSavedSearches] = useState(false);
  
  // Filter Modal States
  const [showFiltersModal, setShowFiltersModal] = useState(false);
  
  // Filters
  const [filters, setFilters] = useState<Filters>({
    query: '',
    location: '',
    jobType: '',
    workType: '',
    experience_level: '',
    salaryMin: '',
    salaryMax: '',
    company: '',
    postedWithin: '',
    page: 1,
  });
  
  // View layout state - Mobile: list, Desktop: grid
  const [isMobile, setIsMobile] = useState(false);

  // Check for mobile screen size
  useEffect(() => {
    const checkMobile = () => {
      const mobile = window.innerWidth < 768; // md breakpoint
      setIsMobile(mobile);
      if (mobile) {
        setViewMode('list'); // Force list view on mobile
      } else {
        setViewMode('grid'); // Default grid on desktop
      }
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);
  
  // Add missing state variables
  // Add missing state variables if needed later

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        q: searchQuery,
        page: filters.page?.toString() || "1",
        limit: "25",
        sort_by: 'relevance',
        posted_age: filters.postedAge || filters.postedWithin,
        ...(filters.workType && { work_type: filters.workType }),
        ...(filters.jobType && { job_type: filters.jobType }),
        ...(filters.experience_level && { experience: filters.experience_level }),
        ...(filters.salaryRange && { salary_range: filters.salaryRange }),
        ...(filters.location && { location: filters.location }),
        ...(filters.company && { company: filters.company }),
      });

      const response = await fetch(`${await import('../utils/apiConfig').then(m => m.getApiUrl())}/jobs/search?${queryParams}`);
      const data = await response.json();
      
      setJobs(data.jobs || []);
      setTotalJobs(data.total || 0);
    } catch (e: any) {
      console.error(e.message);
      setJobs([]);
      setTotalJobs(0);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    setSearchQuery(params.get('q') || '');
    
    // Check if company parameter exists in URL
    const companyParam = params.get('company');
    if (companyParam && companyParam !== filters.company) {
      // Update filters with company from URL
      setFilters(prev => ({ ...prev, company: companyParam, page: 1 }));
    }
    
    fetchJobs();
  }, [location.search, filters]); // eslint-disable-line react-hooks/exhaustive-deps
  
  const handleFiltersChange = useCallback((newFilters: Partial<Filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: newFilters.page || 1 }));
  }, []);

  // Check if any filters are active
  const hasActiveFilters = useMemo(() => {
    return filters.location || filters.jobType || filters.workType || 
           filters.experience_level || filters.company || filters.salaryMin || 
           filters.salaryMax || filters.postedWithin;
  }, [filters]);

  return (
    <Layout>
      <AuthModal isOpen={isAuthModalOpen} onClose={() => setIsAuthModalOpen(false)} />

      {/* Filter Modal */}
      {showFiltersModal && (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-50">
          <div className="bg-white/95 dark:bg-gray-800/95 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 dark:border-gray-700/20 w-11/12 max-w-md lg:max-w-4xl max-h-[90vh] overflow-y-auto">
            {/* Mobile Modal Layout */}
            <div className="lg:hidden">
              <div className="flex items-center justify-between p-6 border-b border-gray-200/50 dark:border-gray-700/50">
                <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h2>
                <button
                  onClick={() => setShowFiltersModal(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-6">
                <SearchFilters 
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                />
              </div>
              <div className="flex gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => setShowFiltersModal(false)}
                  className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Apply Filters
                </button>
                <button
                  onClick={() => {
                    handleFiltersChange({
                      query: '',
                      location: '',
                      jobType: '',
                      workType: '',
                      experience_level: '',
                      salaryMin: '',
                      salaryMax: '',
                      company: '',
                      postedWithin: ''
                    });
                    setShowFiltersModal(false);
                  }}
                  className="px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Clear All
                </button>
              </div>
            </div>

            {/* Desktop Modal Layout */}
            <div className="hidden lg:block">
              <div className="flex items-center justify-between p-8 border-b border-gray-200/50 dark:border-gray-700/50">
                <h2 className="text-xl font-semibold text-gray-900 dark:text-white">Search Filters</h2>
                <button
                  onClick={() => setShowFiltersModal(false)}
                  className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-full transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>
              <div className="p-8 grid grid-cols-2 gap-8">
                <SearchFilters 
                  filters={filters}
                  onFiltersChange={handleFiltersChange}
                />
              </div>
              <div className="flex justify-between gap-4 p-8 border-t border-gray-200 dark:border-gray-700">
                <button
                  onClick={() => {
                    handleFiltersChange({
                      query: '',
                      location: '',
                      jobType: '',
                      workType: '',
                      experience_level: '',
                      salaryMin: '',
                      salaryMax: '',
                      company: '',
                      postedWithin: ''
                    });
                  }}
                  className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Clear All Filters
                </button>
                <div className="flex gap-3">
                  <button
                    onClick={() => setShowFiltersModal(false)}
                    className="px-6 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                  >
                    Cancel
                  </button>
                  <button
                    onClick={() => setShowFiltersModal(false)}
                    className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    Apply Filters
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Save Search Modal */}
      {showSaveDialog && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl w-11/12 max-w-md">
            <div className="flex items-center justify-between p-6 border-b border-gray-200 dark:border-gray-700">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Save Search</h2>
              <button
                onClick={() => setShowSaveDialog(false)}
                className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
              >
                <X className="w-6 h-6" />
              </button>
            </div>
            <div className="p-6">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Search Name
              </label>
              <input
                type="text"
                value={searchName}
                onChange={(e) => setSearchName(e.target.value)}
                placeholder="Enter a name for this search..."
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white rounded-lg focus:ring-blue-500 focus:border-blue-500"
                maxLength={50}
              />
            </div>
            <div className="flex gap-3 p-6 border-t border-gray-200 dark:border-gray-700">
              <button
                onClick={() => setShowSaveDialog(false)}
                className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                Cancel
              </button>
              <button
                onClick={() => {
                  if (searchName.trim()) {
                    // Save search logic here
                    const savedSearches = JSON.parse(localStorage.getItem('savedSearches') || '[]');
                    const newSearch = {
                      id: Date.now().toString(),
                      name: searchName.trim(),
                      filters,
                      createdAt: new Date().toISOString()
                    };
                    savedSearches.push(newSearch);
                    localStorage.setItem('savedSearches', JSON.stringify(savedSearches));
                    setSearchName('');
                    setShowSaveDialog(false);
                    toast.success('Search saved successfully!');
                  }
                }}
                disabled={!searchName.trim()}
                className="flex-1 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
              >
                Save Search
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content - Dark Background */}
      <div className="flex-1 relative bg-gradient-to-br from-gray-50 to-blue-50/30 dark:from-gray-900 dark:to-blue-950/30 min-h-screen">
        <div className="container mx-auto px-4 py-8 max-w-7xl">
          
          {/* Enhanced Search Header */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 mb-8 overflow-hidden">
            {/* Gradient overlay */}
            <div className="bg-gradient-to-r from-blue-600/5 to-purple-600/5 dark:from-blue-400/5 dark:to-purple-400/5 p-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div>
                    <h1 className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white mb-2">
                      Job Search Results
                    </h1>
                    <div className="flex items-center gap-3">
                      <span className="px-4 py-2 bg-gradient-to-r from-blue-100 to-purple-100 dark:from-blue-900/50 dark:to-purple-900/50 text-blue-800 dark:text-blue-200 text-sm font-medium rounded-full border border-blue-200/50 dark:border-blue-700/50">
                        📊 {totalJobs.toLocaleString()} jobs found
                      </span>
                      {hasActiveFilters && (
                        <span className="px-3 py-1 bg-gradient-to-r from-green-100 to-emerald-100 dark:from-green-900/50 dark:to-emerald-900/50 text-green-800 dark:text-green-200 text-xs font-medium rounded-full border border-green-200/50 dark:border-green-700/50">
                          ✨ Filtered
                        </span>
                      )}
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center gap-3">
                  {/* Save Search Button */}
                  <button
                    onClick={() => setShowSaveDialog(true)}
                    className="flex items-center gap-2 px-4 py-2 bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm border border-gray-200/50 dark:border-gray-600/50 text-gray-700 dark:text-gray-300 rounded-xl hover:bg-white dark:hover:bg-gray-600 transition-all duration-200 shadow-sm hover:shadow-md"
                  >
                    <Save className="w-4 h-4" />
                    <span className="hidden sm:inline">Save Search</span>
                  </button>

                  {/* Filter Button */}
                  <button
                    onClick={() => setShowFiltersModal(true)}
                    className={`flex items-center gap-2 px-4 py-2 rounded-xl border transition-all duration-200 shadow-sm hover:shadow-md ${
                      hasActiveFilters 
                        ? 'bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 border-blue-200 dark:border-blue-700 text-blue-700 dark:text-blue-300' 
                        : 'bg-white/80 dark:bg-gray-700/80 backdrop-blur-sm border-gray-200/50 dark:border-gray-600/50 text-gray-700 dark:text-gray-300 hover:bg-white dark:hover:bg-gray-600'
                    }`}
                  >
                    <Filter className="w-4 h-4" />
                    <span className="hidden sm:inline">Filters</span>
                    {hasActiveFilters && (
                      <span className="ml-1 px-2 py-0.5 bg-gradient-to-r from-blue-500 to-purple-500 text-white text-xs rounded-full font-medium">
                        Active
                      </span>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>

          {/* Enhanced Job Results */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 overflow-hidden">
            {loading ? (
              <div className="flex items-center justify-center py-20">
                <div className="text-center">
                  <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                  <div className="text-gray-500 dark:text-gray-400 font-medium">Loading amazing jobs...</div>
                </div>
              </div>
            ) : jobs.length === 0 ? (
              <div className="flex flex-col items-center justify-center py-20">
                <div className="text-6xl mb-4">🔍</div>
                <div className="text-gray-500 dark:text-gray-400 text-lg mb-2 font-medium">No jobs found</div>
                <div className="text-gray-400 dark:text-gray-500 text-sm">Try adjusting your search criteria</div>
              </div>
            ) : (
              <div className="p-6">
                {/* Enhanced View Toggle */}
                <div className="flex items-center justify-between mb-6">
                  <div className="text-sm text-gray-600 dark:text-gray-400 font-medium">
                    Showing {jobs.length} of {totalJobs.toLocaleString()} jobs
                  </div>
                  <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-xl">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`p-2 rounded-lg transition-all duration-200 ${viewMode === 'grid' 
                        ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-300 shadow-sm' 
                        : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'}`}
                    >
                      <div className="w-4 h-4 grid grid-cols-2 gap-0.5">
                        <div className="bg-current rounded-sm"></div>
                        <div className="bg-current rounded-sm"></div>
                        <div className="bg-current rounded-sm"></div>
                        <div className="bg-current rounded-sm"></div>
                      </div>
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`p-2 rounded-lg transition-all duration-200 ${viewMode === 'list' 
                        ? 'bg-white dark:bg-gray-600 text-blue-600 dark:text-blue-300 shadow-sm' 
                        : 'text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300'}`}
                    >
                      <div className="w-4 h-4 space-y-1">
                        <div className="h-0.5 bg-current rounded"></div>
                        <div className="h-0.5 bg-current rounded"></div>
                        <div className="h-0.5 bg-current rounded"></div>
                      </div>
                    </button>
                  </div>
                </div>

                {/* Jobs Grid/List */}
                <div className={viewMode === 'grid' 
                  ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' 
                  : 'space-y-4'
                }>
                  {jobs.map((job, index) => (
                    <JobCard
                      key={job._id || job.id || index}
                      job={job}
                    />
                  ))}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
      
      {/* Click outside to close saved searches dropdown */}
      {showSavedSearches && (
        <div
          className="fixed inset-0 z-40"
          onClick={() => setShowSavedSearches(false)}
        />
      )}
    </Layout>
  );
} 