import React, { useState, useRef } from 'react';
import { 
  FaUpload, 
  FaFilePdf, 
  FaFileWord, 
  FaFileAlt, 
  FaLightbulb, 
  FaCheckCircle, 
  FaExclamationTriangle,
  FaSpinner,
  FaDownload,
  FaEdit,
  FaStar,
  FaCode,
  FaDatabase,
  FaCloud,
  FaTools,
  FaGitAlt,
  FaNetworkWired,
  FaMobile,
  FaDesktop,
  FaServer,
  FaShieldAlt,
  FaChartBar,
  FaBrain,
  FaRocket
} from 'react-icons/fa';
import Layout from '../components/Layout';

interface ExtractedSkill {
  name: string;
  category: string;
  confidence: number;
  years_experience?: number;
  proficiency_level: 'beginner' | 'intermediate' | 'advanced' | 'expert';
}

interface SkillCategory {
  name: string;
  icon: React.ReactNode;
  color: string;
  skills: ExtractedSkill[];
}

const SkillsExtraction: React.FC = () => {
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [extractedSkills, setExtractedSkills] = useState<SkillCategory[]>([]);
  const [overallConfidence, setOverallConfidence] = useState<number>(0);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file) {
      setUploadedFile(file);
      setError(null);
    }
  };

  const extractSkills = async () => {
    if (!uploadedFile) return;

    setLoading(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);

      // Mock API call - gerçek implementasyonda backend'e gönderilecek
      await new Promise(resolve => setTimeout(resolve, 3000));

      const mockExtractedSkills: SkillCategory[] = [
        {
          name: "Programming Languages",
          icon: <FaCode />,
          color: "blue",
          skills: [
            { name: "JavaScript", category: "Programming Languages", confidence: 95, years_experience: 4, proficiency_level: "advanced" },
            { name: "Python", category: "Programming Languages", confidence: 88, years_experience: 3, proficiency_level: "intermediate" },
            { name: "TypeScript", category: "Programming Languages", confidence: 82, years_experience: 2, proficiency_level: "intermediate" },
            { name: "Java", category: "Programming Languages", confidence: 75, years_experience: 1, proficiency_level: "beginner" }
          ]
        },
        {
          name: "Frameworks & Libraries",
          icon: <FaRocket />,
          color: "purple",
          skills: [
            { name: "React", category: "Frameworks & Libraries", confidence: 92, years_experience: 3, proficiency_level: "advanced" },
            { name: "Node.js", category: "Frameworks & Libraries", confidence: 85, years_experience: 3, proficiency_level: "intermediate" },
            { name: "Express.js", category: "Frameworks & Libraries", confidence: 78, years_experience: 2, proficiency_level: "intermediate" },
            { name: "Django", category: "Frameworks & Libraries", confidence: 70, years_experience: 1, proficiency_level: "beginner" }
          ]
        },
        {
          name: "Databases",
          icon: <FaDatabase />,
          color: "green",
          skills: [
            { name: "MongoDB", category: "Databases", confidence: 88, years_experience: 2, proficiency_level: "intermediate" },
            { name: "PostgreSQL", category: "Databases", confidence: 75, years_experience: 1, proficiency_level: "beginner" },
            { name: "Redis", category: "Databases", confidence: 65, years_experience: 1, proficiency_level: "beginner" }
          ]
        },
        {
          name: "Cloud Platforms",
          icon: <FaCloud />,
          color: "orange",
          skills: [
            { name: "AWS", category: "Cloud Platforms", confidence: 82, years_experience: 2, proficiency_level: "intermediate" },
            { name: "Firebase", category: "Cloud Platforms", confidence: 78, years_experience: 1, proficiency_level: "intermediate" },
            { name: "Vercel", category: "Cloud Platforms", confidence: 85, years_experience: 2, proficiency_level: "intermediate" }
          ]
        },
        {
          name: "DevOps & Tools",
          icon: <FaTools />,
          color: "red",
          skills: [
            { name: "Docker", category: "DevOps & Tools", confidence: 80, years_experience: 2, proficiency_level: "intermediate" },
            { name: "Git", category: "DevOps & Tools", confidence: 90, years_experience: 4, proficiency_level: "advanced" },
            { name: "GitHub Actions", category: "DevOps & Tools", confidence: 75, years_experience: 1, proficiency_level: "intermediate" }
          ]
        },
        {
          name: "Version Control",
          icon: <FaGitAlt />,
          color: "gray",
          skills: [
            { name: "Git", category: "Version Control", confidence: 90, years_experience: 4, proficiency_level: "advanced" },
            { name: "GitHub", category: "Version Control", confidence: 88, years_experience: 3, proficiency_level: "advanced" },
            { name: "GitLab", category: "Version Control", confidence: 70, years_experience: 1, proficiency_level: "intermediate" }
          ]
        }
      ];

      setExtractedSkills(mockExtractedSkills);
      setOverallConfidence(82.5);
    } catch (err) {
      setError('Skills extraction failed. Please try again.');
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

  const getProficiencyColor = (level: string) => {
    switch (level) {
      case 'expert':
        return 'text-purple-600 bg-purple-100';
      case 'advanced':
        return 'text-green-600 bg-green-100';
      case 'intermediate':
        return 'text-blue-600 bg-blue-100';
      case 'beginner':
        return 'text-yellow-600 bg-yellow-100';
      default:
        return 'text-gray-600 bg-gray-100';
    }
  };

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 90) return 'text-green-600';
    if (confidence >= 75) return 'text-blue-600';
    if (confidence >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getCategoryColor = (color: string) => {
    const colorMap: { [key: string]: string } = {
      blue: 'bg-blue-500',
      purple: 'bg-purple-500',
      green: 'bg-green-500',
      orange: 'bg-orange-500',
      red: 'bg-red-500',
      gray: 'bg-gray-500'
    };
    return colorMap[color] || 'bg-gray-500';
  };

  const allSkills = extractedSkills.flatMap(category => category.skills);
  const totalSkills = allSkills.length;
  const averageConfidence = allSkills.reduce((sum, skill) => sum + skill.confidence, 0) / totalSkills;

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-green-50 via-white to-blue-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              AI Skills Extraction
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Upload your CV and let our AI extract and categorize your technical skills 
              with confidence scores and proficiency levels.
            </p>
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
            {!extractedSkills.length ? (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaLightbulb className="mr-3 text-green-500" />
                  Extract Skills from CV
                </h2>

                <div className="text-center">
                  <div className="border-2 border-dashed border-gray-300 rounded-lg p-12 mb-6 hover:border-green-400 transition-colors">
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
                          Upload your CV/Resume
                        </p>
                        <p className="text-gray-600 mb-4">
                          Supported formats: PDF, DOCX, TXT (Max 10MB)
                        </p>
                        <button
                          onClick={() => fileInputRef.current?.click()}
                          className="bg-gradient-to-r from-green-500 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200"
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
                          onClick={extractSkills}
                          disabled={loading}
                          className="bg-green-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-green-700 disabled:opacity-50"
                        >
                          {loading ? (
                            <FaSpinner className="animate-spin" />
                          ) : (
                            'Extract Skills'
                          )}
                        </button>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ) : (
              <div className="space-y-6">
                {/* Summary Stats */}
                <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h2 className="text-2xl font-bold text-gray-900 flex items-center">
                      <FaChartBar className="mr-3 text-green-500" />
                      Skills Analysis Summary
                    </h2>
                    <div className="flex space-x-3">
                      <button
                        onClick={() => setIsEditing(!isEditing)}
                        className="text-blue-600 hover:text-blue-800 font-medium flex items-center"
                      >
                        <FaEdit className="mr-2" />
                        {isEditing ? 'Save Changes' : 'Edit Skills'}
                      </button>
                      <button className="text-green-600 hover:text-green-800 font-medium flex items-center">
                        <FaDownload className="mr-2" />
                        Export
                      </button>
                    </div>
                  </div>

                  <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="text-center">
                      <div className="text-3xl font-bold text-gray-900">{totalSkills}</div>
                      <div className="text-gray-600">Total Skills</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-green-600">{averageConfidence.toFixed(1)}%</div>
                      <div className="text-gray-600">Avg Confidence</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-blue-600">{extractedSkills.length}</div>
                      <div className="text-gray-600">Categories</div>
                    </div>
                    <div className="text-center">
                      <div className="text-3xl font-bold text-purple-600">
                        {allSkills.filter(s => s.proficiency_level === 'advanced' || s.proficiency_level === 'expert').length}
                      </div>
                      <div className="text-gray-600">Advanced Skills</div>
                    </div>
                  </div>
                </div>

                {/* Skills Categories */}
                {extractedSkills.map((category, categoryIndex) => (
                  <div key={categoryIndex} className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
                    <div className="flex items-center mb-6">
                      <div className={`w-12 h-12 rounded-lg flex items-center justify-center text-white mr-4 ${getCategoryColor(category.color)}`}>
                        {category.icon}
                      </div>
                      <div>
                        <h3 className="text-xl font-bold text-gray-900">{category.name}</h3>
                        <p className="text-gray-600">{category.skills.length} skills detected</p>
                      </div>
                    </div>

                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                      {category.skills.map((skill, skillIndex) => (
                        <div key={skillIndex} className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition-shadow">
                          <div className="flex justify-between items-start mb-2">
                            <h4 className="font-semibold text-gray-900">{skill.name}</h4>
                            <div className={`text-sm font-medium px-2 py-1 rounded ${getProficiencyColor(skill.proficiency_level)}`}>
                              {skill.proficiency_level}
                            </div>
                          </div>
                          
                          <div className="space-y-2">
                            <div className="flex justify-between items-center">
                              <span className="text-sm text-gray-600">Confidence:</span>
                              <span className={`text-sm font-medium ${getConfidenceColor(skill.confidence)}`}>
                                {skill.confidence}%
                              </span>
                            </div>
                            
                            {skill.years_experience && (
                              <div className="flex justify-between items-center">
                                <span className="text-sm text-gray-600">Experience:</span>
                                <span className="text-sm font-medium text-gray-900">
                                  {skill.years_experience} year{skill.years_experience > 1 ? 's' : ''}
                                </span>
                              </div>
                            )}

                            <div className="w-full bg-gray-200 rounded-full h-2">
                              <div 
                                className={`h-2 rounded-full ${getCategoryColor(category.color)}`}
                                style={{ width: `${skill.confidence}%` }}
                              ></div>
                            </div>
                          </div>

                          {isEditing && (
                            <div className="mt-3 pt-3 border-t border-gray-200">
                              <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                                Edit Skill
                              </button>
                            </div>
                          )}
                        </div>
                      ))}
                    </div>
                  </div>
                ))}

                {/* Recommendations */}
                <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl border border-blue-200 p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4 flex items-center">
                    <FaBrain className="mr-3 text-blue-500" />
                    AI Recommendations
                  </h3>
                  
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Skills to Improve</h4>
                      <ul className="space-y-2">
                        {allSkills
                          .filter(skill => skill.confidence < 75)
                          .slice(0, 3)
                          .map((skill, index) => (
                            <li key={index} className="flex items-center text-gray-700">
                              <FaExclamationTriangle className="text-yellow-500 mr-2 flex-shrink-0" />
                              <span className="font-medium">{skill.name}</span>
                              <span className="ml-2 text-sm text-gray-500">
                                ({skill.confidence}% confidence)
                              </span>
                            </li>
                          ))}
                      </ul>
                    </div>
                    
                    <div>
                      <h4 className="font-semibold text-gray-900 mb-3">Top Skills</h4>
                      <ul className="space-y-2">
                        {allSkills
                          .filter(skill => skill.confidence >= 90)
                          .slice(0, 3)
                          .map((skill, index) => (
                            <li key={index} className="flex items-center text-gray-700">
                              <FaStar className="text-yellow-500 mr-2 flex-shrink-0" />
                              <span className="font-medium">{skill.name}</span>
                              <span className="ml-2 text-sm text-gray-500">
                                ({skill.confidence}% confidence)
                              </span>
                            </li>
                          ))}
                      </ul>
                    </div>
                  </div>
                </div>

                {/* Action Buttons */}
                <div className="flex justify-center space-x-4">
                  <button
                    onClick={() => {
                      setExtractedSkills([]);
                      setUploadedFile(null);
                    }}
                    className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                  >
                    Extract Another CV
                  </button>
                  <button className="bg-green-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-green-700 transition-colors">
                    <FaDownload className="inline mr-2" />
                    Download Report
                  </button>
                  <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                    Update Profile
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default SkillsExtraction; 