import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { getCompanies } from '../services/companyService';
import { Company } from '../types/Company';
import { CompanyCard } from '../components/CompanyCard';
import { SearchBar } from '../components/SearchBar';
import { FilterBar } from '../components/FilterBar';
import { Pagination } from '../components/Pagination';
import { LoadingSpinner } from '../components/LoadingSpinner';
import { ErrorMessage } from '../components/ErrorMessage';

const Companies: React.FC = () => {
  const [page, setPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const [filters, setFilters] = useState({
    location: '',
    type: '',
    category: ''
  });

  const { data, isLoading, error } = useQuery(
    ['companies', page, searchQuery, filters],
    () => getCompanies({ page, search: searchQuery }),
    { keepPreviousData: true }
  );

  if (isLoading) return <LoadingSpinner />;
  if (error) return <ErrorMessage message={(error as Error).message} />;

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold mb-8">Companies</h1>
      
      <div className="mb-6">
        <SearchBar 
          value={searchQuery}
          onChange={setSearchQuery}
          placeholder="Search companies..."
        />
      </div>

      <div className="mb-6">
        <FilterBar filters={filters} onFilterChange={setFilters} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {data?.companies?.map((company: Company) => (
          <CompanyCard key={company.id} company={company} />
        ))}
      </div>

      {data && (
        <div className="mt-8">
          <Pagination
            currentPage={page}
            totalPages={Math.ceil(data.total / 10)}
            onPageChange={setPage}
          />
        </div>
      )}
    </div>
  );
};

export default Companies; 