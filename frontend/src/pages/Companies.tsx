import React, { useState, useEffect } from 'react';
import { Helmet } from 'react-helmet-async';
import { Search, Building2, MapPin, Users, Globe, Star, Filter, TrendingUp, Briefcase, ExternalLink, Heart, Share2 } from 'lucide-react';

interface Company {
  id: string;
  name: string;
  logo?: string;
  description: string;
  location: string;
  industry: string;
  size: string;
  founded: number;
  website: string;
  jobCount: number;
  rating: number;
  isRemote: boolean;
  isHiring: boolean;
  featured: boolean;
}

// Mock data - gerçek uygulamada API'den gelecek
const mockCompanies: Company[] = [
  {
    id: '1',
    name: 'TechCorp Solutions',
    logo: 'https://via.placeholder.com/60x60/3B82F6/FFFFFF?text=TC',
    description: 'Leading technology solutions provider specializing in cloud computing and AI applications.',
    location: 'San Francisco, CA',
    industry: 'Technology',
    size: '500-1000',
    founded: 2015,
    website: 'https://techcorp.com',
    jobCount: 23,
    rating: 4.2,
    isRemote: true,
    isHiring: true,
    featured: true
  },
  {
    id: '2',
    name: 'RemoteWorks Inc',
    logo: 'https://via.placeholder.com/60x60/10B981/FFFFFF?text=RW',
    description: 'Pioneering remote work solutions and digital collaboration tools for modern teams.',
    location: 'Austin, TX',
    industry: 'Software',
    size: '100-500',
    founded: 2018,
    website: 'https://remoteworks.com',
    jobCount: 15,
    rating: 4.5,
    isRemote: true,
    isHiring: true,
    featured: true
  },
  {
    id: '3',
    name: 'DataFlow Analytics',
    logo: 'https://via.placeholder.com/60x60/8B5CF6/FFFFFF?text=DF',
    description: 'Advanced data analytics and business intelligence solutions for enterprise clients.',
    location: 'New York, NY',
    industry: 'Data & Analytics',
    size: '1000+',
    founded: 2012,
    website: 'https://dataflow.com',
    jobCount: 34,
    rating: 4.1,
    isRemote: true,
    isHiring: true,
    featured: false
  },
  {
    id: '4',
    name: 'CloudScale Systems',
    logo: 'https://via.placeholder.com/60x60/F59E0B/FFFFFF?text=CS',
    description: 'Scalable cloud infrastructure and DevOps solutions for growing businesses.',
    location: 'Seattle, WA',
    industry: 'Cloud Computing',
    size: '500-1000',
    founded: 2016,
    website: 'https://cloudscale.com',
    jobCount: 18,
    rating: 4.3,
    isRemote: true,
    isHiring: true,
    featured: false
  },
  {
    id: '5',
    name: 'InnovateLabs',
    logo: 'https://via.placeholder.com/60x60/EF4444/FFFFFF?text=IL',
    description: 'Cutting-edge research and development in emerging technologies and AI.',
    location: 'Boston, MA',
    industry: 'Research & Development',
    size: '100-500',
    founded: 2019,
    website: 'https://innovatelabs.com',
    jobCount: 12,
    rating: 4.6,
    isRemote: true,
    isHiring: true,
    featured: true
  },
  {
    id: '6',
    name: 'SecureNet Solutions',
    logo: 'https://via.placeholder.com/60x60/06B6D4/FFFFFF?text=SN',
    description: 'Cybersecurity solutions and threat intelligence for enterprise security.',
    location: 'Washington, DC',
    industry: 'Cybersecurity',
    size: '500-1000',
    founded: 2014,
    website: 'https://securenet.com',
    jobCount: 27,
    rating: 4.0,
    isRemote: true,
    isHiring: true,
    featured: false
  },
  {
    id: '7',
    name: 'MobileFirst Apps',
    logo: 'https://via.placeholder.com/60x60/84CC16/FFFFFF?text=MF',
    description: 'Mobile application development and cross-platform solutions.',
    location: 'Los Angeles, CA',
    industry: 'Mobile Development',
    size: '100-500',
    founded: 2017,
    website: 'https://mobilefirst.com',
    jobCount: 9,
    rating: 4.4,
    isRemote: true,
    isHiring: true,
    featured: false
  },
  {
    id: '8',
    name: 'AI Dynamics',
    logo: 'https://via.placeholder.com/60x60/EC4899/FFFFFF?text=AI',
    description: 'Artificial intelligence and machine learning solutions for business automation.',
    location: 'Palo Alto, CA',
    industry: 'Artificial Intelligence',
    size: '1000+',
    founded: 2013,
    website: 'https://aidynamics.com',
    jobCount: 31,
    rating: 4.7,
    isRemote: true,
    isHiring: true,
    featured: true
  }
];

