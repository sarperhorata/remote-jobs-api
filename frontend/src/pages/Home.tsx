import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthModal from '../components/AuthModal';
import Onboarding from '../components/Onboarding';
import MultiJobAutocomplete from '../components/MultiJobAutocomplete';
import Layout from '../components/Layout';
import { jobService } from '../services/jobService';
import { Job } from '../types/job';
import { 
  MapPin, 
  Clock, 
  ArrowRight,
  PlayCircle,
  Search
} from 'lucide-react';

interface Position {
  title: string;
  count: number;
  category?: string;
  type?: string; // Added type for country
  code?: string; // Added code for country
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [featuredJobs, setFeaturedJobs] = useState<Job[]>([]);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);

  // Animated counter states
  const [activeJobsCount, setActiveJobsCount] = useState(0);
  const [companiesCount, setCompaniesCount] = useState(0);
  const [countriesCount, setCountriesCount] = useState(0);

  // Target values for animation - will be updated with real data
  const [targetActiveJobs, setTargetActiveJobs] = useState(7181);
  const [targetCompanies, setTargetCompanies] = useState(872);
  const [targetCountries, setTargetCountries] = useState(150);

  // Fetch real statistics data
  useEffect(() => {
    const fetchStatistics = async () => {
      try {
        const response = await fetch('/api/v1/jobs/statistics');
        if (response.ok) {
          const data = await response.json();
          
          // Update target values with real data
          setTargetActiveJobs(Math.floor(data.total_jobs / 1000)); // Convert to K
          setTargetCompanies(data.companies_count || 820);
          setTargetCountries(data.countries_count || 1014);
          
          console.log('📊 Real statistics loaded:', {
            total_jobs: data.total_jobs,
            companies_count: data.companies_count,
            countries_count: data.countries_count
          });
        }
      } catch (error) {
        console.error('❌ Error fetching statistics:', error);
      }
    };

    fetchStatistics();
  }, []);

  // Animated counter effect
  useEffect(() => {
    const duration = 2000; // 2 seconds
    const steps = 60; // 60 steps for smooth animation
    const stepDuration = duration / steps;

    const animateCounter = (setter: React.Dispatch<React.SetStateAction<number>>, target: number) => {
      let current = 0;
      const increment = target / steps;
      
      const timer = setInterval(() => {
        current += increment;
        if (current >= target) {
          current = target;
          clearInterval(timer);
        }
        setter(Math.floor(current));
      }, stepDuration);
    };

    // Start animations with slight delays for staggered effect
    setTimeout(() => animateCounter(setActiveJobsCount, targetActiveJobs), 500);
    setTimeout(() => animateCounter(setCompaniesCount, targetCompanies), 800);
    setTimeout(() => animateCounter(setCountriesCount, targetCountries), 1100);
  }, [targetActiveJobs, targetCompanies, targetCountries]);

  // Check if user needs onboarding
  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('onboardingCompleted');
    if (!onboardingCompleted) {
      setShowOnboarding(true);
    }
  }, []);

  // Load featured jobs
  useEffect(() => {
    const loadFeaturedJobs = async () => {
      try {
        const jobs = await jobService.getFeaturedJobs();
        setFeaturedJobs(jobs);
      } catch (error) {
        console.error('Error loading featured jobs:', error);
      }
    };

    loadFeaturedJobs();
  }, []);

  // Auto-scroll for featured jobs
  useEffect(() => {
    const interval = setInterval(() => {
      // setScrollIndex((prev) => (prev + 1) % Math.max(1, featuredJobs.length - 2));
    }, 5000);

    return () => clearInterval(interval);
  }, [featuredJobs.length]);

  const handleSearch = (positions: Position[]) => {
    console.log('🏠 handleSearch called with positions:', positions);
    
    // Ülke seçiliyse ayrı parametre olarak ekle
    const country = positions.find(p => p.type === 'country');
    const jobPositions = positions.filter(p => !p.type || p.type !== 'country');
    
    console.log('🏠 jobPositions:', jobPositions);
    
    const searchParams = new URLSearchParams();
    
    // Always use multi-keyword endpoint for keyword searches (even single keyword)
    if (jobPositions.length >= 1) {
      const keywords = jobPositions.map(pos => {
        // Extract keyword from title (remove count part)
        return pos.title.split('(')[0].trim();
      });
      console.log('🏠 Extracted keywords:', keywords);
      searchParams.set('keywords', keywords.join(','));
      searchParams.set('multi_keyword', 'true');
    }
    
    if (country) searchParams.set('country', country.code);
    
    const finalUrl = `/jobs/search?${searchParams.toString()}`;
    console.log('🏠 Navigating to:', finalUrl);
    navigate(finalUrl);
  };

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
    localStorage.setItem('onboardingCompleted', 'true');
    navigate('/jobs/search');
  };

  const handleJobCardClick = (job: Job) => {
    // Navigate to job details page
    if (job._id) {
      navigate(`/jobs/${job._id}`);
    } else if (job.id) {
      navigate(`/jobs/${job.id}`);
    } else {
      // Fallback to search results if no job ID
      const searchParams = new URLSearchParams();
      if (job.title) {
        searchParams.set('q', job.title);
      }
      if (typeof job.company === 'string' && job.company) {
        searchParams.set('company', job.company);
      } else if (typeof job.company === 'object' && job.company && 'name' in job.company) {
        searchParams.set('company', job.company.name);
      }
      if (job.location) {
        searchParams.set('location', job.location);
      }
      navigate(`/jobs/search?${searchParams.toString()}`);
    }
  };

  const features = [
    {
      title: "🎯 Smart Matching",
      description: "Our AI finds the perfect job matches based on your skills, experience, and preferences"
    },
    {
      title: "🌍 Global Opportunities", 
      description: "Access remote jobs from companies worldwide, in your timezone"
    },
    {
      title: "💰 Salary Transparency",
      description: "See salary ranges upfront - no surprises, just honest compensation"
    },
    {
      title: "⚡ Real-time Updates",
      description: "Get notified instantly when new jobs matching your skills are posted"
    }
  ];

  return (
    <Layout>
      <div className="min-h-screen">
        {/* Hero Section with Enhanced Design */}
        <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 text-white">
          {/* Background Video */}
          <video
            autoPlay
            loop
            muted
            playsInline
            className="absolute inset-0 w-full h-full object-cover opacity-30"
            style={{ zIndex: 0 }}
          >
            <source src="/Entry video.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          
          {/* Animated background patterns */}
          <div 
            className="absolute inset-0 opacity-30"
            style={{
              backgroundImage: `
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 40% 40%, rgba(120, 219, 255, 0.3) 0%, transparent 50%)
              `
            }}
          />

          {/* Content */}
          <div className="relative z-10 px-4 py-20 sm:px-6 lg:px-8">
            {/* Header */}
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-6xl font-bold mb-6 leading-tight">
                Find Your Dream
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-yellow-400 to-orange-500">
                  Remote Job
                </span>
              </h1>
              <p className="text-xl md:text-2xl text-white/90 mb-8 max-w-3xl mx-auto">
                Discover thousands of remote opportunities from top companies worldwide. 
                Your next career move is just a search away.
              </p>
            </div>

            {/* Enhanced Search Section */}
            <div className="max-w-4xl mx-auto">
              <div className="bg-white/10 backdrop-blur-lg rounded-2xl p-8 border border-white/20 shadow-2xl">
                <div className="space-y-6">
                  {/* Search input with buttons side by side */}
                  <div className="flex gap-3">
                    <div className="flex-1">
                      <MultiJobAutocomplete
                        onSelect={(positions) => {
                          console.log('🏠 Home received positions:', positions);
                          if (positions.length > 0) {
                            handleSearch(positions);
                          }
                        }}
                        placeholder="Search keywords (e.g., react, python, remote)"
                      />
                    </div>
                    <button
                      onClick={() => setShowOnboarding(true)}
                      className="hidden md:flex bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold px-6 py-3 rounded-xl hover:bg-white/20 transition-all duration-200 items-center space-x-2"
                    >
                      <PlayCircle className="w-5 h-5" />
                      <span>Job Wizard</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Hot Remote Jobs Section - Single Row Infinite Scroll */}
        <section className="py-12 bg-black/20 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                🔥 Hot Remote Jobs
              </h2>
              <p className="text-white/80 text-lg mb-8">
                Fresh opportunities from top companies, updated daily
              </p>
              
              {/* Statistics Section */}
              <div className="flex flex-wrap justify-center gap-8">
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold text-yellow-400 transition-all duration-300">
                    {activeJobsCount}K+
                  </div>
                  <div className="text-sm text-white/80">Active Jobs</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold text-green-400 transition-all duration-300">
                    {companiesCount}
                  </div>
                  <div className="text-sm text-white/80">Companies</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold text-purple-400 transition-all duration-300">
                    {countriesCount}
                  </div>
                  <div className="text-sm text-white/80">Countries</div>
                </div>
              </div>
            </div>

            {/* Featured Jobs Grid */}
            {featuredJobs.length > 0 && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {featuredJobs.slice(0, 6).map((job, index) => (
                  <div
                    key={job.id || index}
                    onClick={() => handleJobCardClick(job)}
                    className="bg-white/10 backdrop-blur-lg border border-white/20 rounded-xl p-6 hover:bg-white/20 transition-all duration-300 cursor-pointer group"
                  >
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-white mb-2 group-hover:text-yellow-400 transition-colors">
                          {job.title}
                        </h3>
                        <p className="text-white/80 text-sm">
                          {typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}
                        </p>
                      </div>
                      <div className="text-right">
                        <div className="text-yellow-400 font-semibold">
                          {job.salary_min && job.salary_max 
                            ? `$${job.salary_min.toLocaleString()}-${job.salary_max.toLocaleString()}`
                            : job.salary_min 
                              ? `$${job.salary_min.toLocaleString()}+`
                              : 'Salary not specified'
                          }
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center justify-between text-sm text-white/70">
                      <div className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4" />
                        <span>{job.location || 'Remote'}</span>
                      </div>
                      <div className="flex items-center space-x-2">
                        <Clock className="w-4 h-4" />
                        <span>{job.posted_date ? new Date(job.posted_date).toLocaleDateString() : 'Recently'}</span>
                      </div>
                    </div>
                    
                    {job.isRemote && (
                      <div className="mt-3 inline-block bg-green-500/20 text-green-400 text-xs px-2 py-1 rounded-full">
                        🌍 Remote
                      </div>
                    )}
                  </div>
                ))}
              </div>
            )}

            {/* View All Jobs Button */}
            <div className="text-center mt-12">
              <button
                onClick={() => navigate('/jobs/search')}
                className="bg-gradient-to-r from-orange-500 to-yellow-400 hover:from-orange-600 hover:to-yellow-500 text-white font-semibold px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 mx-auto"
              >
                <span>View All Jobs</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-gradient-to-br from-gray-900 to-black">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-16">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Why Choose Buzz2Remote?
              </h2>
              <p className="text-xl text-gray-300 max-w-3xl mx-auto">
                We're not just another job board. We're your gateway to the future of work.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-xl p-6 hover:bg-white/10 transition-all duration-300 group"
                >
                  <h3 className="text-xl font-semibold text-white mb-3 group-hover:text-yellow-400 transition-colors">
                    {feature.title}
                  </h3>
                  <p className="text-gray-300 leading-relaxed">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* CTA Section */}
        <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600">
          <div className="max-w-4xl mx-auto text-center px-4 sm:px-6 lg:px-8">
            <h2 className="text-3xl md:text-4xl font-bold text-white mb-6">
              Ready to Find Your Dream Remote Job?
            </h2>
            <p className="text-xl text-white/90 mb-8">
              Join thousands of professionals who've already found their perfect remote opportunity.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button
                onClick={() => navigate('/jobs/search')}
                className="bg-white text-blue-600 font-semibold px-8 py-4 rounded-xl hover:bg-gray-100 transition-all duration-200 flex items-center justify-center space-x-2"
              >
                <Search className="w-5 h-5" />
                <span>Start Searching</span>
              </button>
              <button
                onClick={() => setShowAuthModal(true)}
                className="bg-transparent border-2 border-white text-white font-semibold px-8 py-4 rounded-xl hover:bg-white hover:text-blue-600 transition-all duration-200"
              >
                Create Account
              </button>
            </div>
          </div>
        </section>
      </div>

      {/* Modals */}
      {showAuthModal && (
        <AuthModal
          isOpen={showAuthModal}
          onClose={() => setShowAuthModal(false)}
        />
      )}

      {showOnboarding && (
        <Onboarding
          isOpen={showOnboarding}
          onComplete={handleOnboardingComplete}
          onClose={() => setShowOnboarding(false)}
        />
      )}
    </Layout>
  );
};

export default Home; 