import React, { useState } from 'react';
import { 
  FaShieldAlt, 
  FaSearch, 
  FaExclamationTriangle,
  FaCheckCircle,
  FaSpinner,
  FaEye,
  FaDownload,
  FaChartBar,
  FaHistory,
  FaFilter,
  FaSort,
  FaFlag,
  FaBan,
  FaCheck,
  FaTimes,
  FaInfoCircle,
  FaBrain,
  FaRobot,
  FaUserShield,
  FaClipboardCheck,
  FaClock,
  FaMapMarkerAlt,
  FaDollarSign,
  FaBuilding,
  FaStar,
  FaThumbsUp,
  FaThumbsDown
} from 'react-icons/fa';
import Layout from '../components/Layout';

interface JobAnalysis {
  job_id: string;
  title: string;
  company: string;
  location: string;
  risk_level: 'low' | 'medium' | 'high' | 'critical';
  confidence_score: number;
  red_flags: string[];
  suspicious_patterns: string[];
  ai_analysis: string;
  recommendation: string;
  analyzed_at: string;
  status: 'pending' | 'analyzed' | 'flagged' | 'approved';
}

interface AnalysisStats {
  total_jobs: number;
  high_risk_jobs: number;
  medium_risk_jobs: number;
  low_risk_jobs: number;
  average_confidence: number;
  recent_analyses: number;
}

