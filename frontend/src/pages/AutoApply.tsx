import React, { useState } from 'react';
import { 
  FaRocket, 
  FaLink, 
  FaSearch, 
  FaCheckCircle, 
  FaExclamationTriangle,
  FaSpinner,
  FaEye,
  FaEdit,
  FaPaperPlane,
  FaFileAlt,
  FaUser,
  FaEnvelope,
  FaPhone,
  FaMapMarkerAlt,
  FaLinkedin,
  FaGlobe,
  FaClock,
  FaShieldAlt,
  FaBrain,
  FaChartLine,
  FaDownload,
  FaHistory,
  FaCog,
  FaLightbulb
} from 'react-icons/fa';
import Layout from '../components/Layout';

interface FormAnalysis {
  auto_apply_supported: boolean;
  form_data: {
    fields: FormField[];
    total_fields: number;
    estimated_time: number;
  };
  confidence_score: number;
  warnings: string[];
  recommendations: string[];
}

interface FormField {
  name: string;
  type: string;
  required: boolean;
  placeholder?: string;
  options?: string[];
  generated_response?: string;
}

interface AutoApplyResult {
  success: boolean;
  application_id?: string;
  submitted_at: string;
  form_analysis: FormAnalysis;
  field_responses_generated: number;
  message: string;
}

