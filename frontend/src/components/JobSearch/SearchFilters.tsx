import React, { useState, useEffect } from 'react';
import { Search, MapPin, Briefcase } from 'lucide-react';
import LocationAutocomplete from '../LocationAutocomplete';

interface Location {
  name: string;
  country?: string;
  type?: 'city' | 'country' | 'continent' | 'remote' | 'worldwide';
  cached_at?: string;
  flag?: string;
}

interface Filters {
  query: string;
  location: string;
  jobType: string;
  workType: string;
  experience_level: string;
  salaryMin: string;
  salaryMax: string;
  company: string;
  postedWithin: string;
  experiences?: string[];
  postedAge?: string;
  salaryRange?: string;
  page?: number;
}

interface SearchFiltersProps {
  filters: Filters;
  onFiltersChange: (filters: Partial<Filters>) => void;
  availableCompanies?: Array<{name: string; count: number}>;
  availableLocations?: Array<{name: string; count: number}>;
  selectedLocation?: Location | null;
  onLocationChange?: (location: Location | null) => void;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({ 
  filters, 
  onFiltersChange,
  availableCompanies = [],
  availableLocations = [],
  selectedLocation,
  onLocationChange
}) => {
  const [localSearchQuery, setLocalSearchQuery] = useState(filters.query);
  const [showWorkTypeDropdown, setShowWorkTypeDropdown] = useState(false);
  const [showJobTypeDropdown, setShowJobTypeDropdown] = useState(false);
  const [showExperienceDropdown, setShowExperienceDropdown] = useState(false);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);
  const [showCompanyDropdown, setShowCompanyDropdown] = useState(false);
  
  // Update local search query when prop changes
  useEffect(() => {
    setLocalSearchQuery(filters.query);
  }, [filters.query]);

  const handleSearchSubmit = () => {
    onFiltersChange({ query: localSearchQuery });
  };

