import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { HomeJobService } from '../services/AllServices';
import SearchIcon from '@mui/icons-material/Search';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import RadioButtonUncheckedIcon from '@mui/icons-material/RadioButtonUnchecked';
import PublicIcon from '@mui/icons-material/Public';
import WhatshotIcon from '@mui/icons-material/Whatshot';
import TelegramIcon from '@mui/icons-material/Telegram';
import WorkIcon from '@mui/icons-material/Work';
import LocationOnIcon from '@mui/icons-material/LocationOn';
import BusinessIcon from '@mui/icons-material/Business';
import AccessTimeIcon from '@mui/icons-material/AccessTime';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchInput, setSearchInput] = useState('');
  const [excludeInput, setExcludeInput] = useState('');
  const [locationInput, setLocationInput] = useState('');
  const [selectedJobType, setSelectedJobType] = useState('remote');
  const [featuredJobs, setFeaturedJobs] = useState<any[]>([]);
  
  const { data: stats } = useQuery(['jobStats'], () => HomeJobService.getJobStats());

  const { data: jobs } = useQuery(['featuredJobs'], () => HomeJobService.getFeaturedJobs());

  useEffect(() => {
    if (jobs) {
      setFeaturedJobs(jobs.slice(0, 6)); // Show only 6 featured jobs
    }
  }, [jobs]);
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    navigate(`/jobs?search=${encodeURIComponent(searchInput)}&exclude=${encodeURIComponent(excludeInput)}&location=${encodeURIComponent(locationInput)}&type=${selectedJobType}`);
  };

  return (
    <div className="min-h-screen bg-white">
      {/* Hero Section */}
      <div className="bg-gradient-to-r from-blue-900 to-blue-700 text-white">
        <div className="max-w-7xl mx-auto px-4 py-16 md:py-24">
          <div className="text-center mb-8">
            <h1 className="text-4xl md:text-5xl font-bold mb-4">Find Your Perfect Remote Job</h1>
            <p className="text-xl md:text-2xl opacity-90">Discover remote opportunities from around the world that match your skills</p>
          </div>
          
          {/* Search Form */}
          <div className="bg-white rounded-lg shadow-lg p-6 max-w-4xl mx-auto">
            <form onSubmit={handleSearch}>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Position, title, keywords
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. developer, react, python"
                    value={searchInput}
                    onChange={(e) => setSearchInput(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Exclude keywords
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. senior, 5+ years"
                    value={excludeInput}
                    onChange={(e) => setExcludeInput(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Location
                  </label>
                  <input
                    type="text"
                    placeholder="e.g. United States or Europe"
                    value={locationInput}
                    onChange={(e) => setLocationInput(e.target.value)}
                    className="w-full p-3 border border-gray-300 rounded-md focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>
              
              <div className="flex flex-wrap gap-2 mb-4">
                <button
                  type="button"
                  className={`flex items-center px-4 py-2 rounded-full border ${
                    selectedJobType === 'remote' 
                      ? 'bg-blue-100 border-blue-300 text-blue-700' 
                      : 'bg-white border-gray-300'
                  }`}
                  onClick={() => setSelectedJobType('remote')}
                >
                  {selectedJobType === 'remote' ? (
                    <CheckCircleIcon className="h-5 w-5 mr-1 text-blue-500" />
                  ) : (
                    <RadioButtonUncheckedIcon className="h-5 w-5 mr-1 text-gray-400" />
                  )}
                  Remote
                </button>
                <button
                  type="button"
                  className={`flex items-center px-4 py-2 rounded-full border ${
                    selectedJobType === 'hybrid' 
                      ? 'bg-blue-100 border-blue-300 text-blue-700' 
                      : 'bg-white border-gray-300'
                  }`}
                  onClick={() => setSelectedJobType('hybrid')}
                >
                  {selectedJobType === 'hybrid' ? (
                    <CheckCircleIcon className="h-5 w-5 mr-1 text-blue-500" />
                  ) : (
                    <RadioButtonUncheckedIcon className="h-5 w-5 mr-1 text-gray-400" />
                  )}
                  Hybrid
                </button>
                <button
                  type="button"
                  className={`flex items-center px-4 py-2 rounded-full border ${
                    selectedJobType === '24hours' 
                      ? 'bg-blue-100 border-blue-300 text-blue-700' 
                      : 'bg-white border-gray-300'
                  }`}
                  onClick={() => setSelectedJobType('24hours')}
                >
                  {selectedJobType === '24hours' ? (
                    <CheckCircleIcon className="h-5 w-5 mr-1 text-blue-500" />
                  ) : (
                    <RadioButtonUncheckedIcon className="h-5 w-5 mr-1 text-gray-400" />
                  )}
                  Last 24 Hours
                </button>
                <button
                  type="button"
                  className={`flex items-center px-4 py-2 rounded-full border ${
                    selectedJobType === '7days' 
                      ? 'bg-blue-100 border-blue-300 text-blue-700' 
                      : 'bg-white border-gray-300'
                  }`}
                  onClick={() => setSelectedJobType('7days')}
                >
                  {selectedJobType === '7days' ? (
                    <CheckCircleIcon className="h-5 w-5 mr-1 text-blue-500" />
                  ) : (
                    <RadioButtonUncheckedIcon className="h-5 w-5 mr-1 text-gray-400" />
                  )}
                  Last 7 Days
                </button>
              </div>
              
              <button
                type="submit"
                className="w-full bg-blue-600 text-white py-3 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 font-medium text-lg transition-all duration-200"
              >
                <SearchIcon className="h-5 w-5 mr-2" />
                Find Remote Jobs
              </button>
            </form>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Stats Section */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-16">
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 text-center transform hover:scale-105 transition-all duration-200">
            <PublicIcon className="h-12 w-12 text-blue-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-800">Total Jobs</h3>
            <p className="text-blue-600 font-bold text-xl">{stats?.totalJobs || '700,374'}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 text-center transform hover:scale-105 transition-all duration-200">
            <TelegramIcon className="h-12 w-12 text-blue-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-800">Remote Jobs</h3>
            <p className="text-blue-600 font-bold text-xl">{stats?.remoteJobs || '35,333'}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 text-center transform hover:scale-105 transition-all duration-200">
            <WhatshotIcon className="h-12 w-12 text-orange-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-800">Last 24 Hours</h3>
            <p className="text-blue-600 font-bold text-xl">{stats?.jobsLast24h || '39,475'}</p>
          </div>
          
          <div className="bg-white p-6 rounded-lg shadow-md border border-gray-100 text-center transform hover:scale-105 transition-all duration-200">
            <PublicIcon className="h-12 w-12 text-purple-500 mx-auto mb-3" />
            <h3 className="text-lg font-semibold text-gray-800">Companies</h3>
            <p className="text-blue-600 font-bold text-xl">{stats?.totalCompanies || '6,893'}</p>
          </div>
        </div>

        {/* Featured Jobs Section */}
        <div className="mb-16">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-2xl font-bold text-gray-900">Featured Remote Jobs</h2>
            <Link to="/jobs" className="text-blue-600 hover:text-blue-800 font-medium">
              View all jobs →
            </Link>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredJobs && featuredJobs.length > 0 ? (
              featuredJobs.map((job, index) => (
                <div key={job._id || index} className="bg-white rounded-lg shadow-md overflow-hidden border border-gray-200 hover:shadow-lg transition-all duration-200">
                  <div className="p-5">
                    <div className="flex items-start justify-between">
                      <div className="w-12 h-12 rounded-md overflow-hidden bg-gray-100 mr-4">
                        <img src={job.companyLogo || 'https://via.placeholder.com/50?text=🏢'} alt={job.companyName} className="w-full h-full object-cover" />
                      </div>
                      <div className="flex-1">
                        <h3 className="font-semibold text-lg text-gray-900 mb-1">{job.title}</h3>
                        <p className="text-gray-600 text-sm">{job.companyName}</p>
                      </div>
                    </div>
                    
                    <div className="mt-4 space-y-2">
                      <div className="flex items-center text-sm text-gray-500">
                        <LocationOnIcon className="h-4 w-4 mr-1" />
                        <span>{job.location || 'Remote'}</span>
                      </div>
                      
                      <div className="flex items-center text-sm text-gray-500">
                        <BusinessIcon className="h-4 w-4 mr-1" />
                        <span>{job.type || 'Full-time'}</span>
                      </div>
                      
                      <div className="flex items-center text-sm text-gray-500">
                        <AccessTimeIcon className="h-4 w-4 mr-1" />
                        <span>{job.postedAt ? new Date(job.postedAt).toLocaleDateString() : 'Recently posted'}</span>
                      </div>
                    </div>
                    
                    <div className="mt-4">
                      <Link
                        to={`/jobs/${job._id}`}
                        className="block w-full text-center py-2 px-4 bg-blue-50 text-blue-700 font-medium rounded-md hover:bg-blue-100 transition-colors"
                      >
                        View Details
                      </Link>
                    </div>
                  </div>
                </div>
              ))
            ) : (
              <div className="col-span-3 py-8 text-center">
                <p className="text-gray-500">Loading featured jobs...</p>
              </div>
            )}
          </div>
        </div>

        {/* Categories Section */}
        <div className="mb-16">
          <h2 className="text-2xl font-bold mb-6 text-gray-900">Popular Job Categories</h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              'Software Engineering',
              'Design',
              'Marketing',
              'Product Management',
              'Data Science',
              'DevOps',
              'Customer Support',
              'Sales',
              'HR & Recruiting',
              'Finance',
              'Content Writing',
              'Project Management'
            ].map(category => (
              <Link 
                key={category} 
                to={`/jobs?category=${encodeURIComponent(category)}`}
                className="bg-gradient-to-br from-gray-50 to-gray-100 hover:from-blue-50 hover:to-blue-100 p-4 rounded-lg text-center transition-all duration-200 border border-gray-200 shadow-sm"
              >
                <WorkIcon className="h-6 w-6 mx-auto mb-2 text-blue-500" />
                <h3 className="font-medium text-gray-800">{category}</h3>
              </Link>
            ))}
          </div>
        </div>
        
        {/* Call to Action */}
        <div className="bg-gradient-to-r from-blue-700 to-blue-900 text-white rounded-xl p-8 mb-16">
          <div className="text-center">
            <h2 className="text-3xl font-bold mb-4">Ready to find your perfect remote job?</h2>
            <p className="text-xl opacity-90 mb-6">Thousands of remote jobs are updated daily. Create your profile and get matched.</p>
            <Link
              to="/profile"
              className="inline-block bg-white text-blue-700 font-bold py-3 px-8 rounded-lg shadow-lg hover:bg-blue-50 transition-all duration-200"
            >
              Create Your Profile
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-lg font-bold mb-4">My Remote Jobs</h3>
              <p className="text-gray-400 mb-4">Find the best remote jobs from around the world.</p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white">
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fillRule="evenodd" d="M22 12c0-5.523-4.477-10-10-10S2 6.477 2 12c0 4.991 3.657 9.128 8.438 9.878v-6.987h-2.54V12h2.54V9.797c0-2.506 1.492-3.89 3.777-3.89 1.094 0 2.238.195 2.238.195v2.46h-1.26c-1.243 0-1.63.771-1.63 1.562V12h2.773l-.443 2.89h-2.33v6.988C18.343 21.128 22 16.991 22 12z" clipRule="evenodd" />
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-white">
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M8.29 20.251c7.547 0 11.675-6.253 11.675-11.675 0-.178 0-.355-.012-.53A8.348 8.348 0 0022 5.92a8.19 8.19 0 01-2.357.646 4.118 4.118 0 001.804-2.27 8.224 8.224 0 01-2.605.996 4.107 4.107 0 00-6.993 3.743 11.65 11.65 0 01-8.457-4.287 4.106 4.106 0 001.27 5.477A4.072 4.072 0 012.8 9.713v.052a4.105 4.105 0 003.292 4.022 4.095 4.095 0 01-1.853.07 4.108 4.108 0 003.834 2.85A8.233 8.233 0 012 18.407a11.616 11.616 0 006.29 1.84" />
                  </svg>
                </a>
                <a href="#" className="text-gray-400 hover:text-white">
                  <svg className="h-6 w-6" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path fillRule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clipRule="evenodd" />
                  </svg>
                </a>
              </div>
            </div>
            
            <div>
              <h3 className="text-lg font-bold mb-4">For Job Seekers</h3>
              <ul className="space-y-2">
                <li><Link to="/jobs" className="text-gray-400 hover:text-white">Browse Jobs</Link></li>
                <li><Link to="/companies" className="text-gray-400 hover:text-white">Companies</Link></li>
                <li><Link to="/profile" className="text-gray-400 hover:text-white">Create Profile</Link></li>
                <li><Link to="/saved-jobs" className="text-gray-400 hover:text-white">Saved Jobs</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-bold mb-4">For Employers</h3>
              <ul className="space-y-2">
                <li><Link to="/post-job" className="text-gray-400 hover:text-white">Post a Job</Link></li>
                <li><Link to="/pricing" className="text-gray-400 hover:text-white">Pricing</Link></li>
                <li><Link to="/dashboard" className="text-gray-400 hover:text-white">Employer Dashboard</Link></li>
                <li><Link to="/talent-search" className="text-gray-400 hover:text-white">Search Resumes</Link></li>
              </ul>
            </div>
            
            <div>
              <h3 className="text-lg font-bold mb-4">About</h3>
              <ul className="space-y-2">
                <li><Link to="/about" className="text-gray-400 hover:text-white">About Us</Link></li>
                <li><Link to="/contact" className="text-gray-400 hover:text-white">Contact</Link></li>
                <li><Link to="/privacy-policy" className="text-gray-400 hover:text-white">Privacy Policy</Link></li>
                <li><Link to="/terms" className="text-gray-400 hover:text-white">Terms of Service</Link></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-800 mt-8 pt-8 text-center">
            <p className="text-gray-400">© 2023 My Remote Jobs. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home; 