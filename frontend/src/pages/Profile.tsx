import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { jobService } from '../services/AllServices';
import { useAuth } from '../contexts/AuthContext';

// Add this interface to fix the user profile type issues
interface UserProfile {
  name: string;
  email: string;
  phone: string;
  location: string;
  cvUrl: string;
  skills: string[];
  experience: {
    title: string;
    company: string;
    startDate: string;
    endDate: string | null;
    description: string;
  }[];
  education: {
    school: string;
    degree: string;
    field: string;
    startDate: string;
    endDate: string | null;
  }[];
}

interface ExtendedUser {
  id: string;
  profile: UserProfile;
}

// Update the user type
const mockUser = {
  id: 'current-user',
  profile: {
    name: 'John Doe',
    email: 'john.doe@example.com',
    phone: '+1 (555) 123-4567',
    location: 'San Francisco, CA',
    cvUrl: 'https://example.com/cv.pdf',
    skills: ['React', 'TypeScript', 'Node.js', 'AWS', 'Docker'],
    experience: [
      {
        title: 'Senior Frontend Developer',
        company: 'Tech Corp',
        startDate: '2020-01',
        endDate: null,
        description: 'Leading frontend development for multiple projects'
      },
      {
        title: 'Frontend Developer',
        company: 'Startup Inc',
        startDate: '2018-03',
        endDate: '2019-12',
        description: 'Developed and maintained web applications'
      }
    ],
    education: [
      {
        school: 'University of Technology',
        degree: 'Bachelor of Science',
        field: 'Computer Science',
        startDate: '2014-09',
        endDate: '2018-05'
      }
    ]
  }
} as ExtendedUser;

// Mock UserProfileService
const UserProfileService = {
  uploadCV: async (userId: string, file: File) => {
    console.log(`Uploading CV for user ${userId}:`, file.name);
    return Promise.resolve({ success: true, url: URL.createObjectURL(file) });
  },
  importLinkedInProfile: async (userId: string, url: string) => {
    console.log(`Importing LinkedIn profile for user ${userId} from URL:`, url);
    return Promise.resolve({ success: true });
  }
};

