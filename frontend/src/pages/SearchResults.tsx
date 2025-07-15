import React, { useState } from 'react';
import SearchFilters from '../components/JobSearch/SearchFilters';
import SearchResultsList from '../components/JobSearch/SearchResultsList';
import Layout from '../components/Layout';
import { Job } from '../types/job';

interface Filters {
  query: string;
  location: string;
  jobType: string;
  workType: string;
  experience_level: string;
  salaryMin: string;
  salaryMax: string;
  company: string;
  postedWithin: string;
  experiences?: string[];
  postedAge?: string;
  salaryRange?: string;
  page?: number;
}

const SearchResults: React.FC = () => {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(false);
  const [totalResults, setTotalResults] = useState(0);
  const [filters, setFilters] = useState<Filters>({
    query: '',
    location: '',
    jobType: '',
    workType: '',
    experience_level: '',
    salaryMin: '',
    salaryMax: '',
    company: '',
    postedWithin: '',
    experiences: [],
    postedAge: '30DAYS',
    salaryRange: ''
  });

  // Filter change handler
  const handleFiltersChange = (newFilters: any) => {
    setFilters(prev => ({ ...prev, ...newFilters }));
  };

  return (
    <Layout>
      <div className="container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <aside className="lg:col-span-1">
            <SearchFilters 
              filters={filters}
              onFiltersChange={handleFiltersChange}
              availableCompanies={[]}
              availableLocations={[]}
            />
          </aside>
          <section className="lg:col-span-3">
            <SearchResultsList jobs={jobs} totalResults={totalResults} />
          </section>
        </div>
      </div>
    </Layout>
  );
};

export default SearchResults; 