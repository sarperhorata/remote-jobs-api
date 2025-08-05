import React, { useState, useEffect } from 'react';
import { FaStar, FaUsers, FaHeart, FaLightbulb, FaChartLine } from 'react-icons/fa';

interface CompanyCultureTabProps {
  companyId: string;
}

interface CultureData {
  overallRating: number;
  cultureValues: string[];
  workLifeBalance: number;
  careerGrowth: number;
  diversity: number;
  benefits: string[];
  perks: string[];
  workStyle: string;
  teamSize: string;
  remotePolicy: string;
}

const CompanyCultureTab: React.FC<CompanyCultureTabProps> = ({ companyId }) => {
  const [cultureData, setCultureData] = useState<CultureData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchCultureData = async () => {
      try {
        setLoading(true);
        // Mock data - gerçek implementasyonda Glassdoor API'den gelecek
        const mockData: CultureData = {
          overallRating: 4.2,
          cultureValues: [
            'Innovation', 'Collaboration', 'Work-Life Balance', 
            'Continuous Learning', 'Diversity & Inclusion'
          ],
          workLifeBalance: 4.1,
          careerGrowth: 4.3,
          diversity: 4.0,
          benefits: [
            'Health Insurance', 'Dental Coverage', 'Vision Coverage',
            '401(k) Matching', 'Flexible PTO', 'Remote Work Options',
            'Professional Development Budget', 'Gym Membership'
          ],
          perks: [
            'Free Lunch', 'Snacks & Beverages', 'Game Room',
            'Pet-Friendly Office', 'Flexible Hours', 'Summer Fridays'
          ],
          workStyle: 'Hybrid (3 days office, 2 days remote)',
          teamSize: '50-100 employees',
          remotePolicy: 'Flexible remote work with core collaboration hours'
        };
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 1000));
        setCultureData(mockData);
      } catch (err) {
        setError('Failed to load company culture data');
        console.error('Error fetching culture data:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchCultureData();
  }, [companyId]);

  const renderRatingStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <FaStar
            key={star}
            className={`w-4 h-4 ${
              star <= rating
                ? 'text-yellow-400 fill-current'
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-2 text-sm font-medium text-gray-600">
          {rating.toFixed(1)}
        </span>
      </div>
    );
  };

  const renderMetricCard = (title: string, value: number, icon: React.ReactNode) => (
    <div className="bg-white rounded-lg p-4 shadow-sm border border-gray-200">
      <div className="flex items-center gap-3 mb-2">
        <div className="text-blue-600">{icon}</div>
        <h3 className="font-medium text-gray-900">{title}</h3>
      </div>
      {renderRatingStars(value)}
    </div>
  );

  if (loading) {
    return (
      <div className="animate-pulse">
        <div className="h-8 bg-gray-200 rounded w-1/3 mb-6"></div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-8">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-24 bg-gray-200 rounded"></div>
          ))}
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-16 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 mb-2">
          <FaHeart className="w-12 h-12 mx-auto mb-4" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Culture Data Unavailable
        </h3>
        <p className="text-gray-600">
          We couldn't load the company culture information at this time.
        </p>
      </div>
    );
  }

  if (!cultureData) {
    return null;
  }

  return (
    <div className="space-y-8">
      {/* Overall Rating */}
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Company Culture</h2>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600">
              {cultureData.overallRating.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Overall Rating</div>
          </div>
        </div>
        {renderRatingStars(cultureData.overallRating)}
      </div>

      {/* Culture Metrics */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Culture Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {renderMetricCard(
            'Work-Life Balance',
            cultureData.workLifeBalance,
            <FaHeart className="w-5 h-5" />
          )}
          {renderMetricCard(
            'Career Growth',
            cultureData.careerGrowth,
            <FaChartLine className="w-5 h-5" />
          )}
          {renderMetricCard(
            'Diversity & Inclusion',
            cultureData.diversity,
            <FaUsers className="w-5 h-5" />
          )}
        </div>
      </div>

      {/* Culture Values */}
      <div>
        <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
          <FaLightbulb className="text-yellow-500" />
          Company Values
        </h3>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {cultureData.cultureValues.map((value, index) => (
            <div
              key={index}
              className="bg-white rounded-lg p-3 border border-gray-200 hover:border-blue-300 transition-colors"
            >
              <span className="text-gray-800 font-medium">{value}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Work Environment */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Work Environment</h3>
          <div className="space-y-3">
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="text-sm font-medium text-gray-600 mb-1">Work Style</div>
              <div className="text-gray-900">{cultureData.workStyle}</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="text-sm font-medium text-gray-600 mb-1">Team Size</div>
              <div className="text-gray-900">{cultureData.teamSize}</div>
            </div>
            <div className="bg-white rounded-lg p-4 border border-gray-200">
              <div className="text-sm font-medium text-gray-600 mb-1">Remote Policy</div>
              <div className="text-gray-900">{cultureData.remotePolicy}</div>
            </div>
          </div>
        </div>

        <div>
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Benefits & Perks</h3>
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Benefits</h4>
              <div className="grid grid-cols-1 gap-2">
                {cultureData.benefits.map((benefit, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 text-sm text-gray-700"
                  >
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    {benefit}
                  </div>
                ))}
              </div>
            </div>
            <div>
              <h4 className="font-medium text-gray-900 mb-2">Perks</h4>
              <div className="grid grid-cols-1 gap-2">
                {cultureData.perks.map((perk, index) => (
                  <div
                    key={index}
                    className="flex items-center gap-2 text-sm text-gray-700"
                  >
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    {perk}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Glassdoor Integration Notice */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-start gap-3">
          <div className="text-blue-600 mt-1">
            <FaStar className="w-5 h-5" />
          </div>
          <div>
            <h4 className="font-medium text-blue-900 mb-1">
              Powered by Glassdoor
            </h4>
            <p className="text-sm text-blue-700">
              This culture information is sourced from employee reviews and company data on Glassdoor.
              The ratings and reviews are updated regularly to provide the most current insights.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyCultureTab; 