import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { jobService } from '../services/AllServices';

const JobList: React.FC<{
  filters?: any;
  limit?: number;
  onJobSelected?: (job: any) => void;
}> = ({ filters = {}, limit, onJobSelected }) => {
  const [data, setData] = useState<any>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobs = async () => {
      try {
        setIsLoading(true);
        const result = await jobService.getJobs(filters);
        setData(result);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchJobs();
  }, [filters]);

  if (isLoading) return <div>Loading jobs...</div>;
  if (error) return <div>Error loading jobs</div>;

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Latest Jobs</h2>
      <div className="space-y-4">
        {data && data.length > 0 ? (
          data.map((job: any, index: number) => (
            <div key={job.id || job._id || `job-${index}`} className="border p-4 rounded-lg hover:shadow-md transition">
              <Link to={`/jobs/${job.id || job._id || index}`}>
                <h3 className="text-lg font-medium">{job.title}</h3>
                <div className="flex items-center text-gray-600 mt-2">
                  <span>{job.company?.name || 'Unknown Company'}</span>
                  <span className="mx-2">•</span>
                  <span>{job.location || 'Location not specified'}</span>
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