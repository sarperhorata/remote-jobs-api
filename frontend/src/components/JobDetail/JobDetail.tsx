import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { jobService } from '../../services/AllServices';
import { Job } from '../../types/job';

// Extend the Job type to include the optional companyName property
interface ExtendedJob extends Partial<{
  companyName: string;
  _id: string;
}> {
  id: string;
  title: string;
  company?: {
    name: string;
    logo?: string;
    description?: string;
    website?: string;
  };
  description: string;
  location: string;
  type: string;
  postedAt: string;
  skills?: string[];
}

const JobDetail: React.FC = () => {
  const { id } = useParams<{ id?: string }>();
  
  // Early return if no id is provided
  if (!id) {
    return (
      <div className="container mx-auto px-4 py-8">
        <h1 className="text-2xl font-bold mb-4">No job ID provided</h1>
        <p className="mb-4">Please select a job from the job listings.</p>
        <Link to="/jobs" className="text-blue-600 hover:underline">
          Back to Jobs
        </Link>
      </div>
    );
  }

  const { data: job, isLoading } = useQuery(['job', id], () => jobService.getJobById(id), {
    enabled: !!id // Only run the query if id exists
  });

  const { data: similarJobs } = useQuery(['similarJobs', id], () => jobService.getSimilarJobs(id), {
    enabled: !!id // Only run the query if id exists
  });

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
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
              <div className="flex items-center mb-6">
                {job.company?.logo && (
                  <img 
                    src={job.company.logo} 
                    alt={job.company.name} 
                    className="w-16 h-16 rounded-full mr-4"
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
                <span>Posted {job.postedAt ? new Date(job.postedAt).toLocaleDateString() : 'Recently'}</span>
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
                onClick={() => jobService.applyForJob('current-user', id)}
              >
                Apply Now
              </button>
            </div>
          </div>

          {/* Sidebar */}
          <div>
            {/* Company Info */}
            <div className="bg-white rounded-lg shadow-md p-6 mb-6">
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

            {/* Similar Jobs */}
            <div className="bg-white rounded-lg shadow-md p-6">
              <h2 className="text-xl font-semibold mb-4">Similar Jobs</h2>
              <div className="space-y-4">
                {similarJobs?.map((similarJob: Job) => (
                  <Link 
                    key={similarJob._id || similarJob.id} 
                    to={`/jobs/${similarJob._id || similarJob.id}`}
                    className="block p-4 border rounded-lg hover:border-blue-500 transition"
                  >
                    <h3 className="font-medium">{similarJob.title}</h3>
                    <p className="text-gray-600 text-sm">{similarJob.company?.name || similarJob.companyName}</p>
                    <div className="flex flex-wrap gap-2 mt-2">
                      {similarJob.skills?.slice(0, 2).map(skill => (
                        <span 
                          key={skill} 
                          className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </Link>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default JobDetail; 