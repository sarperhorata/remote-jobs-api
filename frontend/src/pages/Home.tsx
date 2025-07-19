import React, { useState, useEffect, useRef } from 'react';
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
  DollarSign, 
  ArrowRight,
  PlayCircle,
  Search,
  X
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
  const [selectedPositions, setSelectedPositions] = useState<Position[]>([]);
  const [featuredJobs, setFeaturedJobs] = useState<Job[]>([]);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [scrollIndex, setScrollIndex] = useState(0);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Animated counter states
  const [activeJobsCount, setActiveJobsCount] = useState(0);
  const [companiesCount, setCompaniesCount] = useState(0);
  const [countriesCount, setCountriesCount] = useState(0);

  // Target values for animation
  const targetActiveJobs = 38;
  const targetCompanies = 2;
  const targetCountries = 150;

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
  }, []);

  // Check if user needs onboarding
  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('onboardingCompleted');
    const userToken = localStorage.getItem('userToken'); // Assuming you store auth token
    
    // Show onboarding for new users who just registered
    if (userToken && !onboardingCompleted) {
      setShowOnboarding(true);
    }
  }, []);

  // Auto-scroll for infinite job cards
  useEffect(() => {
    const interval = setInterval(() => {
      setScrollIndex(prev => {
        if (featuredJobs.length <= 5) return 0;
        return (prev + 1) % (featuredJobs.length - 4);
      });
    }, 3000); // 3 seconds for smooth movement
    return () => clearInterval(interval);
  }, [featuredJobs.length]);

  // Fetch featured jobs on component mount
  useEffect(() => {
    const loadFeaturedJobs = async () => {
      try {
        console.log('🔥 Loading Hot Remote Jobs from API...');
        const response = await jobService.getJobs(1, 25); // Get more jobs for infinite scroll
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
          
          setFeaturedJobs(formattedJobs);
          console.log('✅ Hot Remote Jobs loaded successfully:', formattedJobs.length);
        } else {
          console.warn('⚠️ No jobs returned from API, using fallback data');
          throw new Error('No jobs from API');
        }
      } catch (error) {
        console.error('❌ Error loading featured jobs from API:', error);
        // Fallback to static data if API fails - 20 jobs for infinite scroll
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
            company: 'AppHive Inc.',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$95k - $140k',
            skills: ['React Native', 'iOS', 'Android'],
            created_at: new Date(Date.now() - 6 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Build cross-platform mobile applications.',
            company_logo: '📱',
            url: '#',
            is_active: true
          },
          {
            _id: '8',
            title: 'Data Scientist',
            company: 'AnalyticsPro',
            location: 'Remote (US)',
            job_type: 'Full-time',
            salary_range: '$110k - $160k',
            skills: ['Python', 'ML', 'Statistics'],
            created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Build machine learning models and data insights.',
            company_logo: '📊',
            url: '#',
            is_active: true
          },
          {
            _id: '9',
            title: 'Product Manager',
            company: 'ProductHive',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$100k - $150k',
            skills: ['Product', 'Strategy', 'Remote'],
            created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Lead product strategy and development.',
            company_logo: '🎯',
            url: '#',
            is_active: true
          },
          {
            _id: '10',
            title: 'Full Stack Developer',
            company: 'WebFlow Inc.',
            location: 'Remote (Europe)',
            job_type: 'Full-time',
            salary_range: '$90k - $130k',
            skills: ['React', 'Node.js', 'Full Stack'],
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Build end-to-end web applications.',
            company_logo: '🌐',
            url: '#',
            is_active: true
          },
          {
            _id: '11',
            title: 'Security Engineer',
            company: 'SecureNet',
            location: 'Remote (US)',
            job_type: 'Full-time',
            salary_range: '$120k - $170k',
            skills: ['Security', 'Cybersecurity', 'Remote'],
            created_at: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Protect our systems and data.',
            company_logo: '🔒',
            url: '#',
            is_active: true
          },
          {
            _id: '12',
            title: 'Content Strategist',
            company: 'ContentCraft',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$70k - $100k',
            skills: ['Content', 'SEO', 'Strategy'],
            created_at: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Create compelling content strategies.',
            company_logo: '✍️',
            url: '#',
            is_active: true
          },
          {
            _id: '13',
            title: 'QA Engineer',
            company: 'QualityTech',
            location: 'Remote (US/EU)',
            job_type: 'Full-time',
            salary_range: '$80k - $120k',
            skills: ['Testing', 'Automation', 'QA'],
            created_at: new Date(Date.now() - 13 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Ensure software quality and reliability.',
            company_logo: '✅',
            url: '#',
            is_active: true
          },
          {
            _id: '14',
            title: 'DevOps Engineer',
            company: 'CloudTech',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$95k - $135k',
            skills: ['AWS', 'Docker', 'CI/CD'],
            created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Build and maintain cloud infrastructure.',
            company_logo: '☁️',
            url: '#',
            is_active: true
          },
          {
            _id: '15',
            title: 'Frontend Developer',
            company: 'WebFlow',
            location: 'Remote (Europe)',
            job_type: 'Full-time',
            salary_range: '$75k - $115k',
            skills: ['React', 'Vue.js', 'Frontend'],
            created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Build beautiful user interfaces.',
            company_logo: '🎨',
            url: '#',
            is_active: true
          }
        ]);
      }
    };

    loadFeaturedJobs();
  }, []);

  const handleSearch = (positions: Position[]) => {
    // Ülke seçiliyse ayrı parametre olarak ekle
    const country = positions.find(p => p.type === 'country');
    const titles = positions.filter(p => !p.type || p.type !== 'country').map(pos => pos.title).join(', ');
    const searchParams = new URLSearchParams();
    if (titles) searchParams.set('q', titles);
    if (country) searchParams.set('country', country.code);
    navigate(`/jobs/search?${searchParams.toString()}`);
  };

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
    localStorage.setItem('onboardingCompleted', 'true');
    navigate('/jobs/search');
  };

  const handleJobCardClick = (jobId: string) => {
    window.open(`/jobs/${jobId}`, '_blank');
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
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
              zIndex: 1
            }}
          ></div>
          
          {/* Glassmorphism overlay */}
          <div className="absolute inset-0 bg-white/5 backdrop-blur-sm" style={{ zIndex: 2 }}></div>
          
          <div className="relative container mx-auto px-4 py-12" style={{ zIndex: 3 }}>
            <div className="max-w-5xl mx-auto text-center mb-6">
              {/* Main heading with enhanced typography */}
              <h1 className="text-5xl md:text-7xl font-extrabold mb-6 leading-tight">
                <br />
                Find Your Perfect 
                <span className="block bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                  Remote Job 🐝
                </span>
              </h1>
              
              <p className="text-xl md:text-2xl opacity-95 mb-6 leading-relaxed max-w-3xl mx-auto">
                Discover thousands of remote opportunities from top companies around the world.
                <br />
                Your dream job is just a buzz away!
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
                    <button
                      onClick={() => handleSearch(selectedPositions)}
                      disabled={selectedPositions.length === 0 || selectedPositions.length > 5}
                      className="bg-gradient-to-r from-orange-500 to-yellow-400 hover:from-orange-600 hover:to-yellow-500 disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed text-white font-semibold px-4 md:px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 whitespace-nowrap"
                    >
                      <Search className="w-5 h-5" />
                      <span className="hidden md:inline">Find Jobs</span>
                    </button>
                    <button
                      onClick={() => setShowOnboarding(true)}
                      className="hidden md:flex bg-white/10 backdrop-blur-sm border border-white/20 text-white font-semibold px-6 py-3 rounded-xl hover:bg-white/20 transition-all duration-200 items-center space-x-2"
                    >
                      <PlayCircle className="w-5 h-5" />
                      <span>Job Wizard</span>
                    </button>
                  </div>

                  {/* Selected Positions Display */}
                  {selectedPositions.length > 0 && (
                    <div className="mt-4">
                      <div className="flex flex-wrap gap-2">
                        {selectedPositions.map((position, index) => (
                          <div
                            key={index}
                            className="bg-white/20 backdrop-blur-sm border border-white/30 rounded-lg px-3 py-2 flex items-center space-x-2 text-white"
                          >
                            <span className="font-medium">{position.title}</span>
                            <span className="text-white/70 text-sm">({position.count} jobs)</span>
                            <button
                              onClick={() => {
                                setSelectedPositions(prev => prev.filter((_, i) => i !== index));
                              }}
                              className="ml-2 text-white/70 hover:text-white transition-colors"
                            >
                              <X className="w-4 h-4" />
                            </button>
                          </div>
                        ))}
                      </div>
                      <div className="mt-2 text-white/70 text-sm">
                        {selectedPositions.length} position{selectedPositions.length !== 1 ? 's' : ''} selected
                      </div>
                    </div>
                  )}
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
                    {companiesCount}K+
                  </div>
                  <div className="text-sm text-white/80">Companies</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold text-purple-400 transition-all duration-300">
                    {countriesCount}+
                  </div>
                  <div className="text-sm text-white/80">Countries</div>
                </div>
              </div>
            </div>

            {/* Single Row Infinite Scroll */}
            <div className="relative overflow-hidden mb-8">
              <div 
                ref={scrollRef}
                className="flex gap-6 transition-transform duration-3000 ease-in-out"
                style={{ 
                  transform: `translateX(-${scrollIndex * 400}px)`,
                  width: `${Math.max(100, (featuredJobs.length * 400))}px`
                }}
              >
                {featuredJobs.length > 0 ? (
                  featuredJobs.map((job, index) => (
                    <div
                      key={job._id || index}
                      className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer transform hover:scale-105 flex-shrink-0 min-w-[320px] max-w-[400px] w-full"
                      style={{ minHeight: '140px', maxWidth: '400px' }}
                      onClick={() => handleJobCardClick(job._id || `job-${index}`)}
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
                      
                      <div className="flex flex-wrap gap-2 mb-4">
                        <span className="text-white/60 text-sm flex items-center">
                          <MapPin className="w-3 h-3 mr-1" />
                          {job.location || 'Remote'}
                        </span>
                        <span className="text-white/60 text-sm flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {job.job_type || 'Full-time'}
                        </span>
                      </div>
                      
                      {(job.salary || job.salary_range) ? (
                        <div className="flex items-center text-green-300 font-medium">
                          <DollarSign className="w-4 h-4 mr-1" />
                          <span>
                            {job.salary_range || 
                             (job.salary ? `${job.salary.currency}${job.salary.min || 0}${job.salary.max ? ` - ${job.salary.currency}${job.salary.max}` : '+'}` : '')
                            }
                          </span>
                        </div>
                      ) : null}
                    </div>
                  ))
                ) : (
                  // Fallback loading cards
                  Array.from({ length: 15 }, (_, index) => {
                    const sampleJobs = [
                      { title: "Senior React Developer", company: "TechCorp", location: "Remote", salary_range: "$90k - $130k", job_type: "Full-time" },
                      { title: "Product Designer", company: "DesignStudio", location: "Remote", salary_range: "$70k - $110k", job_type: "Full-time" },
                      { title: "Data Scientist", company: "DataLabs", location: "Remote", salary_range: "$100k - $150k", job_type: "Full-time" },
                      { title: "DevOps Engineer", company: "CloudTech", location: "Remote", salary_range: "$95k - $135k", job_type: "Full-time" },
                      { title: "Frontend Developer", company: "WebFlow", location: "Remote", salary_range: "$75k - $115k", job_type: "Full-time" },
                      { title: "Backend Developer", company: "ApiWorks", location: "Remote", salary_range: "$85k - $125k", job_type: "Full-time" },
                      { title: "Mobile Developer", company: "AppHive", location: "Remote", salary_range: "$95k - $140k", job_type: "Full-time" },
                      { title: "UX Designer", company: "DesignHub", location: "Remote", salary_range: "$80k - $120k", job_type: "Full-time" },
                      { title: "Product Manager", company: "ProductCorp", location: "Remote", salary_range: "$100k - $150k", job_type: "Full-time" },
                      { title: "QA Engineer", company: "QualityTech", location: "Remote", salary_range: "$70k - $110k", job_type: "Full-time" },
                      { title: "Full Stack Developer", company: "WebFlow Inc.", location: "Remote", salary_range: "$90k - $130k", job_type: "Full-time" },
                      { title: "Data Engineer", company: "DataFlow", location: "Remote", salary_range: "$100k - $140k", job_type: "Full-time" },
                      { title: "Security Engineer", company: "SecureNet", location: "Remote", salary_range: "$110k - $160k", job_type: "Full-time" },
                      { title: "Marketing Manager", company: "GrowthBuzz", location: "Remote", salary_range: "$80k - $120k", job_type: "Full-time" },
                      { title: "Content Strategist", company: "ContentCraft", location: "Remote", salary_range: "$70k - $100k", job_type: "Full-time" }
                    ];
                    
                    const job = sampleJobs[index % sampleJobs.length];
                    return (
                      <div
                        key={index}
                        className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer transform hover:scale-105 flex-shrink-0 min-w-[320px] max-w-[400px] w-full"
                        style={{ minHeight: '140px', maxWidth: '400px' }}
                        onClick={() => window.open('/jobs/search', '_blank')}
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
                        
                        <div className="flex flex-wrap gap-2 mb-4">
                          <span className="text-white/60 text-sm flex items-center">
                            <MapPin className="w-3 h-3 mr-1" />
                            {job.location}
                          </span>
                          <span className="text-white/60 text-sm flex items-center">
                            <Clock className="w-3 h-3 mr-1" />
                            {job.job_type}
                          </span>
                        </div>
                        
                        <div className="flex items-center text-green-300 font-medium">
                          <DollarSign className="w-4 h-4 mr-1" />
                          <span>{job.salary_range}</span>
                        </div>
                      </div>
                    );
                  })
                )}
              </div>
            </div>

            {/* View All Jobs Button */}
            <div className="text-center -mt-4">
              <button
                onClick={() => navigate('/jobs/search')}
                className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold px-8 py-4 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 mx-auto text-lg"
              >
                <span>View All Jobs</span>
                <ArrowRight className="w-6 h-6" />
              </button>
            </div>
          </div>
        </section>

        {/* Features Section */}
        <section className="py-16 bg-gradient-to-br from-gray-900/50 via-purple-900/30 to-blue-900/50 backdrop-blur-sm">
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
                  className="bg-white/10 backdrop-blur-md rounded-xl p-6 border border-white/20 hover:bg-white/20 hover:border-white/30 transition-all duration-200 transform hover:scale-105 shadow-lg hover:shadow-xl"
                >
                  <h3 className="text-white font-semibold text-lg mb-3">
                    {feature.title}
                  </h3>
                  <p className="text-white/80">
                    {feature.description}
                  </p>
                </div>
              ))}
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
          onClose={() => setShowOnboarding(false)}
          onComplete={handleOnboardingComplete}
        />
      )}
    </Layout>
  );
};

export default Home; 