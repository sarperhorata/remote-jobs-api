import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import AuthModal from '../components/AuthModal';
import Onboarding from '../components/Onboarding';
import MultiJobAutocomplete from '../components/MultiJobAutocomplete';
import Layout from '../components/Layout';
import { jobService } from '../services/jobService';
import { Job } from '../types/job';
import { useAuth } from '../contexts/AuthContext';
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
  const [topRowIndex, setTopRowIndex] = useState(0);
  const [bottomRowIndex, setBottomRowIndex] = useState(0);
  const topRowRef = useRef<HTMLDivElement>(null);
  const bottomRowRef = useRef<HTMLDivElement>(null);

  // Check if user needs onboarding
  useEffect(() => {
    const onboardingCompleted = localStorage.getItem('onboardingCompleted');
    const userToken = localStorage.getItem('userToken'); // Assuming you store auth token
    
    // Show onboarding for new users who just registered
    if (userToken && !onboardingCompleted) {
      setShowOnboarding(true);
    }
  }, []);

  // Auto-scroll for top row (left to right) - faster speed for visibility
  useEffect(() => {
    const interval = setInterval(() => {
      setTopRowIndex(prev => (prev + 1) % Math.max(1, featuredJobs.length - 10));
    }, 3000); // 3 seconds for visible movement
    return () => clearInterval(interval);
  }, [featuredJobs.length]);

  // Auto-scroll for bottom row (right to left) - faster speed for visibility
  useEffect(() => {
    const interval = setInterval(() => {
      setBottomRowIndex(prev => (prev + 1) % Math.max(1, featuredJobs.length - 10));
    }, 3500); // 3.5 seconds for visible movement
    return () => clearInterval(interval);
  }, [featuredJobs.length]);

  // Fetch featured jobs on component mount
  useEffect(() => {
    const loadFeaturedJobs = async () => {
      try {
        console.log('🔥 Loading Hot Remote Jobs from API...');
        const response = await jobService.getJobs(1, 25); // Get more jobs for infinite scroll (10 visible + buffer)
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
            created_at: new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Build machine learning models and analyze complex data.',
            company_logo: '📊',
            url: '#',
            is_active: true
          },
          {
            _id: '9',
            title: 'Product Designer',
            company: 'DesignHub',
            location: 'Remote (Europe)',
            job_type: 'Full-time',
            salary_range: '$75k - $110k',
            skills: ['UI/UX', 'Prototyping', 'Research'],
            created_at: new Date(Date.now() - 8 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Create user-centered design solutions.',
            company_logo: '🎯',
            url: '#',
            is_active: true
          },
          {
            _id: '10',
            title: 'Full Stack Developer',
            company: 'WebFlow Inc.',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$90k - $130k',
            skills: ['React', 'Node.js', 'MongoDB'],
            created_at: new Date(Date.now() - 9 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Build end-to-end web applications.',
            company_logo: '🌐',
            url: '#',
            is_active: true
          },
          {
            _id: '11',
            title: 'QA Engineer',
            company: 'QualityTech',
            location: 'Remote (US/EU)',
            job_type: 'Full-time',
            salary_range: '$70k - $100k',
            skills: ['Testing', 'Automation', 'Selenium'],
            created_at: new Date(Date.now() - 10 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Ensure software quality through comprehensive testing.',
            company_logo: '🔍',
            url: '#',
            is_active: true
          },
          {
            _id: '12',
            title: 'Content Writer',
            company: 'ContentCraft',
            location: 'Remote (Worldwide)',
            job_type: 'Part-time',
            salary_range: '$50k - $80k',
            skills: ['Writing', 'SEO', 'Marketing'],
            created_at: new Date(Date.now() - 11 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Create engaging content for digital platforms.',
            company_logo: '✍️',
            url: '#',
            is_active: true
          },
          {
            _id: '13',
            title: 'Cybersecurity Analyst',
            company: 'SecureNet',
            location: 'Remote (US)',
            job_type: 'Full-time',
            salary_range: '$100k - $150k',
            skills: ['Security', 'Networking', 'Compliance'],
            created_at: new Date(Date.now() - 12 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Protect systems and data from cyber threats.',
            company_logo: '🔒',
            url: '#',
            is_active: true
          },
          {
            _id: '14',
            title: 'Sales Manager',
            company: 'SalesForce Pro',
            location: 'Remote (US/EU)',
            job_type: 'Full-time',
            salary_range: '$80k - $120k',
            skills: ['Sales', 'CRM', 'Leadership'],
            created_at: new Date(Date.now() - 13 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Lead sales teams and drive revenue growth.',
            company_logo: '💼',
            url: '#',
            is_active: true
          },
          {
            _id: '15',
            title: 'Customer Success Manager',
            company: 'SuccessHub',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$70k - $100k',
            skills: ['Customer Service', 'Onboarding', 'Retention'],
            created_at: new Date(Date.now() - 14 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Ensure customer satisfaction and retention.',
            company_logo: '🤝',
            url: '#',
            is_active: true
          },
          {
            _id: '16',
            title: 'Business Analyst',
            company: 'BusinessIntel',
            location: 'Remote (US)',
            job_type: 'Full-time',
            salary_range: '$85k - $120k',
            skills: ['Analysis', 'Requirements', 'Documentation'],
            created_at: new Date(Date.now() - 15 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Bridge business needs with technical solutions.',
            company_logo: '📋',
            url: '#',
            is_active: true
          },
          {
            _id: '17',
            title: 'DevOps Engineer',
            company: 'CloudOps',
            location: 'Remote (Europe)',
            job_type: 'Full-time',
            salary_range: '$90k - $130k',
            skills: ['Docker', 'Kubernetes', 'CI/CD'],
            created_at: new Date(Date.now() - 16 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Streamline development and deployment processes.',
            company_logo: '⚙️',
            url: '#',
            is_active: true
          },
          {
            _id: '18',
            title: 'UI Developer',
            company: 'InterfaceLab',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$75k - $110k',
            skills: ['HTML', 'CSS', 'JavaScript'],
            created_at: new Date(Date.now() - 17 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Create beautiful and functional user interfaces.',
            company_logo: '🎨',
            url: '#',
            is_active: true
          },
          {
            _id: '19',
            title: 'Technical Writer',
            company: 'DocTech',
            location: 'Remote (US/EU)',
            job_type: 'Part-time',
            salary_range: '$60k - $90k',
            skills: ['Documentation', 'Technical Writing', 'APIs'],
            created_at: new Date(Date.now() - 18 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Create clear technical documentation.',
            company_logo: '📚',
            url: '#',
            is_active: true
          },
          {
            _id: '20',
            title: 'Project Manager',
            company: 'ProjectFlow',
            location: 'Remote (Global)',
            job_type: 'Full-time',
            salary_range: '$90k - $130k',
            skills: ['Agile', 'Scrum', 'Leadership'],
            created_at: new Date(Date.now() - 19 * 24 * 60 * 60 * 1000).toISOString(),
            description: 'Lead projects from conception to completion.',
            company_logo: '📊',
            url: '#',
            is_active: true
          }
        ]);
      }
    };

    loadFeaturedJobs();
  }, []);

  const handleSearch = (positions: Position[]) => {
    if (positions.length > 0) {
      const query = positions.map(p => p.title).join(',');
      navigate(`/jobs/search?q=${encodeURIComponent(query)}`);
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
          {/* Animated background patterns */}
          <div 
            className="absolute inset-0 opacity-30"
            style={{
              backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='0.05'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`
            }}
          ></div>
          
          {/* Glassmorphism overlay */}
          <div className="absolute inset-0 bg-white/5 backdrop-blur-sm"></div>
          
          <div className="relative container mx-auto px-4 py-12">
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
              {/* Top Row - Left to Right Scroll (10 cards) */}
              <div className="relative overflow-hidden">
                <div 
                  ref={topRowRef}
                  className="flex gap-6 transition-transform duration-2000 ease-in-out"
                  style={{ 
                    transform: `translateX(-${topRowIndex * 10}%)`,
                    width: `${Math.max(100, (featuredJobs.length * 10))}%`
                  }}
                >
                  {featuredJobs.length > 0 ? (
                    featuredJobs.slice(0, 10).map((job, index) => (
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
                    Array.from({ length: 10 }, (_, index) => {
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
                        }
                      ];
                      
                      const job = sampleJobs[index];
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

              {/* Bottom Row - Right to Left Scroll (10 cards) */}
              <div className="relative overflow-hidden">
                <div 
                  ref={bottomRowRef}
                  className="flex gap-6 transition-transform duration-2000 ease-in-out"
                  style={{ 
                    transform: `translateX(-${bottomRowIndex * 10}%)`,
                    width: `${Math.max(100, (featuredJobs.length * 10))}%`
                  }}
                >
                  {featuredJobs.length > 0 ? (
                    featuredJobs.slice(0, 10).reverse().map((job, index) => (
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
                    Array.from({ length: 10 }, (_, index) => {
                      const sampleJobs = [
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
                        }
                      ];
                      
                      const job = sampleJobs[index];
                      return (
                        <div
                          key={index}
                          className="bg-white/10 backdrop-blur-sm rounded-xl p-6 border border-white/20 hover:bg-white/20 transition-all duration-200 cursor-pointer transform hover:scale-105 flex-shrink-0"
                          style={{ width: '400px', height: '180px' }}
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
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Post a Job</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Pricing</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Resources</a></li>
                  <li><a href="#" className="text-white/60 hover:text-white transition-colors">Support</a></li>
                </ul>
              </div>
            </div>
            
            <div className="border-t border-white/10 mt-8 pt-8 text-center">
              <p className="text-white/60">
                © 2024 Buzz2Remote. All rights reserved. Made with 💜 for remote workers everywhere.
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