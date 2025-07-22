import React from 'react';
import { Job } from '../../types/job';
import JobCard from '../JobCard/JobCard'; // Assuming JobCard component exists and is suitable

interface SearchResultsListProps {
  jobs: Job[];
  totalResults: number;
}

const SearchResultsList: React.FC<SearchResultsListProps> = ({ jobs, totalResults }) => {
  return (
    <div className="bg-white rounded-lg shadow-md">
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-xl font-bold text-gray-800">
          Job Search Results: {totalResults > 0 ? `${totalResults} jobs found` : 'No jobs found'}
        </h2>
        {/* Sorting options can go here */}
      </div>
      
      {jobs.length > 0 ? (
        <div className="divide-y divide-gray-200">
          {jobs.map((job) => (
            <JobCard key={job.id || job._id} job={job} />
          ))}
        </div>
      ) : (
        <div className="p-6 text-center text-gray-500">
          <p>Your search did not match any jobs.</p>
          <p className="mt-2">Try adjusting your filters.</p>
        </div>
      )}

      {/* Pagination can go here */}
    </div>
  );
};

export default SearchResultsList; 