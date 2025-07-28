import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Job } from '../types/job';
import Layout from '../components/Layout';
import { ArrowLeft, MapPin, Clock, Globe, Calendar, ExternalLink } from 'lucide-react';

const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchJobDetails = async () => {
      if (!id) {
        setError('Job ID is required');
        setLoading(false);
        return;
      }

      try {
        setLoading(true);
        const response = await fetch(`/api/v1/jobs/${id}`);
        
        if (!response.ok) {
          if (response.status === 404) {
            setError('Job not found');
          } else {
            setError('Failed to load job details');
          }
          setLoading(false);
          return;
        }

        const jobData = await response.json();
        setJob(jobData);
      } catch (err) {
        console.error('Error fetching job details:', err);
        setError('Failed to load job details');
      } finally {
        setLoading(false);
      }
    };

    fetchJobDetails();
  }, [id]);

  const getCompanyName = () => {
    if (!job) return '';
    if (typeof job.company === 'string') {
      return job.company;
    }
    return job.company?.name || 'Unknown Company';
  };

  const getCompanyLogo = () => {
    const companyName = getCompanyName();
    const cleanCompanyName = companyName.toLowerCase()
      .replace(/\s+/g, '')
      .replace(/inc\.|ltd\.|llc|corp\.?|corporation|company|co\.|gmbh|ag/gi, '');
    
    return `https://logo.clearbit.com/${cleanCompanyName}.com`;
  };

  const formatSalary = () => {
    if (!job?.salary) return 'Salary not specified';
    
    if (job.salary.min && job.salary.max) {
      return `$${job.salary.min.toLocaleString()} - $${job.salary.max.toLocaleString()}`;
    } else if (job.salary.min) {
      return `$${job.salary.min.toLocaleString()}+`;
    } else if (job.salary.max) {
      return `Up to $${job.salary.max.toLocaleString()}`;
    }
    
    return 'Salary not specified';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric'
    });
  };

  if (loading) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
            <p className="text-gray-600">Loading job details...</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (error || !job) {
    return (
      <Layout>
        <div className="min-h-screen flex items-center justify-center">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Job Not Found</h1>
            <p className="text-gray-600 mb-6">{error || 'The job you are looking for does not exist.'}</p>
            <button
              onClick={() => navigate('/jobs/search')}
              className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Browse All Jobs
            </button>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50">
        {/* Header */}
        <div className="bg-white border-b border-gray-200">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
            <button
              onClick={() => navigate(-1)}
              className="flex items-center text-gray-600 hover:text-gray-900 mb-4 transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-2" />
              Back to Jobs
            </button>
            
            <div className="flex items-start space-x-4">
              <img
                src={getCompanyLogo()}
                alt={`${getCompanyName()} logo`}
                className="w-16 h-16 rounded-lg object-contain bg-gray-50 p-2"
                onError={(e) => {
                  e.currentTarget.style.display = 'none';
                }}
              />
              
              <div className="flex-1">
                <h1 className="text-3xl font-bold text-gray-900 mb-2">{job.title}</h1>
                <p className="text-xl text-gray-600 mb-4">{getCompanyName()}</p>
                
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500">
                  <div className="flex items-center">
                    <MapPin className="w-4 h-4 mr-1" />
                    {job.location || 'Remote'}
                  </div>
                  
                  {job.isRemote && (
                    <div className="flex items-center">
                      <Globe className="w-4 h-4 mr-1" />
                      Remote
                    </div>
                  )}
                  
                  <div className="flex items-center">
                    <Clock className="w-4 h-4 mr-1" />
                    {job.job_type || 'Full-time'}
                  </div>
                  
                  {job.posted_date && (
                    <div className="flex items-center">
                      <Calendar className="w-4 h-4 mr-1" />
                      Posted {formatDate(job.posted_date)}
                    </div>
                  )}
                </div>
              </div>
              
              <div className="text-right">
                <div className="text-2xl font-bold text-green-600 mb-2">
                  {formatSalary()}
                </div>
                <button className="bg-blue-600 text-white px-6 py-3 rounded-lg hover:bg-blue-700 transition-colors">
                  Apply Now
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Content */}
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
            {/* Main Content */}
            <div className="lg:col-span-2">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                <h2 className="text-xl font-semibold text-gray-900 mb-4">Job Description</h2>
                <div className="prose max-w-none">
                  <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                    {job.description || 'No description available.'}
                  </p>
                </div>
              </div>

              {job.requirements && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Requirements</h2>
                  <div className="prose max-w-none">
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {job.requirements}
                    </p>
                  </div>
                </div>
              )}

              {job.benefits && (
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h2 className="text-xl font-semibold text-gray-900 mb-4">Benefits</h2>
                  <div className="prose max-w-none">
                    <p className="text-gray-700 leading-relaxed whitespace-pre-wrap">
                      {job.benefits}
                    </p>
                  </div>
                </div>
              )}
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-1">
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Job Overview</h3>
                
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Salary</span>
                    <span className="font-medium text-green-600">{formatSalary()}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Location</span>
                    <span className="font-medium">{job.location || 'Remote'}</span>
                  </div>
                  
                  <div className="flex items-center justify-between">
                    <span className="text-gray-600">Job Type</span>
                    <span className="font-medium">{job.job_type || 'Full-time'}</span>
                  </div>
                  
                  {job.experience_level && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Experience</span>
                      <span className="font-medium">{job.experience_level}</span>
                    </div>
                  )}
                  
                  {job.posted_date && (
                    <div className="flex items-center justify-between">
                      <span className="text-gray-600">Posted</span>
                      <span className="font-medium">{formatDate(job.posted_date)}</span>
                    </div>
                  )}
                </div>
              </div>

              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Company Info</h3>
                
                <div className="flex items-center space-x-3 mb-4">
                  <img
                    src={getCompanyLogo()}
                    alt={`${getCompanyName()} logo`}
                    className="w-12 h-12 rounded-lg object-contain bg-gray-50 p-1"
                    onError={(e) => {
                      e.currentTarget.style.display = 'none';
                    }}
                  />
                  <div>
                    <h4 className="font-medium text-gray-900">{getCompanyName()}</h4>
                    {job.company && typeof job.company === 'object' && job.company.industry && (
                      <p className="text-sm text-gray-600">{job.company.industry}</p>
                    )}
                  </div>
                </div>

                <button className="w-full bg-gray-100 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-200 transition-colors flex items-center justify-center">
                  <ExternalLink className="w-4 h-4 mr-2" />
                  Visit Company Website
                </button>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default JobDetailPage; 