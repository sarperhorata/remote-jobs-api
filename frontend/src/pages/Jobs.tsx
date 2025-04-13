import React, { useState, useEffect } from 'react';
import { useQuery } from 'react-query';
import { useSearchParams, Link } from 'react-router-dom';
import { jobService } from '../services/AllServices';
import { Job } from '../types/job';

const Jobs: React.FC = () => {
  const [searchParams, setSearchParams] = useSearchParams();
  const [filters, setFilters] = useState({
    category: searchParams.get('category') || '',
    location: searchParams.get('location') || '',
    type: searchParams.get('type') || '',
    search: searchParams.get('search') || ''
  });

  const { data: jobs, isLoading } = useQuery(
    ['jobs', filters],
    () => jobService.getJobs(filters)
  );

  const handleFilterChange = (e: React.ChangeEvent<HTMLInputElement | HTMLSelectElement>) => {
    const { name, value } = e.target;
    setFilters(prev => ({ ...prev, [name]: value }));
  };

  useEffect(() => {
    const params = new URLSearchParams();
    Object.entries(filters).forEach(([key, value]) => {
      if (value) params.set(key, value);
    });
    setSearchParams(params);
  }, [filters, setSearchParams]);

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold mb-8">Remote Jobs</h1>

        {/* Filters */}
        <div className="bg-white p-6 rounded-lg shadow-md mb-8">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <input
              type="text"
              name="search"
              placeholder="Search jobs..."
              value={filters.search}
              onChange={handleFilterChange}
              className="border rounded-lg px-4 py-2"
            />
            <select
              name="category"
              value={filters.category}
              onChange={handleFilterChange}
              className="border rounded-lg px-4 py-2"
            >
              <option value="">All Categories</option>
              <option value="development">Development</option>
              <option value="design">Design</option>
              <option value="marketing">Marketing</option>
              <option value="sales">Sales</option>
              <option value="customer-support">Customer Support</option>
              <option value="product">Product</option>
              <option value="data">Data</option>
              <option value="writing">Writing</option>
            </select>
            <select
              name="type"
              value={filters.type}
              onChange={handleFilterChange}
              className="border rounded-lg px-4 py-2"
            >
              <option value="">All Types</option>
              <option value="full-time">Full Time</option>
              <option value="part-time">Part Time</option>
              <option value="contract">Contract</option>
              <option value="freelance">Freelance</option>
            </select>
            <select
              name="location"
              value={filters.location}
              onChange={handleFilterChange}
              className="border rounded-lg px-4 py-2"
            >
              <option value="">All Locations</option>
              <option value="worldwide">Worldwide</option>
              <option value="europe">Europe</option>
              <option value="north-america">North America</option>
              <option value="asia">Asia</option>
              <option value="africa">Africa</option>
              <option value="south-america">South America</option>
              <option value="oceania">Oceania</option>
            </select>
          </div>
        </div>

        {/* Job Listings */}
        {isLoading ? (
          <div className="flex justify-center">
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-6">
            {jobs?.map((job: Job) => (
              <div key={job.id} className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition">
                <div className="flex flex-col md:flex-row md:items-center justify-between">
                  <div className="flex items-center mb-4 md:mb-0">
                    {job.company.logo && (
                      <img 
                        src={job.company.logo} 
                        alt={job.company.name} 
                        className="w-12 h-12 rounded-full mr-4"
                      />
                    )}
                    <div>
                      <h2 className="text-xl font-semibold">{job.title}</h2>
                      <p className="text-gray-600">{job.company.name}</p>
                    </div>
                  </div>
                  <div className="flex flex-wrap gap-2 mb-4 md:mb-0">
                    {job.skills.slice(0, 3).map(skill => (
                      <span 
                        key={skill} 
                        className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>
                <div className="flex flex-wrap gap-4 text-sm text-gray-500 mb-4">
                  <span>{job.location}</span>
                  <span>•</span>
                  <span>{job.type}</span>
                  <span>•</span>
                  <span>Posted {new Date(job.postedAt).toLocaleDateString()}</span>
                </div>
                <div className="flex justify-between items-center">
                  <Link 
                    to={`/jobs/${job.id}`} 
                    className="text-blue-600 font-medium hover:underline"
                  >
                    View Details
                  </Link>
                  <button 
                    className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                    onClick={() => jobService.applyForJob('current-user', job.id)}
                  >
                    Apply Now
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default Jobs; 