import React, { useState } from 'react';
import { 
  Brain, 
  Sparkles, 
  TrendingUp, 
  Target, 
  Lightbulb, 
  AlertTriangle, 
  Crown, 
  ArrowRight,
  CheckCircle,
  Clock,
  Star,
  Zap
} from 'lucide-react';
import { toast } from 'react-hot-toast';
import { useAuth } from '../contexts/AuthContext';
import { isPremiumUser, getPremiumFeatureMessage, getUserSubscriptionPlan, getUpgradeButtonText, getUpgradeUrl } from '../utils/premiumUtils';

interface CVAnalysisResult {
  overallScore: number;
  strengths: string[];
  weaknesses: string[];
  suggestions: string[];
  keywordOptimization: {
    missing: string[];
    suggested: string[];
  };
  industryMatch: {
    score: number;
    topIndustries: string[];
  };
  salaryRange: {
    min: number;
    max: number;
    currency: string;
  };
  jobRecommendations: Array<{
    title: string;
    matchScore: number;
    reason: string;
  }>;
  aiInsights: string[];
}

interface AICVAnalysisProps {
  cvUrl?: string;
  className?: string;
}

const AICVAnalysis: React.FC<AICVAnalysisProps> = ({ cvUrl, className = '' }) => {
  const { user } = useAuth();
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<CVAnalysisResult | null>(null);
  const [showUpgradeModal, setShowUpgradeModal] = useState(false);

  const isPremium = isPremiumUser(user);
  const subscriptionPlan = getUserSubscriptionPlan(user);

  const handleAnalyzeCV = async () => {
    if (!isPremium) {
      setShowUpgradeModal(true);
      return;
    }

    if (!cvUrl) {
      toast.error('Please upload a CV first to analyze it');
      return;
    }

    try {
      setIsAnalyzing(true);
      
      const token = localStorage.getItem('token');
      const response = await fetch(`${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/ai/cv-analysis`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          cv_url: cvUrl
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to analyze CV');
      }

      const result = await response.json();
      setAnalysisResult(result.data);
      toast.success('CV analysis completed!');
      
    } catch (error: any) {
      console.error('Error analyzing CV:', error);
      toast.error(error.message || 'Failed to analyze CV');
    } finally {
      setIsAnalyzing(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 80) return 'text-green-600';
    if (score >= 60) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBgColor = (score: number): string => {
    if (score >= 80) return 'bg-green-100';
    if (score >= 60) return 'bg-yellow-100';
    return 'bg-red-100';
  };

  if (!isPremium) {
    return (
      <div className={`bg-gradient-to-r from-purple-50 to-blue-50 border border-purple-200 rounded-lg p-6 ${className}`}>
        <div className="text-center">
          <div className="flex justify-center mb-4">
            <div className="p-3 bg-purple-100 rounded-full">
              <Brain className="w-8 h-8 text-purple-600" />
            </div>
          </div>
          
          <h3 className="text-xl font-bold text-gray-900 mb-2">
            AI CV Analysis
          </h3>
          
          <p className="text-gray-600 mb-4">
            {getPremiumFeatureMessage('AI CV Analysis')}
          </p>
          
          <div className="bg-white rounded-lg p-4 mb-6">
            <h4 className="font-semibold text-gray-900 mb-3 flex items-center">
              <Crown className="w-5 h-5 text-yellow-500 mr-2" />
              Premium Features Include:
            </h4>
            <ul className="space-y-2 text-sm text-gray-600">
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                AI-powered CV scoring and optimization
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                Keyword analysis and suggestions
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                Industry matching and salary insights
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                Personalized job recommendations
              </li>
              <li className="flex items-center">
                <CheckCircle className="w-4 h-4 text-green-500 mr-2" />
                Resume improvement suggestions
              </li>
            </ul>
          </div>
          
          <button
            onClick={() => setShowUpgradeModal(true)}
            className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:from-purple-700 hover:to-blue-700 transition-all duration-200 flex items-center mx-auto"
          >
            <Crown className="w-5 h-5 mr-2" />
            {getUpgradeButtonText(subscriptionPlan)}
            <ArrowRight className="w-4 h-4 ml-2" />
          </button>
        </div>

        {/* Upgrade Modal */}
        {showUpgradeModal && (
          <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
            <div className="bg-white rounded-lg p-6 max-w-md mx-4">
              <div className="text-center">
                <div className="p-3 bg-purple-100 rounded-full w-16 h-16 flex items-center justify-center mx-auto mb-4">
                  <Crown className="w-8 h-8 text-purple-600" />
                </div>
                
                <h3 className="text-xl font-bold text-gray-900 mb-2">
                  Upgrade to Premium
                </h3>
                
                <p className="text-gray-600 mb-6">
                  Unlock AI-powered CV analysis and many more advanced features to boost your job search success!
                </p>
                
                <div className="space-y-3 mb-6">
                  <div className="flex items-center text-sm">
                    <Star className="w-4 h-4 text-yellow-500 mr-2" />
                    AI CV scoring and optimization
                  </div>
                  <div className="flex items-center text-sm">
                    <Zap className="w-4 h-4 text-blue-500 mr-2" />
                    Smart keyword suggestions
                  </div>
                  <div className="flex items-center text-sm">
                    <Target className="w-4 h-4 text-green-500 mr-2" />
                    Industry matching insights
                  </div>
                  <div className="flex items-center text-sm">
                    <TrendingUp className="w-4 h-4 text-purple-500 mr-2" />
                    Salary range analysis
                  </div>
                </div>
                
                <div className="flex space-x-3">
                  <button
                    onClick={() => setShowUpgradeModal(false)}
                    className="flex-1 px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                  >
                    Maybe Later
                  </button>
                  <button
                    onClick={() => {
                      setShowUpgradeModal(false);
                      window.location.href = getUpgradeUrl(subscriptionPlan);
                    }}
                    className="flex-1 px-4 py-2 bg-gradient-to-r from-purple-600 to-blue-600 text-white rounded-lg hover:from-purple-700 hover:to-blue-700 transition-all duration-200"
                  >
                    Upgrade Now
                  </button>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    );
  }

  return (
    <div className={`bg-white border border-gray-200 rounded-lg p-6 ${className}`}>
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center">
          <div className="p-2 bg-gradient-to-r from-purple-100 to-blue-100 rounded-lg mr-3">
            <Brain className="w-6 h-6 text-purple-600" />
          </div>
          <div>
            <h3 className="text-xl font-bold text-gray-900">AI CV Analysis</h3>
            <p className="text-sm text-gray-600">Powered by advanced AI algorithms</p>
          </div>
        </div>
        <div className="flex items-center text-sm text-green-600 bg-green-50 px-3 py-1 rounded-full">
          <Crown className="w-4 h-4 mr-1" />
          Premium
        </div>
      </div>

      {!analysisResult ? (
        <div className="text-center">
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-6 mb-4">
            <Sparkles className="w-12 h-12 text-purple-600 mx-auto mb-3" />
            <h4 className="font-semibold text-gray-900 mb-2">Get AI-Powered CV Insights</h4>
            <p className="text-gray-600 text-sm mb-4">
              Our AI will analyze your CV and provide detailed insights on strengths, 
              areas for improvement, and optimization suggestions.
            </p>
            
            {!cvUrl ? (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <AlertTriangle className="w-5 h-5 text-yellow-600 mx-auto mb-2" />
                <p className="text-sm text-yellow-800">
                  Please upload a CV first to analyze it
                </p>
              </div>
            ) : (
              <button
                onClick={handleAnalyzeCV}
                disabled={isAnalyzing}
                className={`px-6 py-3 rounded-lg font-medium transition-all duration-200 flex items-center mx-auto ${
                  isAnalyzing
                    ? 'bg-gray-400 text-gray-600 cursor-not-allowed'
                    : 'bg-gradient-to-r from-purple-600 to-blue-600 text-white hover:from-purple-700 hover:to-blue-700'
                }`}
              >
                {isAnalyzing ? (
                  <>
                    <Clock className="w-5 h-5 mr-2 animate-spin" />
                    Analyzing...
                  </>
                ) : (
                  <>
                    <Brain className="w-5 h-5 mr-2" />
                    Analyze My CV
                  </>
                )}
              </button>
            )}
          </div>
        </div>
      ) : (
        <div className="space-y-6">
          {/* Overall Score */}
          <div className="bg-gradient-to-r from-purple-50 to-blue-50 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <h4 className="font-semibold text-gray-900">Overall CV Score</h4>
              <div className={`px-3 py-1 rounded-full text-sm font-medium ${getScoreBgColor(analysisResult.overallScore)} ${getScoreColor(analysisResult.overallScore)}`}>
                {analysisResult.overallScore}/100
              </div>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-500 ${
                  analysisResult.overallScore >= 80 ? 'bg-green-500' :
                  analysisResult.overallScore >= 60 ? 'bg-yellow-500' : 'bg-red-500'
                }`}
                style={{ width: `${analysisResult.overallScore}%` }}
              ></div>
            </div>
          </div>

          {/* Strengths & Weaknesses */}
          <div className="grid md:grid-cols-2 gap-4">
            <div className="bg-green-50 border border-green-200 rounded-lg p-4">
              <h4 className="font-semibold text-green-900 mb-3 flex items-center">
                <CheckCircle className="w-5 h-5 mr-2" />
                Strengths
              </h4>
              <ul className="space-y-2">
                {analysisResult.strengths.map((strength, index) => (
                  <li key={index} className="text-sm text-green-800 flex items-start">
                    <div className="w-1.5 h-1.5 bg-green-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                    {strength}
                  </li>
                ))}
              </ul>
            </div>

            <div className="bg-red-50 border border-red-200 rounded-lg p-4">
              <h4 className="font-semibold text-red-900 mb-3 flex items-center">
                <AlertTriangle className="w-5 h-5 mr-2" />
                Areas for Improvement
              </h4>
              <ul className="space-y-2">
                {analysisResult.weaknesses.map((weakness, index) => (
                  <li key={index} className="text-sm text-red-800 flex items-start">
                    <div className="w-1.5 h-1.5 bg-red-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                    {weakness}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Keyword Optimization */}
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
            <h4 className="font-semibold text-blue-900 mb-3 flex items-center">
              <Target className="w-5 h-5 mr-2" />
              Keyword Optimization
            </h4>
            <div className="grid md:grid-cols-2 gap-4">
              <div>
                <h5 className="text-sm font-medium text-blue-800 mb-2">Missing Keywords</h5>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.keywordOptimization.missing.map((keyword, index) => (
                    <span key={index} className="bg-red-100 text-red-800 px-2 py-1 rounded text-xs">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
              <div>
                <h5 className="text-sm font-medium text-blue-800 mb-2">Suggested Keywords</h5>
                <div className="flex flex-wrap gap-2">
                  {analysisResult.keywordOptimization.suggested.map((keyword, index) => (
                    <span key={index} className="bg-green-100 text-green-800 px-2 py-1 rounded text-xs">
                      {keyword}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          </div>

          {/* Industry Match */}
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4">
            <h4 className="font-semibold text-purple-900 mb-3 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Industry Match
            </h4>
            <div className="flex items-center justify-between mb-3">
              <span className="text-sm text-purple-700">Match Score</span>
              <span className="text-lg font-bold text-purple-900">{analysisResult.industryMatch.score}%</span>
            </div>
            <div className="w-full bg-purple-200 rounded-full h-2 mb-3">
              <div 
                className="bg-purple-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${analysisResult.industryMatch.score}%` }}
              ></div>
            </div>
            <div>
              <h5 className="text-sm font-medium text-purple-800 mb-2">Top Industries</h5>
              <div className="flex flex-wrap gap-2">
                {analysisResult.industryMatch.topIndustries.map((industry, index) => (
                  <span key={index} className="bg-purple-100 text-purple-800 px-2 py-1 rounded text-xs">
                    {industry}
                  </span>
                ))}
              </div>
            </div>
          </div>

          {/* Salary Range */}
          <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
            <h4 className="font-semibold text-yellow-900 mb-3 flex items-center">
              <TrendingUp className="w-5 h-5 mr-2" />
              Estimated Salary Range
            </h4>
            <div className="text-center">
              <div className="text-2xl font-bold text-yellow-900">
                {analysisResult.salaryRange.currency} {analysisResult.salaryRange.min.toLocaleString()} - {analysisResult.salaryRange.max.toLocaleString()}
              </div>
              <p className="text-sm text-yellow-700 mt-1">Based on your experience and skills</p>
            </div>
          </div>

          {/* AI Insights */}
          <div className="bg-gradient-to-r from-indigo-50 to-purple-50 border border-indigo-200 rounded-lg p-4">
            <h4 className="font-semibold text-indigo-900 mb-3 flex items-center">
              <Lightbulb className="w-5 h-5 mr-2" />
              AI Insights & Recommendations
            </h4>
            <ul className="space-y-3">
              {analysisResult.aiInsights.map((insight, index) => (
                <li key={index} className="text-sm text-indigo-800 flex items-start">
                  <div className="w-1.5 h-1.5 bg-indigo-500 rounded-full mt-2 mr-2 flex-shrink-0"></div>
                  {insight}
                </li>
              ))}
            </ul>
          </div>

          {/* Action Button */}
          <button
            onClick={() => setAnalysisResult(null)}
            className="w-full px-6 py-3 bg-gray-100 text-gray-700 rounded-lg font-medium hover:bg-gray-200 transition-colors"
          >
            Analyze Again
          </button>
        </div>
      )}
    </div>
  );
};

export default AICVAnalysis; 