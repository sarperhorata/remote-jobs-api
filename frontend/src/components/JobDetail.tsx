import React from 'react';
import { Job } from '../types/job';

interface JobDetailProps {
  job: Job;
  similarJobs?: Job[];
  onApply: (jobId: string) => void;
}

const JobDetail: React.FC<JobDetailProps> = ({ job, similarJobs = [], onApply }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <div className="flex items-center mb-6">
        {job.company?.logo && (
          <img 
            src={job.company.logo} 
            alt={job.company.name} 
            className="w-16 h-16 rounded mr-4"
          />
        )}
        <div>
          <h1 className="text-2xl font-bold">{job.title}</h1>
          <p className="text-gray-600">{job.company?.name || job.companyName}</p>
        </div>
      </div>
      
      <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-6">
        <span>{job.location}</span>
        <span>•</span>
        <span>{job.type}</span>
        <span>•</span>
        <span>Posted {new Date(job.postedAt).toLocaleDateString()}</span>
      </div>
      
      <div className="prose max-w-none mb-6">
        <h2 className="text-xl font-semibold mb-4">Job Description</h2>
        <div dangerouslySetInnerHTML={{ __html: job.description }} />
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
        onClick={() => onApply(job._id || job.id)}
      >
        Apply Now
      </button>
      
      {similarJobs.length > 0 && (
        <div className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Similar Jobs</h2>
          <div className="space-y-4">
            {similarJobs.map(similarJob => (
              <div 
                key={similarJob._id || similarJob.id} 
                className="p-4 border rounded-lg hover:border-blue-500 transition cursor-pointer"
                onClick={() => window.location.href = `/jobs/${similarJob._id || similarJob.id}`}
              >
                <h3 className="font-medium">{similarJob.title}</h3>
                <p className="text-gray-600 text-sm">{similarJob.company?.name || similarJob.companyName}</p>
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
            ))}
          </div>
        </div>
      )}
    </div>
  );
};

export default JobDetail; 