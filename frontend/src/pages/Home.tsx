import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthModal from '../components/AuthModal';
import Onboarding from '../components/Onboarding';
import MultiJobAutocomplete from '../components/MultiJobAutocomplete';
import Layout from '../components/Layout';
import { jobService } from '../services/jobService';
import { Job } from '../types/job';
import QuickSearchButton from '../components/QuickSearchButton';
import { 
  MapPin, 
  Clock, 
  DollarSign, 
  Building, 
  Globe, 
  ArrowRight,
  Star,
  CheckCircle,
  PlayCircle
} from 'lucide-react';

// Icons temporarily replaced with text
const Search = () => <span>🔍</span>;
const MapPinIcon = () => <span>📍</span>;
const BuildingIcon = () => <span>🏢</span>;
const GlobeIcon = () => <span>🌍</span>;
const ArrowRightIcon = () => <span>→</span>;
const StarIcon = () => <span>⭐</span>;
const CheckCircleIcon = () => <span>✅</span>;
const DollarSignIcon = () => <span>💲</span>;

interface Position {
  title: string;
  count: number;
  category?: string;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [selectedPositions, setSelectedPositions] = useState<Position[]>([]);
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [authModalTab, setAuthModalTab] = useState<'login' | 'register'>('login');
  const [featuredJobs, setFeaturedJobs] = useState<Job[]>([]);
  const [isOnboardingOpen, setIsOnboardingOpen] = useState(false);
  const [popularPositions, setPopularPositions] = useState<string[]>([]);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [loading, setLoading] = useState(false);

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
        console.log('🔥 Loading Hot Remote Jobs from API...');
        const response = await jobService.getJobs(1, 10); // Get 10 jobs instead of 6
        console.log('API Response:', response);
        
