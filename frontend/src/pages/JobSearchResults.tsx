import React, { useState, useEffect, useMemo, useCallback } from 'react';
import { useLocation } from 'react-router-dom';
import { toast } from 'react-hot-toast';
import Layout from '../components/Layout';
import AuthModal from '../components/AuthModal';
import SearchFilters from '../components/JobSearch/SearchFilters';
import JobCard from '../components/JobCard';
import { useAuth } from '../contexts/AuthContext';
import { Job } from '../types/job';
import { Filter, X, Save, ChevronLeft, ChevronRight, Grid, List } from 'lucide-react';

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
  country?: string; // eklendi
}

interface SavedSearch {
  id: string;
  name: string;
  filters: Omit<Filters, "page">;
  createdAt: string;
}

const countryFlags: Record<string, string> = {
  US: '🇺🇸', GB: '🇬🇧', DE: '🇩🇪', FR: '🇫🇷', TR: '🇹🇷', NL: '🇳🇱', CA: '🇨🇦', IN: '🇮🇳', JP: '🇯🇵', REMOTE: '🌍'
};

export default function JobSearchResults() {
  const location = useLocation();
  
  // States
  const [jobs, setJobs] = useState<Job[]>([]);
  const [totalJobs, setTotalJobs] = useState(0);
  const [viewMode, setViewMode] = useState<'grid' | 'list'>(() => 
    window.innerWidth >= 1024 ? 'grid' : 'list'
  );
  
  // Job status tracking
  const [loading, setLoading] = useState(true);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  
  // Save Search States
  const [searchName, setSearchName] = useState('');
  
  // Saved searches
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
    country: '',
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

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const queryParams = new URLSearchParams({
        q: filters.query,
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
        ...(filters.country && { country: filters.country }), // eklendi
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
    const queryFromUrl = params.get('q') || '';
    const companyFromUrl = params.get('company') || '';
    const countryFromUrl = params.get('country') || '';
    setFilters(prev => {
      const newFilters = {
        ...prev,
        query: queryFromUrl,
        company: companyFromUrl,
        country: countryFromUrl,
      };
      if (
        prev.query === newFilters.query &&
        prev.company === newFilters.company &&
        prev.page === newFilters.page &&
        prev.country === newFilters.country
      ) {
        return prev;
      }
      return newFilters;
    });
  }, [location.search]);

  // `filters` state'i her değiştiğinde iş ilanlarını yeniden çek
  useEffect(() => {
    fetchJobs();
    // Sayfa yüklendiğinde search results bölümüne scroll et
    if (filters.query || filters.company || filters.country) {
      setTimeout(() => {
        const searchResultsSection = document.querySelector('.search-results-section');
        if (searchResultsSection) {
          searchResultsSection.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
      }, 100);
    }
  }, [filters]);
  
  const handleFiltersChange = useCallback((newFilters: Partial<Filters>) => {
    setFilters(prev => ({ ...prev, ...newFilters, page: 1 })); // Filtre değiştiğinde 1. sayfaya dön
  }, []);

  // Check if any filters are active
  const hasActiveFilters = useMemo(() => {
    return filters.location || filters.jobType || filters.workType || 
           filters.experience_level || filters.company || filters.salaryMin || 
           filters.salaryMax || filters.postedWithin;
  }, [filters]);

  // Pagination logic
  const itemsPerPage = 25;
  const totalPages = Math.ceil(totalJobs / itemsPerPage);
  const currentPage = filters.page || 1;

  const handlePageChange = (page: number) => {
    if (page >= 1 && page <= totalPages) {
      setFilters(prev => ({ ...prev, page }));
      // Scroll to top when page changes
      window.scrollTo({ top: 0, behavior: 'smooth' });
    }
  };

  const getPageNumbers = () => {
    const pages = [];
    const maxVisiblePages = 5;
    
    if (totalPages <= maxVisiblePages) {
      for (let i = 1; i <= totalPages; i++) {
        pages.push(i);
      }
    } else {
      if (currentPage <= 3) {
        for (let i = 1; i <= 4; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      } else if (currentPage >= totalPages - 2) {
        pages.push(1);
        pages.push('...');
        for (let i = totalPages - 3; i <= totalPages; i++) {
          pages.push(i);
        }
      } else {
        pages.push(1);
        pages.push('...');
        for (let i = currentPage - 1; i <= currentPage + 1; i++) {
          pages.push(i);
        }
        pages.push('...');
        pages.push(totalPages);
      }
    }
    
    return pages;
  };

  // Sonuç başlığında ülke adı ve bayrağı göster
  const countryLabel = filters.country ?
    `${countryFlags[filters.country] || ''} ${filters.country}` : '';

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
                      location: '',
                      jobType: '',
                      workType: '',
                      experience_level: '',
                      salaryMin: '',
                      salaryMax: '',
                      postedWithin: '',
                    });
                    setShowFiltersModal(false);
                  }}
                  className="flex-1 px-4 py-2 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                >
                  Clear All
                </button>
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

      {/* Hero Section with Enhanced Design - Same as Home Page */}
      <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 text-white">
        {/* Animated background patterns */}
        <div 
          className="absolute inset-0 opacity-30"
          style={{
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
          }}
        ></div>
        
        {/* Glassmorphism overlay */}
        <div className="absolute inset-0 bg-white/5 backdrop-blur-sm"></div>
        
        <div className="relative container mx-auto px-4 py-12">
          <div className="max-w-5xl mx-auto text-center mb-6">
            {/* Main heading with enhanced typography */}
            <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
              <br />
              Job Search 
              <span className="block bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                Results 🐝
              </span>
            </h1>
            
            <p className="text-xl md:text-2xl opacity-95 mb-6 leading-relaxed max-w-3xl mx-auto">
              Found {totalJobs.toLocaleString()} amazing remote opportunities for you. 
              Your perfect job is just a buzz away!
            </p>
          </div>

          {/* Enhanced Search Stats Section */}
          <div className="max-w-4xl mx-auto">
            <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-2xl">
              <div className="flex items-center justify-between flex-wrap gap-4">
                <div className="flex items-center gap-4">
                  {/* SEARCH CRITERIA SUMMARY */}
                  <div className="text-sm text-white/80">
                    {filters.query && (
                      <span className="font-semibold text-yellow-300">{filters.query}</span>
                    )}
                    {filters.company && (
                      <span className="ml-2 font-semibold text-blue-200">@{filters.company}</span>
                    )}
                    {filters.location && (
                      <span className="ml-2 font-semibold text-green-200">in {filters.location}</span>
                    )}
                    {filters.country && countryFlags[filters.country] && (
                      <span className="ml-2 text-lg">{countryFlags[filters.country]}</span>
                    )}
                    {!(filters.query || filters.company || filters.location || (filters.country && countryFlags[filters.country])) && (
                      <span className="text-white/60">All jobs</span>
                    )}
                  </div>
                  {hasActiveFilters && (
                    <div className="text-center">
                      <div className="text-2xl md:text-3xl font-bold text-green-400">✨</div>
                      <div className="text-sm text-white/80">Filtered</div>
                    </div>
                  )}
                </div>
                
                <div className="flex items-center gap-3">
                  {/* Save Search Button */}
                  <button
                    onClick={() => setShowSaveDialog(true)}
                    className="bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold px-6 py-3 rounded-xl hover:bg-white/20 transition-all duration-200 flex items-center space-x-2"
                  >
                    <Save className="w-5 h-5" />
                    <span>Save Search</span>
                  </button>

                  {/* Filter Button */}
                  <button
                    onClick={() => setShowFiltersModal(true)}
                    className={`flex items-center space-x-2 px-6 py-3 rounded-xl border transition-all duration-200 ${
                      hasActiveFilters 
                        ? 'bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white border-blue-400' 
                        : 'bg-white/10 backdrop-blur-sm border-white/20 text-white hover:bg-white/20'
                    }`}
                  >
                    <Filter className="w-5 h-5" />
                    <span>Filters</span>
                    {hasActiveFilters && (
                      <span className="ml-1 px-2 py-0.5 bg-white/20 text-white text-xs rounded-full font-medium">
                        Active
                      </span>
                    )}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="bg-gradient-to-br from-gray-50 to-blue-50/30 dark:from-gray-900 dark:to-blue-950/30 min-h-screen">
        <div className="container mx-auto px-4 py-8 max-w-7xl">

          {/* Enhanced Job Results */}
          <div className="search-results-section bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 overflow-hidden">
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
                    Showing {((currentPage - 1) * itemsPerPage) + 1} to {Math.min(currentPage * itemsPerPage, totalJobs)} of {totalJobs.toLocaleString()} jobs
                  </div>
                  <div className="flex items-center gap-1 bg-gray-100 dark:bg-gray-700 p-1 rounded-xl">
                    <button
                      onClick={() => setViewMode('grid')}
                      className={`
                        p-2 rounded-lg transition-all duration-200 ${
                          viewMode === 'grid'
                            ? 'bg-blue-600 text-white shadow-lg'
                            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }
                      `}
                    >
                      <Grid className="w-5 h-5" />
                    </button>
                    <button
                      onClick={() => setViewMode('list')}
                      className={`
                        p-2 rounded-lg transition-all duration-200 ${
                          viewMode === 'list'
                            ? 'bg-blue-600 text-white shadow-lg'
                            : 'text-gray-600 dark:text-gray-400 hover:bg-gray-200 dark:hover:bg-gray-600'
                        }
                      `}
                    >
                      <List className="w-5 h-5" />
                    </button>
                  </div>
                </div>

                {/* Job Results Grid/List */}
                <div className={viewMode === 'grid' ? 'grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6' : 'space-y-4'}>
                  {jobs.map((job) => (
                    <JobCard key={job._id} job={job} viewMode={viewMode} />
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="mt-8 flex justify-center">
                    <div className="flex items-center gap-2">
                      <button
                        onClick={() => handlePageChange(currentPage - 1)}
                        disabled={currentPage === 1}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        Previous
                      </button>
                      
                      {getPageNumbers().map((pageNum) => (
                        <button
                          key={pageNum}
                          onClick={() => handlePageChange(pageNum)}
                          className={`px-4 py-2 rounded-lg transition-colors ${
                            currentPage === pageNum
                              ? 'bg-blue-600 text-white'
                              : 'border border-gray-300 dark:border-gray-600 hover:bg-gray-50 dark:hover:bg-gray-700'
                          }`}
                        >
                          {pageNum}
                        </button>
                      ))}
                      
                      <button
                        onClick={() => handlePageChange(currentPage + 1)}
                        disabled={currentPage === totalPages}
                        className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
                      >
                        Next
                      </button>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
}