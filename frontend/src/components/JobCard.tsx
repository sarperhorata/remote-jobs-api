import React from 'react';
import { Job } from '../types/job';

interface JobCardProps {
  job: Job;
  viewMode?: 'grid' | 'list';
}

const JobCard: React.FC<JobCardProps> = ({ job, viewMode = 'grid' }) => {
  // Handle company field properly - it can be string or Company object
  const getCompanyName = () => {
    if (typeof job.company === 'string') {
      return job.company;
    }
    return job.company?.name || 'Unknown Company';
  };

  // Get company logo URL using multiple sources
  const getCompanyLogo = () => {
    const companyName = getCompanyName();
    
    // Try to extract domain from company name or use clearbit
    const cleanCompanyName = companyName.toLowerCase()
      .replace(/\s+/g, '')
      .replace(/inc\.|ltd\.|llc|corp\.?|corporation|company|co\.|gmbh|ag/gi, '');
    
    // Common domain mappings for major companies
    const domainMap: { [key: string]: string } = {
      'google': 'google.com',
      'microsoft': 'microsoft.com',
      'apple': 'apple.com',
      'amazon': 'amazon.com',
      'meta': 'meta.com',
      'facebook': 'meta.com',
      'netflix': 'netflix.com',
      'tesla': 'tesla.com',
      'spotify': 'spotify.com',
      'uber': 'uber.com',
      'airbnb': 'airbnb.com',
      'slack': 'slack.com',
      'zoom': 'zoom.us',
      'dropbox': 'dropbox.com',
      'github': 'github.com',
      'linkedin': 'linkedin.com',
      'twitter': 'twitter.com',
      'shopify': 'shopify.com',
      'stripe': 'stripe.com',
      'coinbase': 'coinbase.com'
    };

    const domain = domainMap[cleanCompanyName] || `${cleanCompanyName}.com`;
    
    return `https://logo.clearbit.com/${domain}`;
  };

  // Fallback component for when logo fails to load
  const CompanyLogoFallback = ({ companyName }: { companyName: string }) => {
    const firstLetter = companyName.charAt(0).toUpperCase();
    const colors = [
      'bg-blue-500', 'bg-green-500', 'bg-purple-500', 'bg-red-500', 
      'bg-yellow-500', 'bg-indigo-500', 'bg-pink-500', 'bg-teal-500'
    ];
    const colorIndex = firstLetter.charCodeAt(0) % colors.length;
    
    return (
      <div className={`w-12 h-12 rounded-lg ${colors[colorIndex]} flex items-center justify-center text-white font-bold text-lg`}>
        {firstLetter}
      </div>
    );
  };

  // Logo component with error handling
  const CompanyLogo = () => {
    const [imageError, setImageError] = React.useState(false);
    const companyName = getCompanyName();
    const logoUrl = getCompanyLogo();

    if (imageError) {
      return <CompanyLogoFallback companyName={companyName} />;
    }

    return (
      <img
        src={logoUrl}
        alt={`${companyName} logo`}
        className="w-12 h-12 rounded-lg object-contain bg-gray-50 p-1"
        onError={() => setImageError(true)}
        loading="lazy"
      />
    );
  };

  if (viewMode === 'list') {
    // List view - horizontal layout
    return (
      <div className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow p-4 flex items-center space-x-4">
        <div className="flex items-center space-x-3 flex-1">
          <CompanyLogo />
          <div className="flex-1">
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {job.title}
            </h3>
            <p className="text-gray-600">{getCompanyName()}</p>
            <p className="text-gray-500 text-sm">{job.location}</p>
          </div>
        </div>
        <div className="flex items-center space-x-4">
          {job.salary && (
            <div className="text-sm font-medium text-green-600">
              ${job.salary.min?.toLocaleString()} - ${job.salary.max?.toLocaleString()}
            </div>
          )}
          <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
            {job.job_type}
          </span>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors">
            View Details
          </button>
        </div>
      </div>
    );
  }

  // Grid view - vertical layout (default)
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex justify-between items-start mb-4">
        <div className="flex items-start space-x-3">
          <CompanyLogo />
          <div>
            <h3 className="text-lg font-semibold text-gray-900 mb-1">
              {job.title}
            </h3>
            <p className="text-gray-600">{getCompanyName()}</p>
          </div>
        </div>
        <span className="bg-blue-100 text-blue-800 text-xs font-medium px-2.5 py-0.5 rounded">
          {job.job_type}
        </span>
      </div>
      
      <div className="mb-4">
        <p className="text-gray-700 text-sm line-clamp-3">
          {job.description}
        </p>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="flex items-center text-sm text-gray-500">
          <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
          </svg>
          {job.location}
        </div>
        
        {job.salary && (
          <div className="text-sm font-medium text-green-600">
            ${job.salary.min?.toLocaleString()} - ${job.salary.max?.toLocaleString()}
          </div>
        )}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200">
        <div className="flex justify-between items-center">
          <div className="text-xs text-gray-500">
            Posted {job.postedAt ? new Date(job.postedAt).toLocaleDateString() : 'Recently'}
          </div>
          <button className="bg-blue-600 text-white px-4 py-2 rounded-md text-sm hover:bg-blue-700 transition-colors">
            View Details
          </button>
        </div>
      </div>
    </div>
  );
};

export default JobCard; 