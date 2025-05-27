import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, MapPin, Briefcase, Users, TrendingUp, Star, CheckCircle, ArrowRight, Globe, Clock, DollarSign, Bug, Filter, CalendarDays, Building } from 'lucide-react';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [locationCountry, setLocationCountry] = useState('');
  const [locationRegion, setLocationRegion] = useState('');
  const [jobType, setJobType] = useState('remote');
  const [datePosted, setDatePosted] = useState('any');
  const [isLoading, setIsLoading] = useState(false);

  // Sample data for filters - in a real app, these would come from an API or config
  const countries = [
    { value: 'us', label: 'United States' },
    { value: 'ca', label: 'Canada' },
    { value: 'gb', label: 'United Kingdom' },
    { value: 'de', label: 'Germany' },
    { value: 'any', label: 'Any Country' },
  ];

  const datePostedOptions = [
    { value: 'any', label: 'Any Date' },
    { value: '24h', label: 'Last 24 hours' },
    { value: '3d', label: 'Last 3 days' },
    { value: '7d', label: 'Last 7 days' },
    { value: '30d', label: 'Last 30 days' },
  ];

  const workTypeOptions = [
    { value: 'remote', label: 'Remote' },
    { value: 'hybrid', label: 'Hybrid' },
    { value: 'office', label: 'Office' },
  ];

  const featuredJobs = [
    {
      id: 1,
      title: 'Senior Frontend Developer',
      company: 'TechBuzz Ltd.',
      location: 'Remote (Global)',
      type: 'Full-time',
      salary: '$90k - $130k',
      tags: ['React', 'Next.js', 'Remote'],
      posted: '1 day ago',
      logo: '💻'
    },
    {
      id: 2,
      title: 'AI Product Manager',
      company: 'FutureAI Corp.',
      location: 'Remote (US)',
      type: 'Full-time',
      salary: '$120k - $170k',
      tags: ['AI', 'Product', 'Remote'],
      posted: '3 hours ago',
      logo: '🧠'
    },
    {
      id: 3,
      title: 'Lead DevOps Engineer',
      company: 'CloudHive Inc.',
      location: 'Hybrid (Berlin, DE)',
      type: 'Contract',
      salary: '$100k - $150k',
      tags: ['AWS', 'Kubernetes', 'CI/CD'],
      posted: '5 days ago',
      logo: '☁️'
    }
  ];
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate search
    // In a real app, construct query params based on all selected filters
    const queryParams = new URLSearchParams({
      q: searchQuery,
      country: locationCountry,
      region: locationRegion,
      type: jobType,
      posted: datePosted
    }).toString();
    
    setTimeout(() => {
      setIsLoading(false);
      navigate(`/jobs?${queryParams}`);
    }, 1000);
  };

  const handleGoogleLogin = () => {
    window.location.href = '/api/auth/google';
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <Link to="/" className="flex items-center space-x-3">
              <div className="w-10 h-10 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center shadow-md">
                <Bug className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-gray-900">Buzz2Remote</h1>
                <p className="text-xs text-gray-500">Your Hive for Remote Opportunities</p>
              </div>
            </Link>
            <nav className="hidden md:flex items-center space-x-8">
              <Link to="/jobs" className="text-gray-700 hover:text-orange-600 font-medium">Jobs</Link>
              <Link to="/companies" className="text-gray-700 hover:text-orange-600 font-medium">Companies</Link>
              <Link to="/status" className="text-gray-700 hover:text-orange-600 font-medium">Status</Link>
              <Link to="/pricing" className="text-gray-700 hover:text-orange-600 font-medium">Pricing</Link>
            </nav>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleGoogleLogin}
                className="flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium"
              >
                <svg className="w-5 h-5" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Sign in with Google</span>
              </button>
              <Link
                to="/register"
                className="bg-gradient-to-r from-orange-500 to-yellow-400 text-white px-4 py-2 rounded-lg hover:from-orange-600 hover:to-yellow-500 transition-colors font-medium text-sm shadow-md"
              >
                Get Started
              </Link>
            </div>
          </div>
        </div>
      </header>

      <section className="py-16 md:py-20 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto text-center">
          <h1 className="text-4xl md:text-6xl font-bold text-gray-900 mb-6 leading-tight">
            Find Your Next <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-500 to-yellow-500">Remote Buzz</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-600 mb-10 md:mb-12 max-w-3xl mx-auto">
            AI-powered job matching to connect you with global remote opportunities. Your dream job is just a search away.
          </p>

          <form onSubmit={handleSearch} className="max-w-5xl mx-auto mb-12 md:mb-16">
            <div className="bg-white rounded-xl shadow-2xl p-4 md:p-6 border border-gray-200">
              <div className="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4 items-end">
                {/* Job Title/Keywords */}
                <div className="md:col-span-4">
                  <label htmlFor="searchQuery" className="block text-sm font-medium text-gray-700 text-left mb-1">Keywords</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      id="searchQuery"
                      placeholder="Job title, skill, or company"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                    />
        </div>
      </div>

                {/* Country */}
                <div className="md:col-span-2">
                  <label htmlFor="locationCountry" className="block text-sm font-medium text-gray-700 text-left mb-1">Country</label>
                  <div className="relative">
                    <Globe className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select 
                      id="locationCountry"
                      value={locationCountry}
                      onChange={(e) => setLocationCountry(e.target.value)}
                      className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm bg-white"
                    >
                      {countries.map(country => (
                        <option key={country.value} value={country.value}>{country.label}</option>
                      ))}
                    </select>
          </div>
          </div>

                {/* Region/City */}
                <div className="md:col-span-2">
                  <label htmlFor="locationRegion" className="block text-sm font-medium text-gray-700 text-left mb-1">Region/City</label>
                  <div className="relative">
                    <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      id="locationRegion"
                      placeholder="e.g., California, Berlin"
                      value={locationRegion}
                      onChange={(e) => setLocationRegion(e.target.value)}
                      className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                      disabled={locationCountry === 'any'}
                    />
        </div>
      </div>

                {/* Date Posted */}
                <div className="md:col-span-2">
                   <label htmlFor="datePosted" className="block text-sm font-medium text-gray-700 text-left mb-1">Date Posted</label>
                  <div className="relative">
                    <CalendarDays className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <select 
                      id="datePosted"
                      value={datePosted}
                      onChange={(e) => setDatePosted(e.target.value)}
                      className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm bg-white"
                    >
                      {datePostedOptions.map(option => (
                        <option key={option.value} value={option.value}>{option.label}</option>
                      ))}
                    </select>
        </div>
      </div>

                {/* Search Button */}
                <div className="md:col-span-2">
                  <button
                    type="submit"
                    disabled={isLoading}
                    className="w-full bg-gradient-to-r from-orange-500 to-yellow-500 text-white py-2.5 px-4 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-all duration-200 font-semibold flex items-center justify-center space-x-2 text-sm shadow-md"
                  >
                    {isLoading ? (
                      <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                    ) : (
                      <>
                        <Search className="w-5 h-5" />
                        <span>Search</span>
                      </>
                    )}
                  </button>
          </div>
          </div>
              {/* Job Type Radio Buttons */}
              <div className="mt-4 flex flex-wrap justify-center items-center gap-3 md:gap-4">
                <span className="text-sm font-medium text-gray-700 mr-2">Type:</span>
                {workTypeOptions.map(option => (
                  <label key={option.value} className="flex items-center space-x-2 cursor-pointer p-2 rounded-lg hover:bg-orange-50 transition-colors">
                    <input 
                      type="radio" 
                      name="jobType" 
                      value={option.value} 
                      checked={jobType === option.value}
                      onChange={(e) => setJobType(e.target.value)}
                      className="form-radio h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300"
                    />
                    <span className="text-sm text-gray-700">{option.label}</span>
                  </label>
                ))}
          </div>
          </div>
          </form>
        </div>
      </section>
      
      {/* Stats Section (Removed, as per previous layout. Can be added back if needed) */}

      {/* Featured Jobs */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Hot Remote Jobs 🔥</h2>
            <p className="text-gray-600">Fresh opportunities from leading remote companies</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {featuredJobs.map((job) => (
              <div key={job.id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition-shadow cursor-pointer flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl shadow-sm">
                        {job.logo}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 text-lg">{job.title}</h3>
                        <p className="text-gray-600 text-sm">{job.company}</p>
                      </div>
                    </div>
                    <button className="p-1.5 rounded-full hover:bg-yellow-100 text-gray-400 hover:text-yellow-500 transition-colors">
                       <Star className="w-5 h-5" />
                    </button>
                      </div>
                      
                  <div className="space-y-2 mb-4">
                    <div className="flex items-center text-sm text-gray-600">
                      <MapPin className="w-4 h-4 mr-2 text-gray-400" />
                      {job.location}
                      </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <Building className="w-4 h-4 mr-2 text-gray-400" />
                      {job.type}
                    </div>
                    <div className="flex items-center text-sm text-gray-600">
                      <DollarSign className="w-4 h-4 mr-2 text-gray-400" />
                      {job.salary}
                    </div>
                  </div>

                  <div className="flex flex-wrap gap-2 mb-6">
                    {job.tags.map((tag, index) => (
                      <span key={index} className="px-3 py-1 bg-orange-50 text-orange-600 text-xs font-medium rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <span className="text-xs text-gray-500">Posted: {job.posted}</span>
                  <Link 
                    to={`/jobs/${job.id}`} 
                    className="text-orange-600 hover:text-orange-700 font-semibold text-sm flex items-center space-x-1 group"
                  >
                    <span>View Details</span>
                    <ArrowRight className="w-4 h-4 transition-transform group-hover:translate-x-1" />
                  </Link>
                </div>
              </div>
            ))}
          </div>

          <div className="text-center">
            <Link
              to="/jobs"
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-orange-500 to-yellow-500 text-white px-8 py-3 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-semibold shadow-lg"
            >
              <span>Browse All Jobs</span>
              <ArrowRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Features Section (Simplified) */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-gray-50">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Why Buzz2Remote?</h2>
            <p className="text-gray-600">Your smart way to a successful remote career.</p>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {[{
                icon: <Search className="w-8 h-8 text-orange-500" />,
                title: "AI-Powered Matching",
                description: "Our AI finds perfect job matches for you."
              },
              {
                icon: <CheckCircle className="w-8 h-8 text-green-500" />,
                title: "One-Click Apply",
                description: "Apply to jobs instantly with your saved profile."
              },
              {
                icon: <Globe className="w-8 h-8 text-blue-500" />,
                title: "Global Opportunities",
                description: "Access thousands of remote jobs worldwide."
              }
            ].map(feature => (
              <div key={feature.title} className="bg-white p-8 rounded-xl shadow-lg text-center">
                <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-6">
                  {feature.icon}
                </div>
                <h3 className="text-xl font-semibold text-gray-900 mb-3">{feature.title}</h3>
                <p className="text-gray-600 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 px-4 sm:px-6 lg:px-8 bg-gradient-to-r from-orange-500 to-yellow-500">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
            Ready to Buzz Your Way to a Remote Career?
          </h2>
          <p className="text-xl text-yellow-100 mb-10">
            Join Buzz2Remote today and let our AI find your next big opportunity.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              to="/register"
              className="bg-white text-orange-600 px-10 py-3 rounded-lg hover:bg-yellow-50 transition-colors font-semibold shadow-lg text-lg"
            >
              Create Free Account
            </Link>
             <button
                onClick={handleGoogleLogin}
                className="flex items-center justify-center space-x-2 bg-white bg-opacity-20 text-white px-10 py-3 rounded-lg hover:bg-opacity-30 transition-colors font-semibold border border-white border-opacity-40 text-lg shadow-lg"
              >
                <svg className="w-6 h-6" viewBox="0 0 24 24">
                  <path fill="#4285F4" d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z"/>
                  <path fill="#34A853" d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z"/>
                  <path fill="#FBBC05" d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z"/>
                  <path fill="#EA4335" d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z"/>
                </svg>
                <span>Sign up with Google</span>
              </button>
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-gray-900 text-white py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <Link to="/" className="flex items-center space-x-3 mb-4">
                <div className="w-8 h-8 bg-gradient-to-r from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center shadow-md">
                  <Bug className="w-5 h-5 text-white" />
                </div>
                <span className="text-xl font-bold">Buzz2Remote</span>
              </Link>
              <p className="text-gray-400 text-sm mb-4">
                Your hive for global remote opportunities, powered by AI.
              </p>
              <div className="flex space-x-4">
                <a href="#" className="text-gray-400 hover:text-white"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M14.016 0H9.984L0 9.984V14.016L9.984 24H14.016L24 14.016V9.984L14.016 0ZM12 19.25L4.75 12L12 4.75L19.25 12L12 19.25Z"/></svg></a>
                <a href="#" className="text-gray-400 hover:text-white"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M19 0h-14c-2.761 0-5 2.239-5 5v14c0 2.761 2.239 5 5 5h14c2.762 0 5-2.239 5-5v-14c0-2.761-2.238-5-5-5zm-11 19h-3v-11h3v11zm-1.5-12.268c-.966 0-1.75-.79-1.75-1.764s.784-1.764 1.75-1.764 1.75.79 1.75 1.764-.783 1.764-1.75 1.764zm13.5 12.268h-3v-5.604c0-3.368-4-3.113-4 0v5.604h-3v-11h3v1.765c1.396-2.586 7-2.777 7 2.476v6.759z"/></svg></a>
                <a href="#" className="text-gray-400 hover:text-white"><svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg></a>
              </div>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">For Job Seekers</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/jobs" className="hover:text-white">Browse Jobs</Link></li>
                <li><Link to="/companies" className="hover:text-white">Companies</Link></li>
                <li><Link to="/profile" className="hover:text-white">My Profile</Link></li>
                <li><Link to="/applications" className="hover:text-white">My Applications</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">For Employers</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><a href="#" className="hover:text-white">Post a Job</a></li>
                <li><a href="#" className="hover:text-white">Employer Pricing</a></li>
                <li><a href="#" className="hover:text-white">Employer Dashboard</a></li>
                <li><a href="#" className="hover:text-white">Contact Sales</a></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Resources</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/help" className="hover:text-white">Help Center</Link></li>
                <li><Link to="/status" className="hover:text-white">System Status</Link></li>
                <li><Link to="/terms" className="hover:text-white">Terms & Conditions</Link></li>
                <li><Link to="/privacy" className="hover:text-white">Privacy Policy</Link></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
            <p>&copy; {new Date().getFullYear()} Buzz2Remote. All rights reserved. AI Powered Remote Job Matching.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home; 