import React from 'react';
import { Job } from '../types/job';
import DOMPurify from 'dompurify';

interface JobDetailProps {
  job: Job;
  similarJobs?: Job[];
  onApply: (jobId: string) => void;
}

const JobDetail: React.FC<JobDetailProps> = ({ job, similarJobs = [], onApply }) => {
  // Helper functions to handle company data
  const getCompanyName = () => {
    if (typeof job.company === 'string') {
      return job.company;
    }
    return job.company?.name || job.companyName || 'Unknown Company';
  };

  const getCompanyLogo = () => {
    if (typeof job.company === 'object' && job.company?.logo) {
      return job.company.logo;
    }
    return job.company_logo || job.companyLogo;
  };

  const companyLogo = getCompanyLogo();

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        {companyLogo && (
          <img 
            src={companyLogo} 
            alt={getCompanyName()} 
            className="w-16 h-16 rounded mr-4"
          />
        )}
        <div>
          <h1 className="text-2xl font-bold">{job.title}</h1>
          <p className="text-gray-600">{getCompanyName()}</p>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-6">
        <span>{job.location}</span>
        <span>•</span>
        <span>{job.job_type}</span>
        <span>•</span>
        <span>Posted {job.postedAt ? new Date(job.postedAt).toLocaleDateString() : 'Recently'}</span>
      </div>
      
      <div className="prose max-w-none mb-6">
        <h2 className="text-xl font-semibold mb-4">Job Description</h2>
        <div className="whitespace-pre-wrap">{job.description}</div>
      </div>
      
      <div className="mb-6">
        <h2 className="text-xl font-semibold mb-4">Required Skills</h2>
        <div className="flex flex-wrap gap-2">
          {job.skills?.map(skill => (
            <span 
              key={skill} 
              className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full"
            >
              {skill}
            </span>
          ))}
        </div>
      </div>
      
      <button 
        className="w-full bg-blue-600 text-white py-3 rounded-lg font-medium hover:bg-blue-700 transition"
        onClick={() => onApply(job._id || job.id || '')}
      >
        Apply Now
      </button>
      
      {similarJobs.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Similar Jobs</h2>
          <div className="space-y-4">
            {similarJobs.map(similarJob => {
              const getSimilarCompanyName = () => {
                if (typeof similarJob.company === 'string') {
                  return similarJob.company;
                }
                return similarJob.company?.name || similarJob.companyName || 'Unknown Company';
              };

              return (
                <div 
                  key={similarJob._id || similarJob.id} 
                  className="p-4 border rounded-lg hover:border-blue-500 transition cursor-pointer"
                  onClick={() => window.location.href = `/jobs/${similarJob._id || similarJob.id}`}
                >
                  <h3 className="font-medium">{similarJob.title}</h3>
                  <p className="text-gray-600 text-sm">{getSimilarCompanyName()}</p>
                  <div className="flex flex-wrap gap-2 mt-2">
                    {similarJob.skills?.slice(0, 3).map(skill => (
                      <span 
                        key={skill} 
                        className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDetail; 