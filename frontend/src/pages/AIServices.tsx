import React, { useState, useRef } from 'react';
import { 
  FaUpload, 
  FaFilePdf, 
  FaFileWord, 
  FaFileAlt, 
  FaSearch, 
  FaChartLine, 
  FaLightbulb, 
  FaCheckCircle, 
  FaExclamationTriangle,
  FaSpinner,
  FaDownload,
  FaEye,
  FaStar,
  FaDollarSign,
  FaBriefcase,
  FaGraduationCap,
  FaMapMarkerAlt,
  FaClock,
  FaUser
} from 'react-icons/fa';
import Layout from '../components/Layout';

interface ParsedResume {
  personal_info: {
    name: string;
    email: string;
    phone: string;
    location: string;
  };
  experience: Array<{
    title: string;
    company: string;
    duration: string;
    description: string;
  }>;
  education: Array<{
    degree: string;
    institution: string;
    year: string;
  }>;
  skills: string[];
  summary: string;
}

interface JobMatch {
  job_id: string;
  title: string;
  company: string;
  location: string;
  match_score: number;
  salary_range: string;
  required_skills: string[];
  matching_skills: string[];
  missing_skills: string[];
}

interface SalaryPrediction {
  predicted_salary: number;
  confidence: number;
  factors: string[];
  market_comparison: {
    average: number;
    percentile: number;
  };
}

