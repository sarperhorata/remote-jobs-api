import React, { useState, useEffect } from 'react';
import { Bookmark, Search, Filter, MapPin, Calendar, Building, DollarSign, ExternalLink, Trash2 } from 'lucide-react';
import Header from '../components/Header';
import { useAuth } from '../contexts/AuthContext';

interface SavedJob {
  id: string;
  title: string;
  company: string;
  location: string;
  salary?: string;
  postedDate: string;
  description: string;
  url: string;
  savedAt: string;
}

const SavedJobs: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [savedJobs, setSavedJobs] = useState<SavedJob[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<SavedJob[]>([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedFilter, setSelectedFilter] = useState('all');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadSavedJobs();
  }, []);

  useEffect(() => {
    filterJobs();
  }, [savedJobs, searchTerm, selectedFilter]);

  const loadSavedJobs = () => {
    try {
      const saved = localStorage.getItem('savedJobs');
      if (saved) {
        const jobs = JSON.parse(saved);
        setSavedJobs(jobs);
      }
    } catch (error) {
      console.error('Error loading saved jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const filterJobs = () => {
    let filtered = savedJobs;

    // Apply search filter
    if (searchTerm) {
      filtered = filtered.filter(job =>
        job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
        job.location.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    // Apply category filter
    if (selectedFilter !== 'all') {
      // You can add more specific filtering logic here
      // For now, we'll just filter by company type or job category
    }

    setFilteredJobs(filtered);
  };

  const removeSavedJob = (jobId: string) => {
    const updatedJobs = savedJobs.filter(job => job.id !== jobId);
    setSavedJobs(updatedJobs);
    localStorage.setItem('savedJobs', JSON.stringify(updatedJobs));
  };

  const clearAllSavedJobs = () => {
    setSavedJobs([]);
    localStorage.removeItem('savedJobs');
  };

  const openJobUrl = (url: string) => {
    window.open(url, '_blank');
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen bg-gray-50">
        <Header />
        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Please log in to view saved jobs</h1>
            <p className="text-gray-600">You need to be authenticated to access this page.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      
      <div className="max-w-7xl mx-auto px-4 py-8">
        <div className="mb-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Saved Jobs</h1>
              <p className="text-gray-600">
                {savedJobs.length} job{savedJobs.length !== 1 ? 's' : ''} saved
              </p>
            </div>
            {savedJobs.length > 0 && (
              <button
                onClick={clearAllSavedJobs}
                className="text-red-600 hover:text-red-700 text-sm font-medium"
              >
                Clear All
              </button>
            )}
          </div>
        </div>

        {savedJobs.length > 0 && (
          <div className="mb-6">
            {/* Search and Filter Bar */}
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-4 mb-6">
              <div className="flex flex-col md:flex-row gap-4">
                <div className="flex-1">
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      placeholder="Search saved jobs..."
                      value={searchTerm}
                      onChange={(e) => setSearchTerm(e.target.value)}
                      className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
                <div className="flex gap-2">
                  <select
                    value={selectedFilter}
                    onChange={(e) => setSelectedFilter(e.target.value)}
                    className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="all">All Jobs</option>
                    <option value="remote">Remote</option>
                    <option value="onsite">On-site</option>
                    <option value="hybrid">Hybrid</option>
                  </select>
                </div>
              </div>
            </div>

            {/* Results Count */}
            <div className="text-sm text-gray-600 mb-4">
              Showing {filteredJobs.length} of {savedJobs.length} saved job{filteredJobs.length !== 1 ? 's' : ''}
            </div>
          </div>
        )}

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
            <p className="text-gray-600 mt-4">Loading saved jobs...</p>
          </div>
        ) : savedJobs.length === 0 ? (
          <div className="text-center py-12">
            <Bookmark className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">No saved jobs yet</h3>
            <p className="text-gray-600 mb-6">
              Start browsing jobs and save the ones you're interested in to view them here later.
            </p>
            <a
              href="/"
              className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              Browse Jobs
            </a>
          </div>
        ) : filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <Search className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h3 className="text-xl font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600">
              Try adjusting your search terms or filters to find what you're looking for.
            </p>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredJobs.map((job) => (
              <div
                key={job.id}
                className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-1">
                          {job.title}
                        </h3>
                        <div className="flex items-center text-gray-600 mb-2">
                          <Building className="w-4 h-4 mr-1" />
                          <span className="text-sm">{job.company}</span>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={() => openJobUrl(job.url)}
                          className="text-blue-600 hover:text-blue-700 p-1"
                          title="View job"
                        >
                          <ExternalLink className="w-4 h-4" />
                        </button>
                        <button
                          onClick={() => removeSavedJob(job.id)}
                          className="text-red-600 hover:text-red-700 p-1"
                          title="Remove from saved"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>

                    <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-3">
                      <div className="flex items-center">
                        <MapPin className="w-4 h-4 mr-1" />
                        <span>{job.location}</span>
                      </div>
                      {job.salary && (
                        <div className="flex items-center">
                          <DollarSign className="w-4 h-4 mr-1" />
                          <span>{job.salary}</span>
                        </div>
                      )}
                      <div className="flex items-center">
                        <Calendar className="w-4 h-4 mr-1" />
                        <span>Posted {job.postedDate}</span>
                      </div>
                    </div>

                    <p className="text-gray-700 text-sm line-clamp-2 mb-3">
                      {job.description}
                    </p>

                    <div className="flex items-center justify-between">
                      <span className="text-xs text-gray-500">
                        Saved on {new Date(job.savedAt).toLocaleDateString()}
                      </span>
                      <button
                        onClick={() => openJobUrl(job.url)}
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white text-sm rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        View Job
                        <ExternalLink className="w-4 h-4 ml-1" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SavedJobs; 