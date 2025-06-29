import React, { useState, useEffect } from 'react';
import { Heart, ExternalLink, MapPin, DollarSign, Calendar, Briefcase } from 'lucide-react';
import Header from '../components/Header';
import { useAuth } from '../contexts/AuthContext';

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

const Favorites: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [favoriteJobs, setFavoriteJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Mock favorite jobs for demo
    setTimeout(() => {
      setFavoriteJobs([
        {
          _id: 'fav-1',
          title: 'Senior React Developer',
          company: 'TechCorp Inc.',
          location: 'Remote',
          salary: '$80,000 - $120,000',
          job_type: 'Full-time',
          work_type: 'Remote',
          posted_date: '2024-06-28',
          required_skills: ['React', 'TypeScript', 'Node.js'],
          description: 'We are looking for a Senior React Developer to join our team...',
          url: 'https://example.com/job/1'
        },
        {
          _id: 'fav-2',
          title: 'Frontend Engineer',
          company: 'StartupXYZ',
          location: 'San Francisco, CA',
          salary: '$90,000 - $130,000',
          job_type: 'Full-time',
          work_type: 'Hybrid',
          posted_date: '2024-06-27',
          required_skills: ['Vue.js', 'JavaScript', 'CSS'],
          description: 'Join our dynamic team as a Frontend Engineer...',
          url: 'https://example.com/job/2'
        }
      ]);
      setLoading(false);
    }, 1000);
  }, []);

  const removeFavorite = (jobId: string) => {
    setFavoriteJobs(prev => prev.filter(job => job._id !== jobId));
  };

  if (!isAuthenticated) {
    return (
      <div className="min-h-screen" style={{ backgroundColor: '#f5f5f5' }}>
        <Header />
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="max-w-md mx-auto">
            <Heart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Please Login</h1>
            <p className="text-gray-600">You need to be logged in to view your favorite jobs.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen" style={{ backgroundColor: '#f5f5f5' }}>
      <Header />
      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 flex items-center gap-3">
            <Heart className="w-8 h-8 text-red-500" />
            My Favorite Jobs
          </h1>
          <p className="text-gray-600 mt-2">
            {favoriteJobs.length} job{favoriteJobs.length !== 1 ? 's' : ''} in your favorites
          </p>
        </div>

        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Loading your favorite jobs...</p>
          </div>
        ) : favoriteJobs.length > 0 ? (
          <div className="space-y-4">
            {favoriteJobs.map((job) => (
              <div key={job._id} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-start gap-4">
                      {/* Company Logo */}
                      <div className="w-12 h-12 rounded-lg bg-gray-100 flex items-center justify-center flex-shrink-0">
                        <div className="w-12 h-12 rounded-lg bg-gray-200 flex items-center justify-center text-gray-500 text-sm font-semibold">
                          {typeof job.company === 'object' ? job.company.name?.charAt(0) : job.company?.charAt(0)}
                        </div>
                      </div>
                      
                      <div className="flex-1">
                        <h2 className="text-lg font-semibold text-gray-900 mb-1">
                          {job.url ? (
                            <a 
                              href={job.url} 
                              target="_blank" 
                              rel="noopener noreferrer"
                              className="hover:text-blue-600 transition-colors"
                            >
                              {job.title}
                            </a>
                          ) : (
                            job.title
                          )}
                        </h2>
                        <p className="text-gray-600 mb-3">{typeof job.company === 'object' ? job.company.name : job.company}</p>
                        
                        {/* Job Details Tags */}
                        <div className="flex flex-wrap gap-2 mb-3">
                          {job.location && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded-full">
                              <MapPin className="w-3 h-3" />
                              {job.location}
                            </span>
                          )}
                          {job.job_type && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-green-50 text-green-700 text-xs rounded-full">
                              <Briefcase className="w-3 h-3" />
                              {job.job_type}
                            </span>
                          )}
                          {job.work_type && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-purple-50 text-purple-700 text-xs rounded-full">
                              🏠 {job.work_type}
                            </span>
                          )}
                          {job.salary && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-yellow-50 text-yellow-700 text-xs rounded-full">
                              <DollarSign className="w-3 h-3" />
                              {job.salary}
                            </span>
                          )}
                          {job.posted_date && (
                            <span className="inline-flex items-center gap-1 px-2 py-1 bg-orange-50 text-orange-700 text-xs rounded-full">
                              <Calendar className="w-3 h-3" />
                              {new Date(job.posted_date).toLocaleDateString()}
                            </span>
                          )}
                        </div>
                        
                        {job.required_skills && job.required_skills.length > 0 && (
                          <div className="flex flex-wrap gap-2 mb-3">
                            {job.required_skills.slice(0, 6).map((skill, index) => (
                              <span key={index} className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded border">
                                {skill}
                              </span>
                            ))}
                            {job.required_skills.length > 6 && (
                              <span className="px-2 py-1 bg-gray-100 text-gray-500 text-xs rounded border">
                                +{job.required_skills.length - 6} more
                              </span>
                            )}
                          </div>
                        )}
                        
                        {job.description && (
                          <p className="text-gray-600 text-sm line-clamp-2 mb-3">
                            {job.description.substring(0, 200)}...
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                  
                  {/* Action Buttons */}
                  <div className="flex items-center gap-2 ml-4">
                    <button 
                      onClick={() => removeFavorite(job._id || '')} 
                      title="Remove from Favorites" 
                      className="p-2 text-red-500 bg-red-50 hover:bg-red-100 rounded-full transition-colors"
                    >
                      <Heart className="w-5 h-5 fill-current" />
                    </button>
                    
                    {job.url && (
                      <a 
                        href={job.url} 
                        target="_blank" 
                        rel="noopener noreferrer" 
                        title="View Original Post" 
                        className="p-2 text-gray-400 hover:text-blue-500 hover:bg-blue-50 rounded-full transition-colors"
                      >
                        <ExternalLink className="w-5 h-5" />
                      </a>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-12">
            <Heart className="w-16 h-16 text-gray-400 mx-auto mb-4" />
            <h2 className="text-xl font-semibold text-gray-900 mb-2">No Favorite Jobs Yet</h2>
            <p className="text-gray-600 mb-6">Start adding jobs to your favorites to see them here.</p>
            <a 
              href="/jobs/search" 
              className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              Browse Jobs
            </a>
          </div>
        )}
      </div>
    </div>
  );
};

export default Favorites; 