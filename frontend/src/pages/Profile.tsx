import React, { useState, useEffect } from 'react';
import { jobService } from '../services/AllServices';
import { useAuth } from '../contexts/AuthContext';
import { User, Heart, FileText, Upload, ExternalLink } from 'lucide-react';

interface ApplicationHistory {
  applications: any[];
  savedJobs: any[];
}

const Profile: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [linkedinUrl, setLinkedinUrl] = useState('');
  const [applicationHistory, setApplicationHistory] = useState<ApplicationHistory>({ applications: [], savedJobs: [] });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchApplicationHistory = async () => {
      if (!user?.id) return;
      
      try {
        setIsLoading(true);
        const data = await jobService.getJobApplications(user.id);
        setApplicationHistory(data || { applications: [], savedJobs: [] });
      } catch (error) {
        console.error('Error fetching application history:', error);
      } finally {
        setIsLoading(false);
      }
    };

    fetchApplicationHistory();
  }, [user?.id]);

  const handleCvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCvFile(e.target.files[0]);
      console.log('CV uploaded:', e.target.files[0].name);
    }
  };

  const handleLinkedInImport = async () => {
    if (linkedinUrl) {
      console.log('Importing LinkedIn profile:', linkedinUrl);
    }
  };

  const menuItems = [
    {
      id: 'profile',
      label: 'My Profile',
      icon: User,
      description: 'Personal information & CV'
    },
    {
      id: 'saved',
      label: 'My Favorites',
      icon: Heart,
      description: 'Saved job opportunities'
    },
    {
      id: 'applications',
      label: 'My Applications',
      icon: FileText,
      description: 'Application history & status'
    }
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="flex gap-8">
          {/* Left Sidebar Menu */}
          <div className="w-80 bg-white rounded-lg shadow-md h-fit">
            {/* User Header */}
            <div className="p-6 border-b border-gray-200">
              <div className="flex items-center space-x-4">
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-xl font-bold">
                  {user?.name?.charAt(0) || 'U'}
                </div>
                <div>
                  <h2 className="text-xl font-bold text-gray-900">{user?.name || 'User'}</h2>
                  <p className="text-gray-600">{user?.email}</p>
                  <p className="text-sm text-blue-600 font-medium">Product Manager</p>
                </div>
              </div>
            </div>

            {/* Navigation Menu */}
            <nav className="p-4">
              <ul className="space-y-2">
                {menuItems.map((item) => {
                  const IconComponent = item.icon;
                  return (
                    <li key={item.id}>
                      <button
                        onClick={() => setActiveTab(item.id)}
                        className={`w-full flex items-center space-x-3 px-4 py-3 rounded-lg text-left transition-colors ${
                          activeTab === item.id
                            ? 'bg-blue-50 text-blue-700 border border-blue-200'
                            : 'text-gray-700 hover:bg-gray-50 hover:text-blue-600'
                        }`}
                      >
                        <IconComponent 
                          size={20} 
                          className={activeTab === item.id ? 'text-blue-600' : 'text-gray-500'} 
                        />
                        <div>
                          <div className="font-medium">{item.label}</div>
                          <div className="text-sm text-gray-500">{item.description}</div>
                        </div>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </nav>

            {/* Stats Cards */}
            <div className="p-4 border-t border-gray-200">
              <div className="grid grid-cols-2 gap-3">
                <div className="bg-blue-50 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-blue-600">
                    {applicationHistory?.applications?.length || 0}
                  </div>
                  <div className="text-xs text-blue-700">Applications</div>
                </div>
                <div className="bg-purple-50 p-3 rounded-lg text-center">
                  <div className="text-2xl font-bold text-purple-600">
                    {applicationHistory?.savedJobs?.length || 0}
                  </div>
                  <div className="text-xs text-purple-700">Saved Jobs</div>
                </div>
              </div>
            </div>
          </div>

          {/* Right Content Area */}
          <div className="flex-1 bg-white rounded-lg shadow-md">
            {/* Content Header */}
            <div className="p-6 border-b border-gray-200">
              <h1 className="text-2xl font-bold text-gray-900">
                {menuItems.find(item => item.id === activeTab)?.label}
              </h1>
              <p className="text-gray-600 mt-1">
                {menuItems.find(item => item.id === activeTab)?.description}
              </p>
            </div>

            {/* Content */}
            <div className="p-6">
              {activeTab === 'profile' && (
                <div className="space-y-8">
                  {/* Profile Summary Card */}
                  <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-lg p-6 border border-blue-100">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Profile Summary</h3>
                    <div className="grid grid-cols-2 gap-6">
                      <div>
                        <label className="text-sm font-medium text-gray-700">Full Name</label>
                        <p className="text-gray-900">{user?.profile?.name || user?.name}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Email</label>
                        <p className="text-gray-900">{user?.profile?.email || user?.email}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Phone</label>
                        <p className="text-gray-900">{user?.profile?.phone || 'Not provided'}</p>
                      </div>
                      <div>
                        <label className="text-sm font-medium text-gray-700">Location</label>
                        <p className="text-gray-900">{user?.profile?.location || 'Not provided'}</p>
                      </div>
                    </div>
                  </div>

                  {/* CV Upload Section */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4 flex items-center">
                      <Upload className="mr-2" size={20} />
                      CV / Resume
                    </h3>
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-6 text-center">
                      <div className="flex items-center justify-center gap-4">
                        <input
                          type="file"
                          accept=".pdf,.doc,.docx"
                          onChange={handleCvUpload}
                          className="hidden"
                          id="cv-upload"
                        />
                        <label
                          htmlFor="cv-upload"
                          className="bg-blue-600 text-white px-6 py-3 rounded-lg cursor-pointer hover:bg-blue-700 transition flex items-center gap-2"
                        >
                          <Upload size={16} />
                          Upload New CV
                        </label>
                        {user?.profile?.cvUrl && (
                          <a
                            href={user.profile.cvUrl}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-blue-600 hover:text-blue-800 flex items-center gap-2"
                          >
                            <ExternalLink size={16} />
                            View Current CV
                          </a>
                        )}
                      </div>
                      <p className="text-gray-500 text-sm mt-2">
                        Supported formats: PDF, DOC, DOCX (Max 5MB)
                      </p>
                    </div>
                  </div>

                  {/* Skills */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Skills & Expertise</h3>
                    <div className="flex flex-wrap gap-3">
                      {user?.profile?.skills?.map((skill) => (
                        <span
                          key={skill}
                          className="bg-gradient-to-r from-blue-100 to-purple-100 text-blue-800 px-4 py-2 rounded-full text-sm font-medium border border-blue-200"
                        >
                          {skill}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Experience */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Professional Experience</h3>
                    <div className="space-y-6">
                      {user?.profile?.experience?.map((exp, index) => (
                        <div key={index} className="relative pl-8 pb-6">
                          <div className="absolute left-0 top-0 w-4 h-4 bg-blue-600 rounded-full"></div>
                          {index < (user?.profile?.experience?.length || 0) - 1 && (
                            <div className="absolute left-2 top-4 w-0.5 h-full bg-gray-300"></div>
                          )}
                          <div className="bg-gray-50 rounded-lg p-4">
                            <h4 className="font-semibold text-gray-900">{exp.title}</h4>
                            <p className="text-blue-600 font-medium">{exp.company}</p>
                            <p className="text-sm text-gray-600 mb-2">
                              {new Date(exp.startDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} -{' '}
                              {exp.endDate
                                ? new Date(exp.endDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
                                : 'Present'}
                            </p>
                            <p className="text-gray-700">{exp.description}</p>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Education */}
                  <div>
                    <h3 className="text-lg font-semibold mb-4">Education</h3>
                    <div className="space-y-4">
                      {user?.profile?.education?.map((edu, index) => (
                        <div key={index} className="bg-gray-50 rounded-lg p-4">
                          <h4 className="font-semibold text-gray-900">{edu.school}</h4>
                          <p className="text-blue-600 font-medium">
                            {edu.degree} in {edu.field}
                          </p>
                          <p className="text-sm text-gray-600">
                            {new Date(edu.startDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })} -{' '}
                            {edu.endDate
                              ? new Date(edu.endDate).toLocaleDateString('en-US', { month: 'long', year: 'numeric' })
                              : 'Present'}
                          </p>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'applications' && (
                <div>
                  <div className="space-y-4">
                    {applicationHistory?.applications?.length > 0 ? (
                      applicationHistory.applications.map((application, index) => (
                        <div
                          key={application.jobId || index}
                          className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md transition-all"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900 text-lg">
                                {application.job?.title || 'Job Title'}
                              </h3>
                              <p className="text-blue-600 font-medium">
                                {application.job?.company?.name || 'Company Name'}
                              </p>
                              <p className="text-gray-600 mt-1">
                                {application.job?.location || 'Location not specified'}
                              </p>
                            </div>
                            <div className="text-right">
                              <span
                                className={`inline-flex px-3 py-1 rounded-full text-sm font-medium ${
                                  application.status === 'applied'
                                    ? 'bg-yellow-100 text-yellow-800'
                                    : application.status === 'interviewing'
                                    ? 'bg-blue-100 text-blue-800'
                                    : application.status === 'offered'
                                    ? 'bg-green-100 text-green-800'
                                    : application.status === 'rejected'
                                    ? 'bg-red-100 text-red-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {application.status ? application.status.charAt(0).toUpperCase() + application.status.slice(1) : 'Pending'}
                              </span>
                              <div className="text-sm text-gray-500 mt-2">
                                Applied on{' '}
                                {application.appliedAt ? new Date(application.appliedAt).toLocaleDateString() : 'Recent'}
                              </div>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12">
                        <FileText size={48} className="mx-auto text-gray-400 mb-4" />
                        <p className="text-gray-500 text-lg">No applications yet</p>
                        <p className="text-gray-400">Start applying to jobs to see your application history here</p>
                      </div>
                    )}
                  </div>
                </div>
              )}

              {activeTab === 'saved' && (
                <div>
                  <div className="space-y-4">
                    {applicationHistory?.savedJobs?.length > 0 ? (
                      applicationHistory.savedJobs.map((job, index) => (
                        <div
                          key={job.id || index}
                          className="border border-gray-200 rounded-lg p-6 hover:border-blue-300 hover:shadow-md transition-all"
                        >
                          <div className="flex justify-between items-start">
                            <div className="flex-1">
                              <h3 className="font-semibold text-gray-900 text-lg">{job.title}</h3>
                              <p className="text-blue-600 font-medium">
                                {typeof job.company === 'string' ? job.company : (job.company?.name || job.companyName)}
                              </p>
                              <p className="text-gray-600 mt-1">{job.location || 'Remote'}</p>
                              {job.skills && (
                                <div className="mt-3 flex flex-wrap gap-2">
                                  {job.skills.slice(0, 5).map((skill: string, skillIndex: number) => (
                                    <span
                                      key={skillIndex}
                                      className="bg-gray-100 text-gray-700 text-xs px-2 py-1 rounded-full"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                  {job.skills.length > 5 && (
                                    <span className="text-gray-500 text-xs">
                                      +{job.skills.length - 5} more
                                    </span>
                                  )}
                                </div>
                              )}
                            </div>
                            <div className="flex flex-col gap-2">
                              <button
                                className="text-red-600 hover:text-red-800 text-sm font-medium"
                                onClick={() => jobService.unsaveJob(user?.id!, job.id)}
                              >
                                Remove from Favorites
                              </button>
                              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                                View Job Details
                              </button>
                            </div>
                          </div>
                        </div>
                      ))
                    ) : (
                      <div className="text-center py-12">
                        <Heart size={48} className="mx-auto text-gray-400 mb-4" />
                        <p className="text-gray-500 text-lg">No saved jobs yet</p>
                        <p className="text-gray-400">Save interesting job opportunities to review them later</p>
                      </div>
                    )}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;
