import React, { useState, useRef } from 'react';
import { getApiUrl } from '../../utils/apiConfig';

interface SearchFiltersProps {
  filters: {
    workTypes: string[];
    jobTypes: string[];
    experiences: string[];
    postedAge: string;
    sortBy: string;
    salaryRange: string;
    location: string;
    company: string;
    page: number;
    limit: number;
  };
  onFiltersChange: (filters: any) => void;
  availableCompanies?: string[];
  availableLocations?: string[];
}

interface AutocompleteItem {
  name: string;
  count: number;
}

const SearchFilters: React.FC<SearchFiltersProps> = ({
  filters,
  onFiltersChange,
  availableCompanies = [],
  availableLocations = []
}) => {
  const [locationSuggestions, setLocationSuggestions] = useState<AutocompleteItem[]>([]);
  const [companySuggestions, setCompanySuggestions] = useState<AutocompleteItem[]>([]);
  const [locationLoading, setLocationLoading] = useState(false);
  const [companyLoading, setCompanyLoading] = useState(false);
  const [showLocationDropdown, setShowLocationDropdown] = useState(false);
  const [showCompanyDropdown, setShowCompanyDropdown] = useState(false);
  
  const locationTimeoutRef = useRef<NodeJS.Timeout>();
  const companyTimeoutRef = useRef<NodeJS.Timeout>();

  // Handle work type change
  const handleWorkTypeChange = (workType: string, checked: boolean) => {
    const newWorkTypes = checked
      ? [...filters.workTypes, workType]
      : filters.workTypes.filter(type => type !== workType);
    onFiltersChange({ ...filters, workTypes: newWorkTypes, page: 1 });
  };

  // Handle job type change
  const handleJobTypeChange = (jobType: string, checked: boolean) => {
    const newJobTypes = checked
      ? [...filters.jobTypes, jobType]
      : filters.jobTypes.filter(type => type !== jobType);
    onFiltersChange({ ...filters, jobTypes: newJobTypes, page: 1 });
  };

  // Handle experience change
  const handleExperienceChange = (experience: string, checked: boolean) => {
    const newExperiences = checked
      ? [...filters.experiences, experience]
      : filters.experiences.filter(exp => exp !== experience);
    onFiltersChange({ ...filters, experiences: newExperiences, page: 1 });
  };

  // Fetch location suggestions
  const fetchLocationSuggestions = async (query: string) => {
    if (!query || query.length < 2) {
      setLocationSuggestions([]);
      setShowLocationDropdown(false);
      return;
    }

    setLocationLoading(true);
    try {
      const apiUrl = await getApiUrl();
      const finalApiUrl = apiUrl.includes('localhost:8002') 
        ? apiUrl.replace('localhost:8002', 'localhost:8001')
        : apiUrl;
      
      const response = await fetch(`${finalApiUrl}/jobs/locations/search?q=${encodeURIComponent(query)}&limit=5`);
      if (response.ok) {
        const data = await response.json();
        setLocationSuggestions(data);
        setShowLocationDropdown(data.length > 0);
      }
    } catch (error) {
      console.error('Error fetching location suggestions:', error);
    } finally {
      setLocationLoading(false);
    }
  };

  // Fetch company suggestions
  const fetchCompanySuggestions = async (query: string) => {
    if (!query || query.length < 2) {
      setCompanySuggestions([]);
      setShowCompanyDropdown(false);
      return;
    }

    setCompanyLoading(true);
    try {
      const apiUrl = await getApiUrl();
      const finalApiUrl = apiUrl.includes('localhost:8002') 
        ? apiUrl.replace('localhost:8002', 'localhost:8001')
        : apiUrl;
      
      const response = await fetch(`${finalApiUrl}/jobs/companies/search?q=${encodeURIComponent(query)}&limit=5`);
      if (response.ok) {
        const data = await response.json();
        setCompanySuggestions(data);
        setShowCompanyDropdown(data.length > 0);
      }
    } catch (error) {
      console.error('Error fetching company suggestions:', error);
    } finally {
      setCompanyLoading(false);
    }
  };

  // Handle location input change with debounce
  const handleLocationChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onFiltersChange({ ...filters, location: value, page: 1 });

    // Clear previous timeout
    if (locationTimeoutRef.current) {
      clearTimeout(locationTimeoutRef.current);
    }

    // Set new timeout for search
    if (value.trim()) {
      locationTimeoutRef.current = setTimeout(() => {
        fetchLocationSuggestions(value.trim());
      }, 1000); // 1 second delay
    } else {
      setLocationSuggestions([]);
      setShowLocationDropdown(false);
    }
  };

  // Handle company input change with debounce
  const handleCompanyChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    onFiltersChange({ ...filters, company: value, page: 1 });

    // Clear previous timeout
    if (companyTimeoutRef.current) {
      clearTimeout(companyTimeoutRef.current);
    }

    // Set new timeout for search
    if (value.trim()) {
      companyTimeoutRef.current = setTimeout(() => {
        fetchCompanySuggestions(value.trim());
      }, 1000); // 1 second delay
    } else {
      setCompanySuggestions([]);
      setShowCompanyDropdown(false);
    }
  };

  // Clear all filters
  const clearAllFilters = () => {
    onFiltersChange({
      workTypes: [],
      jobTypes: [],
      experiences: [],
      postedAge: '30DAYS',
      sortBy: 'relevance',
      salaryRange: '',
      location: '',
      company: '',
      page: 1,
      limit: filters.limit
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Filters</h3>
        <button
          onClick={clearAllFilters}
          className="text-sm text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300"
        >
          Clear All
        </button>
      </div>

      {/* Work Type */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Work Type</h4>
        <div className="space-y-2">
          {[
            { value: 'remote', label: 'Remote' },
            { value: 'hybrid', label: 'Hybrid' },
            { value: 'on-site', label: 'On-site' }
          ].map(({ value, label }) => (
            <label key={value} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.workTypes.includes(value)}
                onChange={(e) => handleWorkTypeChange(value, e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
              />
              <span className="ml-3 text-sm text-gray-600 dark:text-gray-400">{label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Job Type */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Job Type</h4>
        <div className="space-y-2">
          {[
            { value: 'full-time', label: 'Full-time' },
            { value: 'part-time', label: 'Part-time' },
            { value: 'contract', label: 'Contract' },
            { value: 'freelance', label: 'Freelance' }
          ].map(({ value, label }) => (
            <label key={value} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.jobTypes.includes(value)}
                onChange={(e) => handleJobTypeChange(value, e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
              />
              <span className="ml-3 text-sm text-gray-600 dark:text-gray-400">{label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Experience Level */}
      <div>
        <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3">Experience Level</h4>
        <div className="space-y-2">
          {[
            { value: 'entry', label: 'Entry (0-2y)' },
            { value: 'mid', label: 'Mid (3-5y)' },
            { value: 'senior', label: 'Senior (6y+)' },
            { value: 'lead', label: 'Lead/Manager' }
          ].map(({ value, label }) => (
            <label key={value} className="flex items-center">
              <input
                type="checkbox"
                checked={filters.experiences.includes(value)}
                onChange={(e) => handleExperienceChange(value, e.target.checked)}
                className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 dark:border-gray-600 rounded"
              />
              <span className="ml-3 text-sm text-gray-600 dark:text-gray-400">{label}</span>
            </label>
          ))}
        </div>
      </div>

      {/* Posted Within */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Posted Within
        </label>
        <select
          value={filters.postedAge}
          onChange={(e) => onFiltersChange({ ...filters, postedAge: e.target.value, page: 1 })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="1DAY">24 hours</option>
          <option value="3DAYS">3 days</option>
          <option value="7DAYS">1 week</option>
          <option value="30DAYS">1 month</option>
        </select>
      </div>

      {/* Salary Range */}
      <div>
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Salary Range
        </label>
        <select
          value={filters.salaryRange}
          onChange={(e) => onFiltersChange({ ...filters, salaryRange: e.target.value, page: 1 })}
          className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
        >
          <option value="">Any</option>
          <option value="0-36000">$0-36K</option>
          <option value="36000-72000">$36K-72K</option>
          <option value="72000-108000">$72K-108K</option>
          <option value="108000-144000">$108K-144K</option>
          <option value="144000-180000">$144K-180K</option>
          <option value="180000+">$180K+</option>
        </select>
      </div>

      {/* Location with Autocomplete */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Location
        </label>
        <div className="relative">
          <input
            type="text"
            value={filters.location}
            onChange={handleLocationChange}
            placeholder="City, country..."
            className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
          />
          {locationLoading && (
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
              <div role="status" className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </div>
        
        {showLocationDropdown && locationSuggestions.length > 0 && (
          <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-40 overflow-y-auto">
            {locationSuggestions.map((suggestion, index) => (
              <div
                key={index}
                className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-sm"
                onClick={() => {
                  onFiltersChange({ ...filters, location: suggestion.name, page: 1 });
                  setShowLocationDropdown(false);
                }}
              >
                <div className="flex justify-between items-center">
                  <span className="text-gray-900 dark:text-gray-100">{suggestion.name}</span>
                  <span className="text-gray-500 dark:text-gray-400 text-xs">{suggestion.count}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Company with Autocomplete */}
      <div className="relative">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Company
        </label>
        <div className="relative">
          <input
            type="text"
            value={filters.company}
            onChange={handleCompanyChange}
            placeholder="Company name..."
            className="w-full px-3 py-2 pr-8 border border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-gray-100 rounded-lg text-sm focus:ring-blue-500 focus:border-blue-500"
          />
          {companyLoading && (
            <div className="absolute right-2 top-1/2 transform -translate-y-1/2">
              <div className="w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
            </div>
          )}
        </div>
        
        {showCompanyDropdown && companySuggestions.length > 0 && (
          <div className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-40 overflow-y-auto">
            {companySuggestions.map((suggestion, index) => (
              <div
                key={index}
                className="px-3 py-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer text-sm"
                onClick={() => {
                  onFiltersChange({ ...filters, company: suggestion.name, page: 1 });
                  setShowCompanyDropdown(false);
                }}
              >
                <div className="flex justify-between items-center">
                  <span className="text-gray-900 dark:text-gray-100">{suggestion.name}</span>
                  <span className="text-gray-500 dark:text-gray-400 text-xs">{suggestion.count}</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default SearchFilters; 