import React from 'react';
import { useQuery } from 'react-query';
import { Link } from 'react-router-dom';
import { jobService } from '../services/AllServices';
import WorkIcon from '@mui/icons-material/Work';
import DocumentScannerIcon from '@mui/icons-material/DocumentScanner';
import StackedLineChartIcon from '@mui/icons-material/StackedLineChart';
import FavoriteIcon from '@mui/icons-material/Favorite';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import PendingIcon from '@mui/icons-material/Pending';

const Dashboard: React.FC = () => {
  const { data: recentJobs, isLoading: isLoadingJobs } = useQuery(
    ['recentJobs'],
    () => jobService.getJobs({ limit: 5 })
  );

  const { data: recommendations, isLoading: isLoadingRecommendations } = useQuery(
    ['recommendations'],
    () => jobService.getJobs({ recommended: true, limit: 3 })
  );

  // Mock data for dashboard statistics
  const stats = {
    applications: {
      total: 12,
      pending: 5,
      viewed: 3,
      interviews: 2,
      rejected: 2
    },
    savedJobs: 8,
    profileViews: 24,
    profileCompleteness: 85,
    skills: ['React', 'JavaScript', 'TypeScript', 'Node.js', 'HTML/CSS']
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Dashboard</h1>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <WorkIcon className="text-blue-500 mr-3" />
            <h2 className="text-lg font-semibold">Applications</h2>
          </div>
          <p className="text-3xl font-bold mb-2">{stats.applications.total}</p>
          <div className="flex flex-col text-sm text-gray-500">
            <span>{stats.applications.pending} pending</span>
            <span>{stats.applications.interviews} interviews</span>
          </div>
          <Link to="/my-jobs" className="text-blue-600 text-sm mt-3 inline-block">View all applications</Link>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <FavoriteIcon className="text-red-500 mr-3" />
            <h2 className="text-lg font-semibold">Saved Jobs</h2>
          </div>
          <p className="text-3xl font-bold mb-2">{stats.savedJobs}</p>
          <div className="flex flex-col text-sm text-gray-500">
            <span>Last saved: 2 days ago</span>
          </div>
          <Link to="/saved-jobs" className="text-blue-600 text-sm mt-3 inline-block">View saved jobs</Link>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <DocumentScannerIcon className="text-green-500 mr-3" />
            <h2 className="text-lg font-semibold">Resume</h2>
          </div>
          <p className="text-3xl font-bold mb-2">{stats.profileCompleteness}%</p>
          <div className="flex flex-col text-sm text-gray-500">
            <span>Profile completeness</span>
          </div>
          <Link to="/my-resumes" className="text-blue-600 text-sm mt-3 inline-block">Update resume</Link>
        </div>
        
        <div className="bg-white rounded-lg shadow p-6">
          <div className="flex items-center mb-4">
            <StackedLineChartIcon className="text-purple-500 mr-3" />
            <h2 className="text-lg font-semibold">Activity</h2>
          </div>
          <p className="text-3xl font-bold mb-2">{stats.profileViews}</p>
          <div className="flex flex-col text-sm text-gray-500">
            <span>Profile views this month</span>
          </div>
          <Link to="/profile" className="text-blue-600 text-sm mt-3 inline-block">View profile</Link>
        </div>
      </div>
      
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2">
          <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
            <div className="p-4 bg-blue-50 border-b border-blue-100">
              <h2 className="text-lg font-semibold">Recent Applications</h2>
            </div>
            {isLoadingJobs ? (
              <div className="p-6 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {recentJobs?.slice(0, 5).map((job, index) => (
                  <div key={index} className="p-4 hover:bg-gray-50">
                    <div className="flex justify-between items-start">
                      <div>
                        <h3 className="font-medium">{job.title}</h3>
                        <p className="text-sm text-gray-600">{job.company.name}</p>
                        <div className="flex items-center mt-1 text-xs text-gray-500">
                          <span className="mr-3">Applied on {new Date().toLocaleDateString()}</span>
                          {index % 3 === 0 ? (
                            <span className="flex items-center text-yellow-600">
                              <PendingIcon className="h-4 w-4 mr-1" /> Pending
                            </span>
                          ) : (
                            <span className="flex items-center text-green-600">
                              <CheckCircleIcon className="h-4 w-4 mr-1" /> Viewed
                            </span>
                          )}
                        </div>
                      </div>
                      <Link to={`/jobs/${job.id}`} className="text-sm text-blue-600">View</Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="p-4 bg-gray-50 border-t border-gray-200">
              <Link to="/my-jobs" className="text-blue-600 text-sm">View all applications</Link>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 bg-blue-50 border-b border-blue-100">
              <h2 className="text-lg font-semibold">Job Search Tips</h2>
            </div>
            <div className="p-6">
              <div className="mb-4">
                <h3 className="font-medium mb-2">Complete Your Profile</h3>
                <p className="text-sm text-gray-600">A complete profile increases your chances of getting noticed by employers.</p>
              </div>
              <div className="mb-4">
                <h3 className="font-medium mb-2">Keep Your Skills Updated</h3>
                <p className="text-sm text-gray-600">Regularly update your skills to match the job market demands.</p>
              </div>
              <div>
                <h3 className="font-medium mb-2">Follow Up On Applications</h3>
                <p className="text-sm text-gray-600">Sending a follow-up email after a week can show your continued interest.</p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="lg:col-span-1">
          <div className="bg-white rounded-lg shadow overflow-hidden mb-6">
            <div className="p-4 bg-blue-50 border-b border-blue-100">
              <h2 className="text-lg font-semibold">Your Skills</h2>
            </div>
            <div className="p-6">
              <div className="flex flex-wrap gap-2 mb-4">
                {stats.skills.map((skill, index) => (
                  <span key={index} className="bg-gray-100 px-3 py-1 rounded-full text-sm">
                    {skill}
                  </span>
                ))}
              </div>
              <Link to="/my-skills" className="text-blue-600 text-sm">Manage skills</Link>
            </div>
          </div>
          
          <div className="bg-white rounded-lg shadow overflow-hidden">
            <div className="p-4 bg-blue-50 border-b border-blue-100">
              <h2 className="text-lg font-semibold">Recommended Jobs</h2>
            </div>
            {isLoadingRecommendations ? (
              <div className="p-6 text-center">
                <div className="animate-spin rounded-full h-8 w-8 border-t-2 border-b-2 border-blue-500 mx-auto"></div>
              </div>
            ) : (
              <div className="divide-y divide-gray-200">
                {recommendations?.slice(0, 3).map((job, index) => (
                  <div key={index} className="p-4 hover:bg-gray-50">
                    <h3 className="font-medium">{job.title}</h3>
                    <p className="text-sm text-gray-600">{job.company.name}</p>
                    <div className="flex justify-between items-center mt-2">
                      <span className="text-xs text-gray-500">{job.location}</span>
                      <Link to={`/jobs/${job.id}`} className="text-sm text-blue-600">View</Link>
                    </div>
                  </div>
                ))}
              </div>
            )}
            <div className="p-4 bg-gray-50 border-t border-gray-200">
              <Link to="/jobs" className="text-blue-600 text-sm">See more jobs</Link>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard; 