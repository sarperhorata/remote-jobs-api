import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Search, MapPin, Building, Globe, ArrowRight, Star, CheckCircle, Bug, DollarSign } from 'lucide-react';
import AuthModal from '../components/AuthModal';
import Onboarding from '../components/Onboarding';
import { JobService } from '../services/jobService';
import { Job } from '../types/job';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchQuery, setSearchQuery] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState<'login' | 'register'>('login');
  const [featuredJobs, setFeaturedJobs] = useState<Job[]>([]);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);

  // Check if user needs onboarding
  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('onboardingCompleted');
    const userToken = localStorage.getItem('userToken'); // Assuming you store auth token
    
    // Show onboarding for new users who just registered
    if (userToken && !onboardingCompleted) {
      setIsOnboardingOpen(true);
    }
  }, []);

  // Fetch featured jobs on component mount
  useEffect(() => {
    const loadFeaturedJobs = async () => {
      try {
        const jobs = await JobService.getFeaturedJobs();
        setFeaturedJobs(jobs.slice(0, 3)); // Take first 3 jobs
      } catch (error) {
        console.error('Error loading featured jobs:', error);
        // Fallback to static data if API fails
        setFeaturedJobs([
          {
            _id: '1',
            title: 'Senior Frontend Developer',
            company: 'TechBuzz Ltd.',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$90k - $130k',
            skills: ['React', 'Next.js', 'Remote'],
            created_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
            description: 'Join our team as a Senior Frontend Developer working on cutting-edge web applications.',
            company_logo: '💻',
            url: '#',
            is_active: true
          },
          {
            _id: '2',
            title: 'AI Product Manager',
            company: 'FutureAI Corp.',
            location: 'Remote (US)',
            job_type: 'Full-time',
            salary_range: '$120k - $170k',
            skills: ['AI', 'Product', 'Remote'],
            created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
            description: 'Lead AI product development and strategy for innovative machine learning solutions.',
            company_logo: '🧠',
            url: '#',
            is_active: true
          },
          {
            _id: '3',
            title: 'Lead DevOps Engineer',
            company: 'CloudHive Inc.',
            location: 'Hybrid (Berlin, DE)',
            job_type: 'Contract',
            salary_range: '$100k - $150k',
            skills: ['AWS', 'Kubernetes', 'CI/CD'],
            created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Architect and maintain cloud infrastructure for high-scale applications.',
            company_logo: '☁️',
            url: '#',
            is_active: true
          }
        ] as Job[]);
      }
    };

    loadFeaturedJobs();
  }, []);

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    // Simulate search
    // In a real app, construct query params based on selected filters
    const queryParams = new URLSearchParams({
      q: searchQuery
    }).toString();
    
    setTimeout(() => {
      setIsLoading(false);
      navigate(`/jobs?${queryParams}`);
    }, 1000);
  };

  const handleGetStartedClick = () => {
    setAuthModalTab('register');
    setIsAuthModalOpen(true);
  };

  const handleSignUpWithGoogleClick = () => {
    setAuthModalTab('register');
    setIsAuthModalOpen(true);
  };

  const handleOnboardingComplete = () => {
    setIsOnboardingOpen(false);
    // Optionally redirect to jobs page or show success message
    navigate('/jobs');
  };

  // Helper function to format time ago
  const getTimeAgo = (dateString: string) => {
    const now = new Date();
    const posted = new Date(dateString);
    const diffMs = now.getTime() - posted.getTime();
    const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
    const diffDays = Math.floor(diffHours / 24);

    if (diffHours < 1) return 'Just now';
    if (diffHours < 24) return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
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
            </nav>
            <div className="flex items-center space-x-4">
              <button
                onClick={handleGetStartedClick}
                className="bg-gradient-to-r from-orange-500 to-yellow-400 text-white px-4 py-2 rounded-lg hover:from-orange-600 hover:to-yellow-500 transition-colors font-medium text-sm shadow-md"
              >
                Get Started
              </button>
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
              <div className="grid grid-cols-1 md:grid-cols-6 gap-3 md:gap-4 items-end">
                {/* Job Title/Keywords - Extended */}
                <div className="md:col-span-4">
                  <label htmlFor="searchQuery" className="block text-sm font-medium text-gray-700 text-left mb-1">Please enter job title</label>
                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
                    <input
                      type="text"
                      id="searchQuery"
                      placeholder="e.g. Software Engineer, Product Manager, Data Scientist"
                      value={searchQuery}
                      onChange={(e) => setSearchQuery(e.target.value)}
                      className="w-full pl-10 pr-3 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
                    />
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
            </div>
          </form>
        </div>
      </section>
      
      {/* Featured Jobs */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Hot Remote Jobs 🔥</h2>
            <p className="text-gray-600">Fresh opportunities from leading remote companies</p>
          </div>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-12">
            {featuredJobs.map((job) => (
              <div key={job._id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition-shadow cursor-pointer flex flex-col justify-between">
                <div>
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl shadow-sm">
                        {job.company_logo || (typeof job.company === 'string' ? job.company[0] : job.company.name[0])}
                      </div>
                      <div>
                        <h3 className="font-semibold text-gray-900 text-lg">{job.title}</h3>
                        <p className="text-gray-600 text-sm">{typeof job.company === 'string' ? job.company : job.company.name}</p>
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
                      {job.job_type}
                    </div>
                    {job.salary_range && (
                      <div className="flex items-center text-sm text-gray-600">
                        <DollarSign className="w-4 h-4 mr-2 text-gray-400" />
                        {job.salary_range}
                      </div>
                    )}
                  </div>

                  <div className="flex flex-wrap gap-2 mb-6">
                    {(job.skills || []).slice(0, 3).map((tag, index) => (
                      <span key={index} className="px-3 py-1 bg-orange-50 text-orange-600 text-xs font-medium rounded-full">
                        {tag}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="flex items-center justify-between pt-4 border-t border-gray-100">
                  <span className="text-xs text-gray-500">Posted: {getTimeAgo(job.created_at)}</span>
                  <Link 
                    to={`/jobs/${job._id}`} 
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
            <button
              onClick={handleGetStartedClick}
              className="bg-white text-orange-600 px-10 py-3 rounded-lg hover:bg-yellow-50 transition-colors font-semibold shadow-lg text-lg"
            >
              Create Free Account
            </button>
             <button
                onClick={handleSignUpWithGoogleClick}
                className="flex items-center justify-center space-x-2 bg-white text-orange-600 px-10 py-3 rounded-lg hover:bg-yellow-50 transition-colors font-semibold border border-orange-200 text-lg shadow-lg"
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
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">For Job Seekers</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/profile" className="hover:text-white">My Profile</Link></li>
                <li><Link to="/applications" className="hover:text-white">My Applications</Link></li>
                <li><Link to="/help" className="hover:text-white">Help Center</Link></li>
              </ul>
            </div>
            <div>
              <h3 className="text-lg font-semibold mb-4">Company</h3>
              <ul className="space-y-2 text-sm text-gray-400">
                <li><Link to="/pricing" className="hover:text-white">Pricing</Link></li>
                <li><Link to="/terms" className="hover:text-white">Terms & Conditions</Link></li>
                <li><Link to="/privacy" className="hover:text-white">Privacy Policy</Link></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">For Employers</h4>
              <ul className="space-y-2">
                <li><a href="/post-job" className="text-gray-400 hover:text-white">Post a Job</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-500 text-sm">
            <p>&copy; {new Date().getFullYear()} Buzz2Remote. All rights reserved. AI Powered Remote Job Matching.</p>
          </div>
        </div>
      </footer>

      <AuthModal 
        isOpen={isAuthModalOpen} 
        onClose={() => setIsAuthModalOpen(false)} 
        defaultTab={authModalTab}
      />

      <Onboarding 
        isOpen={isOnboardingOpen} 
        onClose={() => setIsOnboardingOpen(false)}
        onComplete={handleOnboardingComplete}
      />
    </div>
  );
};

export default Home; 