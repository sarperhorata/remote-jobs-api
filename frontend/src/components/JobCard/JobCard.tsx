import React from 'react';
import { MapPin, Clock, ExternalLink } from 'lucide-react';
import { Job } from '../../types/job';

interface JobCardProps {
  job: Job;
}

const JobCard: React.FC<JobCardProps> = ({ job }) => {
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
        return `$${salary.min.toLocaleString()} - $${salary.max.toLocaleString()}`;
      }
      if (salary.amount) {
        return `$${salary.amount.toLocaleString()}`;
      }
    }
    return null;
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

  return (
    <div className="bg-white dark:bg-slate-800 rounded-lg shadow-sm border border-gray-200 dark:border-slate-600 p-4 hover:shadow-md transition-shadow duration-200 cursor-pointer"
         onClick={handleJobClick}>
      {/* Header */}
      <div className="flex justify-between items-start mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1 line-clamp-2 hover:text-blue-600 dark:hover:text-blue-400">
            {job.title}
          </h3>
          <button
            onClick={handleCompanyClick}
            className="text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 hover:underline font-medium"
          >
            {typeof job.company === 'string' ? job.company : job.company?.name || 'Unknown Company'}
          </button>
        </div>
        <div className="flex items-center text-gray-500 dark:text-gray-400 text-sm ml-4">
          <Clock className="w-4 h-4 mr-1" />
          {formatPostedDate(job.posted_date || job.created_at || new Date().toISOString())}
        </div>
      </div>

      {/* Tags Row */}
      <div className="flex flex-wrap gap-2 mb-3">
        <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 text-xs rounded-full">
          {job.job_type || 'Full-time'}
        </span>
        <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 text-xs rounded-full">
          {getWorkTypeDisplay()}
        </span>
        <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 text-xs rounded-full flex items-center">
          <MapPin className="w-3 h-3 mr-1" />
          {getLocationDisplay()}
        </span>
      </div>

      {/* Description */}
      {job.description && (
        <p className="text-gray-600 dark:text-gray-300 text-sm mb-3 line-clamp-3" 
           title={job.description}>
          {job.description}
        </p>
      )}

      {/* Skills */}
      {job.skills && job.skills.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-3">
          {job.skills.slice(0, 4).map((skill, index) => (
            <span key={index} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded">
              {skill}
            </span>
          ))}
          {job.skills.length > 4 && (
            <span className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-500 dark:text-gray-400 text-xs rounded">
              +{job.skills.length - 4} more
            </span>
          )}
        </div>
      )}

      {/* Footer */}
      <div className="flex justify-between items-center pt-3 border-t border-gray-100 dark:border-slate-600">
        <div className="flex items-center text-gray-600 dark:text-gray-300">
          {formatSalary(job.salary) && (
            <span className="text-sm font-medium">
              {formatSalary(job.salary)}
            </span>
          )}
        </div>
        <div className="flex items-center text-blue-600 dark:text-blue-400 text-sm">
          <span>Apply Now</span>
          <ExternalLink className="w-4 h-4 ml-1" />
        </div>
      </div>
    </div>
  );
};

export default JobCard; 