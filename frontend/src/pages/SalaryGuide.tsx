import React, { useState } from 'react';
import { Helmet } from 'react-helmet-async';
import { Search, TrendingUp, DollarSign, Briefcase, BarChart3, Globe } from 'lucide-react';
import Header from '../components/Header';
import Footer from '../components/Footer';

interface SalaryData {
  title: string;
  min: number;
  max: number;
  avg: number;
  currency: string;
  location: string;
  experience: string;
  category: string;
  demand: 'High' | 'Medium' | 'Low';
  growth: number;
}

const salaryData: SalaryData[] = [
  { title: 'Senior Frontend Developer', min: 80000, max: 150000, avg: 115000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Frontend', demand: 'High', growth: 12 },
  { title: 'Senior Backend Developer', min: 90000, max: 160000, avg: 125000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Backend', demand: 'High', growth: 15 },
  { title: 'Full Stack Developer', min: 85000, max: 155000, avg: 120000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Full Stack', demand: 'High', growth: 18 },
  { title: 'Product Manager', min: 100000, max: 180000, avg: 140000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Product', demand: 'High', growth: 20 },
  { title: 'Senior Data Scientist', min: 110000, max: 190000, avg: 150000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Data', demand: 'High', growth: 25 },
  { title: 'Senior UI/UX Designer', min: 70000, max: 130000, avg: 100000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Design', demand: 'Medium', growth: 10 },
  { title: 'Senior DevOps Engineer', min: 100000, max: 170000, avg: 135000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'DevOps', demand: 'High', growth: 22 },
  { title: 'Senior QA Engineer', min: 70000, max: 120000, avg: 95000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'QA', demand: 'Medium', growth: 8 },
  { title: 'Junior Frontend Developer', min: 45000, max: 75000, avg: 60000, currency: 'USD', location: 'Remote/Global', experience: '0-2 years', category: 'Frontend', demand: 'Medium', growth: 10 },
  { title: 'Junior Backend Developer', min: 50000, max: 80000, avg: 65000, currency: 'USD', location: 'Remote/Global', experience: '0-2 years', category: 'Backend', demand: 'Medium', growth: 12 },
  { title: 'Junior Product Manager', min: 60000, max: 90000, avg: 75000, currency: 'USD', location: 'Remote/Global', experience: '0-2 years', category: 'Product', demand: 'Medium', growth: 15 },
  { title: 'Junior Data Scientist', min: 65000, max: 95000, avg: 80000, currency: 'USD', location: 'Remote/Global', experience: '0-2 years', category: 'Data', demand: 'High', growth: 20 },
  { title: 'Lead Software Engineer', min: 120000, max: 200000, avg: 160000, currency: 'USD', location: 'Remote/Global', experience: '5+ years', category: 'Engineering', demand: 'High', growth: 18 },
  { title: 'Engineering Manager', min: 130000, max: 220000, avg: 175000, currency: 'USD', location: 'Remote/Global', experience: '5+ years', category: 'Management', demand: 'Medium', growth: 15 },
  { title: 'Senior Mobile Developer', min: 90000, max: 160000, avg: 125000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Mobile', demand: 'Medium', growth: 12 },
  { title: 'Senior Security Engineer', min: 110000, max: 180000, avg: 145000, currency: 'USD', location: 'Remote/Global', experience: '3-5 years', category: 'Security', demand: 'High', growth: 25 },
];

const categories = ['All', 'Frontend', 'Backend', 'Full Stack', 'Product', 'Data', 'Design', 'DevOps', 'QA', 'Engineering', 'Management', 'Mobile', 'Security'];
const experienceLevels = ['All', '0-2 years', '3-5 years', '5+ years'];
const demandLevels = ['All', 'High', 'Medium', 'Low'];

const SalaryGuide: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('All');
  const [selectedExperience, setSelectedExperience] = useState('All');
  const [selectedDemand, setSelectedDemand] = useState('All');
  const [sortBy, setSortBy] = useState<'avg' | 'growth' | 'demand'>('avg');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const filteredData = salaryData
    .filter(item => {
      const matchesSearch = item.title.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesCategory = selectedCategory === 'All' || item.category === selectedCategory;
      const matchesExperience = selectedExperience === 'All' || item.experience === selectedExperience;
      const matchesDemand = selectedDemand === 'All' || item.demand === selectedDemand;
      return matchesSearch && matchesCategory && matchesExperience && matchesDemand;
    })
    .sort((a, b) => {
      let comparison = 0;
      if (sortBy === 'avg') comparison = a.avg - b.avg;
      else if (sortBy === 'growth') comparison = a.growth - b.growth;
      else if (sortBy === 'demand') comparison = a.demand.localeCompare(b.demand);
      
      return sortOrder === 'asc' ? comparison : -comparison;
    });

  const getDemandColor = (demand: string) => {
    switch (demand) {
      case 'High': return 'text-green-600 bg-green-100 dark:text-green-400 dark:bg-green-900/20';
      case 'Medium': return 'text-yellow-600 bg-yellow-100 dark:text-yellow-400 dark:bg-yellow-900/20';
      case 'Low': return 'text-red-600 bg-red-100 dark:text-red-400 dark:bg-red-900/20';
      default: return 'text-gray-600 bg-gray-100 dark:text-gray-400 dark:bg-gray-900/20';
    }
  };

  const getGrowthColor = (growth: number) => {
    if (growth >= 20) return 'text-green-600 dark:text-green-400';
    if (growth >= 10) return 'text-yellow-600 dark:text-yellow-400';
    return 'text-red-600 dark:text-red-400';
  };

  const averageSalary = Math.round(salaryData.reduce((sum, item) => sum + item.avg, 0) / salaryData.length);
  const totalPositions = salaryData.length;
  const highDemandPositions = salaryData.filter(item => item.demand === 'High').length;

  return (
    <>
      <Helmet>
        <title>Salary Guide - Remote Job Salaries | Buzz2Remote</title>
        <meta name="description" content="Comprehensive salary guide for remote tech jobs. Find average salaries, growth trends, and demand levels for various remote positions." />
      </Helmet>

      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-yellow-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        <Header />
        
        {/* Main Content with top padding for fixed header */}
        <div className="pt-16">
          {/* Header Section */}
          <div className="bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b border-gray-200 dark:border-gray-700">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
              <div className="text-center">
                <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-blue-600 to-yellow-500 bg-clip-text text-transparent mb-4">
                  Remote Job Salary Guide
                </h1>
                <p className="text-xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl mx-auto">
                  Discover competitive salaries, growth trends, and market demand for remote tech positions worldwide
                </p>
                
                {/* Stats Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-center w-12 h-12 bg-blue-100 dark:bg-blue-900/20 rounded-lg mb-4 mx-auto">
                      <DollarSign className="w-6 h-6 text-blue-600 dark:text-blue-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">${averageSalary.toLocaleString()}</h3>
                    <p className="text-gray-600 dark:text-gray-400">Average Salary</p>
                  </div>
                  
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-center w-12 h-12 bg-green-100 dark:bg-green-900/20 rounded-lg mb-4 mx-auto">
                      <Briefcase className="w-6 h-6 text-green-600 dark:text-green-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{totalPositions}</h3>
                    <p className="text-gray-600 dark:text-gray-400">Positions Tracked</p>
                  </div>
                  
                  <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                    <div className="flex items-center justify-center w-12 h-12 bg-yellow-100 dark:bg-yellow-900/20 rounded-lg mb-4 mx-auto">
                      <TrendingUp className="w-6 h-6 text-yellow-600 dark:text-yellow-400" />
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">{highDemandPositions}</h3>
                    <p className="text-gray-600 dark:text-gray-400">High Demand Jobs</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          {/* Filters Section */}
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 p-6 mb-8">
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
                {/* Search */}
                <div className="relative">
                  <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                  <input
                    type="text"
                    placeholder="Search positions..."
                    value={searchTerm}
                    onChange={(e) => setSearchTerm(e.target.value)}
                    className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  />
                </div>

                {/* Category Filter */}
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>

                {/* Experience Filter */}
                <select
                  value={selectedExperience}
                  onChange={(e) => setSelectedExperience(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {experienceLevels.map(level => (
                    <option key={level} value={level}>{level}</option>
                  ))}
                </select>

                {/* Demand Filter */}
                <select
                  value={selectedDemand}
                  onChange={(e) => setSelectedDemand(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {demandLevels.map(demand => (
                    <option key={demand} value={demand}>{demand}</option>
                  ))}
                </select>
              </div>

              {/* Sort Options */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-200 dark:border-gray-600">
                <div className="flex items-center space-x-4">
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Sort by:</span>
                  <select
                    value={sortBy}
                    onChange={(e) => setSortBy(e.target.value as 'avg' | 'growth' | 'demand')}
                    className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white text-sm focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="avg">Average Salary</option>
                    <option value="growth">Growth Rate</option>
                    <option value="demand">Demand Level</option>
                  </select>
                  <button
                    onClick={() => setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc')}
                    className="p-1 rounded-md hover:bg-gray-100 dark:hover:bg-gray-700"
                  >
                    {sortOrder === 'asc' ? '↑' : '↓'}
                  </button>
                </div>
                <span className="text-sm text-gray-600 dark:text-gray-400">
                  {filteredData.length} positions found
                </span>
              </div>
            </div>

            {/* Salary Table */}
            <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 overflow-hidden">
              <div className="overflow-x-auto">
                <table className="min-w-full">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Position</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Experience</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Min</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Max</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Average</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Growth</th>
                      <th className="px-6 py-4 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase tracking-wider">Demand</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200 dark:divide-gray-600">
                    {filteredData.map((item, idx) => (
                      <tr key={item.title} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                        <td className="px-6 py-4">
                          <div>
                            <div className="font-semibold text-gray-900 dark:text-white">{item.title}</div>
                            <div className="text-sm text-gray-500 dark:text-gray-400">{item.category}</div>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">{item.experience}</td>
                        <td className="px-6 py-4 text-sm text-green-600 dark:text-green-400 font-medium">
                          ${item.min.toLocaleString()}
                        </td>
                        <td className="px-6 py-4 text-sm text-red-600 dark:text-red-400 font-medium">
                          ${item.max.toLocaleString()}
                        </td>
                        <td className="px-6 py-4">
                          <div className="font-bold text-blue-600 dark:text-blue-400">
                            ${item.avg.toLocaleString()}
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <div className={`flex items-center text-sm font-medium ${getGrowthColor(item.growth)}`}>
                            <TrendingUp className="w-4 h-4 mr-1" />
                            {item.growth}%
                          </div>
                        </td>
                        <td className="px-6 py-4">
                          <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${getDemandColor(item.demand)}`}>
                            {item.demand}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Additional Info */}
            <div className="mt-8 grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <BarChart3 className="w-5 h-5 mr-2 text-blue-600 dark:text-blue-400" />
                  Salary Trends
                </h3>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>• Data Science roles show the highest growth at 25% annually</li>
                  <li>• Product Management positions have the highest average salaries</li>
                  <li>• Security Engineering is experiencing rapid salary growth</li>
                  <li>• Junior positions offer competitive entry-level salaries</li>
                </ul>
              </div>

              <div className="bg-white dark:bg-gray-800 rounded-xl p-6 shadow-lg border border-gray-200 dark:border-gray-700">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4 flex items-center">
                  <Globe className="w-5 h-5 mr-2 text-green-600 dark:text-green-400" />
                  Market Insights
                </h3>
                <ul className="space-y-2 text-sm text-gray-600 dark:text-gray-400">
                  <li>• Remote work has increased salary transparency globally</li>
                  <li>• High-demand skills command premium salaries</li>
                  <li>• Experience level significantly impacts earning potential</li>
                  <li>• Location-independent roles offer competitive compensation</li>
                </ul>
              </div>
            </div>

            {/* CTA Section */}
            <div className="mt-8 bg-gradient-to-r from-blue-600 to-yellow-500 rounded-2xl p-8 text-center">
              <h3 className="text-2xl font-bold text-white mb-4">Ready to Find Your Next Remote Job?</h3>
              <p className="text-blue-100 mb-6 max-w-2xl mx-auto">
                Use our comprehensive job search to find positions that match your salary expectations and career goals.
              </p>
              <button className="bg-white text-blue-600 px-8 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                Browse Remote Jobs
              </button>
            </div>
          </div>
        </div>
        
        <Footer />
      </div>
    </>
  );
};

export default SalaryGuide; 