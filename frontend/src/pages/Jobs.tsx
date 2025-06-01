import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { getJobs } from '../services/jobService';
import { Job } from '../types/job';
import { JobCard } from '../components/JobCard';
import { SearchBar } from '../components/SearchBar';
import { FilterBar } from '../components/FilterBar';
import { Pagination } from '../components/Pagination';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

const Jobs: React.FC = () => {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    company: '',
    location: '',
    type: '',
    category: ''
  });

  const { data, isLoading, error } = useQuery(
    ['jobs', page, searchQuery, filters],
    () => getJobs({ page, searchQuery, ...filters }),
    { keepPreviousData: true }
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={(error as Error).message} />;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Remote Jobs</h1>
      
      <div className="mb-6">
        <SearchBar 
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search jobs..."
        />
      </div>

      <div className="mb-6">
        <FilterBar filters={filters} onFilterChange={setFilters} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {(data?.items || data?.jobs || []).map((job: Job) => (
          <JobCard key={job._id || job.id} job={job} />
        ))}
      </div>

      {data && (
        <div className="mt-8">
          <Pagination
            currentPage={page}
            totalPages={data.total_pages || Math.ceil((data.total || 0) / 10)}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  );
};

export default Jobs; 