        // API'den gelen verileri kontrol et
        const jobs = (response as any)?.jobs || (response as any)?.items || response || [];
        if (jobs && jobs.length > 0) {
          // Real API'den gelen job'ları kullan
          const formattedJobs = jobs.map((job: any) => ({
            _id: job._id || job.id,
            title: job.title,
            company: job.company || 'Unknown Company',
            location: job.location || 'Remote',
            job_type: job.job_type || job.employment_type || 'Full-time',
            salary_range: job.salary || job.salary_range || 'Competitive',
            skills: job.skills || (job.title ? job.title.split(' ').slice(0, 3) : ['Remote']),
            created_at: job.created_at || job.posted_date || new Date().toISOString(),
            description: job.description || 'Exciting remote opportunity',
            company_logo: job.company_logo || (typeof job.company === 'string' ? job.company[0]?.toUpperCase() : '🏢'),
            url: job.url || job.external_url || '#',
            is_active: job.is_active !== false
          }));
          
          setFeaturedJobs(formattedJobs); // Show all 10
          console.log('✅ Hot Remote Jobs loaded successfully:', formattedJobs.length);
        } else {
          console.warn('⚠️ No jobs returned from API, using fallback data');
          throw new Error('No jobs from API');
        }
      } catch (error) {
        console.error('❌ Error loading featured jobs from API:', error);
        // Fallback to static data if API fails - 10 jobs
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
          },
          {
            _id: '4',
            title: 'UX/UI Designer',
            company: 'DesignBee Studio',
            location: 'Remote (Europe)',
            job_type: 'Full-time',
            salary_range: '$70k - $100k',
            skills: ['Figma', 'Design Systems', 'Remote'],
            created_at: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Create beautiful user experiences for our digital products.',
            company_logo: '🎨',
            url: '#',
            is_active: true
          },
          {
            _id: '5',
            title: 'Backend Engineer',
            company: 'DataFlow Systems',
            location: 'Remote (Worldwide)',
            job_type: 'Full-time',
            salary_range: '$85k - $125k',
            skills: ['Python', 'Django', 'PostgreSQL'],
            created_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
            description: 'Build scalable backend systems for data processing.',
            company_logo: '🔧',
            url: '#',
            is_active: true
          },
          {
            _id: '6',
            title: 'Marketing Manager',
            company: 'GrowthBuzz Inc.',
            location: 'Remote (US/EU)',
            job_type: 'Full-time',
            salary_range: '$80k - $110k',
            skills: ['SEO', 'Content', 'Analytics'],
            created_at: new Date(Date.now() - 4 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Lead our marketing efforts to drive growth.',
            company_logo: '📈',
            url: '#',
            is_active: true
          },
          {
            _id: '7',
            title: 'Mobile Developer',
            company: 'AppHive Ltd.',
            location: 'Remote (Global)',
            job_type: 'Contract',
            salary_range: '$95k - $140k',
            skills: ['React Native', 'iOS', 'Android'],
            created_at: new Date(Date.now() - 6 * 60 * 60 * 1000).toISOString(),
            description: 'Develop cross-platform mobile applications.',
            company_logo: '📱',
            url: '#',
            is_active: true
          },
          {
            _id: '8',
            title: 'Data Scientist',
            company: 'InsightBee Analytics',
            location: 'Remote (US)',
            job_type: 'Full-time',
            salary_range: '$110k - $160k',
            skills: ['Python', 'ML', 'Statistics'],
            created_at: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
            description: 'Turn data into actionable insights.',
            company_logo: '📊',
            url: '#',
            is_active: true
          },
          {
            _id: '9',
            title: 'Customer Success Manager',
            company: 'SupportHive',
            location: 'Remote (EU)',
            job_type: 'Full-time',
            salary_range: '$65k - $85k',
            skills: ['CRM', 'Communication', 'SaaS'],
            created_at: new Date(Date.now() - 8 * 60 * 60 * 1000).toISOString(),
            description: 'Ensure customer satisfaction and retention.',
            company_logo: '🤝',
            url: '#',
            is_active: true
          },
          {
            _id: '10',
            title: 'Blockchain Developer',
            company: 'CryptoBee Tech',
            location: 'Remote (Worldwide)',
            job_type: 'Full-time',
            salary_range: '$130k - $180k',
            skills: ['Solidity', 'Web3', 'Smart Contracts'],
            created_at: new Date(Date.now() - 16 * 60 * 60 * 1000).toISOString(),
            description: 'Build the future of decentralized applications.',
            company_logo: '⛓️',
            url: '#',
            is_active: true
          }
        ] as Job[]);
        console.log('📋 Using fallback job data');
      }
    };

    loadFeaturedJobs();
  }, []);

  const handleQuickSearch = (term: string) => {
    navigate(`/search?q=${encodeURIComponent(term)}`);
  };

  useEffect(() => {
    const loadData = async () => {
      try {
        // Popular search terms - fallback if API fails
        const fallbackPositions = ['Software Engineer', 'Product Manager', 'Data Scientist', 'DevOps Engineer', 'UX Designer'];
        
        // Get popular job titles for quick search
        const positionsResult = await jobService.getJobTitleSuggestions('', 5); // 5 popular positions
        const positions = positionsResult.filter(pos => pos.title).map(pos => pos.title);
        setPopularPositions(positions.length > 0 ? positions : fallbackPositions);
      } catch (error) {
        console.error('Error loading popular positions:', error);
        // Use fallback positions if API fails
        const fallbackPositions = ['Software Engineer', 'Product Manager', 'Data Scientist', 'DevOps Engineer', 'UX Designer'];
        setPopularPositions(fallbackPositions);
      }
    };

    loadData();
  }, []); // Remove fallbackPositions dependency since it's defined inside useEffect

  // Handle search with multiple positions
  const handleMultiPositionSearch = (positions: Position[]) => {
    if (positions.length === 0) {
      alert('Please select at least one position to search.');
      return;
    }

    const searchParams = new URLSearchParams();
    searchParams.set('multi_search', 'true');
    searchParams.set('job_titles', positions.map(p => p.title).join(','));
    
    navigate(`/jobs/search?${searchParams.toString()}`);
  };

  const handleSearch = (positions: Position[]) => {
    if (positions.length > 0) {
      const query = positions.map(p => p.title).join(',');
      navigate(`/jobs/search?q=${encodeURIComponent(query)}`);
    } else {
      navigate('/jobs/search');
    }
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

  const handleJobTitleSelect = (jobTitle: string) => {
    navigate(`/search?q=${encodeURIComponent(jobTitle)}`);
  };

  const handleAdvancedSearch = () => {
    navigate('/jobs');
  };

  const stats = [
    { label: "Active Jobs", value: "38K+", icon: Building },
    { label: "Companies", value: "2K+", icon: Building },
    { label: "Countries", value: "150+", icon: Globe }
  ];

  const features = [
    {
      title: "🎯 Smart Job Matching",
      description: "AI-powered matching connects you with perfect remote opportunities"
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
        {/* Hero Section - Kompakt tasarım */}
        <section className="relative pt-8 pb-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center">
              {/* Ana başlık */}
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                <span className="bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                  Remote Job 🐝
                </span>
                <br />
                <span className="text-white">Your Dream Career</span>
              </h1>
              
              <p className="text-xl text-white/80 mb-8 max-w-2xl mx-auto">
                Discover amazing remote opportunities from top companies worldwide. 
                Work from anywhere, live everywhere! 🌍
              </p>

              {/* Search Section */}
              <div className="max-w-4xl mx-auto mb-8">
                {/* İstatistikler - Search alanının üstünde */}
                <div className="flex justify-center items-center space-x-8 mb-6">
                  {stats.map((stat, index) => (
                    <div key={index} className="text-center">
                      <div className="text-2xl font-bold text-white">{stat.value}</div>
                      <div className="text-sm text-white/70">{stat.label}</div>
                    </div>
                  ))}
                </div>

                {/* Search Container */}
                <div className="bg-white/10 backdrop-blur-sm rounded-2xl p-6 border border-white/20 shadow-xl">
                  <div className="flex flex-col lg:flex-row gap-4 items-end">
                    {/* Autocomplete */}
                    <div className="flex-1">
                      <label className="block text-white/90 text-sm font-medium mb-2">
                        What kind of job are you looking for?
                      </label>
                                             <MultiJobAutocomplete
                         onSelect={(position) => {
                           setSelectedPositions(prev => {
                             const exists = prev.find(p => p.title === position.title);
                             if (exists) return prev;
                             return [...prev, position];
                           });
                         }}
                         placeholder="Try: Frontend Developer, Product Manager, Designer..."
                       />
                    </div>
                    
                    {/* Search Button */}
                                         <button
                       onClick={() => handleSearch(selectedPositions)}
                       className="bg-gradient-to-r from-orange-500 to-yellow-400 hover:from-orange-600 hover:to-yellow-500 text-white font-semibold px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 whitespace-nowrap"
                     >
                      <span>Find Jobs</span>
                      <ArrowRight className="w-5 h-5" />
                    </button>
                  </div>
                </div>
              </div>

              {/* Quick CTA - Daha kompakt */}
              <div className="flex flex-col sm:flex-row gap-4 justify-center items-center">
                <button
                  onClick={() => setShowAuthModal(true)}
                  className="bg-gradient-to-r from-purple-500 to-pink-500 hover:from-purple-600 hover:to-pink-600 text-white font-semibold px-6 py-3 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2"
                >
                  <Star className="w-5 h-5" />
                  <span>Start Your Journey</span>
                </button>
                
                <button
                  onClick={() => setShowOnboarding(true)}
                  className="bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold px-6 py-3 rounded-xl hover:bg-white/20 transition-all duration-200 flex items-center space-x-2"
                >
                  <PlayCircle className="w-5 h-5" />
                  <span>Watch Demo</span>
                </button>
              </div>
            </div>
          </div>
        </section>

        {/* Hot Remote Jobs Section */}
        <section className="py-12 bg-black/20 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                🔥 Hot Remote Jobs
              </h2>
              <p className="text-white/80 text-lg">
                Fresh opportunities from top companies, updated daily
              </p>
            </div>

            {/* Featured Jobs Grid */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 mb-8">
              {featuredJobs.length > 0 ? (
                featuredJobs.slice(0, 6).map((job, index) => (
                  <div
                    key={job._id || index}
                    className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer transform hover:scale-105"
                    onClick={() => navigate(`/jobs/${job._id}`)}
                  >
                    <div className="flex items-start justify-between mb-4">
                      <div className="flex-1">
                        <h3 className="font-semibold text-white text-lg mb-1 line-clamp-2">
                          {job.title}
                        </h3>
                        <p className="text-white/70 font-medium">{typeof job.company === 'string' ? job.company : job.company?.name}</p>
                      </div>
                      <span className="bg-green-500/20 text-green-300 px-2 py-1 rounded-full text-xs font-medium">
                        NEW
                      </span>
                    </div>

                    <div className="space-y-2 mb-4">
                      <div className="flex items-center text-white/60 text-sm">
                        <MapPin className="w-4 h-4 mr-2" />
                        {job.location || 'Remote'}
                      </div>
                      {job.salary_range && (
                        <div className="flex items-center text-white/60 text-sm">
                          <DollarSign className="w-4 h-4 mr-2" />
                          {job.salary_range}
                        </div>
                      )}
                      <div className="flex items-center text-white/60 text-sm">
                        <Clock className="w-4 h-4 mr-2" />
                        {job.job_type}
                      </div>
                    </div>

                    {job.skills && job.skills.length > 0 && (
                      <div className="flex flex-wrap gap-2">
                        {job.skills.slice(0, 3).map((skill: string, skillIndex: number) => (
                          <span
                            key={skillIndex}
                            className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full text-xs"
                          >
                            {skill}
                          </span>
                        ))}
                        {job.skills.length > 3 && (
                          <span className="text-white/60 text-xs px-2 py-1">
                            +{job.skills.length - 3} more
                          </span>
                        )}
                      </div>
                    )}
                  </div>
                ))
              ) : (
                // Sample jobs as fallback
                Array.from({ length: 6 }, (_, index) => {
                  const sampleJobs = [
                    {
                      title: "Senior Frontend Developer",
                      company: "TechCorp Inc.",
                      location: "Remote (US)",
                      salary: "$90k - $130k",
                      type: "Full-time",
                      skills: ["React", "TypeScript", "Node.js"]
                    },
                    {
                      title: "Product Manager",
                      company: "StartupX",
                      location: "Remote (EU)",
                      salary: "$80k - $120k", 
                      type: "Full-time",
                      skills: ["Strategy", "Analytics", "Agile"]
                    },
                    {
                      title: "UX Designer",
                      company: "DesignHub",
                      location: "Remote (Global)",
                      salary: "$70k - $100k",
                      type: "Contract",
                      skills: ["Figma", "Research", "Prototyping"]
                    },
                    {
                      title: "DevOps Engineer", 
                      company: "CloudFirst",
                      location: "Remote",
                      salary: "$100k - $150k",
                      type: "Full-time",
                      skills: ["AWS", "Docker", "Kubernetes"]
                    },
                    {
                      title: "Data Scientist",
                      company: "DataCorp",
                      location: "Remote (US)",
                      salary: "$110k - $160k",
                      type: "Full-time", 
                      skills: ["Python", "ML", "SQL"]
                    },
                    {
                      title: "Backend Developer",
                      company: "ApiWorks",
                      location: "Remote",
                      salary: "$85k - $125k",
                      type: "Full-time",
                      skills: ["Node.js", "MongoDB", "GraphQL"]
                    }
                  ];
                  
                  const job = sampleJobs[index];
                  return (
                    <div
                      key={index}
                      className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer transform hover:scale-105"
                      onClick={() => navigate('/jobs/search')}
                    >
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex-1">
                          <h3 className="font-semibold text-white text-lg mb-1">
                            {job.title}
                          </h3>
                          <p className="text-white/70 font-medium">{job.company}</p>
                        </div>
                        <span className="bg-green-500/20 text-green-300 px-2 py-1 rounded-full text-xs font-medium">
                          NEW
                        </span>
                      </div>

                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-white/60 text-sm">
                          <MapPin className="w-4 h-4 mr-2" />
                          {job.location}
                        </div>
                        <div className="flex items-center text-white/60 text-sm">
                          <DollarSign className="w-4 h-4 mr-2" />
                          {job.salary}
                        </div>
                        <div className="flex items-center text-white/60 text-sm">
                          <Clock className="w-4 h-4 mr-2" />
                          {job.type}
                        </div>
                      </div>

                      <div className="flex flex-wrap gap-2">
                        {job.skills.map((skill, skillIndex) => (
                          <span
                            key={skillIndex}
                            className="bg-blue-500/20 text-blue-300 px-2 py-1 rounded-full text-xs"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  );
                })
              )}
            </div>

            {/* View All Jobs Button */}
            <div className="text-center">
              <button
                onClick={() => navigate('/jobs/search')}
                className="bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold px-8 py-3 rounded-xl hover:bg-white/20 transition-all duration-200 inline-flex items-center space-x-2"
              >
                <span>View All Jobs</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-white mb-4">
                Why Choose Buzz2Remote? 🚀
              </h2>
              <p className="text-white/80 text-lg max-w-2xl mx-auto">
                We're not just another job board. We're your partner in finding the perfect remote career.
              </p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-8">
              {features.map((feature, index) => (
                <div
                  key={index}
                  className="bg-white/5 backdrop-blur-sm rounded-xl p-6 border border-white/10 hover:bg-white/10 transition-all duration-200"
                >
                  <h3 className="text-white font-semibold text-lg mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-white/70">
                    {feature.description}
                  </p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-black/30 backdrop-blur-sm border-t border-white/10 py-12">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
              <div className="col-span-1 md:col-span-2">
                <div className="flex items-center space-x-2 mb-4">
                  <span className="text-2xl">🐝</span>
                  <span className="font-bold text-xl text-white">Buzz2Remote</span>
                </div>
                <p className="text-white/70 mb-4">
                  Your gateway to the best remote jobs worldwide. 
                  Connect with top companies and build your dream career from anywhere.
                </p>
                <div className="flex space-x-4">
                  <a href="#" className="text-white/60 hover:text-white transition-colors">
                    Twitter
                  </a>
                  <a href="#" className="text-white/60 hover:text-white transition-colors">
                    LinkedIn
                  </a>
                  <a href="#" className="text-white/60 hover:text-white transition-colors">
                    GitHub
                  </a>
                </div>
              </div>
              
              <div>
                <h4 className="font-semibold text-white mb-4">For Job Seekers</h4>
                <ul className="space-y-2">
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Browse Jobs</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Create Profile</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Career Tips</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Salary Guide</a></li>
                </ul>
              </div>
              
              <div>
                <h4 className="font-semibold text-white mb-4">For Employers</h4>
                <ul className="space-y-2">
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Post Jobs</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Find Talent</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Pricing</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Resources</a></li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-white/10 mt-8 pt-8 text-center">
              <p className="text-white/60">
                © 2024 Buzz2Remote. Made with ❤️ for remote workers worldwide.
              </p>
            </div>
          </div>
        </footer>
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
           onClose={() => setShowOnboarding(false)}
           onComplete={handleOnboardingComplete}
         />
       )}
    </Layout>
  );
};

export default Home; 