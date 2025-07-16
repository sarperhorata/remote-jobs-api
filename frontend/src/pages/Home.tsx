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
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [selectedPositions, setSelectedPositions] = useState<Position[]>([]);
  const [featuredJobs, setFeaturedJobs] = useState<Job[]>([]);
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [scrollIndex, setScrollIndex] = useState(0);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Check if user needs onboarding
  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('onboardingCompleted');
    const userToken = localStorage.getItem('userToken'); // Assuming you store auth token
    
    // Show onboarding for new users who just registered
    if (userToken && !onboardingCompleted) {
      setShowOnboarding(true);
    }
  }, []);

  // Auto-scroll for single row - very slow and smooth movement to the right
  useEffect(() => {
    const interval = setInterval(() => {
      setScrollIndex(prev => {
        // Infinite scroll: when we reach the end, start over
        const maxIndex = Math.max(1, featuredJobs.length - 20);
        return (prev + 1) % maxIndex;
      });
    }, 3000); // 3 seconds for very slow movement
    return () => clearInterval(interval);
  }, [featuredJobs.length]);

  // Fetch featured jobs on component mount
  useEffect(() => {
    const loadFeaturedJobs = async () => {
      try {
        console.log('🔥 Loading Hot Remote Jobs from API...');
        const response = await jobService.getJobs(1, 50); // Get more jobs for infinite scroll (20 visible + buffer)
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
          
          // Ensure we have enough jobs for smooth infinite scrolling
          const extendedJobs = [...formattedJobs, ...formattedJobs, ...formattedJobs];
          setFeaturedJobs(extendedJobs);
          console.log('✅ Hot Remote Jobs loaded successfully:', extendedJobs.length);
        } else {
          console.warn('⚠️ No jobs returned from API, using fallback data');
          throw new Error('No jobs from API');
        }
      } catch (error) {
        console.error('❌ Error loading featured jobs from API:', error);
        // Fallback to static data if API fails - 30 jobs for infinite scroll
        const fallbackJobs = [
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
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Analyze complex data sets and build predictive models.',
            company_logo: '📊',
            url: '#',
            is_active: true
          },
          {
            _id: '9',
            title: 'Security Engineer',
            company: 'SecureNet',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$100k - $150k',
            skills: ['Cybersecurity', 'Penetration Testing', 'Compliance'],
            created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Protect our systems and data from security threats.',
            company_logo: '🔒',
            url: '#',
            is_active: true
          },
          {
            _id: '10',
            title: 'Product Manager',
            company: 'ProductCorp',
            location: 'Remote (Europe)',
            job_type: 'Full-time',
            salary_range: '$90k - $130k',
            skills: ['Product Strategy', 'Agile', 'User Research'],
            created_at: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Lead product development from concept to launch.',
            company_logo: '🎯',
            url: '#',
            is_active: true
          }
        ];
        
        // Create extended array for smooth infinite scrolling
        const extendedFallbackJobs = [...fallbackJobs, ...fallbackJobs, ...fallbackJobs];
        setFeaturedJobs(extendedFallbackJobs);
        console.log('✅ Fallback jobs loaded:', extendedFallbackJobs.length);
      }
    };

    loadFeaturedJobs();
  }, []);

  const handleSearch = (positions: Position[]) => {
    if (positions.length > 0) {
      // Seçilen pozisyonların title'larını al ve virgülle ayır
      const searchTerms = positions.map(p => p.title).join(',');
      // URL'ye pozisyonları ekle
      navigate(`/jobs/search?positions=${encodeURIComponent(searchTerms)}`);
    } else {
      navigate('/jobs/search');
    }
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
          {/* Video Background */}
          <div className="absolute inset-0 w-full h-full">
            <video
              autoPlay
              loop
              muted
              playsInline
              className="w-full h-full object-cover opacity-40"
              style={{ filter: 'brightness(0.3) contrast(1.2)' }}
            >
              <source src="/Entry video.mp4" type="video/mp4" />
              Your browser does not support the video tag.
            </video>
          </div>
          
          {/* Animated background patterns */}
          <div 
            className="absolute inset-0 opacity-20"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
            }}
          ></div>
          
          {/* Glassmorphism overlay */}
          <div className="absolute inset-0 bg-black/30 backdrop-blur-sm"></div>
          
          <div className="relative container mx-auto px-4 py-6">
            <div className="max-w-5xl mx-auto text-center mb-3">
              {/* Main heading with enhanced typography */}
              <h1 className="text-5xl md:text-7xl font-extrabold mb-3 leading-tight">
                <br />
                Find Your Perfect 
                <span className="block bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                  Remote Job 🐝
                </span>
              </h1>
              
              <p className="text-xl md:text-2xl opacity-95 mb-3 leading-relaxed max-w-3xl mx-auto">
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
                      className="bg-gradient-to-br from-orange-400 to-yellow-500 hover:from-orange-500 hover:to-yellow-400 disabled:from-orange-300 disabled:to-yellow-400 disabled:opacity-50 disabled:cursor-not-allowed text-white font-extrabold px-4 md:px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 whitespace-nowrap tracking-tight text-lg"
                    >
                      <Search className="w-5 h-5" />
                      <span>Search!</span>
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

        {/* Hot Remote Jobs Section */}
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
                  <div className="text-2xl md:text-3xl font-bold text-yellow-400">38K+</div>
                  <div className="text-sm text-white/80">Active Jobs</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold text-green-400">2K+</div>
                  <div className="text-sm text-white/80">Companies</div>
                </div>
                <div className="text-center">
                  <div className="text-2xl md:text-3xl font-bold text-purple-400">150+</div>
                  <div className="text-sm text-white/80">Countries</div>
                </div>
              </div>
            </div>

            {/* Featured Jobs with Infinite Scroll */}
            <div className="space-y-8 mb-8">
              {/* Single Row - Left to Right Scroll */}
              <div className="relative overflow-hidden">
                <div 
                  ref={scrollContainerRef}
                  className="flex gap-6 transition-transform duration-[15000ms] ease-in-out"
                  style={{ 
                    transform: `translateX(-${scrollIndex * 8}%)`,
                    width: `${Math.max(100, (featuredJobs.length * 8))}%`
                  }}
                >
                  {featuredJobs.length > 0 ? (
                    featuredJobs.slice(0, 25).map((job, index) => (
                      <div
                        key={job._id || index}
                        className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer transform hover:scale-105 flex-shrink-0"
                        style={{ width: '400px', height: '210px' }}
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
                    Array.from({ length: 25 }, (_, index) => {
                      const sampleJobs = [
                        {
                          title: "Senior React Developer",
                          company: "TechCorp",
                          location: "Remote",
                          salary_range: "$90k - $130k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Product Designer", 
                          company: "DesignStudio",
                          location: "Remote",
                          salary_range: "$70k - $110k", 
                          job_type: "Full-time"
                        },
                        {
                          title: "Data Scientist",
                          company: "DataLabs",
                          location: "Remote", 
                          salary_range: "$100k - $150k",
                          job_type: "Full-time"
                        },
                        {
                          title: "DevOps Engineer",
                          company: "CloudTech",
                          location: "Remote",
                          salary_range: "$95k - $135k", 
                          job_type: "Full-time"
                        },
                        {
                          title: "Frontend Developer",
                          company: "WebFlow",
                          location: "Remote",
                          salary_range: "$75k - $115k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Backend Developer",
                          company: "ApiWorks",
                          location: "Remote",
                          salary_range: "$85k - $125k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Mobile Developer",
                          company: "AppHive",
                          location: "Remote",
                          salary_range: "$95k - $140k",
                          job_type: "Full-time"
                        },
                        {
                          title: "UX Designer",
                          company: "DesignHub",
                          location: "Remote",
                          salary_range: "$80k - $120k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Product Manager",
                          company: "ProductCorp",
                          location: "Remote",
                          salary_range: "$100k - $150k",
                          job_type: "Full-time"
                        },
                        {
                          title: "QA Engineer",
                          company: "QualityTech",
                          location: "Remote",
                          salary_range: "$70k - $110k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Full Stack Developer",
                          company: "WebFlow Inc.",
                          location: "Remote",
                          salary_range: "$90k - $130k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Data Engineer",
                          company: "DataFlow",
                          location: "Remote",
                          salary_range: "$100k - $140k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Security Engineer",
                          company: "SecureNet",
                          location: "Remote",
                          salary_range: "$110k - $160k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Marketing Manager",
                          company: "GrowthBuzz",
                          location: "Remote",
                          salary_range: "$80k - $120k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Content Strategist",
                          company: "ContentCraft",
                          location: "Remote",
                          salary_range: "$70k - $100k",
                          job_type: "Full-time"
                        },
                        {
                          title: "AI Engineer",
                          company: "AI Solutions",
                          location: "Remote",
                          salary_range: "$120k - $180k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Blockchain Developer",
                          company: "CryptoTech",
                          location: "Remote",
                          salary_range: "$100k - $150k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Game Developer",
                          company: "GameStudio",
                          location: "Remote",
                          salary_range: "$85k - $130k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Cloud Architect",
                          company: "CloudCorp",
                          location: "Remote",
                          salary_range: "$130k - $180k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Machine Learning Engineer",
                          company: "ML Labs",
                          location: "Remote",
                          salary_range: "$110k - $160k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Site Reliability Engineer",
                          company: "Reliability Inc.",
                          location: "Remote",
                          salary_range: "$100k - $150k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Technical Lead",
                          company: "TechLead Corp",
                          location: "Remote",
                          salary_range: "$120k - $170k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Business Analyst",
                          company: "BusinessTech",
                          location: "Remote",
                          salary_range: "$80k - $120k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Sales Engineer",
                          company: "SalesTech",
                          location: "Remote",
                          salary_range: "$90k - $140k",
                          job_type: "Full-time"
                        },
                        {
                          title: "Customer Success Manager",
                          company: "SuccessCorp",
                          location: "Remote",
                          salary_range: "$75k - $110k",
                          job_type: "Full-time"
                        }
                      ];
                      
                      const job = sampleJobs[index % sampleJobs.length];
                      return (
                        <div
                          key={index}
                          className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer transform hover:scale-105 flex-shrink-0"
                          style={{ width: '400px', height: '210px' }}
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
            </div>

            {/* View All Jobs Button */}
            <div className="text-center">
              <button
                onClick={() => navigate('/jobs/search')}
                className="bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 text-white font-semibold px-8 py-3 rounded-xl shadow-lg hover:shadow-xl transform hover:scale-105 transition-all duration-200 flex items-center space-x-2 mx-auto"
              >
                <span>View All Jobs</span>
                <ArrowRight className="w-5 h-5" />
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