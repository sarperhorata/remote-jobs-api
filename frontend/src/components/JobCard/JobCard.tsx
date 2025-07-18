import React, { useState } from 'react';
import { MapPin, Clock, ExternalLink } from 'lucide-react';
import { Job } from '../../types/job';
import SalaryEstimation from '../SalaryEstimation';

interface JobCardProps {
  job: Job;
}

const JobCard: React.FC<JobCardProps> = ({ job }) => {
  const [showSalaryEstimation, setShowSalaryEstimation] = useState(false);

  // Format posted date
  const formatPostedDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffTime = Math.abs(now.getTime() - date.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
    
    if (diffDays === 1) return '1 day ago';
    if (diffDays < 7) return `${diffDays} days ago`;
    if (diffDays < 30) return `${Math.ceil(diffDays / 7)} weeks ago`;
    return `${Math.ceil(diffDays / 30)} months ago`;
  };

  // Format salary
  const formatSalary = (salary: any) => {
    if (!salary) return null;
    if (typeof salary === 'string') return salary;
    if (typeof salary === 'object') {
      if (salary.min && salary.max) {
        const isEstimated = salary.is_estimated || salary.isEstimated;
        const estimatedText = isEstimated ? ' (est.)' : '';
        return `$${salary.min.toLocaleString()} - $${salary.max.toLocaleString()}${estimatedText}`;
      }
      if (salary.amount) {
        const isEstimated = salary.is_estimated || salary.isEstimated;
        const estimatedText = isEstimated ? ' (est.)' : '';
        return `$${salary.amount.toLocaleString()}${estimatedText}`;
      }
    }
    return null;
  };

  // Check if job has salary information
  const hasSalaryInfo = (): boolean => {
    if (job.salary) return true;
    if (job.salary_min && job.salary_max) return true;
    return false;
  };

  // Get work type display
  const getWorkTypeDisplay = () => {
    if (job.isRemote || job.remote_type === 'remote' || job.work_type === 'remote') {
      return 'Remote';
    }
    if (job.remote_type === 'hybrid' || job.work_type === 'hybrid') {
      return 'Hybrid';
    }
    return 'On-site';
  };

  // Get location display
  const getLocationDisplay = () => {
    if (job.isRemote || job.remote_type === 'remote' || job.work_type === 'remote') {
      return 'Remote';
    }
    return job.location || 'Location not specified';
  };

  const handleCompanyClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    const company = typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company';
    window.location.href = `/search?company=${encodeURIComponent(company)}`;
  };

  const handleJobClick = () => {
    // Build apply URL
    let applyUrl = '';
    
    if (job.apply_url) {
      applyUrl = job.apply_url;
    } else if (job.source_url) {
      applyUrl = job.source_url;
    } else if (job.url) {
      applyUrl = job.url;
    } else {
      // Fallback to a generic job search
      const companyName = typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company';
      applyUrl = `https://www.google.com/search?q="${encodeURIComponent(job.title)}"+at+"${encodeURIComponent(companyName)}"`;
    }

    // Open in new tab
    window.open(applyUrl, '_blank', 'noopener,noreferrer');
  };

  const handleSalaryEstimationClick = (e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();
    setShowSalaryEstimation(true);
  };

  return (
    <div className="group bg-white dark:bg-slate-800 rounded-xl shadow-sm border border-gray-200 dark:border-slate-600 p-6 hover:shadow-xl hover:border-blue-200 dark:hover:border-blue-700 transition-all duration-300 cursor-pointer transform hover:-translate-y-1 relative overflow-hidden"
         onClick={handleJobClick}>
      
      {/* Subtle gradient overlay on hover */}
      <div className="absolute inset-0 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-blue-900/10 dark:to-purple-900/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 rounded-xl"></div>
      
      {/* Content */}
      <div className="relative z-10">
        {/* Header */}
        <div className="flex justify-between items-start mb-3">
          <div className="flex-1 min-w-0">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1 line-clamp-2 group-hover:text-blue-600 dark:group-hover:text-blue-400 transition-colors duration-200">
              {job.title}
            </h3>
            <button
              onClick={handleCompanyClick}
              className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline font-medium transition-colors duration-200"
            >
              {typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}
            </button>
          </div>
          <div className="flex items-center text-gray-500 dark:text-gray-400 text-sm ml-4 bg-gray-50 dark:bg-slate-700 px-2 py-1 rounded-full">
            <Clock className="w-3 h-3 mr-1" />
            {formatPostedDate(job.posted_date || job.created_at || new Date().toISOString())}
          </div>
        </div>

        {/* Tags Row */}
        <div className="flex flex-wrap gap-2 mb-3">
          <span className="px-3 py-1 bg-gradient-to-r from-blue-100 to-blue-200 dark:from-blue-900 dark:to-blue-800 text-blue-800 dark:text-blue-200 text-xs rounded-full font-medium">
            {job.job_type || 'Full-time'}
          </span>
          <span className="px-3 py-1 bg-gradient-to-r from-green-100 to-emerald-200 dark:from-green-900 dark:to-emerald-800 text-green-800 dark:text-green-200 text-xs rounded-full font-medium">
            {getWorkTypeDisplay()}
          </span>
          <span className="px-3 py-1 bg-gradient-to-r from-gray-100 to-gray-200 dark:from-gray-700 dark:to-gray-600 text-gray-800 dark:text-gray-200 text-xs rounded-full flex items-center font-medium">
            <MapPin className="w-3 h-3 mr-1" />
            {getLocationDisplay()}
          </span>
        </div>

        {/* Description */}
        {job.description && (
          <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-3 leading-relaxed" 
             title={job.description}>
            {job.description}
          </p>
        )}

        {/* Skills */}
        {job.skills && job.skills.length > 0 && (
          <div className="flex flex-wrap gap-1 mb-3">
            {job.skills.slice(0, 4).map((skill, index) => (
              <span key={index} className="px-2 py-1 bg-purple-50 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-xs rounded-md font-medium">
                {skill}
              </span>
            ))}
            {job.skills.length > 4 && (
              <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs rounded-md">
                +{job.skills.length - 4} more
              </span>
            )}
          </div>
        )}

        {/* Salary Section */}
        <div className="mb-3">
          {hasSalaryInfo() ? (
            <div className="text-sm font-semibold bg-gradient-to-r from-green-600 to-emerald-600 bg-clip-text text-transparent">
              {formatSalary(job.salary) || 
               (job.salary_min && job.salary_max ? 
                `$${job.salary_min.toLocaleString()} - $${job.salary_max.toLocaleString()}${job.is_estimated ? ' (est.)' : ''}` : 
                'Maaş bilgisi mevcut')}
            </div>
          ) : (
            <div className="flex items-center space-x-2">
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Maaş bilgisi mevcut değil
              </span>
              {!showSalaryEstimation && (
                <button
                  onClick={handleSalaryEstimationClick}
                  className="inline-flex items-center px-2 py-1 text-xs font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-md hover:bg-blue-100 hover:border-blue-300 transition-colors"
                >
                  <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                  </svg>
                  Tahmin Et
                </button>
              )}
            </div>
          )}
          
          {/* Salary Estimation Component */}
          {showSalaryEstimation && (
            <div className="mt-2">
              <SalaryEstimation
                jobTitle={job.title}
                location={job.location}
                companySize={job.company_size}
                experienceLevel={job.experience_level}
                showDetails={false}
                className="text-sm"
              />
            </div>
          )}
        </div>

        {/* Footer */}
        <div className="flex justify-between items-center pt-3 border-t border-gray-100 dark:border-slate-600">
          <div className="flex items-center text-gray-600 dark:text-gray-300">
            {/* Salary info moved to above section */}
          </div>
          <div className="flex items-center text-blue-600 dark:text-blue-400 text-sm font-medium group-hover:text-blue-700 dark:group-hover:text-blue-300 transition-colors duration-200">
            <span>Apply Now</span>
            <ExternalLink className="w-4 h-4 ml-1 group-hover:translate-x-1 transition-transform duration-200" />
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobCard; 