const AutoApply: React.FC = () => {
  const [jobUrl, setJobUrl] = useState('');
  const [formAnalysis, setFormAnalysis] = useState<FormAnalysis | null>(null);
  const [autoApplyResult, setAutoApplyResult] = useState<AutoApplyResult | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeStep, setActiveStep] = useState<'url' | 'analysis' | 'preview' | 'result'>('url');

  const analyzeForm = async () => {
    if (!jobUrl.trim()) return;

    setLoading(true);
    setError(null);

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 2000));

      const mockFormAnalysis: FormAnalysis = {
        auto_apply_supported: true,
        form_data: {
          fields: [
            {
              name: "full_name",
              type: "text",
              required: true,
              placeholder: "Full Name",
              generated_response: "John Doe"
            },
            {
              name: "email",
              type: "email",
              required: true,
              placeholder: "Email Address",
              generated_response: "john.doe@email.com"
            },
            {
              name: "phone",
              type: "tel",
              required: true,
              placeholder: "Phone Number",
              generated_response: "+1 (555) 123-4567"
            },
            {
              name: "location",
              type: "text",
              required: true,
              placeholder: "Location",
              generated_response: "San Francisco, CA"
            },
            {
              name: "experience_years",
              type: "select",
              required: true,
              options: ["0-1", "1-3", "3-5", "5-10", "10+"],
              generated_response: "3-5"
            },
            {
              name: "cover_letter",
              type: "textarea",
              required: false,
              placeholder: "Cover Letter",
              generated_response: "I am excited to apply for this position. With my experience in React and Node.js, I believe I would be a great fit for your team..."
            },
            {
              name: "salary_expectation",
              type: "number",
              required: false,
              placeholder: "Expected Salary",
              generated_response: "120000"
            }
          ],
          total_fields: 7,
          estimated_time: 45
        },
        confidence_score: 92,
        warnings: [
          "Cover letter field is optional but recommended",
          "Salary expectation field detected - consider your response carefully"
        ],
        recommendations: [
          "Review generated responses before submission",
          "Customize cover letter for better personalization",
          "Consider market rates for salary expectation"
        ]
      };

      setFormAnalysis(mockFormAnalysis);
      setActiveStep('analysis');
    } catch (err) {
      setError('Form analysis failed. Please check the URL and try again.');
    } finally {
      setLoading(false);
    }
  };

  const previewResponses = () => {
    setActiveStep('preview');
  };

  const submitApplication = async () => {
    setLoading(true);
    setError(null);

    try {
      // Mock API call
      await new Promise(resolve => setTimeout(resolve, 3000));

      const mockResult: AutoApplyResult = {
        success: true,
        application_id: "APP_" + Math.random().toString(36).substr(2, 9).toUpperCase(),
        submitted_at: new Date().toISOString(),
        form_analysis: formAnalysis!,
        field_responses_generated: formAnalysis!.form_data.fields.length,
        message: "Application submitted successfully! You will receive a confirmation email shortly."
      };

      setAutoApplyResult(mockResult);
      setActiveStep('result');
    } catch (err) {
      setError('Application submission failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const getFieldTypeIcon = (type: string) => {
    switch (type) {
      case 'text':
      case 'email':
        return <FaUser className="text-blue-500" />;
      case 'tel':
        return <FaPhone className="text-green-500" />;
      case 'textarea':
        return <FaFileAlt className="text-purple-500" />;
      case 'select':
        return <FaCog className="text-orange-500" />;
      case 'number':
        return <FaChartLine className="text-red-500" />;
      default:
        return <FaFileAlt className="text-gray-500" />;
    }
  };

  const getConfidenceColor = (score: number) => {
    if (score >= 90) return 'text-green-600 bg-green-100';
    if (score >= 75) return 'text-blue-600 bg-blue-100';
    if (score >= 60) return 'text-yellow-600 bg-yellow-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
        <div className="container mx-auto px-4 py-8">
          {/* Header */}
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              AI Auto Apply
            </h1>
            <p className="text-lg text-gray-600 max-w-2xl mx-auto">
              Let our AI automatically fill out job application forms for you. 
              Just provide the job URL and we'll handle the rest!
            </p>
          </div>

          {/* Progress Steps */}
          <div className="flex justify-center mb-8">
            <div className="flex items-center space-x-4">
              <div className={`flex items-center ${activeStep === 'url' ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${activeStep === 'url' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                  1
                </div>
                <span className="ml-2 font-medium">Job URL</span>
              </div>
              <div className="w-8 h-0.5 bg-gray-300"></div>
              <div className={`flex items-center ${activeStep === 'analysis' || activeStep === 'preview' || activeStep === 'result' ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${activeStep === 'analysis' || activeStep === 'preview' || activeStep === 'result' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                  2
                </div>
                <span className="ml-2 font-medium">Analysis</span>
              </div>
              <div className="w-8 h-0.5 bg-gray-300"></div>
              <div className={`flex items-center ${activeStep === 'preview' || activeStep === 'result' ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${activeStep === 'preview' || activeStep === 'result' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                  3
                </div>
                <span className="ml-2 font-medium">Preview</span>
              </div>
              <div className="w-8 h-0.5 bg-gray-300"></div>
              <div className={`flex items-center ${activeStep === 'result' ? 'text-blue-600' : 'text-gray-400'}`}>
                <div className={`w-8 h-8 rounded-full flex items-center justify-center ${activeStep === 'result' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}>
                  4
                </div>
                <span className="ml-2 font-medium">Submit</span>
              </div>
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
          <div className="max-w-4xl mx-auto">
            {/* Step 1: Job URL Input */}
            {activeStep === 'url' && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaLink className="mr-3 text-purple-500" />
                  Enter Job URL
                </h2>

                <div className="space-y-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Job Application URL
                    </label>
                    <input
                      type="url"
                      value={jobUrl}
                      onChange={(e) => setJobUrl(e.target.value)}
                      placeholder="https://example.com/job-application/123"
                      className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                    />
                  </div>

                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
                      <FaShieldAlt className="mr-2" />
                      How it works
                    </h3>
                    <ul className="text-blue-800 space-y-1 text-sm">
                      <li>• Our AI analyzes the application form structure</li>
                      <li>• Generates appropriate responses based on your profile</li>
                      <li>• You can review and edit responses before submission</li>
                      <li>• Secure and private - your data stays with you</li>
                    </ul>
                  </div>

                  <button
                    onClick={analyzeForm}
                    disabled={!jobUrl.trim() || loading}
                    className="w-full bg-gradient-to-r from-purple-500 to-blue-600 text-white py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                  >
                    {loading ? (
                      <FaSpinner className="animate-spin mx-auto" />
                    ) : (
                      <>
                        <FaSearch className="inline mr-2" />
                        Analyze Application Form
                      </>
                    )}
                  </button>
                </div>
              </div>
            )}

            {/* Step 2: Form Analysis */}
            {activeStep === 'analysis' && formAnalysis && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaBrain className="mr-3 text-purple-500" />
                  Form Analysis Results
                </h2>

                <div className="space-y-6">
                  {/* Analysis Summary */}
                  <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-green-600">
                        {formAnalysis.auto_apply_supported ? '✅' : '❌'}
                      </div>
                      <div className="text-sm font-medium text-green-800">
                        Auto Apply {formAnalysis.auto_apply_supported ? 'Supported' : 'Not Supported'}
                      </div>
                    </div>
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-blue-600">
                        {formAnalysis.form_data.total_fields}
                      </div>
                      <div className="text-sm font-medium text-blue-800">Form Fields</div>
                    </div>
                    <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
                      <div className="text-2xl font-bold text-purple-600">
                        {formAnalysis.confidence_score}%
                      </div>
                      <div className="text-sm font-medium text-purple-800">Confidence</div>
                    </div>
                  </div>

                  {/* Warnings */}
                  {formAnalysis.warnings.length > 0 && (
                    <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
                      <h3 className="font-semibold text-yellow-900 mb-2 flex items-center">
                        <FaExclamationTriangle className="mr-2" />
                        Warnings
                      </h3>
                      <ul className="text-yellow-800 space-y-1 text-sm">
                        {formAnalysis.warnings.map((warning, index) => (
                          <li key={index}>• {warning}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Recommendations */}
                  {formAnalysis.recommendations.length > 0 && (
                    <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                      <h3 className="font-semibold text-blue-900 mb-2 flex items-center">
                        <FaLightbulb className="mr-2" />
                        Recommendations
                      </h3>
                      <ul className="text-blue-800 space-y-1 text-sm">
                        {formAnalysis.recommendations.map((rec, index) => (
                          <li key={index}>• {rec}</li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {/* Action Buttons */}
                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveStep('url')}
                      className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                    >
                      Back
                    </button>
                    <button
                      onClick={previewResponses}
                      disabled={!formAnalysis.auto_apply_supported}
                      className="bg-gradient-to-r from-purple-500 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                    >
                      <FaEye className="inline mr-2" />
                      Preview Responses
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Step 3: Preview Responses */}
            {activeStep === 'preview' && formAnalysis && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-6 flex items-center">
                  <FaEye className="mr-3 text-purple-500" />
                  Preview Generated Responses
                </h2>

                <div className="space-y-6">
                  {/* Form Fields */}
                  <div className="space-y-4">
                    {formAnalysis.form_data.fields.map((field, index) => (
                      <div key={index} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-center justify-between mb-3">
                          <div className="flex items-center">
                            {getFieldTypeIcon(field.type)}
                            <span className="ml-2 font-medium text-gray-900">
                              {field.name.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </span>
                            {field.required && (
                              <span className="ml-2 text-red-500 text-sm">*</span>
                            )}
                          </div>
                          <span className="text-sm text-gray-500 capitalize">{field.type}</span>
                        </div>

                        <div className="space-y-2">
                          {field.type === 'textarea' ? (
                            <textarea
                              value={field.generated_response || ''}
                              onChange={(e) => {
                                // Update the generated response
                                const updatedFields = [...formAnalysis.form_data.fields];
                                updatedFields[index].generated_response = e.target.value;
                                setFormAnalysis({
                                  ...formAnalysis,
                                  form_data: {
                                    ...formAnalysis.form_data,
                                    fields: updatedFields
                                  }
                                });
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                              rows={4}
                            />
                          ) : field.type === 'select' ? (
                            <select
                              value={field.generated_response || ''}
                              onChange={(e) => {
                                const updatedFields = [...formAnalysis.form_data.fields];
                                updatedFields[index].generated_response = e.target.value;
                                setFormAnalysis({
                                  ...formAnalysis,
                                  form_data: {
                                    ...formAnalysis.form_data,
                                    fields: updatedFields
                                  }
                                });
                              }}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            >
                              <option value="">Select an option</option>
                              {field.options?.map((option, optIndex) => (
                                <option key={optIndex} value={option}>{option}</option>
                              ))}
                            </select>
                          ) : (
                            <input
                              type={field.type}
                              value={field.generated_response || ''}
                              onChange={(e) => {
                                const updatedFields = [...formAnalysis.form_data.fields];
                                updatedFields[index].generated_response = e.target.value;
                                setFormAnalysis({
                                  ...formAnalysis,
                                  form_data: {
                                    ...formAnalysis.form_data,
                                    fields: updatedFields
                                  }
                                });
                              }}
                              placeholder={field.placeholder}
                              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-transparent"
                            />
                          )}
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Action Buttons */}
                  <div className="flex justify-between">
                    <button
                      onClick={() => setActiveStep('analysis')}
                      className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                    >
                      Back
                    </button>
                    <button
                      onClick={submitApplication}
                      disabled={loading}
                      className="bg-gradient-to-r from-green-500 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:shadow-lg transition-all duration-200 disabled:opacity-50"
                    >
                      {loading ? (
                        <FaSpinner className="animate-spin" />
                      ) : (
                        <>
                          <FaPaperPlane className="inline mr-2" />
                          Submit Application
                        </>
                      )}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Step 4: Result */}
            {activeStep === 'result' && autoApplyResult && (
              <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-8">
                <div className="text-center">
                  {autoApplyResult.success ? (
                    <div className="space-y-6">
                      <div className="text-6xl text-green-500 mb-4">
                        <FaCheckCircle />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        Application Submitted Successfully!
                      </h2>
                      <p className="text-gray-600">
                        {autoApplyResult.message}
                      </p>

                      <div className="bg-green-50 border border-green-200 rounded-lg p-6">
                        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {autoApplyResult.application_id}
                            </div>
                            <div className="text-sm text-green-800">Application ID</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {autoApplyResult.field_responses_generated}
                            </div>
                            <div className="text-sm text-green-800">Fields Filled</div>
                          </div>
                          <div className="text-center">
                            <div className="text-2xl font-bold text-green-600">
                              {new Date(autoApplyResult.submitted_at).toLocaleTimeString()}
                            </div>
                            <div className="text-sm text-green-800">Submitted At</div>
                          </div>
                        </div>
                      </div>

                      <div className="flex justify-center space-x-4">
                        <button
                          onClick={() => {
                            setActiveStep('url');
                            setJobUrl('');
                            setFormAnalysis(null);
                            setAutoApplyResult(null);
                          }}
                          className="bg-gray-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-gray-700 transition-colors"
                        >
                          Apply to Another Job
                        </button>
                        <button className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors">
                          <FaDownload className="inline mr-2" />
                          Download Receipt
                        </button>
                      </div>
                    </div>
                  ) : (
                    <div className="space-y-6">
                      <div className="text-6xl text-red-500 mb-4">
                        <FaExclamationTriangle />
                      </div>
                      <h2 className="text-2xl font-bold text-gray-900">
                        Application Failed
                      </h2>
                      <p className="text-gray-600">
                        {autoApplyResult.message}
                      </p>

                      <button
                        onClick={() => setActiveStep('preview')}
                        className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
                      >
                        Try Again
                      </button>
                    </div>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default AutoApply; 