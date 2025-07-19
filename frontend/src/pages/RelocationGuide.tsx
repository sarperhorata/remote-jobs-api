import React from 'react';
import Layout from '../components/Layout';
import { ArrowLeft, MapPin, Home, Plane, DollarSign, FileText, Users, CheckCircle, Clock, AlertCircle } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const RelocationGuide: React.FC = () => {
  const navigate = useNavigate();

  const relocationSteps = [
    {
      step: 1,
      title: 'Research & Planning',
      description: 'Understand your destination and plan your move',
      tasks: [
        'Research cost of living in your destination',
        'Check visa requirements and processing times',
        'Research neighborhoods and housing options',
        'Understand local customs and culture',
        'Plan your budget for relocation expenses'
      ],
      timeline: '2-3 months before',
      icon: <FileText className="w-6 h-6" />
    },
    {
      step: 2,
      title: 'Legal & Documentation',
      description: 'Handle all legal requirements and paperwork',
      tasks: [
        'Apply for work visa and permits',
        'Get your passport updated if needed',
        'Obtain necessary certifications',
        'Prepare employment contracts',
        'Research tax implications'
      ],
      timeline: '1-2 months before',
      icon: <CheckCircle className="w-6 h-6" />
    },
    {
      step: 3,
      title: 'Housing & Logistics',
      description: 'Secure accommodation and plan logistics',
      tasks: [
        'Find temporary or permanent housing',
        'Arrange for moving services',
        'Plan transportation for arrival',
        'Set up utilities and internet',
        'Research local transportation options'
      ],
      timeline: '1 month before',
      icon: <Home className="w-6 h-6" />
    },
    {
      step: 4,
      title: 'Financial Preparation',
      description: 'Set up your finances in the new country',
      tasks: [
        'Open a local bank account',
        'Set up international banking',
        'Research health insurance options',
        'Plan for currency exchange',
        'Budget for initial expenses'
      ],
      timeline: '2-3 weeks before',
      icon: <DollarSign className="w-6 h-6" />
    },
    {
      step: 5,
      title: 'Travel & Arrival',
      description: 'Execute your travel plans and settle in',
      tasks: [
        'Book flights and accommodation',
        'Pack essential documents',
        'Arrange airport pickup',
        'Set up phone and internet',
        'Register with local authorities'
      ],
      timeline: '1 week before',
      icon: <Plane className="w-6 h-6" />
    },
    {
      step: 6,
      title: 'Settlement & Integration',
      description: 'Establish yourself in your new home',
      tasks: [
        'Find permanent housing',
        'Register for local services',
        'Join expat communities',
        'Learn local language basics',
        'Explore your new city'
      ],
      timeline: 'First month',
      icon: <Users className="w-6 h-6" />
    }
  ];

  const popularDestinations = [
    {
      city: 'San Francisco, CA',
      country: 'United States',
      highlights: ['Tech hub', 'High salaries', 'Diverse culture'],
      challenges: ['High cost of living', 'Competitive housing'],
      avgSalary: '$120,000',
      costOfLiving: 'Very High'
    },
    {
      city: 'London, UK',
      country: 'United Kingdom',
      highlights: ['Global finance center', 'Rich history', 'Multicultural'],
      challenges: ['Expensive housing', 'Weather'],
      avgSalary: '£65,000',
      costOfLiving: 'High'
    },
    {
      city: 'Berlin, Germany',
      country: 'Germany',
      highlights: ['Startup scene', 'Affordable living', 'Great culture'],
      challenges: ['Language barrier', 'Bureaucracy'],
      avgSalary: '€65,000',
      costOfLiving: 'Medium'
    },
    {
      city: 'Toronto, Canada',
      country: 'Canada',
      highlights: ['Welcoming to immigrants', 'Good healthcare', 'Safe'],
      challenges: ['Cold winters', 'High taxes'],
      avgSalary: 'C$85,000',
      costOfLiving: 'Medium-High'
    },
    {
      city: 'Amsterdam, Netherlands',
      country: 'Netherlands',
      highlights: ['Bike-friendly', 'English widely spoken', 'Progressive'],
      challenges: ['Housing shortage', 'High taxes'],
      avgSalary: '€70,000',
      costOfLiving: 'High'
    },
    {
      city: 'Singapore',
      country: 'Singapore',
      highlights: ['Low taxes', 'Safe', 'Efficient'],
      challenges: ['High cost of living', 'Hot weather'],
      avgSalary: 'S$85,000',
      costOfLiving: 'Very High'
    }
  ];

  const tips = [
    'Start planning at least 6 months before your move',
    'Keep digital copies of all important documents',
    'Research healthcare systems and insurance requirements',
    'Learn basic phrases in the local language',
    'Connect with expat communities before moving',
    'Plan for culture shock and homesickness',
    'Have a financial buffer for unexpected expenses',
    'Research local customs and business etiquette'
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
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
                  Relocation Guide
                </h1>
                <p className="text-gray-600 dark:text-gray-400 mt-1">
                  Your complete guide to moving abroad for work
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          {/* Introduction */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-8 mb-8">
            <div className="flex items-start space-x-4">
              <div className="p-3 bg-green-100 dark:bg-green-900/30 rounded-xl">
                <MapPin className="w-8 h-8 text-green-600 dark:text-green-400" />
              </div>
              <div>
                <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">
                  Planning Your International Move
                </h2>
                <p className="text-gray-600 dark:text-gray-300 leading-relaxed">
                  Relocating for work is an exciting adventure, but it requires careful planning and preparation. 
                  This guide will walk you through every step of the process, from initial research to settling 
                  into your new home. Whether you're moving across the country or to a different continent, 
                  proper preparation is key to a successful transition.
                </p>
              </div>
            </div>
          </div>

          {/* Relocation Steps */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              Relocation Timeline & Steps
            </h2>
            <div className="space-y-6">
              {relocationSteps.map((step, index) => (
                <div key={index} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-6">
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0">
                      <div className="w-12 h-12 bg-blue-100 dark:bg-blue-900/30 rounded-xl flex items-center justify-center">
                        <span className="text-blue-600 dark:text-blue-400 font-bold text-lg">{step.step}</span>
                      </div>
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="text-xl font-semibold text-gray-900 dark:text-white">
                          {step.title}
                        </h3>
                        <span className="px-3 py-1 bg-orange-100 dark:bg-orange-900/30 text-orange-800 dark:text-orange-300 text-sm font-medium rounded-full flex items-center">
                          <Clock className="w-3 h-3 mr-1" />
                          {step.timeline}
                        </span>
                      </div>
                      <p className="text-gray-600 dark:text-gray-300 mb-4">
                        {step.description}
                      </p>
                      <ul className="space-y-2">
                        {step.tasks.map((task, taskIndex) => (
                          <li key={taskIndex} className="text-sm text-gray-600 dark:text-gray-300 flex items-start">
                            <CheckCircle className="w-4 h-4 text-green-500 mr-2 mt-0.5 flex-shrink-0" />
                            {task}
                          </li>
                        ))}
                      </ul>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Popular Destinations */}
          <div className="mb-12">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-8">
              Popular Relocation Destinations
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {popularDestinations.map((destination, index) => (
                <div key={index} className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-6">
                  <div className="mb-4">
                    <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                      {destination.city}
                    </h3>
                    <p className="text-gray-500 dark:text-gray-400 text-sm">
                      {destination.country}
                    </p>
                  </div>

                  <div className="space-y-4">
                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center">
                        <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                        Highlights
                      </h4>
                      <ul className="space-y-1">
                        {destination.highlights.map((highlight, idx) => (
                          <li key={idx} className="text-sm text-gray-600 dark:text-gray-300">
                            • {highlight}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div>
                      <h4 className="font-medium text-gray-900 dark:text-white mb-2 flex items-center">
                        <AlertCircle className="w-4 h-4 text-orange-500 mr-2" />
                        Challenges
                      </h4>
                      <ul className="space-y-1">
                        {destination.challenges.map((challenge, idx) => (
                          <li key={idx} className="text-sm text-gray-600 dark:text-gray-300">
                            • {challenge}
                          </li>
                        ))}
                      </ul>
                    </div>

                    <div className="grid grid-cols-2 gap-4 pt-4 border-t border-gray-200 dark:border-gray-700">
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Avg Salary</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{destination.avgSalary}</p>
                      </div>
                      <div>
                        <p className="text-xs text-gray-500 dark:text-gray-400">Cost of Living</p>
                        <p className="font-semibold text-gray-900 dark:text-white">{destination.costOfLiving}</p>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Tips Section */}
          <div className="bg-gradient-to-r from-green-500 to-blue-600 rounded-2xl shadow-xl p-8 mb-8">
            <div className="flex items-center mb-6">
              <Users className="w-8 h-8 text-white mr-3" />
              <h2 className="text-2xl font-bold text-white">
                Pro Tips for Successful Relocation
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

          {/* Checklist */}
          <div className="bg-white/80 dark:bg-gray-800/80 backdrop-blur-lg rounded-2xl shadow-xl border border-white/20 dark:border-gray-700/20 p-8">
            <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-6">
              Pre-Move Checklist
            </h2>
            
            <div className="grid md:grid-cols-2 gap-8">
              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Documents & Legal</h3>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Valid passport (6+ months validity)
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Work visa and permits
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Educational certificates (translated)
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Employment contract
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Health insurance documents
                  </li>
                </ul>
              </div>

              <div>
                <h3 className="font-semibold text-gray-900 dark:text-white mb-4">Financial & Practical</h3>
                <ul className="space-y-2">
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    International bank account
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Emergency fund (3-6 months)
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Accommodation arrangements
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Flight bookings
                  </li>
                  <li className="flex items-center text-sm text-gray-600 dark:text-gray-300">
                    <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                    Local phone number setup
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default RelocationGuide; 