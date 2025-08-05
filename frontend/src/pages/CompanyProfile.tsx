import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { 
  Briefcase, 
  Heart, 
  Users, 
  Star,
  ArrowLeft,
  Share2
} from 'lucide-react';
import Layout from '../components/Layout';
import CompanyHeader from '../components/company/CompanyHeader';
import TabNavigation from '../components/company/TabNavigation';
import CompanyJobsTab from '../components/company/CompanyJobsTab';
import CompanyCultureTab from '../components/company/CompanyCultureTab';
import EmployeeReviewsTab from '../components/company/EmployeeReviewsTab';

interface Company {
  _id: string;
  name: string;
  logo?: string;
  website?: string;
  location?: string;
  industry?: string;
  founded?: string;
  size?: string;
  description?: string;
  rating?: number;
  reviewCount?: number;
  email?: string;
  phone?: string;
}

const CompanyProfile: React.FC = () => {
  const { companyId } = useParams<{ companyId: string }>();
  const navigate = useNavigate();
  const [company, setCompany] = useState<Company | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState('jobs');
  const [isFollowing, setIsFollowing] = useState(false);

  useEffect(() => {
    if (companyId) {
      loadCompanyData();
    }
  }, [companyId]);

  const loadCompanyData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/companies/${companyId}`
      );
      
      if (response.ok) {
        const data = await response.json();
        setCompany(data);
      } else if (response.status === 404) {
        setError('Company not found');
      } else {
        setError('Failed to load company data');
      }
    } catch (error) {
      console.error('Error loading company data:', error);
      setError('Failed to load company data');
    } finally {
      setLoading(false);
    }
  };

  const handleFollowToggle = () => {
    setIsFollowing(!isFollowing);
    // TODO: Implement follow/unfollow API call
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: company?.name || 'Company Profile',
        url: window.location.href,
      });
    } else {
      // Fallback: copy to clipboard
      navigator.clipboard.writeText(window.location.href);
      // TODO: Show toast notification
    }
  };

  const tabs = [
    {
      id: 'jobs',
      label: 'Open Positions',
      icon: <Briefcase className="w-4 h-4" />,
      count: 0 // TODO: Get actual job count
    },
    {
      id: 'culture',
      label: 'Company Culture',
      icon: <Heart className="w-4 h-4" />,
      count: undefined
    },
    {
      id: 'reviews',
      label: 'Employee Reviews',
      icon: <Star className="w-4 h-4" />,
      count: company?.reviewCount
    },
    {
      id: 'about',
      label: 'About',
      icon: <Users className="w-4 h-4" />,
      count: undefined
    }
  ];

  if (loading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !company) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center py-12">
            <div className="w-16 h-16 bg-red-100 rounded-full flex items-center justify-center mx-auto mb-4">
              <Users className="w-8 h-8 text-red-600" />
            </div>
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
              {error === 'Company not found' ? 'Company Not Found' : 'Error Loading Company'}
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mb-6">
              {error === 'Company not found' 
                ? 'The company you\'re looking for doesn\'t exist or has been removed.'
                : 'There was an error loading the company data. Please try again.'
              }
            </p>
            <button
              onClick={() => navigate('/companies')}
              className="inline-flex items-center px-4 py-2 border border-transparent rounded-lg text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Companies
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-6xl mx-auto">
          {/* Back Button */}
          <div className="mb-6">
            <button
              onClick={() => navigate(-1)}
              className="inline-flex items-center text-sm text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back
            </button>
          </div>

          {/* Company Header */}
          <CompanyHeader company={company} className="mb-8" />

          {/* Action Buttons */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-4">
              <button
                onClick={handleFollowToggle}
                className={`inline-flex items-center px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isFollowing
                    ? 'bg-red-100 text-red-700 hover:bg-red-200 dark:bg-red-900 dark:text-red-300 dark:hover:bg-red-800'
                    : 'bg-blue-100 text-blue-700 hover:bg-blue-200 dark:bg-blue-900 dark:text-blue-300 dark:hover:bg-blue-800'
                }`}
              >
                <Heart className={`w-4 h-4 mr-2 ${isFollowing ? 'fill-current' : ''}`} />
                {isFollowing ? 'Following' : 'Follow Company'}
              </button>

              <button
                onClick={handleShare}
                className="inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Share2 className="w-4 h-4 mr-2" />
                Share
              </button>
            </div>
          </div>

          {/* Tab Navigation */}
          <TabNavigation
            tabs={tabs}
            activeTab={activeTab}
            onTabChange={setActiveTab}
            className="mb-8"
          />

          {/* Tab Content */}
          <div className="min-h-[400px]">
            {activeTab === 'jobs' && (
              <CompanyJobsTab companyId={company._id} />
            )}
            
            {activeTab === 'culture' && (
              <CompanyCultureTab companyId={company._id} />
            )}
            
            {activeTab === 'reviews' && (
              <EmployeeReviewsTab companyId={company._id} />
            )}
            
            {activeTab === 'about' && (
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6">
                <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">
                  About {company.name}
                </h3>
                {company.description ? (
                  <p className="text-gray-700 dark:text-gray-300 leading-relaxed">
                    {company.description}
                  </p>
                ) : (
                  <p className="text-gray-600 dark:text-gray-400">
                    No description available for this company.
                  </p>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CompanyProfile; 