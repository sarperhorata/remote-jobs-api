import React from 'react';
import SearchFilters from '../components/JobSearch/SearchFilters';
import SearchResultsList from '../components/JobSearch/SearchResultsList';
import Header from '../components/Header';

const SearchResults = () => {
  // Mock data for now
  const jobs = []; 
  const totalResults = 0;

  return (
    <div className="flex flex-col min-h-screen bg-gray-50">
      <Header />
      <main className="flex-grow container mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          <aside className="lg:col-span-1">
            <SearchFilters />
          </aside>
          <section className="lg:col-span-3">
            <SearchResultsList jobs={jobs} totalResults={totalResults} />
          </section>
        </div>
      </main>
    </div>
  );
};

export default SearchResults; 