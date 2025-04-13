import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useQuery } from 'react-query';
import { BsSearch, BsMap, BsBuilding, BsBriefcase, BsCode, BsMegaphone, BsPencil, BsChatDots, BsServer } from 'react-icons/bs';
import { BiHealth, BiDollar, BiChalkboard, BiStore, BiPalette } from 'react-icons/bi';
import { HomeJobService } from '../../services/AllServices';
import JobCard from '../JobCard/JobCard';
import { Job } from '../../types/job';
import { IconType } from 'react-icons';

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [searchTerm, setSearchTerm] = useState('');
  const [location, setLocation] = useState('');
  const [jobType, setJobType] = useState('');

  const { data: featuredJobs } = useQuery('featuredJobs', () => HomeJobService.getFeaturedJobs());

  const { data: jobStats } = useQuery('jobStats', () => HomeJobService.getJobStats());

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    const params = new URLSearchParams();
    if (searchTerm) params.append('q', searchTerm);
    if (location) params.append('location', location);
    if (jobType) params.append('type', jobType);
    
    navigate(`/jobs?${params.toString()}`);
  };

  const categories: { name: string; icon: IconType; count: number }[] = [
    { name: 'Software Development', icon: BsCode, count: 120 },
    { name: 'Marketing', icon: BsMegaphone, count: 85 },
    { name: 'Design', icon: BiPalette, count: 64 },
    { name: 'Customer Support', icon: BsChatDots, count: 53 },
    { name: 'Sales', icon: BiDollar, count: 47 },
    { name: 'Content Writing', icon: BsPencil, count: 42 },
    { name: 'DevOps', icon: BsServer, count: 38 },
    { name: 'Healthcare', icon: BiHealth, count: 31 },
    { name: 'Education', icon: BiChalkboard, count: 28 },
    { name: 'E-commerce', icon: BiStore, count: 25 },
  ];

  const SearchIcon = BsSearch;
  const MapIcon = BsMap;
  const BriefcaseIcon = BsBriefcase;

  return (
    <div className="min-h-screen">
      {/* Hero Section with Gradient */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-800 text-white">
        <div className="container mx-auto px-4 py-16 md:py-24">
          <div className="max-w-4xl mx-auto text-center mb-10">
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Find Your Perfect Remote Job
            </h1>
            <p className="text-xl opacity-90 mb-10">
              Discover thousands of remote opportunities from top companies around the world
            </p>
          </div>

          {/* Search Form */}
          <div className="bg-white p-6 rounded-lg shadow-lg max-w-4xl mx-auto">
            <form onSubmit={handleSearch} className="grid grid-cols-1 md:grid-cols-4 gap-4">
              <div className="md:col-span-2">
                <div className="relative">
                  {(SearchIcon as any)({ className: "absolute left-3 top-3 text-gray-400", size: 16 })}
                  <input
                    type="text"
                    placeholder="Job title or keyword"
                    className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <div className="relative">
                  {(MapIcon as any)({ className: "absolute left-3 top-3 text-gray-400", size: 16 })}
                  <input
                    type="text"
                    placeholder="Location"
                    className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                    value={location}
                    onChange={(e) => setLocation(e.target.value)}
                  />
                </div>
              </div>
              <div>
                <div className="relative">
                  {(BriefcaseIcon as any)({ className: "absolute left-3 top-3 text-gray-400", size: 16 })}
                  <select
                    className="w-full pl-10 pr-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 appearance-none"
                    value={jobType}
                    onChange={(e) => setJobType(e.target.value)}
                  >
                    <option value="">All Job Types</option>
                    <option value="full-time">Full-time</option>
                    <option value="part-time">Part-time</option>
                    <option value="contract">Contract</option>
                    <option value="freelance">Freelance</option>
                  </select>
                </div>
              </div>
              <div className="md:col-span-4">
                <button
                  type="submit"
                  className="w-full bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded-md font-medium transition-colors"
                >
                  Search Jobs
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <h3 className="text-4xl font-bold text-blue-600 mb-2">{jobStats?.totalJobs || '1000+'}</h3>
              <p className="text-gray-600">Available Jobs</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <h3 className="text-4xl font-bold text-blue-600 mb-2">{jobStats?.totalCompanies || '300+'}</h3>
              <p className="text-gray-600">Companies Hiring</p>
            </div>
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <h3 className="text-4xl font-bold text-blue-600 mb-2">{jobStats?.jobsLast24h || '5000+'}</h3>
              <p className="text-gray-600">Applications Submitted</p>
            </div>
          </div>
        </div>
      </div>

      {/* Featured Jobs Section */}
      <div className="py-12">
        <div className="container mx-auto px-4">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-4">Featured Remote Jobs</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Explore our handpicked selection of top remote opportunities from around the world
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {featuredJobs?.map((job: Job) => (
              <JobCard key={job._id || job.id} job={job} />
            ))}
          </div>

          <div className="mt-10 text-center">
            <button 
              onClick={() => navigate('/jobs')}
              className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-6 rounded-md font-medium transition-colors"
            >
              View All Jobs
            </button>
          </div>
        </div>
      </div>

      {/* Categories Section */}
      <div className="py-12 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-10">
            <h2 className="text-3xl font-bold mb-4">Popular Job Categories</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Browse top job categories and find the perfect role for your skills and experience
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
            {categories.map((category) => {
              const IconComponent = category.icon;
              return (
                <div
                  key={category.name}
                  className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 hover:shadow-md transition-shadow cursor-pointer"
                  onClick={() => navigate(`/jobs?category=${encodeURIComponent(category.name)}`)}
                >
                  <div className="text-blue-600 mb-3">{(IconComponent as any)({ size: 24 })}</div>
                  <h3 className="font-semibold text-lg mb-1">{category.name}</h3>
                  <p className="text-gray-500 text-sm">{category.count} jobs available</p>
                </div>
              );
            })}
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="py-16 bg-gradient-to-r from-blue-600 to-indigo-800 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready to Find Your Dream Remote Job?</h2>
          <p className="text-xl opacity-90 mb-8 max-w-2xl mx-auto">
            Create your profile today and start applying to thousands of remote positions
          </p>
          <button 
            onClick={() => navigate('/register')}
            className="bg-white text-blue-600 hover:bg-gray-100 py-3 px-8 rounded-md font-medium transition-colors"
          >
            Create Your Profile
          </button>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-800 text-white py-12">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
            <div>
              <h3 className="text-xl font-bold mb-4">Remote Jobs</h3>
              <p className="text-gray-400">
                Your gateway to the best remote opportunities worldwide.
              </p>
            </div>
            <div>
              <h4 className="font-bold mb-4">For Job Seekers</h4>
              <ul className="space-y-2">
                <li><a href="/jobs" className="text-gray-400 hover:text-white">Browse Jobs</a></li>
                <li><a href="/companies" className="text-gray-400 hover:text-white">Companies</a></li>
                <li><a href="/saved" className="text-gray-400 hover:text-white">Saved Jobs</a></li>
                <li><a href="/profile" className="text-gray-400 hover:text-white">My Profile</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">For Employers</h4>
              <ul className="space-y-2">
                <li><a href="/post-job" className="text-gray-400 hover:text-white">Post a Job</a></li>
                <li><a href="/pricing" className="text-gray-400 hover:text-white">Pricing</a></li>
                <li><a href="/resources" className="text-gray-400 hover:text-white">Resources</a></li>
              </ul>
            </div>
            <div>
              <h4 className="font-bold mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="/about" className="text-gray-400 hover:text-white">About Us</a></li>
                <li><a href="/contact" className="text-gray-400 hover:text-white">Contact</a></li>
                <li><a href="/privacy" className="text-gray-400 hover:text-white">Privacy Policy</a></li>
                <li><a href="/terms" className="text-gray-400 hover:text-white">Terms of Service</a></li>
              </ul>
            </div>
          </div>
          <div className="border-t border-gray-700 mt-8 pt-8 text-sm text-gray-400">
            <p>© {new Date().getFullYear()} Remote Jobs. All rights reserved.</p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Home; 