const Profile: React.FC = () => {
  const { user = mockUser } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [cvFile, setCvFile] = useState<File | null>(null);
  const [linkedinUrl, setLinkedinUrl] = useState('');

  interface ApplicationHistory {
    applications: any[];
    savedJobs: any[];
  }

  const { data: applicationHistory = { applications: [], savedJobs: [] } } = useQuery<ApplicationHistory>(
    ['applications', user?.id],
    () => jobService.getJobApplications(user?.id || ''),
    { enabled: !!user?.id }
  );

  const handleCvUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setCvFile(e.target.files[0]);
      await UserProfileService.uploadCV(user?.id!, e.target.files[0]);
    }
  };

  const handleLinkedInImport = async () => {
    if (linkedinUrl) {
      await UserProfileService.importLinkedInProfile(user?.id!, linkedinUrl);
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="container mx-auto px-4">
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          {/* Tabs */}
          <div className="border-b">
            <div className="flex">
              <button
                className={`px-6 py-4 font-medium ${
                  activeTab === 'profile'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                onClick={() => setActiveTab('profile')}
              >
                Profile
              </button>
              <button
                className={`px-6 py-4 font-medium ${
                  activeTab === 'applications'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                onClick={() => setActiveTab('applications')}
              >
                Applications
              </button>
              <button
                className={`px-6 py-4 font-medium ${
                  activeTab === 'saved'
                    ? 'border-b-2 border-blue-600 text-blue-600'
                    : 'text-gray-500 hover:text-gray-700'
                }`}
                onClick={() => setActiveTab('saved')}
              >
                Saved Jobs
              </button>
            </div>
          </div>

          {/* Content */}
          <div className="p-6">
            {activeTab === 'profile' && (
              <div className="space-y-6">
                {/* CV Upload */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">CV / Resume</h2>
                  <div className="flex items-center gap-4">
                    <input
                      type="file"
                      accept=".pdf,.doc,.docx"
                      onChange={handleCvUpload}
                      className="hidden"
                      id="cv-upload"
                    />
                    <label
                      htmlFor="cv-upload"
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg cursor-pointer hover:bg-blue-700 transition"
                    >
                      Upload CV
                    </label>
                    {user?.profile?.cvUrl && (
                      <a
                        href={user.profile.cvUrl}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-blue-600 hover:underline"
                      >
                        View Current CV
                      </a>
                    )}
                  </div>
                </div>

                {/* LinkedIn Integration */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">LinkedIn Profile</h2>
                  <div className="flex items-center gap-4">
                    <input
                      type="text"
                      placeholder="Enter LinkedIn URL"
                      value={linkedinUrl}
                      onChange={(e) => setLinkedinUrl(e.target.value)}
                      className="border rounded-lg px-4 py-2 flex-grow"
                    />
                    <button
                      className="bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition"
                      onClick={handleLinkedInImport}
                    >
                      Import Profile
                    </button>
                  </div>
                </div>

                {/* Skills */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">Skills</h2>
                  <div className="flex flex-wrap gap-2">
                    {user?.profile?.skills?.map((skill) => (
                      <span
                        key={skill}
                        className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
                      >
                        {skill}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Experience */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">Experience</h2>
                  <div className="space-y-4">
                    {user?.profile?.experience?.map((exp, index) => (
                      <div key={index} className="border-l-2 border-blue-600 pl-4">
                        <h3 className="font-medium">{exp.title}</h3>
                        <p className="text-gray-600">{exp.company}</p>
                        <p className="text-sm text-gray-500">
                          {new Date(exp.startDate).toLocaleDateString()} -{' '}
                          {exp.endDate
                            ? new Date(exp.endDate).toLocaleDateString()
                            : 'Present'}
                        </p>
                        <p className="text-gray-600 mt-2">{exp.description}</p>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Education */}
                <div>
                  <h2 className="text-xl font-semibold mb-4">Education</h2>
                  <div className="space-y-4">
                    {user?.profile?.education?.map((edu, index) => (
                      <div key={index} className="border-l-2 border-blue-600 pl-4">
                        <h3 className="font-medium">{edu.school}</h3>
                        <p className="text-gray-600">
                          {edu.degree} in {edu.field}
                        </p>
                        <p className="text-sm text-gray-500">
                          {new Date(edu.startDate).toLocaleDateString()} -{' '}
                          {edu.endDate
                            ? new Date(edu.endDate).toLocaleDateString()
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
                <h2 className="text-xl font-semibold mb-4">Application History</h2>
                <div className="space-y-4">
                  {applicationHistory?.applications.length > 0 ? (
                    applicationHistory.applications.map((application) => (
                      <div
                        key={application.jobId}
                        className="border rounded-lg p-4 hover:border-blue-500 transition"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium">{application.job?.title || 'Job Title'}</h3>
                            <p className="text-gray-600">
                              {application.job?.company?.name || 'Company Name'}
                            </p>
                          </div>
                          <span
                            className={`px-3 py-1 rounded-full text-sm ${
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
                        </div>
                        <div className="mt-2 text-sm text-gray-500">
                          Applied on{' '}
                          {application.appliedAt ? new Date(application.appliedAt).toLocaleDateString() : 'Recent'}
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500">No applications yet.</p>
                  )}
                </div>
              </div>
            )}

            {activeTab === 'saved' && (
              <div>
                <h2 className="text-xl font-semibold mb-4">Saved Jobs</h2>
                <div className="space-y-4">
                  {applicationHistory?.savedJobs?.length > 0 ? (
                    applicationHistory.savedJobs.map((job) => (
                      <div
                        key={job.id}
                        className="border rounded-lg p-4 hover:border-blue-500 transition"
                      >
                        <div className="flex justify-between items-start">
                          <div>
                            <h3 className="font-medium">{job.title}</h3>
                            <p className="text-gray-600">{job.company?.name || job.companyName}</p>
                          </div>
                          <button
                            className="text-blue-600 hover:underline"
                            onClick={() => jobService.unsaveJob(user?.id!, job.id)}
                          >
                            Remove
                          </button>
                        </div>
                        <div className="mt-2 flex flex-wrap gap-2">
                          {job.skills?.slice(0, 3).map((skill) => (
                            <span
                              key={skill}
                              className="bg-gray-100 text-gray-800 text-xs px-2 py-1 rounded"
                            >
                              {skill}
                            </span>
                          ))}
                        </div>
                      </div>
                    ))
                  ) : (
                    <p className="text-gray-500">No saved jobs yet.</p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile; 