  // Handle enter key for search
  const handleSearchKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      handleSearchSubmit();
    }
  };

  // Click outside to close dropdowns
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      setShowWorkTypeDropdown(false);
      setShowJobTypeDropdown(false);
      setShowExperienceDropdown(false);
      setShowLocationDropdown(false);
      setShowCompanyDropdown(false);
    };

    if (showWorkTypeDropdown || showJobTypeDropdown || showExperienceDropdown || showLocationDropdown || showCompanyDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => document.removeEventListener('mousedown', handleClickOutside);
    }
  }, [showWorkTypeDropdown, showJobTypeDropdown, showExperienceDropdown, showLocationDropdown, showCompanyDropdown]);

  // Initialize experiences array if not exists
  const experiences = filters.experiences || [];

  // Work type options
  const workTypeOptions = [
    { value: 'remote', label: 'Remote' },
    { value: 'hybrid', label: 'Hybrid' },
    { value: 'on-site', label: 'On-site' }
  ];

  // Job type options
  const jobTypeOptions = [
    { value: 'full-time', label: 'Full-time' },
    { value: 'part-time', label: 'Part-time' },
    { value: 'contract', label: 'Contract' },
    { value: 'freelance', label: 'Freelance' }
  ];

  // Experience level options
  const experienceOptions = [
    { value: 'entry', label: 'Entry Level' },
    { value: 'mid', label: 'Mid Level' },
    { value: 'senior', label: 'Senior' },
    { value: 'lead', label: 'Lead/Manager' }
  ];

  return (
    <div className="space-y-6 p-6 bg-white dark:bg-gray-800 rounded-lg shadow">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h3>

      {/* Search Query */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Search
        </label>
        <div className="relative">
          <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={localSearchQuery}
            onChange={(e) => setLocalSearchQuery(e.target.value)}
            placeholder="Job title, keywords..."
            className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
            onKeyDown={handleSearchKeyPress}
          />
        </div>
      </div>

      {/* Work Type Multi-Select */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Work Type</label>
        <div 
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded text-sm cursor-pointer flex justify-between items-center"
          onClick={() => setShowWorkTypeDropdown(!showWorkTypeDropdown)}
        >
          <span>{filters.workType || "Select work type..."}</span>
          <svg className={`w-4 h-4 text-gray-400 transition-transform ${showWorkTypeDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        
        {showWorkTypeDropdown && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded shadow-lg z-50 max-h-60 overflow-y-auto">
            {workTypeOptions.map(({ value, label }) => (
              <div
                key={value}
                className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer flex items-center"
              >
                <input
                  type="radio"
                  name="workType"
                  value={value}
                  checked={filters.workType === value}
                  onChange={(e) => {
                    onFiltersChange({ ...filters, workType: e.target.value });
                    setShowWorkTypeDropdown(false);
                  }}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 mr-2"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Job Type */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Job Type</label>
        <div 
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded text-sm cursor-pointer flex justify-between items-center"
          onClick={() => setShowJobTypeDropdown(!showJobTypeDropdown)}
        >
          <span>{filters.jobType || "Select job type..."}</span>
          <svg className={`w-4 h-4 text-gray-400 transition-transform ${showJobTypeDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        
        {showJobTypeDropdown && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded shadow-lg z-50 max-h-60 overflow-y-auto">
            {jobTypeOptions.map(({ value, label }) => (
              <div
                key={value}
                className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer flex items-center"
              >
                <input
                  type="radio"
                  name="jobType"
                  value={value}
                  checked={filters.jobType === value}
                  onChange={(e) => {
                    onFiltersChange({ ...filters, jobType: e.target.value });
                    setShowJobTypeDropdown(false);
                  }}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 mr-2"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Experience Level */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Experience Level</label>
        <div 
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded text-sm cursor-pointer flex justify-between items-center"
          onClick={() => setShowExperienceDropdown(!showExperienceDropdown)}
        >
          <span>
            {experiences.length === 0 
              ? "Select experience..." 
              : `${experiences.length} selected`}
          </span>
          <svg className={`w-4 h-4 text-gray-400 transition-transform ${showExperienceDropdown ? 'rotate-180' : ''}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
          </svg>
        </div>
        
        {showExperienceDropdown && (
          <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-700 border border-gray-300 dark:border-gray-600 rounded shadow-lg z-50 max-h-60 overflow-y-auto">
            {experienceOptions.map(({ value, label }) => (
              <div
                key={value}
                className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-600 cursor-pointer flex items-center"
                onClick={() => {
                  const newExperiences = experiences.includes(value)
                    ? experiences.filter(t => t !== value)
                    : [...experiences, value];
                  onFiltersChange({ ...filters, experiences: newExperiences });
                }}
              >
                <input
                  type="checkbox"
                  readOnly
                  checked={experiences.includes(value)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded mr-2 pointer-events-none"
                />
                <span className="text-sm text-gray-700 dark:text-gray-300">{label}</span>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Posted */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Posted</label>
        <select
          value={filters.postedAge || filters.postedWithin || ''}
          onChange={(e) => onFiltersChange({ ...filters, postedWithin: e.target.value, postedAge: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Any time</option>
          <option value="1DAY">24h</option>
          <option value="3DAYS">3 days</option>
          <option value="7DAYS">1 week</option>
          <option value="30DAYS">1 month</option>
        </select>
      </div>

      {/* Salary */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Salary</label>
        <select
          value={filters.salaryRange || ''}
          onChange={(e) => onFiltersChange({ ...filters, salaryRange: e.target.value })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Any</option>
          <option value="36000-72000">$36k - $72k</option>
          <option value="72000-108000">$72k - $108k</option>
          <option value="108000-144000">$108k - $144k</option>
          <option value="144000-180000">$144k - $180k</option>
          <option value="180000+">$180k+</option>
        </select>
      </div>

      {/* Location */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Location</label>
        <LocationAutocomplete
          selectedLocation={selectedLocation}
          onLocationChange={onLocationChange}
        />
      </div>

      {/* Company */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Company</label>
        <div className="relative">
          <Briefcase className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
          <input
            type="text"
            value={filters.company}
            onChange={(e) => onFiltersChange({ ...filters, company: e.target.value })}
            placeholder="Company name..."
            className="w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded text-sm focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
      </div>

      {/* Clear Filters */}
      <button
        onClick={() => onFiltersChange({ 
          query: '', 
          location: '', 
          jobType: '', 
          workType: '', 
          experiences: [], 
          company: '', 
          postedAge: '',
          salaryRange: '' 
        })}
        className="w-full px-4 py-2 text-sm text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200 border border-gray-300 dark:border-gray-600 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
      >
        Clear All Filters
      </button>
    </div>
  );
};

export default SearchFilters; 