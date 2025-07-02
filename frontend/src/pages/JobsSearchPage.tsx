import React, { useState, useEffect } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { Search, Filter, MapPin, Clock, DollarSign, Building2, ExternalLink, BookmarkPlus, Bookmark, CheckCircle2, Briefcase } from '../components/icons/EmojiIcons';
import { Job } from '../types/job';
import { jobService } from '../services/jobService';
import JobApplicationModal from '../components/JobSearch/JobApplicationModal';

interface SearchFilters {
  query: string;
  location: string;
  jobType: string;
  workType: string[];
  experience_level: string;
  salaryMin: string;
  salaryMax: string;
  company: string;
  postedWithin: string;
  negativeKeywords?: string;
}

const JobsSearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [jobs, setJobs] = useState<Job[]>([]);
  const [filteredJobs, setFilteredJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [showApplicationModal, setShowApplicationModal] = useState(false);
  const [appliedJobs, setAppliedJobs] = useState<Set<string>>(new Set());
  const [savedJobs, setSavedJobs] = useState<Set<string>>(new Set());

  const [filters, setFilters] = useState<SearchFilters>({
    query: searchParams.get('q') || '',
    location: searchParams.get('location') || '',
    jobType: searchParams.get('jobType') || '',
    workType: searchParams.get('workType') ? searchParams.get('workType').split(',') : [],
    experience_level: searchParams.get('experience_level') || '',
    salaryMin: searchParams.get('salaryMin') || '',
    salaryMax: searchParams.get('salaryMax') || '',
    company: searchParams.get('company') || '',
    postedWithin: searchParams.get('postedWithin') || '',
    negativeKeywords: searchParams.get('negativeKeywords') || ''
  });

  const [showFilters, setShowFilters] = useState(false);

  const workTypeOptions = [
    { value: 'remote', label: 'Remote', icon: '🌍' },
    { value: 'hybrid', label: 'Hybrid', icon: '🏢' },
    { value: 'onsite', label: 'On-site', icon: '🏙️' },
    { value: 'contract', label: 'Contract', icon: '📋' },
    { value: 'freelance', label: 'Freelance', icon: '💼' }
  ];

  const postedAgeOptions = [
    { value: '1DAY', label: 'Last 24 hours' },
    { value: '3DAYS', label: 'Last 3 days' },
    { value: '7DAYS', label: 'Last week' },
    { value: '30DAYS', label: 'Last month' },
    { value: 'ALL', label: 'Any time' }
  ];

  const salaryRanges = [
    { value: '0-50k', label: '$0 - $50k' },
    { value: '50k-100k', label: '$50k - $100k' },
    { value: '100k-150k', label: '$100k - $150k' },
    { value: '150k-200k', label: '$150k - $200k' },
    { value: '200k+', label: '$200k+' }
  ];

  const experienceLevels = [
    { value: 'internship', label: 'Internship' },
    { value: 'entry', label: 'Entry Level' },
    { value: 'mid', label: 'Mid Level' },
    { value: 'senior', label: 'Senior Level' },
    { value: 'lead', label: 'Lead' },
    { value: 'executive', label: 'Executive' }
  ];

  const companySizes = [
    { value: 'startup', label: 'Startup (1-50)' },
    { value: 'small', label: 'Small (51-200)' },
    { value: 'medium', label: 'Medium (201-1000)' },
    { value: 'large', label: 'Large (1000+)' }
  ];

  useEffect(() => {
    searchJobs();
    loadUserApplications();
  }, []);

  useEffect(() => {
    applyFilters();
  }, [jobs, filters]);

  useEffect(() => {
    updateUrlParams();
  }, [filters]);

  const searchJobs = async () => {
    setLoading(true);
    try {
      const searchQuery = filters.query || searchParams.get('query') || '';
      const response = await jobService.searchJobs({
        q: searchQuery,
        location: filters.location !== 'anywhere' ? filters.location : '',
        limit: 50,
        page: currentPage
      });
      
      setJobs(response.jobs || []);
      setTotalResults(response.total || 0);
    } catch (error) {
      console.error('Error searching jobs:', error);
      setJobs([]);
    } finally {
      setLoading(false);
    }
  };

  const loadUserApplications = async () => {
    try {
      const applications = await jobService.getMyApplications();
      const appliedJobIds = new Set(applications.map((app: any) => String(app.job_id))) as Set<string>;
      setAppliedJobs(appliedJobIds);
      
      // Load saved jobs from localStorage
      const saved = localStorage.getItem('savedJobs');
      if (saved) {
        setSavedJobs(new Set(JSON.parse(saved)));
      }
    } catch (error) {
      console.error('Error loading applications:', error);
    }
  };

  const applyFilters = () => {
    let filtered = jobs.filter(job => {
      // Work type filter
      if (filters.workType && filters.workType.length > 0 && !filters.workType.includes(job.isRemote ? 'remote' : 'onsite')) {
        return false;
      }

      // Posted age filter
      if (filters.postedWithin && filters.postedWithin !== 'ALL') {
        const jobDate = new Date(job.createdAt);
        const now = new Date();
        const daysDiff = Math.floor((now.getTime() - jobDate.getTime()) / (1000 * 60 * 60 * 24));

        switch (filters.postedWithin) {
          case '1DAY':
            if (daysDiff > 1) return false;
            break;
          case '3DAYS':
            if (daysDiff > 3) return false;
            break;
          case '7DAYS':
            if (daysDiff > 7) return false;
            break;
          case '30DAYS':
            if (daysDiff > 30) return false;
            break;
        }
      }

      // Salary range filter
      if (filters.salaryMin && filters.salaryMax) {
        const [minSalary, maxSalary] = [filters.salaryMin, filters.salaryMax].map(s => 
          s.includes('k') ? parseInt(s) * 1000 : s === '+' ? Infinity : parseInt(s)
        );
        
        if (job.salary) {
          const jobMin = typeof job.salary === 'object' ? job.salary.min : 0;
          const jobMax = typeof job.salary === 'object' ? job.salary.max : jobMin;
          
          if (jobMax < minSalary || (maxSalary !== Infinity && jobMin > maxSalary)) {
            return false;
          }
        }
      }

      // Experience level filtering with intelligent matching
      if (filters.experience_level) {
        // Map selected experience level to keywords
        const experienceMap: { [key: string]: string[] } = {
          'Entry Level': ['entry', 'junior', 'jr', 'intern', 'graduate', 'trainee', '0-2', 'beginner'],
          'Mid Level': ['mid', 'intermediate', '2-5', '3-5', 'experienced'],
          'Senior Level': ['senior', 'sr', '5+', '6+', 'expert', 'specialist', 'lead'],
          'Lead': ['lead', 'principal', 'manager', 'head', 'director', 'team lead'],
          'Executive': ['executive', 'chief', 'ceo', 'cto', 'vp', 'vice president']
        };
        
        const levelKeywords = experienceMap[filters.experience_level] || [];
        const jobLevel = job.experience_level?.toLowerCase() || '';
        const jobTitle = job.title.toLowerCase();
        
        if (!levelKeywords.some(keyword => 
          jobLevel.includes(keyword) || jobTitle.includes(keyword)
        )) {
          return false;
        }
      }

      // Negative keywords filter
      if (filters.negativeKeywords) {
        const negativeWords = filters.negativeKeywords.toLowerCase().split(',').map(w => w.trim());
        const jobText = `${job.title} ${job.description} ${typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}`.toLowerCase();
        
        if (negativeWords.some(word => word && jobText.includes(word))) {
          return false;
        }
      }

      return true;
    });

    setFilteredJobs(filtered);
  };

  const updateUrlParams = () => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value && value !== 'anywhere' && value !== 'ALL') {
        if (Array.isArray(value)) {
          if (value.length > 0) {
            params.set(key, value.join(','));
          }
        } else {
          params.set(key, value);
        }
      }
    });
    setSearchParams(params);
  };

  const handleSearch = () => {
    setCurrentPage(1);
    searchJobs();
  };

  const handleApply = async (job: Job) => {
    setSelectedJob(job);
    setShowApplicationModal(true);
  };

  const handleApplicationSubmit = async (applicationData: any) => {
    if (selectedJob) {
      // Mark job as applied
      setAppliedJobs(prev => new Set([...prev, selectedJob.id]));
      
      // Track application
      await jobService.trackJobInteraction(selectedJob.id, 'applied');
    }
    setShowApplicationModal(false);
    setSelectedJob(null);
  };

  const toggleSaveJob = (jobId: string) => {
    const newSavedJobs = new Set(savedJobs);
    if (newSavedJobs.has(jobId)) {
      newSavedJobs.delete(jobId);
    } else {
      newSavedJobs.add(jobId);
    }
    setSavedJobs(newSavedJobs);
    localStorage.setItem('savedJobs', JSON.stringify([...newSavedJobs]));
  };

  const formatSalary = (salary: any) => {
    if (!salary) return null;
    if (typeof salary === 'string') return salary;
    if (salary.min && salary.max) {
      return `$${(salary.min / 1000).toFixed(0)}k - $${(salary.max / 1000).toFixed(0)}k`;
    }
    if (salary.min) return `$${(salary.min / 1000).toFixed(0)}k+`;
    return null;
  };

  const getTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 24) {
      return diffInHours === 1 ? '1 hour ago' : `${diffInHours} hours ago`;
    }
    const diffInDays = Math.floor(diffInHours / 24);
    return diffInDays === 1 ? '1 day ago' : `${diffInDays} days ago`;
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            {/* Search Bar */}
            <div className="flex flex-col lg:flex-row gap-4 mb-6">
              <div className="flex-1 relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <input
                  type="text"
                  placeholder="Search jobs, companies, or keywords..."
                  value={filters.query}
                  onChange={(e) => setFilters(prev => ({ ...prev, query: e.target.value }))}
                  onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                />
              </div>
              
              <div className="lg:w-64 relative">
                <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 h-5 w-5" />
                <select
                  value={filters.location}
                  onChange={(e) => setFilters(prev => ({ ...prev, location: e.target.value }))}
                  className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-transparent text-lg"
                >
                  <option value="anywhere">Anywhere</option>
                  <option value="remote">Remote</option>
                  <option value="istanbul">Istanbul</option>
                  <option value="ankara">Ankara</option>
                  <option value="izmir">Izmir</option>
                  <option value="usa">United States</option>
                  <option value="europe">Europe</option>
                </select>
              </div>

              <button
                onClick={handleSearch}
                disabled={loading}
                className="px-8 py-3 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 flex items-center justify-center gap-2 font-medium"
              >
                {loading ? (
                  <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full" />
                ) : (
                  <Search className="h-5 w-5" />
                )}
                Search
              </button>
            </div>

            {/* Quick Filters */}
            <div className="flex flex-wrap gap-3 mb-4">
              {/* Work Types */}
              <div className="flex gap-2">
                {workTypeOptions.map(option => (
                  <button
                    key={option.value}
                    onClick={() => {
                      const newWorkTypes = filters.workType.includes(option.value)
                        ? filters.workType.filter(t => t !== option.value)
                        : [...filters.workType, option.value];
                      setFilters(prev => ({ ...prev, workType: newWorkTypes }));
                    }}
                    className={`px-4 py-2 rounded-full text-sm font-medium transition-colors ${
                      filters.workType.includes(option.value)
                        ? 'bg-blue-100 text-blue-800 border-2 border-blue-300'
                        : 'bg-white text-gray-700 border-2 border-gray-200 hover:border-gray-300'
                    }`}
                  >
                    <span className="mr-1">{option.icon}</span>
                    {option.label}
                  </button>
                ))}
              </div>

              {/* Posted Age */}
              <select
                value={filters.postedWithin}
                onChange={(e) => setFilters(prev => ({ ...prev, postedWithin: e.target.value }))}
                className="px-4 py-2 border-2 border-gray-200 rounded-full text-sm font-medium focus:ring-2 focus:ring-blue-500 focus:border-blue-300"
              >
                {postedAgeOptions.map(option => (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>

              {/* Advanced Filters Toggle */}
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="px-4 py-2 border-2 border-gray-200 rounded-full text-sm font-medium hover:border-gray-300 flex items-center gap-2"
              >
                <Filter className="h-4 w-4" />
                More Filters
              </button>
            </div>

            {/* Advanced Filters */}
            {showFilters && (
              <div className="bg-gray-50 rounded-xl p-6 mb-4">
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                  {/* Salary Range */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Salary Range</label>
                    <select
                      value={filters.salaryMin}
                      onChange={(e) => setFilters(prev => ({ ...prev, salaryMin: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Any Salary</option>
                      {salaryRanges.map(range => (
                        <option key={range.value} value={range.value}>{range.label}</option>
                      ))}
                    </select>
                  </div>

                  {/* Experience Level */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Experience Level</label>
                    <select
                      value={filters.experience_level}
                      onChange={(e) => setFilters(prev => ({ ...prev, experience_level: e.target.value }))}
                      className="w-full p-3 border border-gray-300 dark:border-slate-600 dark:bg-slate-700 dark:text-white rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                    >
                      <option value="">All Experience Levels</option>
                      {experienceLevels.map(level => (
                        <option key={level.value} value={level.value}>{level.label}</option>
                      ))}
                    </select>
                  </div>

                  {/* Company Size */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Company Size</label>
                    <select
                      value={filters.company}
                      onChange={(e) => setFilters(prev => ({ ...prev, company: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    >
                      <option value="">Any Size</option>
                      {companySizes.map(size => (
                        <option key={size.value} value={size.value}>{size.label}</option>
                      ))}
                    </select>
                  </div>

                  {/* Negative Keywords */}
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">Exclude Keywords</label>
                    <input
                      type="text"
                      placeholder="e.g. sales, marketing"
                      value={filters.negativeKeywords}
                      onChange={(e) => setFilters(prev => ({ ...prev, negativeKeywords: e.target.value }))}
                      className="w-full border border-gray-300 rounded-lg px-3 py-2 focus:ring-2 focus:ring-blue-500"
                    />
                  </div>
                </div>
              </div>
            )}

            {/* Results Summary */}
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                {loading ? 'Searching...' : `${filteredJobs.length.toLocaleString()} jobs found`}
                {filters.query && ` for "${filters.query}"`}
                {filters.location !== 'anywhere' && ` in ${filters.location}`}
              </span>
              <div className="flex items-center gap-4">
                <span>{appliedJobs.size} applied</span>
                <span>{savedJobs.size} saved</span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Results */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {loading ? (
          <div className="text-center py-12">
            <div className="animate-spin h-8 w-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto mb-4" />
            <p className="text-gray-600">Searching for the perfect jobs...</p>
          </div>
        ) : filteredJobs.length === 0 ? (
          <div className="text-center py-12">
            <Briefcase className="h-12 w-12 text-gray-400 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No jobs found</h3>
            <p className="text-gray-600 mb-4">Try adjusting your search criteria or filters</p>
            <button
              onClick={() => {
                setFilters({
                  query: '',
                  location: '',
                  jobType: '',
                  workType: [],
                  experience_level: '',
                  salaryMin: '',
                  salaryMax: '',
                  company: '',
                  postedWithin: '',
                  negativeKeywords: ''
                });
              }}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              Clear All Filters
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {filteredJobs.map((job) => (
              <div key={job.id} className="bg-white rounded-xl shadow-sm border border-gray-200 p-6 hover:shadow-md transition-shadow">
                <div className="flex justify-between items-start">
                  <div className="flex-1">
                    {/* Job Header */}
                    <div className="flex items-start justify-between mb-3">
                      <div className="flex-1">
                        <h3 className="text-xl font-semibold text-gray-900 mb-2 hover:text-blue-600 cursor-pointer">
                          {job.title}
                        </h3>
                        <div className="flex items-center gap-4 text-sm text-gray-600 mb-3">
                          <div className="flex items-center gap-1">
                            <Building2 className="h-4 w-4" />
                            <span className="font-medium">{typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}</span>
                          </div>
                          <div className="flex items-center gap-1">
                            <MapPin className="h-4 w-4" />
                            {job.location}
                            {job.isRemote && <span className="text-green-600 font-medium ml-1">• Remote</span>}
                          </div>
                          {formatSalary(job.salary) && (
                            <div className="flex items-center gap-1">
                              <DollarSign className="h-4 w-4" />
                              {formatSalary(job.salary)}
                            </div>
                          )}
                          <div className="flex items-center gap-1">
                            <Clock className="h-4 w-4" />
                            {getTimeAgo(job.createdAt)}
                          </div>
                        </div>
                      </div>

                      {/* Actions */}
                      <div className="flex items-center gap-2 ml-4">
                        <button
                          onClick={() => toggleSaveJob(job.id)}
                          className="p-2 hover:bg-gray-100 rounded-lg transition-colors"
                          title={savedJobs.has(job.id) ? 'Remove from saved' : 'Save job'}
                        >
                          {savedJobs.has(job.id) ? (
                            <Bookmark className="h-5 w-5 text-blue-600 fill-current" />
                          ) : (
                            <BookmarkPlus className="h-5 w-5 text-gray-400" />
                          )}
                        </button>
                      </div>
                    </div>

                    {/* Job Description */}
                    <div className="mb-4">
                      <p className="text-gray-700 line-clamp-2">
                        {job.description.length > 200 
                          ? job.description.substring(0, 200) + '...'
                          : job.description
                        }
                      </p>
                    </div>

                    {/* Job Tags */}
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.jobType && (
                        <span className="px-3 py-1 bg-blue-100 text-blue-800 text-xs rounded-full font-medium">
                          {job.jobType}
                        </span>
                      )}
                      {job.experience_level && (
                        <span className="px-3 py-1 bg-green-100 text-green-800 text-xs rounded-full font-medium">
                          {job.experience_level}
                        </span>
                      )}
                      {job.isRemote && (
                        <span className="px-3 py-1 bg-purple-100 text-purple-800 text-xs rounded-full font-medium">
                          🌍 Remote
                        </span>
                      )}
                      {job.skills?.slice(0, 3).map((skill, index) => (
                        <span key={index} className="px-3 py-1 bg-gray-100 text-gray-700 text-xs rounded-full">
                          {skill}
                        </span>
                      ))}
                      {job.skills && job.skills.length > 3 && (
                        <span className="px-3 py-1 bg-gray-100 text-gray-600 text-xs rounded-full">
                          +{job.skills.length - 3} more
                        </span>
                      )}
                    </div>

                    {/* Job Footer */}
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-4 text-sm text-gray-500">
                        {job.applicantCount && (
                          <span>{job.applicantCount} applicants</span>
                        )}
                        {appliedJobs.has(job.id) && (
                          <span className="flex items-center gap-1 text-green-600 font-medium">
                            <CheckCircle2 className="h-4 w-4" />
                            Applied
                          </span>
                        )}
                      </div>

                      {/* Action Buttons */}
                      <div className="flex gap-3">
                        <button
                          onClick={() => navigate(`/jobs/${job.id}`)}
                          className="px-4 py-2 text-blue-600 border border-blue-600 rounded-lg hover:bg-blue-50 transition-colors font-medium"
                        >
                          View Details
                        </button>
                        
                        {appliedJobs.has(job.id) ? (
                          <button
                            disabled
                            className="px-6 py-2 bg-gray-100 text-gray-500 rounded-lg cursor-not-allowed font-medium flex items-center gap-2"
                          >
                            <CheckCircle2 className="h-4 w-4" />
                            Applied
                          </button>
                        ) : (
                          <button
                            onClick={() => handleApply(job)}
                            className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors font-medium flex items-center gap-2"
                          >
                            <ExternalLink className="h-4 w-4" />
                            Apply Now
                          </button>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Application Modal */}
      {showApplicationModal && selectedJob && (
        <JobApplicationModal
          job={selectedJob}
          onClose={() => {
            setShowApplicationModal(false);
            setSelectedJob(null);
          }}
          onSubmit={handleApplicationSubmit}
        />
      )}
    </div>
  );
};

export default JobsSearchPage; 