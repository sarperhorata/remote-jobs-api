import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthModal from '../components/AuthModal';
import Onboarding from '../components/Onboarding';
import MultiJobAutocomplete from '../components/MultiJobAutocomplete';
import Layout from '../components/Layout';
import { jobService } from '../services/jobService';
import { Job } from '../types/job';

// Icons temporarily replaced with text
const Search = () => <span>🔍</span>;
const MapPin = () => <span>📍</span>;
const Building = () => <span>🏢</span>;
const Globe = () => <span>🌍</span>;
const ArrowRight = () => <span>→</span>;
const Star = () => <span>⭐</span>;
const CheckCircle = () => <span>✅</span>;
const DollarSign = () => <span>💲</span>;

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
    <Layout>

      <section className="py-16 md:py-20 px-4 sm:px-6 lg:px-8 relative overflow-hidden">
        {/* Video Background */}
        <div className="absolute inset-0 z-0">
          <video 
            autoPlay 
            loop 
            muted 
            playsInline
            className="absolute inset-0 w-full h-full object-cover"
            poster="/path/to/poster-image.jpg"
          >
            <source src="/Entry video.mp4" type="video/mp4" />
            Your browser does not support the video tag.
          </video>
          <div className="absolute inset-0 bg-black/60"></div>
        </div>
        
        <div className="max-w-7xl mx-auto text-center relative z-10">
          <h1 className="text-4xl md:text-6xl font-bold text-white mb-6 leading-tight drop-shadow-lg">
            Find Your Next <span className="text-transparent bg-clip-text bg-gradient-to-r from-orange-400 to-yellow-400">Remote Buzz</span>
          </h1>
          <p className="text-lg md:text-xl text-gray-200 mb-10 md:mb-12 max-w-3xl mx-auto drop-shadow-md">
            AI-powered job matching to connect you with global remote opportunities. Select multiple job titles and let our smart search find the perfect matches.
          </p>

          {/* Updated Search Section with MultiJobAutocomplete */}
          <div className="max-w-3xl mx-auto">
            <h2 className="text-2xl font-bold text-white mb-6 text-center drop-shadow-md">
              Find Your Perfect Remote Job
            </h2>
            
            <MultiJobAutocomplete
              selectedPositions={selectedPositions}
              onPositionsChange={setSelectedPositions}
              onSearch={handleMultiPositionSearch}
              placeholder="Search job titles (e.g., Frontend Developer, Backend Engineer)"
              maxSelections={10}
            />
          </div>
        </div>
      </section>
      
      {/* Featured Jobs with Infinite Horizontal Scroll */}
      <section className="py-16 px-4 sm:px-6 lg:px-8 bg-white">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">Hot Remote Jobs 🔥</h2>
            <p className="text-gray-600">Fresh opportunities from leading remote companies</p>
          </div>
          
          {/* Infinite Horizontal Scrollable Container */}
          <div className="relative">
            <div className="overflow-x-auto pb-4 -mx-4 px-4">
              <div className="flex gap-6 w-max animate-scroll-infinite">
                {/* First set of jobs */}
                {featuredJobs.map((job) => (
                  <div key={job._id} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition-shadow cursor-pointer flex flex-col justify-between w-80 flex-shrink-0">
                    <div>
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl shadow-sm">
                            {job.company_logo || (typeof job.company === 'string' ? job.company[0] : job.company.name[0])}
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 text-lg line-clamp-1">{job.title}</h3>
                            <p className="text-gray-600 text-sm line-clamp-1">{typeof job.company === 'string' ? job.company : job.company.name}</p>
                          </div>
                        </div>
                        <button 
                          onClick={() => {
                            const userToken = localStorage.getItem('userToken');
                            if (!userToken) {
                              setAuthModalTab('login');
                              setIsAuthModalOpen(true);
                            } else {
                              console.log('Adding job to favorites:', job._id);
                            }
                          }}
                          className="p-1.5 rounded-full hover:bg-yellow-100 text-gray-400 hover:text-yellow-500 transition-colors"
                        >
                           <div className="w-5 h-5 flex items-center justify-center">
                             <Star />
                           </div>
                        </button>
                      </div>
                          
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <div className="w-4 h-4 mr-2 text-gray-400 flex items-center justify-center">
                            <MapPin />
                          </div>
                          <span className="line-clamp-1">{job.location}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <div className="w-4 h-4 mr-2 text-gray-400 flex items-center justify-center">
                            <Building />
                          </div>
                          {job.job_type}
                        </div>
                        {job.salary_range && (
                          <div className="flex items-center text-sm text-gray-600">
                            <div className="w-4 h-4 mr-2 text-gray-400 flex items-center justify-center">
                              <DollarSign />
                            </div>
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
                        <div className="w-4 h-4 transition-transform group-hover:translate-x-1 flex items-center justify-center">
                          <ArrowRight />
                        </div>
                      </Link>
                    </div>
                  </div>
                ))}
                
                {/* Duplicate set for infinite scroll effect */}
                {featuredJobs.map((job) => (
                  <div key={`duplicate-${job._id}`} className="bg-white border border-gray-200 rounded-xl p-6 hover:shadow-xl transition-shadow cursor-pointer flex flex-col justify-between w-80 flex-shrink-0">
                    <div>
                      <div className="flex items-start justify-between mb-4">
                        <div className="flex items-center space-x-3">
                          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl shadow-sm">
                            {job.company_logo || (typeof job.company === 'string' ? job.company[0] : job.company.name[0])}
                          </div>
                          <div>
                            <h3 className="font-semibold text-gray-900 text-lg line-clamp-1">{job.title}</h3>
                            <p className="text-gray-600 text-sm line-clamp-1">{typeof job.company === 'string' ? job.company : job.company.name}</p>
                          </div>
                        </div>
                        <button 
                          onClick={() => {
                            const userToken = localStorage.getItem('userToken');
                            if (!userToken) {
                              setAuthModalTab('login');
                              setIsAuthModalOpen(true);
                            } else {
                              console.log('Adding job to favorites:', job._id);
                            }
                          }}
                          className="p-1.5 rounded-full hover:bg-yellow-100 text-gray-400 hover:text-yellow-500 transition-colors"
                        >
                           <div className="w-5 h-5 flex items-center justify-center">
                             <Star />
                           </div>
                        </button>
                      </div>
                          
                      <div className="space-y-2 mb-4">
                        <div className="flex items-center text-sm text-gray-600">
                          <div className="w-4 h-4 mr-2 text-gray-400 flex items-center justify-center">
                            <MapPin />
                          </div>
                          <span className="line-clamp-1">{job.location}</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                          <div className="w-4 h-4 mr-2 text-gray-400 flex items-center justify-center">
                            <Building />
                          </div>
                          {job.job_type}
                        </div>
                        {job.salary_range && (
                          <div className="flex items-center text-sm text-gray-600">
                            <div className="w-4 h-4 mr-2 text-gray-400 flex items-center justify-center">
                              <DollarSign />
                            </div>
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
                        <div className="w-4 h-4 transition-transform group-hover:translate-x-1 flex items-center justify-center">
                          <ArrowRight />
                        </div>
                      </Link>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>

          <div className="text-center mt-12">
            <Link
              to="/jobs"
              className="inline-flex items-center space-x-2 bg-gradient-to-r from-orange-500 to-yellow-500 text-white px-8 py-3 rounded-lg hover:from-orange-600 hover:to-yellow-600 transition-colors font-semibold shadow-lg"
            >
              <span>Browse All Jobs</span>
              <div className="w-5 h-5 flex items-center justify-center">
                <ArrowRight />
              </div>
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
                icon: <div className="w-8 h-8 text-orange-500 flex items-center justify-center"><Search /></div>,
                title: "AI-Powered Matching",
                description: "Our AI finds perfect job matches for you."
              },
              {
                icon: <div className="w-8 h-8 text-green-500 flex items-center justify-center"><CheckCircle /></div>,
                title: "One-Click Apply",
                description: "Apply to jobs instantly with your saved profile."
              },
              {
                icon: <div className="w-8 h-8 text-blue-500 flex items-center justify-center"><Globe /></div>,
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
                  <span className="text-xl">🐝</span>
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
    </Layout>
  );
};

export default Home; 