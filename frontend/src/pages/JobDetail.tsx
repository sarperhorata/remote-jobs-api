import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { jobService } from '../services/AllServices';
import { Job } from '../types/job';
import JobDetail from '../components/JobDetail';

const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  
  const { data: job, isLoading } = useQuery(['job', id], () => jobService.getJobById(id || ''));

  const { data: similarJobs } = useQuery<Job[]>(['similarJobs', id], () => 
    jobService.getSimilarJobs(id || '')
  );

  const handleApply = (jobId: string) => {
    // Handle job application logic
    console.log(`Applying for job: ${jobId}`);
    // Add actual application logic here
  };

  if (isLoading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">Job not found</h1>
        <Link to="/jobs" className="text-blue-600 hover:underline">
          Back to Jobs
        </Link>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            <JobDetail 
              job={job} 
              similarJobs={similarJobs || []} 
              onApply={handleApply} 
            />
          </div>

          {/* Sidebar */}
          <div>
            {/* Company Info */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">About {job.company?.name || job.companyName}</h2>
              <p className="text-gray-600 mb-4">{job.company?.description || ''}</p>
              {job.company?.website && (
                <a 
                  href={job.company.website} 
                  target="_blank" 
                  rel="noopener noreferrer"
                  className="text-blue-600 hover:underline"
                >
                  Visit Website
                </a>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetailPage; 