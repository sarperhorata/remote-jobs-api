import React from 'react';
import Layout from '../components/Layout';
import { ArrowLeft, Globe, Building, Users, CheckCircle, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const VisaSponsorship: React.FC = () => {
  const navigate = useNavigate();

  const visaTypes = [
    {
      country: 'United States',
      visa: 'H-1B',
      description: 'Most common work visa for skilled professionals',
      requirements: ['Bachelor\'s degree or equivalent', 'Job offer from US employer', 'Specialty occupation'],
      processingTime: '3-6 months',
      quota: 'Annual cap applies'
    },
    {
      country: 'United Kingdom',
      visa: 'Skilled Worker Visa',
      description: 'Points-based system for skilled workers',
      requirements: ['Job offer from licensed sponsor', 'English language proficiency', 'Minimum salary requirement'],
      processingTime: '3-8 weeks',
      quota: 'No annual cap'
    },
    {
      country: 'Canada',
      visa: 'Express Entry',
      description: 'Fast-track immigration for skilled workers',
      requirements: ['Age under 45', 'Language proficiency', 'Work experience', 'Education'],
      processingTime: '6-8 months',
      quota: 'No annual cap'
    },
    {
      country: 'Germany',
      visa: 'EU Blue Card',
      description: 'Work permit for highly qualified professionals',
      requirements: ['University degree', 'Job offer with minimum salary', 'Health insurance'],
      processingTime: '1-3 months',
      quota: 'No annual cap'
    },
    {
      country: 'Australia',
      visa: 'Skilled Independent Visa (189)',
      description: 'Permanent residency for skilled workers',
      requirements: ['Age under 45', 'Skilled occupation', 'Points test', 'English proficiency'],
      processingTime: '6-12 months',
      quota: 'Annual cap applies'
    }
  ];

  const tips = [
    'Start the process early - visa applications can take months',
    'Ensure all documents are properly translated and certified',
    'Maintain a clean criminal record',
    'Keep your passport valid for at least 6 months beyond your intended stay',
    'Consider working with an immigration lawyer for complex cases',
    'Research company sponsorship policies before applying',
    'Network with professionals who have gone through the process'
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
        {/* Header */}
        <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg border-b border-gray-200/50 dark:border-gray-700/50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => navigate(-1)}
                className="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <ArrowLeft className="w-5 h-5 text-gray-600 dark:text-gray-300" />
              </button>
              <div>
                <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                  Visa Sponsorship Guide
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  Everything you need to know about work visas and sponsorship
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Introduction */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-8 mb-8">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-blue-100 dark:bg-blue-900/30 rounded-xl">
                <Globe className="w-8 h-8 text-blue-600 dark:text-blue-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  Understanding Visa Sponsorship
                </h2>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  Visa sponsorship is when a company agrees to sponsor your work visa application, 
                  allowing you to work legally in a foreign country. This process involves the employer 
                  demonstrating that they cannot find a suitable local candidate for the position and 
                  that hiring you will benefit the local economy.
                </p>
              </div>
            </div>
          </div>

          {/* Visa Types by Country */}
          <div className="grid gap-8 mb-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white">
              Popular Work Visa Types
            </h2>
            {visaTypes.map((visa, index) => (
              <div key={index} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-6">
                <div className="flex items-start justify-between mb-4">
                  <div>
                    <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                      {visa.country}
                    </h3>
                    <p className="text-lg font-medium text-blue-600 dark:text-blue-400">
                      {visa.visa}
                    </p>
                  </div>
                  <span className="px-3 py-1 bg-green-100 dark:bg-green-900/30 text-green-800 dark:text-green-300 text-sm font-medium rounded-full">
                    {visa.processingTime}
                  </span>
                </div>
                
                <p className="text-gray-600 dark:text-gray-300 mb-4">
                  {visa.description}
                </p>

                <div className="grid md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                      <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                      Requirements
                    </h4>
                    <ul className="space-y-2">
                      {visa.requirements.map((req, reqIndex) => (
                        <li key={reqIndex} className="text-sm text-gray-600 dark:text-gray-300 flex items-start">
                          <span className="w-1.5 h-1.5 bg-blue-500 rounded-full mt-2 mr-2 flex-shrink-0"></span>
                          {req}
                        </li>
                      ))}
                    </ul>
                  </div>
                  
                  <div>
                    <h4 className="font-semibold text-gray-900 dark:text-white mb-3 flex items-center">
                      <AlertCircle className="w-4 h-4 text-orange-500 mr-2" />
                      Important Notes
                    </h4>
                    <div className="text-sm text-gray-600 dark:text-gray-300">
                      <p><strong>Processing Time:</strong> {visa.processingTime}</p>
                      <p><strong>Quota:</strong> {visa.quota}</p>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>

          {/* Tips Section */}
          <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl shadow-xl p-8 mb-8">
            <div className="flex items-center mb-6">
              <Users className="w-8 h-8 text-white mr-3" />
              <h2 className="text-2xl font-bold text-white">
                Pro Tips for Visa Sponsorship
              </h2>
            </div>
            
            <div className="grid md:grid-cols-2 gap-4">
              {tips.map((tip, index) => (
                <div key={index} className="flex items-start space-x-3">
                  <div className="w-2 h-2 bg-white rounded-full mt-2 flex-shrink-0"></div>
                  <p className="text-white/90 text-sm leading-relaxed">
                    {tip}
                  </p>
                </div>
              ))}
            </div>
          </div>

          {/* Company Sponsorship */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-8">
            <div className="flex items-start space-x-4 mb-6">
              <div className="p-3 bg-purple-100 dark:bg-purple-900/30 rounded-xl">
                <Building className="w-8 h-8 text-purple-600 dark:text-purple-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
                  Finding Companies That Sponsor Visas
                </h2>
                <p className="text-gray-600 dark:text-gray-300">
                  Not all companies are willing or able to sponsor visas. Here's how to identify those that do:
                </p>
              </div>
            </div>

            <div className="grid md:grid-cols-3 gap-6">
              <div className="text-center p-4">
                <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <span className="text-blue-600 dark:text-blue-400 font-bold">1</span>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Check Job Postings
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Look for keywords like "visa sponsorship available", "willing to sponsor", or "H-1B sponsorship"
                </p>
              </div>

              <div className="text-center p-4">
                <div className="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <span className="text-green-600 dark:text-green-400 font-bold">2</span>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Research Companies
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Check company websites, LinkedIn, and employee reviews for sponsorship policies
                </p>
              </div>

              <div className="text-center p-4">
                <div className="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-xl flex items-center justify-center mx-auto mb-3">
                  <span className="text-purple-600 dark:text-purple-400 font-bold">3</span>
                </div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-2">
                  Network
                </h3>
                <p className="text-sm text-gray-600 dark:text-gray-300">
                  Connect with professionals who have been sponsored and ask about their experiences
                </p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default VisaSponsorship; 