import React from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import { jobService } from '../services/AllServices';

const JobList: React.FC<{
  filters?: any;
  limit?: number;
  onJobSelected?: (job: any) => void;
}> = ({ filters = {}, limit, onJobSelected }) => {
  const { data, isLoading, error } = useQuery(['jobs', filters], () => jobService.getJobs(filters));

  if (isLoading) return <div>Loading jobs...</div>;
  if (error) return <div>Error loading jobs</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Latest Jobs</h2>
      <div className="space-y-4">
        {data && data.length > 0 ? (
          data.map((job: any) => (
            <div key={job.id} className="border p-4 rounded-lg hover:shadow-md transition">
              <Link to={`/jobs/${job.id}`}>
                <h3 className="text-lg font-medium">{job.title}</h3>
                <div className="flex items-center text-gray-600 mt-2">
                  <span>{job.company.name}</span>
                  <span className="mx-2">•</span>
                  <span>{job.location}</span>
                </div>
              </Link>
            </div>
          ))
        ) : (
          <div>No jobs available</div>
        )}
      </div>
    </div>
  );
};

export default JobList; 