const AIServices: React.FC = () => {
  const [activeTab, setActiveTab] = useState<'resume' | 'matching' | 'salary'>('resume');
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [parsedResume, setParsedResume] = useState<ParsedResume | null>(null);
  const [jobMatches, setJobMatches] = useState<JobMatch[]>([]);
  const [salaryPrediction, setSalaryPrediction] = useState<SalaryPrediction | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setError(null);
    }
  };

  const parseResume = async () => {
    if (!uploadedFile) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      // Mock API call - gerçek implementasyonda backend'e gönderilecek
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockParsedResume: ParsedResume = {
        personal_info: {
          name: "John Doe",
          email: "john.doe@email.com",
          phone: "+1 (555) 123-4567",
          location: "San Francisco, CA"
        },
        experience: [
          {
            title: "Senior Software Engineer",
            company: "Tech Corp",
            duration: "2020 - Present",
            description: "Led development of scalable web applications using React and Node.js"
          },
          {
            title: "Software Engineer",
            company: "Startup Inc",
            duration: "2018 - 2020",
            description: "Developed full-stack applications and implemented CI/CD pipelines"
          }
        ],
        education: [
          {
            degree: "Bachelor of Science in Computer Science",
            institution: "University of Technology",
            year: "2018"
          }
        ],
        skills: ["React", "Node.js", "Python", "TypeScript", "AWS", "Docker", "MongoDB"],
        summary: "Experienced software engineer with 5+ years in full-stack development..."
      };

      setParsedResume(mockParsedResume);
    } catch (err) {
      setError('Resume parsing failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const findJobMatches = async () => {
    if (!parsedResume) return;

    setLoading(true);
    setError(null);

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      const mockJobMatches: JobMatch[] = [
        {
          job_id: "1",
          title: "Senior Frontend Developer",
          company: "Tech Giants Inc",
          location: "San Francisco, CA",
          match_score: 92,
          salary_range: "$120,000 - $150,000",
          required_skills: ["React", "TypeScript", "Node.js"],
          matching_skills: ["React", "TypeScript", "Node.js"],
          missing_skills: []
        },
        {
          job_id: "2",
          title: "Full Stack Engineer",
          company: "StartupXYZ",
          location: "Remote",
          match_score: 88,
          salary_range: "$100,000 - $130,000",
          required_skills: ["React", "Python", "AWS"],
          matching_skills: ["React", "Python", "AWS"],
          missing_skills: []
        },
        {
          job_id: "3",
          title: "Software Engineer",
          company: "Big Corp",
          location: "New York, NY",
          match_score: 75,
          salary_range: "$90,000 - $120,000",
          required_skills: ["Java", "Spring", "Docker"],
          matching_skills: ["Docker"],
          missing_skills: ["Java", "Spring"]
        }
      ];

      setJobMatches(mockJobMatches);
    } catch (err) {
      setError('Job matching failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const predictSalary = async () => {
    if (!parsedResume) return;

    setLoading(true);
    setError(null);

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockSalaryPrediction: SalaryPrediction = {
        predicted_salary: 125000,
        confidence: 85,
        factors: [
          "5+ years of experience",
          "Strong React/Node.js skills",
          "San Francisco market",
          "Senior level position"
        ],
        market_comparison: {
          average: 115000,
          percentile: 75
        }
      };

      setSalaryPrediction(mockSalaryPrediction);
    } catch (err) {
      setError('Salary prediction failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getFileIcon = (fileName: string) => {
    const extension = fileName.split('.').pop()?.toLowerCase();
    switch (extension) {
      case 'pdf':
        return <FaFilePdf className="text-red-500" />;
      case 'docx':
      case 'doc':
        return <FaFileWord className="text-blue-500" />;
      case 'txt':
        return <FaFileAlt className="text-gray-500" />;
      default:
        return <FaFileAlt className="text-gray-500" />;
    }
  };

  const getMatchScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              AI-Powered Career Services
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Leverage artificial intelligence to parse your resume, find perfect job matches, 
              and get accurate salary predictions to advance your career.
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-1">
              <button
                onClick={() => setActiveTab('resume')}
                className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                  activeTab === 'resume'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <FaUpload className="inline mr-2" />
                Resume Parser
              </button>
              <button
                onClick={() => setActiveTab('matching')}
                className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                  activeTab === 'matching'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <FaSearch className="inline mr-2" />
                Job Matching
              </button>
              <button
                onClick={() => setActiveTab('salary')}
                className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                  activeTab === 'salary'
                    ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <FaChartLine className="inline mr-2" />
                Salary Prediction
              </button>
            </div>
          </div>

          {/* Error Display */}
          {error && (
            <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-6">
              <div className="flex items-center">
                <FaExclamationTriangle className="text-red-500 mr-2" />
                <span className="text-red-700">{error}</span>
              </div>
            </div>
          )}

          {/* Resume Parser Tab */}
          {activeTab === 'resume' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaUpload className="mr-3 text-blue-500" />
                  Resume Parser
                </h2>

                {!parsedResume ? (
                  <div className="text-center">
                    <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 mb-6 hover:border-blue-400 transition-colors">
                      <input
                        type="file"
                        ref={fileInputRef}
                        onChange={handleFileUpload}
                        accept=".pdf,.docx,.txt"
                        className="hidden"
                      />
                      <div className="space-y-4">
                        <div className="flex justify-center space-x-4 text-4xl">
                          <FaFilePdf className="text-red-500" />
                          <FaFileWord className="text-blue-500" />
                          <FaFileAlt className="text-gray-500" />
                        </div>
                        <div>
                          <p className="text-lg font-medium text-gray-900 mb-2">
                            Upload your resume
                          </p>
                          <p className="text-gray-600 mb-4">
                            Supported formats: PDF, DOCX, TXT (Max 10MB)
                          </p>
                          <button
                            onClick={() => fileInputRef.current?.click()}
                            className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200"
                          >
                            Choose File
                          </button>
                        </div>
                      </div>
                    </div>

                    {uploadedFile && (
                      <div className="bg-green-50 border border-green-200 rounded-lg p-4 mb-6">
                        <div className="flex items-center justify-between">
                          <div className="flex items-center">
                            {getFileIcon(uploadedFile.name)}
                            <span className="ml-3 font-medium text-green-800">
                              {uploadedFile.name}
                            </span>
                          </div>
                          <button
                            onClick={parseResume}
                            disabled={loading}
                            className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
                          >
                            {loading ? (
                              <FaSpinner className="animate-spin" />
                            ) : (
                              'Parse Resume'
                            )}
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                ) : (
                  <div className="space-y-6">
                    <div className="flex justify-between items-center">
                      <h3 className="text-xl font-semibold text-gray-900">
                        Parsed Resume Data
                      </h3>
                      <button
                        onClick={() => setParsedResume(null)}
                        className="text-gray-500 hover:text-gray-700"
                      >
                        Parse Another Resume
                      </button>
                    </div>

                    {/* Personal Info */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                        <FaUser className="mr-2" />
                        Personal Information
                      </h4>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div>
                          <label className="text-sm font-medium text-gray-600">Name</label>
                          <p className="text-gray-900">{parsedResume.personal_info.name}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-600">Email</label>
                          <p className="text-gray-900">{parsedResume.personal_info.email}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-600">Phone</label>
                          <p className="text-gray-900">{parsedResume.personal_info.phone}</p>
                        </div>
                        <div>
                          <label className="text-sm font-medium text-gray-600">Location</label>
                          <p className="text-gray-900">{parsedResume.personal_info.location}</p>
                        </div>
                      </div>
                    </div>

                    {/* Experience */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                        <FaBriefcase className="mr-2" />
                        Experience
                      </h4>
                      <div className="space-y-4">
                        {parsedResume.experience.map((exp, index) => (
                          <div key={index} className="border-l-4 border-blue-500 pl-4">
                            <h5 className="font-medium text-gray-900">{exp.title}</h5>
                            <p className="text-gray-600">{exp.company} • {exp.duration}</p>
                            <p className="text-gray-700 mt-2">{exp.description}</p>
                          </div>
                        ))}
                      </div>
                    </div>

                    {/* Skills */}
                    <div className="bg-gray-50 rounded-lg p-6">
                      <h4 className="font-semibold text-gray-900 mb-4 flex items-center">
                        <FaGraduationCap className="mr-2" />
                        Skills
                      </h4>
                      <div className="flex flex-wrap gap-2">
                        {parsedResume.skills.map((skill, index) => (
                          <span
                            key={index}
                            className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                          >
                            {skill}
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Job Matching Tab */}
          {activeTab === 'matching' && (
            <div className="max-w-6xl mx-auto">
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaSearch className="mr-3 text-blue-500" />
                  AI Job Matching
                </h2>

                {!parsedResume ? (
                  <div className="text-center py-12">
                    <FaLightbulb className="text-4xl text-yellow-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Parse Your Resume First
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Upload and parse your resume to find the best job matches
                    </p>
                    <button
                      onClick={() => setActiveTab('resume')}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200"
                    >
                      Go to Resume Parser
                    </button>
                  </div>
                ) : (
                  <div>
                    <div className="flex justify-between items-center mb-6">
                      <p className="text-gray-600">
                        Based on your resume, we'll find the best job opportunities for you
                      </p>
                      <button
                        onClick={findJobMatches}
                        disabled={loading}
                        className="bg-gradient-to-r from-green-500 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                      >
                        {loading ? (
                          <FaSpinner className="animate-spin" />
                        ) : (
                          'Find Job Matches'
                        )}
                      </button>
                    </div>

                    {jobMatches.length > 0 && (
                      <div className="space-y-6">
                        {jobMatches.map((job) => (
                          <div key={job.job_id} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                            <div className="flex justify-between items-start mb-4">
                              <div className="flex-1">
                                <h3 className="text-xl font-semibold text-gray-900 mb-2">
                                  {job.title}
                                </h3>
                                <div className="flex items-center text-gray-600 mb-2">
                                  <FaBriefcase className="mr-2" />
                                  <span>{job.company}</span>
                                  <span className="mx-2">•</span>
                                  <FaMapMarkerAlt className="mr-2" />
                                  <span>{job.location}</span>
                                </div>
                                <div className="flex items-center text-gray-600">
                                  <FaDollarSign className="mr-2" />
                                  <span>{job.salary_range}</span>
                                </div>
                              </div>
                              <div className="text-right">
                                <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getMatchScoreColor(job.match_score)}`}>
                                  <FaStar className="mr-1" />
                                  {job.match_score}% Match
                                </div>
                              </div>
                            </div>

                            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                              <div>
                                <h4 className="font-medium text-gray-900 mb-2">Matching Skills</h4>
                                <div className="flex flex-wrap gap-2">
                                  {job.matching_skills.map((skill, index) => (
                                    <span
                                      key={index}
                                      className="bg-green-100 text-green-800 px-2 py-1 rounded text-sm"
                                    >
                                      {skill}
                                    </span>
                                  ))}
                                </div>
                              </div>
                              {job.missing_skills.length > 0 && (
                                <div>
                                  <h4 className="font-medium text-gray-900 mb-2">Missing Skills</h4>
                                  <div className="flex flex-wrap gap-2">
                                    {job.missing_skills.map((skill, index) => (
                                      <span
                                        key={index}
                                        className="bg-red-100 text-red-800 px-2 py-1 rounded text-sm"
                                      >
                                        {skill}
                                      </span>
                                    ))}
                                  </div>
                                </div>
                              )}
                            </div>

                            <div className="mt-4 flex justify-end space-x-3">
                              <button className="text-blue-600 hover:text-blue-800 font-medium">
                                View Job Details
                              </button>
                              <button className="bg-blue-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-blue-700">
                                Apply Now
                              </button>
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Salary Prediction Tab */}
          {activeTab === 'salary' && (
            <div className="max-w-4xl mx-auto">
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaChartLine className="mr-3 text-blue-500" />
                  AI Salary Prediction
                </h2>

                {!parsedResume ? (
                  <div className="text-center py-12">
                    <FaLightbulb className="text-4xl text-yellow-500 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      Parse Your Resume First
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Upload and parse your resume to get accurate salary predictions
                    </p>
                    <button
                      onClick={() => setActiveTab('resume')}
                      className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200"
                    >
                      Go to Resume Parser
                    </button>
                  </div>
                ) : (
                  <div>
                    <div className="flex justify-between items-center mb-6">
                      <p className="text-gray-600">
                        Get AI-powered salary predictions based on your experience and skills
                      </p>
                      <button
                        onClick={predictSalary}
                        disabled={loading}
                        className="bg-gradient-to-r from-green-500 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                      >
                        {loading ? (
                          <FaSpinner className="animate-spin" />
                        ) : (
                          'Predict Salary'
                        )}
                      </button>
                    </div>

                    {salaryPrediction && (
                      <div className="space-y-6">
                        {/* Main Prediction */}
                        <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
                          <div className="text-center">
                            <h3 className="text-2xl font-bold mb-2">
                              Predicted Salary
                            </h3>
                            <div className="text-4xl font-bold mb-2">
                              ${salaryPrediction.predicted_salary.toLocaleString()}
                            </div>
                            <div className="flex items-center justify-center">
                              <FaCheckCircle className="mr-2" />
                              <span>{salaryPrediction.confidence}% Confidence</span>
                            </div>
                          </div>
                        </div>

                        {/* Market Comparison */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                          <div className="bg-gray-50 rounded-lg p-6">
                            <h4 className="font-semibold text-gray-900 mb-4">Market Comparison</h4>
                            <div className="space-y-3">
                              <div className="flex justify-between">
                                <span className="text-gray-600">Market Average:</span>
                                <span className="font-medium">${salaryPrediction.market_comparison.average.toLocaleString()}</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Your Percentile:</span>
                                <span className="font-medium">{salaryPrediction.market_comparison.percentile}%</span>
                              </div>
                              <div className="flex justify-between">
                                <span className="text-gray-600">Difference:</span>
                                <span className={`font-medium ${salaryPrediction.predicted_salary > salaryPrediction.market_comparison.average ? 'text-green-600' : 'text-red-600'}`}>
                                  +${(salaryPrediction.predicted_salary - salaryPrediction.market_comparison.average).toLocaleString()}
                                </span>
                              </div>
                            </div>
                          </div>

                          <div className="bg-gray-50 rounded-lg p-6">
                            <h4 className="font-semibold text-gray-900 mb-4">Key Factors</h4>
                            <ul className="space-y-2">
                              {salaryPrediction.factors.map((factor, index) => (
                                <li key={index} className="flex items-center text-gray-700">
                                  <FaCheckCircle className="text-green-500 mr-2 flex-shrink-0" />
                                  {factor}
                                </li>
                              ))}
                            </ul>
                          </div>
                        </div>

                        {/* Action Buttons */}
                        <div className="flex justify-center space-x-4">
                          <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                            <FaDownload className="inline mr-2" />
                            Download Report
                          </button>
                          <button className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors">
                            <FaEye className="inline mr-2" />
                            View Similar Jobs
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default AIServices; 