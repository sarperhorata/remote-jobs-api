import React from 'react';
import { Link } from 'react-router-dom';
import { Job } from '../../types/job';

interface JobCardProps {
  job: Job;
}

const JobCard: React.FC<JobCardProps> = ({ job }) => {
  // Helper function to get company name
  const getCompanyName = () => {
    if (typeof job.company === 'string') {
      return job.company;
    }
    return job.company?.name || job.companyName || 'Unknown Company';
  };

  // Helper function to get company logo
  const getCompanyLogo = () => {
    if (typeof job.company === 'object' && job.company?.logo) {
      return job.company.logo;
    }
    return job.company_logo || job.companyLogo;
  };

  const companyLogo = getCompanyLogo();

  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
      <div className="flex items-start mb-4">
        {companyLogo && (
          <img 
            src={companyLogo} 
            alt={getCompanyName()} 
            className="w-12 h-12 rounded-full mr-4"
          />
        )}
        <div>
          <h3 className="font-semibold text-lg">{job.title}</h3>
          <p className="text-gray-600">{getCompanyName()}</p>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="text-sm text-gray-500">{job.location}</span>
        <span className="text-sm text-gray-500">•</span>
        <span className="text-sm text-gray-500">{job.job_type}</span>
      </div>
      
      <div className="flex flex-wrap gap-2 mb-4">
        {job.skills?.slice(0, 3).map(skill => (
          <span 
            key={skill} 
            className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
          >
            {skill}
          </span>
        ))}
        {job.skills && job.skills.length > 3 && (
          <span className="text-xs text-gray-500">+{job.skills.length - 3} more</span>
        )}
      </div>
      
      <div className="flex justify-between items-center">
        <Link 
          to={`/jobs/${job._id || job.id}`}
          className="text-blue-600 hover:underline"
        >
          View Details
        </Link>
        <span className="text-xs text-gray-500">
          Posted {job.postedAt ? new Date(job.postedAt).toLocaleDateString() : 'Recently'}
        </span>
      </div>
    </div>
  );
};

export default JobCard; 