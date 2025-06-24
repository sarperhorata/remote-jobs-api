import React, { useState, useEffect } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { 
  Search, 
  MapPin, 
  Building, 
  DollarSign, 
  Clock, 
  Filter,
  ChevronDown,
  ChevronUp,
  Star,
  ArrowRight,
  Briefcase,
  Calendar,
  Users
} from 'lucide-react';
import { jobService } from '../services/jobService';
import { Job } from '../types/job';

interface FilterState {
  jobTypes: string[];
  salaryRanges: string[];
  experienceLevels: string[];
  companies: string[];
  skills: string[];
  datePosted: string;
}

const Jobs: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalJobs, setTotalJobs] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(true);
  const [expandedJobs, setExpandedJobs] = useState<Set<string>>(new Set());
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());
  
  // Filter states
  const [filters, setFilters] = useState<FilterState>({
    jobTypes: [],
    salaryRanges: [],
    experienceLevels: [],
    companies: [],
    skills: [],
    datePosted: ''
  });

  // Expanded filter sections
  const [expandedSections, setExpandedSections] = useState({
    jobType: true,
    salary: true,
    experience: true,
    company: false,
    skills: false,
    date: true
  });

  const jobTypes = [
    { value: 'full-time', label: 'Full-time', count: 1250 },
    { value: 'part-time', label: 'Part-time', count: 320 },
    { value: 'contract', label: 'Contract', count: 180 },
    { value: 'freelance', label: 'Freelance', count: 95 },
    { value: 'internship', label: 'Internship', count: 45 }
  ];

  const salaryRanges = [
    { value: '0-50k', label: '$0 - $50k', count: 280 },
    { value: '50k-80k', label: '$50k - $80k', count: 420 },
    { value: '80k-120k', label: '$80k - $120k', count: 650 },
    { value: '120k-150k', label: '$120k - $150k', count: 380 },
    { value: '150k+', label: '$150k+', count: 160 }
  ];

  const experienceLevels = [
    { value: 'entry', label: 'Entry Level (0-2 years)', count: 340 },
    { value: 'mid', label: 'Mid Level (2-5 years)', count: 780 },
    { value: 'senior', label: 'Senior Level (5+ years)', count: 520 },
    { value: 'lead', label: 'Lead/Principal', count: 180 },
    { value: 'executive', label: 'Executive', count: 70 }
  ];

  const topCompanies = [
    { value: 'google', label: 'Google', count: 45 },
    { value: 'microsoft', label: 'Microsoft', count: 38 },
    { value: 'amazon', label: 'Amazon', count: 42 },
    { value: 'meta', label: 'Meta', count: 28 },
    { value: 'apple', label: 'Apple', count: 22 }
  ];

  const topSkills = [
    { value: 'react', label: 'React', count: 320 },
    { value: 'python', label: 'Python', count: 280 },
    { value: 'javascript', label: 'JavaScript', count: 450 },
    { value: 'aws', label: 'AWS', count: 180 },
    { value: 'node', label: 'Node.js', count: 220 }
  ];

  const dateOptions = [
    { value: 'today', label: 'Today', count: 25 },
    { value: 'week', label: 'Past Week', count: 180 },
    { value: 'month', label: 'Past Month', count: 650 },
    { value: 'all', label: 'All Time', count: 1890 }
  ];

  useEffect(() => {
    fetchJobs();
  }, [searchParams, currentPage, filters]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const position = searchParams.get('position') || '';
      const location = searchParams.get('location') || '';
      
      // In a real app, you'd pass filters to the API
      const response = await jobService.searchJobs({
        q: position,
        page: currentPage,
        per_page: 20,
        location,
        ...filters
      });
      
      setJobs(response.jobs || []);
      setTotalJobs(response.total || 0);
    } catch (error) {
      console.error('Error fetching jobs:', error);
      // Fallback data
      setJobs([
        {
          _id: '1',
          title: 'Senior Frontend Developer',
          company: 'TechBuzz Ltd.',
          location: 'Remote (Global)',
          job_type: 'Full-time',
          salary_range: '$90k - $130k',
          skills: ['React', 'TypeScript', 'Next.js'],
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
          skills: ['AI', 'Product Management', 'Strategy'],
          created_at: new Date(Date.now() - 3 * 60 * 60 * 1000).toISOString(),
          description: 'Lead AI product development and strategy for innovative machine learning solutions.',
          company_logo: '🧠',
          url: '#',
          is_active: true
        },
        {
          _id: '3',
          title: 'DevOps Engineer',
          company: 'CloudHive Inc.',
          location: 'Remote (Europe)',
          job_type: 'Contract',
          salary_range: '$100k - $150k',
          skills: ['AWS', 'Kubernetes', 'Docker'],
          created_at: new Date(Date.now() - 5 * 24 * 60 * 60 * 1000).toISOString(),
          description: 'Architect and maintain cloud infrastructure for high-scale applications.',
          company_logo: '☁️',
          url: '#',
          is_active: true
        }
      ] as Job[]);
      setTotalJobs(1890);
    } finally {
      setLoading(false);
    }
  };

  const handleFilterChange = (filterType: keyof FilterState, value: string, checked: boolean) => {
    setFilters(prev => {
      const newFilters = { ...prev };
      if (filterType === 'datePosted') {
        newFilters[filterType] = checked ? value : '';
      } else {
        const currentValues = newFilters[filterType] as string[];
        if (checked) {
          newFilters[filterType] = [...currentValues, value];
        } else {
          newFilters[filterType] = currentValues.filter(v => v !== value);
        }
      }
      return newFilters;
    });
    setCurrentPage(1); // Reset to first page when filters change
  };

  const toggleSection = (section: keyof typeof expandedSections) => {
    setExpandedSections(prev => ({
      ...prev,
      [section]: !prev[section]
    }));
  };

  const toggleJobExpansion = (jobId: string) => {
    setExpandedJobs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
      } else {
        newSet.add(jobId);
      }
      return newSet;
    });
  };

  const toggleJobSave = (jobId: string) => {
    setSavedJobs(prev => {
      const newSet = new Set(prev);
      if (newSet.has(jobId)) {
        newSet.delete(jobId);
      } else {
        newSet.add(jobId);
      }
      return newSet;
    });
  };

  const handleApplyToJob = (jobId: string) => {
    // Navigate to application page or open modal
    console.log('Applying to job:', jobId);
    // You could open a modal or navigate to application page
  };

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

  const FilterSection: React.FC<{
    title: string;
    sectionKey: keyof typeof expandedSections;
    children: React.ReactNode;
  }> = ({ title, sectionKey, children }) => (
    <div className="border-b border-gray-200 pb-4 mb-4">
      <button
        onClick={() => toggleSection(sectionKey)}
        className="flex items-center justify-between w-full text-left font-medium text-gray-900 hover:text-blue-600"
      >
        {title}
        {expandedSections[sectionKey] ? (
          <ChevronUp className="w-4 h-4" />
        ) : (
          <ChevronDown className="w-4 h-4" />
        )}
      </button>
      {expandedSections[sectionKey] && (
        <div className="mt-3 space-y-2">
          {children}
        </div>
      )}
    </div>
  );

  const CheckboxFilter: React.FC<{
    options: Array<{ value: string; label: string; count: number }>;
    selectedValues: string[];
    filterType: keyof FilterState;
  }> = ({ options, selectedValues, filterType }) => (
    <>
      {options.map(option => (
        <label key={option.value} className="flex items-center justify-between cursor-pointer hover:bg-gray-50 p-1 rounded">
          <div className="flex items-center">
            <input
              type="checkbox"
              checked={selectedValues.includes(option.value)}
              onChange={(e) => handleFilterChange(filterType, option.value, e.target.checked)}
              className="mr-2 text-blue-600 focus:ring-blue-500"
            />
            <span className="text-sm text-gray-700">{option.label}</span>
          </div>
          <span className="text-xs text-gray-500">({option.count})</span>
        </label>
      ))}
    </>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                {searchParams.get('position') || 'All Jobs'}
                {searchParams.get('location') && (
                  <span className="text-gray-600"> in {searchParams.get('location')}</span>
                )}
              </h1>
              <p className="text-gray-600 mt-1">
                {loading ? 'Loading...' : `${totalJobs.toLocaleString()} remote jobs found`}
              </p>
            </div>
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="lg:hidden flex items-center space-x-2 px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50"
            >
              <Filter className="w-4 h-4" />
              <span>Filters</span>
            </button>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
        <div className="flex gap-6">
          {/* Filters Sidebar */}
          <div className={`${showFilters ? 'block' : 'hidden'} lg:block w-full lg:w-80 flex-shrink-0`}>
            <div className="bg-white rounded-lg shadow-sm border p-6 sticky top-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Filters</h2>
              
              <FilterSection title="Job Type" sectionKey="jobType">
                <CheckboxFilter
                  options={jobTypes}
                  selectedValues={filters.jobTypes}
                  filterType="jobTypes"
                />
              </FilterSection>

              <FilterSection title="Salary Range" sectionKey="salary">
                <CheckboxFilter
                  options={salaryRanges}
                  selectedValues={filters.salaryRanges}
                  filterType="salaryRanges"
                />
              </FilterSection>

              <FilterSection title="Experience Level" sectionKey="experience">
                <CheckboxFilter
                  options={experienceLevels}
                  selectedValues={filters.experienceLevels}
                  filterType="experienceLevels"
                />
              </FilterSection>

              <FilterSection title="Date Posted" sectionKey="date">
                {dateOptions.map(option => (
                  <label key={option.value} className="flex items-center justify-between cursor-pointer hover:bg-gray-50 p-1 rounded">
                    <div className="flex items-center">
                      <input
                        type="radio"
                        name="datePosted"
                        checked={filters.datePosted === option.value}
                        onChange={(e) => handleFilterChange('datePosted', option.value, e.target.checked)}
                        className="mr-2 text-blue-600 focus:ring-blue-500"
                      />
                      <span className="text-sm text-gray-700">{option.label}</span>
                    </div>
                    <span className="text-xs text-gray-500">({option.count})</span>
                  </label>
                ))}
              </FilterSection>

              <FilterSection title="Top Companies" sectionKey="company">
                <CheckboxFilter
                  options={topCompanies}
                  selectedValues={filters.companies}
                  filterType="companies"
                />
              </FilterSection>

              <FilterSection title="Skills" sectionKey="skills">
                <CheckboxFilter
                  options={topSkills}
                  selectedValues={filters.skills}
                  filterType="skills"
                />
              </FilterSection>
            </div>
          </div>

          {/* Job Results */}
          <div className="flex-1">
            {loading ? (
              <div className="space-y-4">
                {[...Array(5)].map((_, i) => (
                  <div key={i} className="bg-white rounded-lg shadow-sm border p-6 animate-pulse">
                    <div className="flex items-start space-x-4">
                      <div className="w-12 h-12 bg-gray-200 rounded-lg"></div>
                      <div className="flex-1 space-y-2">
                        <div className="h-4 bg-gray-200 rounded w-3/4"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/2"></div>
                        <div className="h-3 bg-gray-200 rounded w-1/4"></div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="space-y-4">
                {jobs.map((job) => (
                  <div key={job._id} className="bg-white rounded-lg shadow-sm border hover:shadow-md transition-shadow">
                    <div className="p-6">
                      <div className="flex items-start justify-between">
                        <div className="flex items-start space-x-4 flex-1">
                          <div className="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center text-2xl shadow-sm">
                            {job.company_logo || (typeof job.company === 'string' ? job.company[0] : job.company.name[0])}
                          </div>
                          <div className="flex-1">
                            <div className="flex items-start justify-between">
                              <div>
                                <h3 className="text-lg font-semibold text-gray-900 hover:text-blue-600">
                                  <Link to={`/jobs/${job._id}`}>{job.title}</Link>
                                </h3>
                                <p className="text-gray-600 font-medium">
                                  {typeof job.company === 'string' ? job.company : job.company.name}
                                </p>
                              </div>
                              <button className="p-2 rounded-full hover:bg-yellow-100 text-gray-400 hover:text-yellow-500 transition-colors">
                                <Star className="w-5 h-5" />
                              </button>
                            </div>
                            
                            <div className="flex flex-wrap items-center gap-4 mt-3 text-sm text-gray-600">
                              <div className="flex items-center">
                                <MapPin className="w-4 h-4 mr-1" />
                                {job.location}
                              </div>
                              <div className="flex items-center">
                                <Briefcase className="w-4 h-4 mr-1" />
                                {job.job_type}
                              </div>
                              {job.salary_range && (
                                <div className="flex items-center">
                                  <DollarSign className="w-4 h-4 mr-1" />
                                  {job.salary_range}
                                </div>
                              )}
                              <div className="flex items-center">
                                <Clock className="w-4 h-4 mr-1" />
                                {getTimeAgo(job.created_at)}
                              </div>
                            </div>

                            <p className="text-gray-700 mt-3 line-clamp-2">
                              {job.description}
                            </p>

                            <div className="flex flex-wrap gap-2 mt-4">
                              {(job.skills || []).slice(0, 5).map((skill, index) => (
                                <span key={index} className="px-3 py-1 bg-blue-50 text-blue-600 text-xs font-medium rounded-full">
                                  {skill}
                                </span>
                              ))}
                            </div>
                          </div>
                        </div>
                      </div>
                      
                      <div className="flex items-center justify-between mt-6 pt-4 border-t border-gray-100">
                        <div className="flex items-center space-x-4 text-xs text-gray-500">
                          <span className="flex items-center">
                            <Users className="w-3 h-3 mr-1" />
                            50+ applicants
                          </span>
                          <span className="flex items-center">
                            <Calendar className="w-3 h-3 mr-1" />
                            Posted {getTimeAgo(job.created_at)}
                          </span>
                        </div>
                        <Link
                          to={`/jobs/${job._id}`}
                          className="inline-flex items-center space-x-1 bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors font-medium text-sm"
                        >
                          <span>View Details</span>
                          <ArrowRight className="w-4 h-4" />
                        </Link>
                      </div>
                    </div>
                  </div>
                ))}

                {/* Pagination */}
                {totalJobs > 20 && (
                  <div className="flex items-center justify-center space-x-2 mt-8">
                    <button
                      onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                      disabled={currentPage === 1}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Previous
                    </button>
                    <span className="px-4 py-2 text-gray-600">
                      Page {currentPage} of {Math.ceil(totalJobs / 20)}
                    </span>
                    <button
                      onClick={() => setCurrentPage(prev => prev + 1)}
                      disabled={currentPage >= Math.ceil(totalJobs / 20)}
                      className="px-4 py-2 border border-gray-300 rounded-lg hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Next
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Jobs; 