const industries = ['All', 'Technology', 'Software', 'Data & Analytics', 'Cloud Computing', 'Research & Development', 'Cybersecurity', 'Mobile Development', 'Artificial Intelligence'];
const companySizes = ['All', '1-50', '50-100', '100-500', '500-1000', '1000+'];
const locations = ['All', 'San Francisco, CA', 'Austin, TX', 'New York, NY', 'Seattle, WA', 'Boston, MA', 'Washington, DC', 'Los Angeles, CA', 'Palo Alto, CA'];

const Companies: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedIndustry, setSelectedIndustry] = useState('All');
  const [selectedSize, setSelectedSize] = useState('All');
  const [selectedLocation, setSelectedLocation] = useState('All');
  const [sortBy, setSortBy] = useState<'name' | 'rating' | 'jobCount' | 'founded'>('name');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('asc');
  const [showFeaturedOnly, setShowFeaturedOnly] = useState(false);
  const [showHiringOnly, setShowHiringOnly] = useState(false);

  const filteredCompanies = mockCompanies
    .filter(company => {
      const matchesSearch = company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                           company.description.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesIndustry = selectedIndustry === 'All' || company.industry === selectedIndustry;
      const matchesSize = selectedSize === 'All' || company.size === selectedSize;
      const matchesLocation = selectedLocation === 'All' || company.location === selectedLocation;
      const matchesFeatured = !showFeaturedOnly || company.featured;
      const matchesHiring = !showHiringOnly || company.isHiring;
      
      return matchesSearch && matchesIndustry && matchesSize && matchesLocation && matchesFeatured && matchesHiring;
    })
    .sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'name') comparison = a.name.localeCompare(b.name);
      else if (sortBy === 'rating') comparison = a.rating - b.rating;
      else if (sortBy === 'jobCount') comparison = a.jobCount - b.jobCount;
      else if (sortBy === 'founded') comparison = a.founded - b.founded;
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const totalCompanies = mockCompanies.length;
  const featuredCompanies = mockCompanies.filter(c => c.featured).length;
  const hiringCompanies = mockCompanies.filter(c => c.isHiring).length;

  const renderStars = (rating: number) => {
    return Array.from({ length: 5 }, (_, i) => (
      <Star
        key={i}
        className={`w-4 h-4 ${i < Math.floor(rating) ? 'text-yellow-400 fill-current' : 'text-gray-300'}`}
      />
    ));
  };

  return (
    <>
      <Helmet>
        <title>Companies - Remote Work Companies | Buzz2Remote</title>
        <meta name="description" content="Discover top remote work companies hiring globally. Find companies that offer remote positions, competitive salaries, and great work culture." />
      </Helmet>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-green-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        {/* Header Section */}
        <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
            <div className="text-center">
              <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-green-500 bg-clip-text text-transparent mb-4">
                Remote Work Companies
              </h1>
              <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
                Discover top companies that embrace remote work and offer amazing opportunities worldwide
              </p>
              
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg mb-4 mx-auto">
                    <Building2 className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{totalCompanies}</h3>
                  <p className="text-gray-600 dark:text-gray-400">Total Companies</p>
                </div>
                
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-center w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg mb-4 mx-auto">
                    <Star className="w-6 h-6 text-green-600 dark:text-green-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{featuredCompanies}</h3>
                  <p className="text-gray-600 dark:text-gray-400">Featured Companies</p>
                </div>
                
                <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                  <div className="flex items-center justify-center w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg mb-4 mx-auto">
                    <Briefcase className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{hiringCompanies}</h3>
                  <p className="text-gray-600 dark:text-gray-400">Currently Hiring</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Filters Section */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-4">
              {/* Search */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  type="text"
                  placeholder="Search companies..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Industry Filter */}
              <select
                value={selectedIndustry}
                onChange={(e) => setSelectedIndustry(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {industries.map(industry => (
                  <option key={industry} value={industry}>{industry}</option>
                ))}
              </select>

              {/* Size Filter */}
              <select
                value={selectedSize}
                onChange={(e) => setSelectedSize(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {companySizes.map(size => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>

              {/* Location Filter */}
              <select
                value={selectedLocation}
                onChange={(e) => setSelectedLocation(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                {locations.map(location => (
                  <option key={location} value={location}>{location}</option>
                ))}
              </select>
            </div>

            {/* Additional Filters */}
            <div className="flex items-center justify-between pt-4 border-t border-gray-200 dark:border-gray-600">
              <div className="flex items-center space-x-6">
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showFeaturedOnly}
                    onChange={(e) => setShowFeaturedOnly(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Featured Only</span>
                </label>
                
                <label className="flex items-center space-x-2">
                  <input
                    type="checkbox"
                    checked={showHiringOnly}
                    onChange={(e) => setShowHiringOnly(e.target.checked)}
                    className="rounded border-gray-300 text-blue-600 focus:ring-blue-500"
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">Currently Hiring</span>
                </label>
              </div>

              <div className="flex items-center space-x-4">
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Sort by:</span>
                <select
                  value={sortBy}
                  onChange={(e) => setSortBy(e.target.value as 'name' | 'rating' | 'jobCount' | 'founded')}
                  className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="name">Company Name</option>
                  <option value="rating">Rating</option>
                  <option value="jobCount">Job Count</option>
                  <option value="founded">Founded Year</option>
                </select>
                <button
                  onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                  className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  {sortOrder === 'asc' ? '↑' : '↓'}
                </button>
              </div>
            </div>
          </div>

          {/* Companies Grid */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredCompanies.map((company) => (
              <div
                key={company.id}
                className={`bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-all duration-300 ${
                  company.featured ? 'ring-2 ring-blue-500' : ''
                }`}
              >
                {/* Company Header */}
                <div className="p-6 border-b border-gray-200 dark:border-gray-700">
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex items-center space-x-3">
                      <img
                        src={company.logo}
                        alt={`${company.name} logo`}
                        className="w-12 h-12 rounded-lg object-cover"
                      />
                      <div>
                        <h3 className="font-bold text-lg text-gray-900 dark:text-white">{company.name}</h3>
                        <div className="flex items-center space-x-1">
                          {renderStars(company.rating)}
                          <span className="text-sm text-gray-600 dark:text-gray-400 ml-1">
                            ({company.rating})
                          </span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      {company.featured && (
                        <span className="px-2 py-1 text-xs font-semibold bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-400 rounded-full">
                          Featured
                        </span>
                      )}
                      {company.isHiring && (
                        <span className="px-2 py-1 text-xs font-semibold bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 rounded-full">
                          Hiring
                        </span>
                      )}
                    </div>
                  </div>

                  <p className="text-gray-600 dark:text-gray-400 text-sm mb-4 line-clamp-2">
                    {company.description}
                  </p>

                  <div className="flex items-center justify-between text-sm text-gray-500 dark:text-gray-400">
                    <div className="flex items-center space-x-1">
                      <MapPin className="w-4 h-4" />
                      <span>{company.location}</span>
                    </div>
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span>{company.size}</span>
                    </div>
                  </div>
                </div>

                {/* Company Details */}
                <div className="p-6">
                  <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Industry:</span>
                      <p className="font-medium text-gray-900 dark:text-white">{company.industry}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Founded:</span>
                      <p className="font-medium text-gray-900 dark:text-white">{company.founded}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Open Positions:</span>
                      <p className="font-medium text-blue-600 dark:text-blue-400">{company.jobCount}</p>
                    </div>
                    <div>
                      <span className="text-gray-500 dark:text-gray-400">Remote:</span>
                      <p className="font-medium text-green-600 dark:text-green-400">
                        {company.isRemote ? 'Yes' : 'No'}
                      </p>
                    </div>
                  </div>

                  {/* Action Buttons */}
                  <div className="flex items-center justify-between">
                    <a
                      href={company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center space-x-1 text-blue-600 dark:text-blue-400 hover:text-blue-700 dark:hover:text-blue-300 text-sm font-medium"
                    >
                      <ExternalLink className="w-4 h-4" />
                      <span>Visit Website</span>
                    </a>
                    
                    <div className="flex items-center space-x-2">
                      <button className="p-2 text-gray-400 hover:text-red-500 transition-colors">
                        <Heart className="w-4 h-4" />
                      </button>
                      <button className="p-2 text-gray-400 hover:text-blue-500 transition-colors">
                        <Share2 className="w-4 h-4" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* No Results */}
          {filteredCompanies.length === 0 && (
            <div className="text-center py-12">
              <Building2 className="w-16 h-16 text-gray-400 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">No companies found</h3>
              <p className="text-gray-600 dark:text-gray-400">
                Try adjusting your search criteria or filters
              </p>
            </div>
          )}

          {/* Results Count */}
          <div className="mt-8 text-center">
            <p className="text-gray-600 dark:text-gray-400">
              Showing {filteredCompanies.length} of {totalCompanies} companies
            </p>
          </div>

          {/* CTA Section */}
          <div className="mt-12 bg-gradient-to-r from-blue-600 to-green-500 rounded-2xl p-8 text-center">
            <h3 className="text-2xl font-bold text-white mb-4">Ready to Join These Amazing Companies?</h3>
            <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
              Browse thousands of remote job opportunities from top companies worldwide and find your perfect match.
            </p>
            <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
              Browse Remote Jobs
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default Companies; 