const FakeJobDetection: React.FC = () => {
  const [jobUrl, setJobUrl] = useState('');
  const [jobAnalysis, setJobAnalysis] = useState<JobAnalysis | null>(null);
  const [analysisHistory, setAnalysisHistory] = useState<JobAnalysis[]>([]);
  const [stats, setStats] = useState<AnalysisStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'analyze' | 'history' | 'stats'>('analyze');

  const analyzeJob = async () => {
    if (!jobUrl.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2500));

      const mockAnalysis: JobAnalysis = {
        job_id: "JOB_" + Math.random().toString(36).substr(2, 9).toUpperCase(),
        title: "Senior Software Engineer - Remote",
        company: "TechStartup Inc",
        location: "Remote",
        risk_level: "medium",
        confidence_score: 78,
        red_flags: [
          "Company website is very basic with limited information",
          "Job posting contains multiple spelling errors",
          "Salary range is unusually high for the position",
          "Contact email is generic (hr@company.com)"
        ],
        suspicious_patterns: [
          "Urgent hiring language",
          "Vague job requirements",
          "No specific company details",
          "Generic job description"
        ],
        ai_analysis: "This job posting shows several concerning patterns that suggest it may not be legitimate. The combination of urgent hiring language, vague requirements, and a generic company profile raises red flags. However, some legitimate startups may have similar characteristics, so this should be investigated further.",
        recommendation: "Proceed with caution. Verify the company's existence and contact them directly through official channels. Request additional information about the role and company before proceeding with any application.",
        analyzed_at: new Date().toISOString(),
        status: 'analyzed'
      };

      setJobAnalysis(mockAnalysis);
      setAnalysisHistory(prev => [mockAnalysis, ...prev.slice(0, 9)]);
    } catch (err) {
      setError('Job analysis failed. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  const loadStats = async () => {
    setLoading(true);
    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 1000));

      const mockStats: AnalysisStats = {
        total_jobs: 1247,
        high_risk_jobs: 89,
        medium_risk_jobs: 234,
        low_risk_jobs: 924,
        average_confidence: 82.5,
        recent_analyses: 156
      };

      setStats(mockStats);
    } catch (err) {
      setError('Failed to load statistics.');
    } finally {
      setLoading(false);
    }
  };

  const getRiskLevelColor = (level: string) => {
    switch (level) {
      case 'critical':
        return 'text-red-600 bg-red-100 border-red-200';
      case 'high':
        return 'text-orange-600 bg-orange-100 border-orange-200';
      case 'medium':
        return 'text-yellow-600 bg-yellow-100 border-yellow-200';
      case 'low':
        return 'text-green-600 bg-green-100 border-green-200';
      default:
        return 'text-gray-600 bg-gray-100 border-gray-200';
    }
  };

  const getRiskLevelIcon = (level: string) => {
    switch (level) {
      case 'critical':
        return <FaExclamationTriangle className="text-red-500" />;
      case 'high':
        return <FaExclamationTriangle className="text-orange-500" />;
      case 'medium':
        return <FaInfoCircle className="text-yellow-500" />;
      case 'low':
        return <FaCheckCircle className="text-green-500" />;
      default:
        return <FaInfoCircle className="text-gray-500" />;
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-blue-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-red-50 via-white to-orange-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              AI Fake Job Detection
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Protect yourself from fraudulent job postings with our AI-powered detection system. 
              Analyze job listings for suspicious patterns and red flags.
            </p>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center mb-8">
            <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-1">
              <button
                onClick={() => setActiveTab('analyze')}
                className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                  activeTab === 'analyze'
                    ? 'bg-gradient-to-r from-red-500 to-orange-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <FaSearch className="inline mr-2" />
                Analyze Job
              </button>
              <button
                onClick={() => setActiveTab('history')}
                className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                  activeTab === 'history'
                    ? 'bg-gradient-to-r from-red-500 to-orange-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <FaHistory className="inline mr-2" />
                Analysis History
              </button>
              <button
                onClick={() => {
                  setActiveTab('stats');
                  loadStats();
                }}
                className={`px-6 py-3 rounded-md font-medium transition-all duration-200 ${
                  activeTab === 'stats'
                    ? 'bg-gradient-to-r from-red-500 to-orange-600 text-white shadow-lg'
                    : 'text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}
              >
                <FaChartBar className="inline mr-2" />
                Statistics
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

          {/* Main Content */}
          <div className="max-w-6xl mx-auto">
            {/* Analyze Job Tab */}
            {activeTab === 'analyze' && (
              <div className="space-y-6">
                {/* Job URL Input */}
                <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                  <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                    <FaShieldAlt className="mr-3 text-red-500" />
                    Analyze Job Posting
                  </h2>

                  <div className="space-y-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Job Posting URL
                      </label>
                      <input
                        type="url"
                        value={jobUrl}
                        onChange={(e) => setJobUrl(e.target.value)}
                        placeholder="https://example.com/job-posting/123"
                        className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent"
                      />
                    </div>

                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
                        <FaBrain className="mr-2" />
                        How AI Detection Works
                      </h3>
                      <ul className="text-blue-800 space-y-1 text-sm">
                        <li>• Analyzes job posting content and company information</li>
                        <li>• Identifies suspicious patterns and red flags</li>
                        <li>• Checks for common fraud indicators</li>
                        <li>• Provides confidence scores and recommendations</li>
                      </ul>
                    </div>

                    <button
                      onClick={analyzeJob}
                      disabled={!jobUrl.trim() || loading}
                      className="w-full bg-gradient-to-r from-red-500 to-orange-600 text-white py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                    >
                      {loading ? (
                        <FaSpinner className="animate-spin mx-auto" />
                      ) : (
                        <>
                          <FaSearch className="inline mr-2" />
                          Analyze for Fraud
                        </>
                      )}
                    </button>
                  </div>
                </div>

                {/* Analysis Results */}
                {jobAnalysis && (
                  <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                    <h3 className="text-xl font-bold text-gray-900 mb-6 flex items-center">
                      <FaRobot className="mr-3 text-red-500" />
                      Analysis Results
                    </h3>

                    <div className="space-y-6">
                      {/* Job Info */}
                      <div className="bg-gray-50 rounded-lg p-6">
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                          <div>
                            <h4 className="font-semibold text-gray-900">{jobAnalysis.title}</h4>
                            <div className="flex items-center text-gray-600 mt-1">
                              <FaBuilding className="mr-2" />
                              <span>{jobAnalysis.company}</span>
                            </div>
                          </div>
                          <div className="flex items-center text-gray-600">
                            <FaMapMarkerAlt className="mr-2" />
                            <span>{jobAnalysis.location}</span>
                          </div>
                        </div>
                      </div>

                      {/* Risk Assessment */}
                      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                        <div className={`border rounded-lg p-4 ${getRiskLevelColor(jobAnalysis.risk_level)}`}>
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold">Risk Level</span>
                            {getRiskLevelIcon(jobAnalysis.risk_level)}
                          </div>
                          <div className="text-2xl font-bold capitalize">{jobAnalysis.risk_level}</div>
                        </div>
                        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-blue-900">Confidence</span>
                            <FaStar className="text-blue-500" />
                          </div>
                          <div className={`text-2xl font-bold ${getConfidenceColor(jobAnalysis.confidence_score)}`}>
                            {jobAnalysis.confidence_score}%
                          </div>
                        </div>
                        <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
                          <div className="flex items-center justify-between mb-2">
                            <span className="font-semibold text-purple-900">Red Flags</span>
                            <FaFlag className="text-purple-500" />
                          </div>
                          <div className="text-2xl font-bold text-purple-600">
                            {jobAnalysis.red_flags.length}
                          </div>
                        </div>
                      </div>

                      {/* Red Flags */}
                      {jobAnalysis.red_flags.length > 0 && (
                        <div className="bg-red-50 border border-red-200 rounded-lg p-6">
                          <h4 className="font-semibold text-red-900 mb-4 flex items-center">
                            <FaExclamationTriangle className="mr-2" />
                            Red Flags Detected
                          </h4>
                          <ul className="space-y-2">
                            {jobAnalysis.red_flags.map((flag, index) => (
                              <li key={index} className="flex items-start text-red-800">
                                <FaTimes className="text-red-500 mr-2 mt-1 flex-shrink-0" />
                                <span>{flag}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* Suspicious Patterns */}
                      {jobAnalysis.suspicious_patterns.length > 0 && (
                        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                                                <h4 className="font-semibold text-yellow-900 mb-4 flex items-center">
                        <FaExclamationTriangle className="mr-2" />
                        Suspicious Patterns
                      </h4>
                          <ul className="space-y-2">
                            {jobAnalysis.suspicious_patterns.map((pattern, index) => (
                              <li key={index} className="flex items-start text-yellow-800">
                                <FaInfoCircle className="text-yellow-500 mr-2 mt-1 flex-shrink-0" />
                                <span>{pattern}</span>
                              </li>
                            ))}
                          </ul>
                        </div>
                      )}

                      {/* AI Analysis */}
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                        <h4 className="font-semibold text-blue-900 mb-4 flex items-center">
                          <FaBrain className="mr-2" />
                          AI Analysis
                        </h4>
                        <p className="text-blue-800 leading-relaxed">
                          {jobAnalysis.ai_analysis}
                        </p>
                      </div>

                      {/* Recommendation */}
                      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                        <h4 className="font-semibold text-green-900 mb-4 flex items-center">
                          <FaClipboardCheck className="mr-2" />
                          Recommendation
                        </h4>
                        <p className="text-green-800 leading-relaxed">
                          {jobAnalysis.recommendation}
                        </p>
                      </div>

                      {/* Action Buttons */}
                      <div className="flex justify-center space-x-4">
                        <button
                          onClick={() => {
                            setJobAnalysis(null);
                            setJobUrl('');
                          }}
                          className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                        >
                          Analyze Another Job
                        </button>
                        <button className="bg-red-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-red-700 transition-colors">
                          <FaFlag className="inline mr-2" />
                          Report Job
                        </button>
                        <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                          <FaDownload className="inline mr-2" />
                          Download Report
                        </button>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}

            {/* Analysis History Tab */}
            {activeTab === 'history' && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaHistory className="mr-3 text-red-500" />
                  Analysis History
                </h2>

                {analysisHistory.length === 0 ? (
                  <div className="text-center py-12">
                    <FaHistory className="text-4xl text-gray-400 mx-auto mb-4" />
                    <h3 className="text-xl font-semibold text-gray-900 mb-2">
                      No Analysis History
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Start by analyzing a job posting to see your history here.
                    </p>
                    <button
                      onClick={() => setActiveTab('analyze')}
                      className="bg-gradient-to-r from-red-500 to-orange-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200"
                    >
                      Analyze a Job
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {analysisHistory.map((analysis, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
                        <div className="flex justify-between items-start mb-4">
                          <div className="flex-1">
                            <h4 className="font-semibold text-gray-900 mb-2">{analysis.title}</h4>
                            <div className="flex items-center text-gray-600 mb-2">
                              <FaBuilding className="mr-2" />
                              <span>{analysis.company}</span>
                              <span className="mx-2">•</span>
                              <FaMapMarkerAlt className="mr-2" />
                              <span>{analysis.location}</span>
                            </div>
                            <div className="flex items-center text-gray-600">
                              <FaClock className="mr-2" />
                              <span>{new Date(analysis.analyzed_at).toLocaleDateString()}</span>
                            </div>
                          </div>
                          <div className="text-right">
                            <div className={`inline-flex items-center px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(analysis.risk_level)}`}>
                              {getRiskLevelIcon(analysis.risk_level)}
                              <span className="ml-1 capitalize">{analysis.risk_level}</span>
                            </div>
                          </div>
                        </div>

                        <div className="flex justify-between items-center">
                          <div className="flex items-center space-x-4 text-sm text-gray-600">
                            <span>Confidence: {analysis.confidence_score}%</span>
                            <span>Red Flags: {analysis.red_flags.length}</span>
                          </div>
                          <div className="flex space-x-2">
                            <button className="text-blue-600 hover:text-blue-800 font-medium">
                              <FaEye className="inline mr-1" />
                              View Details
                            </button>
                            <button className="text-red-600 hover:text-red-800 font-medium">
                              <FaFlag className="inline mr-1" />
                              Report
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Statistics Tab */}
            {activeTab === 'stats' && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaChartBar className="mr-3 text-red-500" />
                  Detection Statistics
                </h2>

                {loading ? (
                  <div className="text-center py-12">
                    <FaSpinner className="animate-spin text-4xl text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">Loading statistics...</p>
                  </div>
                ) : stats ? (
                  <div className="space-y-6">
                    {/* Summary Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
                        <div className="text-3xl font-bold text-blue-600">{stats.total_jobs}</div>
                        <div className="text-blue-800">Total Jobs Analyzed</div>
                      </div>
                      <div className="bg-red-50 border border-red-200 rounded-lg p-6 text-center">
                        <div className="text-3xl font-bold text-red-600">{stats.high_risk_jobs}</div>
                        <div className="text-red-800">High Risk Jobs</div>
                      </div>
                      <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6 text-center">
                        <div className="text-3xl font-bold text-yellow-600">{stats.medium_risk_jobs}</div>
                        <div className="text-yellow-800">Medium Risk Jobs</div>
                      </div>
                      <div className="bg-green-50 border border-green-200 rounded-lg p-6 text-center">
                        <div className="text-3xl font-bold text-green-600">{stats.low_risk_jobs}</div>
                        <div className="text-green-800">Low Risk Jobs</div>
                      </div>
                    </div>

                    {/* Additional Stats */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                        <h3 className="font-semibold text-purple-900 mb-4">Detection Accuracy</h3>
                        <div className="text-3xl font-bold text-purple-600 mb-2">
                          {stats.average_confidence}%
                        </div>
                        <p className="text-purple-800 text-sm">
                          Average confidence score across all analyses
                        </p>
                      </div>
                      <div className="bg-orange-50 border border-orange-200 rounded-lg p-6">
                        <h3 className="font-semibold text-orange-900 mb-4">Recent Activity</h3>
                        <div className="text-3xl font-bold text-orange-600 mb-2">
                          {stats.recent_analyses}
                        </div>
                        <p className="text-orange-800 text-sm">
                          Jobs analyzed in the last 30 days
                        </p>
                      </div>
                    </div>

                    {/* Risk Distribution Chart */}
                    <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
                      <h3 className="font-semibold text-gray-900 mb-4">Risk Distribution</h3>
                      <div className="space-y-3">
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">Low Risk</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-green-500 h-2 rounded-full" 
                                style={{ width: `${(stats.low_risk_jobs / stats.total_jobs) * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600">{Math.round((stats.low_risk_jobs / stats.total_jobs) * 100)}%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">Medium Risk</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-yellow-500 h-2 rounded-full" 
                                style={{ width: `${(stats.medium_risk_jobs / stats.total_jobs) * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600">{Math.round((stats.medium_risk_jobs / stats.total_jobs) * 100)}%</span>
                          </div>
                        </div>
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-700">High Risk</span>
                          <div className="flex items-center space-x-2">
                            <div className="w-32 bg-gray-200 rounded-full h-2">
                              <div 
                                className="bg-red-500 h-2 rounded-full" 
                                style={{ width: `${(stats.high_risk_jobs / stats.total_jobs) * 100}%` }}
                              ></div>
                            </div>
                            <span className="text-sm text-gray-600">{Math.round((stats.high_risk_jobs / stats.total_jobs) * 100)}%</span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-12">
                    <FaChartBar className="text-4xl text-gray-400 mx-auto mb-4" />
                    <p className="text-gray-600">No statistics available.</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default FakeJobDetection; 