import React, { useState } from 'react';
import Layout from '../components/Layout';
import { DollarSign, TrendingUp, MapPin, Briefcase, Users, BarChart3 } from 'lucide-react';

const SalaryGuide: React.FC = () => {
  const [selectedRole, setSelectedRole] = useState('all');
  const [selectedExperience, setSelectedExperience] = useState('all');

  const roles = [
    { value: 'all', label: 'All Roles' },
    { value: 'software-engineer', label: 'Software Engineer' },
    { value: 'product-manager', label: 'Product Manager' },
    { value: 'designer', label: 'Designer' },
    { value: 'marketing', label: 'Marketing' },
    { value: 'sales', label: 'Sales' },
    { value: 'customer-support', label: 'Customer Support' },
    { value: 'data-scientist', label: 'Data Scientist' },
    { value: 'devops', label: 'DevOps Engineer' },
    { value: 'content-writer', label: 'Content Writer' }
  ];

  const experienceLevels = [
    { value: 'all', label: 'All Levels' },
    { value: 'entry', label: 'Entry Level (0-2 years)' },
    { value: 'mid', label: 'Mid Level (3-5 years)' },
    { value: 'senior', label: 'Senior Level (6-10 years)' },
    { value: 'lead', label: 'Lead/Manager (10+ years)' }
  ];

  const salaryData = [
    {
      role: 'Software Engineer',
      entry: { min: 60000, max: 90000, avg: 75000 },
      mid: { min: 80000, max: 130000, avg: 105000 },
      senior: { min: 120000, max: 180000, avg: 150000 },
      lead: { min: 150000, max: 250000, avg: 200000 }
    },
    {
      role: 'Product Manager',
      entry: { min: 70000, max: 100000, avg: 85000 },
      mid: { min: 90000, max: 140000, avg: 115000 },
      senior: { min: 130000, max: 190000, avg: 160000 },
      lead: { min: 160000, max: 280000, avg: 220000 }
    },
    {
      role: 'Designer',
      entry: { min: 50000, max: 80000, avg: 65000 },
      mid: { min: 70000, max: 120000, avg: 95000 },
      senior: { min: 100000, max: 160000, avg: 130000 },
      lead: { min: 130000, max: 220000, avg: 175000 }
    },
    {
      role: 'Marketing',
      entry: { min: 45000, max: 70000, avg: 57500 },
      mid: { min: 65000, max: 110000, avg: 87500 },
      senior: { min: 90000, max: 150000, avg: 120000 },
      lead: { min: 120000, max: 200000, avg: 160000 }
    },
    {
      role: 'Sales',
      entry: { min: 40000, max: 65000, avg: 52500 },
      mid: { min: 60000, max: 100000, avg: 80000 },
      senior: { min: 85000, max: 140000, avg: 112500 },
      lead: { min: 110000, max: 180000, avg: 145000 }
    },
    {
      role: 'Data Scientist',
      entry: { min: 70000, max: 100000, avg: 85000 },
      mid: { min: 90000, max: 140000, avg: 115000 },
      senior: { min: 130000, max: 190000, avg: 160000 },
      lead: { min: 160000, max: 280000, avg: 220000 }
    }
  ];

  const formatSalary = (amount: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(amount);
  };

  const getFilteredData = () => {
    if (selectedRole === 'all' && selectedExperience === 'all') {
      return salaryData;
    }
    
    return salaryData.filter(item => {
      const roleMatch = selectedRole === 'all' || item.role.toLowerCase().replace(' ', '-') === selectedRole;
      return roleMatch;
    });
  };

  const getExperienceData = (data: any) => {
    switch (selectedExperience) {
      case 'entry': return data.entry;
      case 'mid': return data.mid;
      case 'senior': return data.senior;
      case 'lead': return data.lead;
      default: return data.mid; // Default to mid level
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-12">
            <h1 className="text-4xl md:text-5xl font-bold bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 bg-clip-text text-transparent mb-4">
              Remote Salary Guide
            </h1>
            <p className="text-xl text-gray-600 max-w-3xl mx-auto">
              Discover competitive salary ranges for remote positions across different roles and experience levels.
            </p>
          </div>

          {/* Filters */}
          <div className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20 mb-8">
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Briefcase className="w-4 h-4 inline mr-2" />
                  Job Role
                </label>
                <select
                  value={selectedRole}
                  onChange={(e) => setSelectedRole(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {roles.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  <Users className="w-4 h-4 inline mr-2" />
                  Experience Level
                </label>
                <select
                  value={selectedExperience}
                  onChange={(e) => setSelectedExperience(e.target.value)}
                  className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  {experienceLevels.map((level) => (
                    <option key={level.value} value={level.value}>
                      {level.label}
                    </option>
                  ))}
                </select>
              </div>
            </div>
          </div>

          {/* Salary Data */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-12">
            {getFilteredData().map((data, index) => {
              const salaryInfo = getExperienceData(data);
              return (
                <div
                  key={index}
                  className="bg-white/80 backdrop-blur-sm rounded-2xl p-6 shadow-lg border border-white/20 hover:shadow-xl transition-all duration-300"
                >
                  <div className="flex items-center justify-between mb-4">
                    <h3 className="text-xl font-bold text-gray-900">{data.role}</h3>
                    <DollarSign className="w-6 h-6 text-green-500" />
                  </div>
                  
                  <div className="space-y-3">
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Average:</span>
                      <span className="text-2xl font-bold text-green-600">
                        {formatSalary(salaryInfo.avg)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-gray-600">Range:</span>
                      <span className="text-lg text-gray-800">
                        {formatSalary(salaryInfo.min)} - {formatSalary(salaryInfo.max)}
                      </span>
                    </div>
                  </div>

                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <div className="flex items-center text-sm text-gray-500">
                      <TrendingUp className="w-4 h-4 mr-1" />
                      <span>Based on 2024 remote job market data</span>
                    </div>
                  </div>
                </div>
              );
            })}
          </div>

          {/* Insights */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 rounded-2xl p-8 text-white mb-8">
            <h2 className="text-3xl font-bold mb-6 text-center">Key Insights</h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="text-center">
                <BarChart3 className="w-12 h-12 mx-auto mb-3 text-yellow-300" />
                <h3 className="text-xl font-semibold mb-2">Remote Premium</h3>
                <p className="text-blue-100">
                  Remote workers often earn 10-20% more than local counterparts due to cost savings for companies.
                </p>
              </div>
              <div className="text-center">
                <MapPin className="w-12 h-12 mx-auto mb-3 text-yellow-300" />
                <h3 className="text-xl font-semibold mb-2">Location Flexibility</h3>
                <p className="text-blue-100">
                  Salaries vary by company location, with tech hubs typically offering higher compensation.
                </p>
              </div>
              <div className="text-center">
                <TrendingUp className="w-12 h-12 mx-auto mb-3 text-yellow-300" />
                <h3 className="text-xl font-semibold mb-2">Growth Potential</h3>
                <p className="text-blue-100">
                  Remote roles offer excellent growth opportunities with clear advancement paths.
                </p>
              </div>
            </div>
          </div>

          {/* Call to Action */}
          <div className="text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-4">
              Ready to Find Your Perfect Remote Role?
            </h2>
            <p className="text-xl text-gray-600 mb-6">
              Use this salary guide to negotiate better compensation for your next remote position.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <button className="bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold px-8 py-3 rounded-lg hover:from-blue-700 hover:to-purple-700 transition-all duration-200">
                Browse Remote Jobs
              </button>
              <button className="border-2 border-blue-600 text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-blue-600 hover:text-white transition-colors duration-200">
                Create Profile
              </button>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SalaryGuide; 