import React, { useState, useEffect } from 'react';
import { Heart, ExternalLink, MapPin, DollarSign, Calendar, Briefcase } from 'lucide-react';
import Layout from '../components/Layout';
import { useAuth } from '../contexts/AuthContext';
import { jobService } from '../services/jobService';

interface Job {
  id?: string;
  _id?: string;
  title: string;
  company: string | { name: string; logo?: string };
  company_logo?: string;
  location?: string;
  salary?: string;
  salary_range?: string;
  description?: string;
  job_type?: string;
  work_type?: string;
  posted_date?: string;
  isRemote?: boolean;
  required_skills?: string[];
  url?: string;
  apply_url?: string;
  category?: string;
  seniority_level?: string;
}

const Favorites: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const [favoriteJobs, setFavoriteJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (isAuthenticated && user) {
      loadFavoriteJobs();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, user]);

  const loadFavoriteJobs = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get saved job IDs from localStorage
      const savedJobIds = JSON.parse(localStorage.getItem('savedJobs') || '[]');
      
      if (savedJobIds.length === 0) {
        setFavoriteJobs([]);
        return;
      }

      // Fetch job details for saved IDs
      const jobPromises = savedJobIds.map(async (jobId: string) => {
        try {
          return await jobService.getJobById(jobId);
        } catch (error) {
          console.error(`Failed to fetch job ${jobId}:`, error);
          return null;
        }
      });

      const jobs = (await Promise.all(jobPromises)).filter((job): job is Job => job !== null);
      setFavoriteJobs(jobs);
    } catch (error) {
      console.error('Error loading favorite jobs:', error);
      setError('Failed to load favorite jobs');
    } finally {
      setLoading(false);
    }
  };

  const removeFavorite = async (jobId: string) => {
    try {
      // Remove from localStorage
      const savedJobIds = JSON.parse(localStorage.getItem('savedJobs') || '[]');
      const updatedIds = savedJobIds.filter((id: string) => id !== jobId);
      localStorage.setItem('savedJobs', JSON.stringify(updatedIds));
      
      // Remove from state
      setFavoriteJobs(prev => prev.filter(job => (job._id || job.id) !== jobId));
      
      // Remove from backend if user is authenticated
      if (isAuthenticated && user) {
        await jobService.unsaveJob(user.id!, jobId);
      }
    } catch (error) {
      console.error('Error removing favorite:', error);
    }
  };

  const getJobUrl = (job: Job) => {
    return job.apply_url || job.url || `https://www.google.com/search?q=${encodeURIComponent(job.title + ' ' + (typeof job.company === 'string' ? job.company : job.company?.name || ''))}`;
  };

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="max-w-md mx-auto">
            <Heart className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Please Login</h1>
            <p className="text-gray-600 dark:text-gray-300">You need to be logged in to view your favorite jobs.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <Heart className="w-8 h-8 text-red-500" />
            My Favorite Jobs
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            {favoriteJobs.length} job{favoriteJobs.length !== 1 ? 's' : ''} in your favorites
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600 dark:text-gray-300">Loading your favorite jobs...</p>
          </div>
        ) : error ? (
          <div className="text-center py-12">
            <div className="text-red-500 mb-4">⚠️</div>
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">Error Loading Favorites</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">{error}</p>
            <button 
              onClick={loadFavoriteJobs}
              className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Try Again
            </button>
          </div>
        ) : favoriteJobs.length > 0 ? (
          <div className="space-y-4">
            {favoriteJobs.map((job) => (
              <div key={job._id || job.id} className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start gap-4">
                      {/* Company Logo */}
                      <div className="w-12 h-12 rounded-lg bg-gray-100 dark:bg-slate-700 flex items-center justify-center flex-shrink-0">
                        <div className="w-12 h-12 rounded-lg bg-gray-200 dark:bg-slate-600 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm font-semibold">
                          {typeof job.company === 'object' ? job.company.name?.charAt(0) : job.company?.charAt(0)}
                        </div>
                      </div>
                      
                      <div className="flex-1">
                        <h2 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                          <a 
                            href={getJobUrl(job)} 
                            target="_blank" 
                            rel="noopener noreferrer"
                            className="hover:text-blue-600 dark:hover:text-blue-400 transition-colors"
                          >
                            {job.title}
                          </a>
                        </h2>
                        <p className="text-gray-600 dark:text-gray-300 mb-3">
                          {typeof job.company === 'object' ? job.company.name : job.company}
                        </p>
                        
                        {/* Job Details Tags */}
                        <div className="flex flex-wrap gap-2 mb-3">
                          {job.location && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 dark:bg-blue-900/30 text-blue-700 dark:text-blue-300 text-xs rounded-full">
                              <MapPin className="w-3 h-3" />
                              {job.location}
                            </span>
                          )}
                          {job.job_type && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 dark:bg-green-900/30 text-green-700 dark:text-green-300 text-xs rounded-full">
                              <Briefcase className="w-3 h-3" />
                              {job.job_type}
                            </span>
                          )}
                          {job.work_type && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-full">
                              🏠 {job.work_type}
                            </span>
                          )}
                          {(job.salary || job.salary_range) && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-50 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-300 text-xs rounded-full">
                              <DollarSign className="w-3 h-3" />
                              {job.salary || job.salary_range}
                            </span>
                          )}
                          {job.posted_date && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-50 dark:bg-orange-900/30 text-orange-700 dark:text-orange-300 text-xs rounded-full">
                              <Calendar className="w-3 h-3" />
                              {new Date(job.posted_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                        
                        {job.required_skills && job.required_skills.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {job.required_skills.slice(0, 6).map((skill, index) => (
                              <span key={index} className="px-2 py-1 bg-gray-100 dark:bg-slate-700 text-gray-700 dark:text-gray-300 text-xs rounded border dark:border-slate-600">
                                {skill}
                              </span>
                            ))}
                            {job.required_skills.length > 6 && (
                              <span className="px-2 py-1 bg-gray-100 dark:bg-slate-700 text-gray-500 dark:text-gray-400 text-xs rounded border dark:border-slate-600">
                                +{job.required_skills.length - 6} more
                              </span>
                            )}
                          </div>
                        )}
                        
                        {job.description && (
                          <p className="text-gray-600 dark:text-gray-300 text-sm line-clamp-2 mb-3">
                            {job.description.substring(0, 200)}...
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex items-center gap-2 ml-4">
                    <button 
                      onClick={() => removeFavorite(job._id || job.id || '')} 
                      title="Remove from Favorites" 
                      className="p-2 text-red-500 bg-red-50 dark:bg-red-900/30 hover:bg-red-100 dark:hover:bg-red-900/50 rounded-full transition-colors"
                    >
                      <Heart className="w-5 h-5 fill-current" />
                    </button>
                    
                    <a 
                      href={getJobUrl(job)} 
                      target="_blank" 
                      rel="noopener noreferrer" 
                      title="Apply to Job" 
                      className="p-2 text-gray-400 dark:text-gray-500 hover:text-blue-500 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-full transition-colors"
                    >
                      <ExternalLink className="w-5 h-5" />
                    </a>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Heart className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">No Favorite Jobs Yet</h2>
            <p className="text-gray-600 dark:text-gray-300 mb-6">Start adding jobs to your favorites to see them here.</p>
            <a 
              href="/jobs/search" 
              className="inline-flex items-center px-4 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md transition-colors"
            >
              Browse Jobs
            </a>
          </div>
        )}
      </div>
    </Layout>
  );
};

export default Favorites; 