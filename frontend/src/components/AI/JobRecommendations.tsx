import React, { useState, useEffect } from 'react';
import { 
  Brain, 
  Star, 
  MapPin, 
  DollarSign, 
  Clock,
  TrendingUp,
  Target,
  Zap
} from 'lucide-react';
import JobCard from '../JobCard/JobCard';
import { Job } from '../../types/job';
import { getApiUrl } from '../../utils/apiConfig';

interface AIJobRecommendationsProps {
  userId?: string;
  limit?: number;
  className?: string;
}

interface RecommendationResponse {
  user_id: string;
  recommendations: Job[];
  total_count: number;
  filters_applied: any;
}

interface SkillDemand {
  skill: string;
  demand_count: number;
  average_salary: number;
  company_count: number;
  trend: string;
}

interface SalaryInsights {
  average_salary: number;
  salary_range: {
    min: number;
    max: number;
  };
  total_jobs_analyzed: number;
  companies_offering: number;
  market_trend: string;
}

const AIJobRecommendations: React.FC<AIJobRecommendationsProps> = ({
  userId = 'demo_user',
  limit = 6,
  className = ''
}) => {
  const [recommendations, setRecommendations] = useState<Job[]>([]);
  const [skillsDemand, setSkillsDemand] = useState<SkillDemand[]>([]);
  const [salaryInsights, setSalaryInsights] = useState<SalaryInsights | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string>('');
  const [activeTab, setActiveTab] = useState<'recommendations' | 'skills' | 'salary'>('recommendations');

  useEffect(() => {
    loadAIData();
  }, [userId, limit]);

  const loadAIData = async () => {
    setLoading(true);
    setError('');
    
    try {
      const apiUrl = await getApiUrl();
      
      // Load recommendations, skills demand, and salary insights in parallel
      const [recommendationsRes, skillsRes, salaryRes] = await Promise.all([
        fetch(`${apiUrl}/api/ai/recommendations?user_id=${userId}&limit=${limit}`).catch(() => null),
        fetch(`${apiUrl}/api/ai/skills-demand?limit=10`).catch(() => null),
        fetch(`${apiUrl}/api/ai/salary-insights?position=developer`).catch(() => null)
      ]);

      if (recommendationsRes?.ok) {
        const recommendationsData: RecommendationResponse = await recommendationsRes.json();
        setRecommendations(recommendationsData.recommendations || []);
      }

      if (skillsRes?.ok) {
        const skillsData = await skillsRes.json();
        setSkillsDemand(skillsData.skills_demand || []);
      }

      if (salaryRes?.ok) {
        const salaryData = await salaryRes.json();
        setSalaryInsights(salaryData.salary_insights || null);
      }

    } catch (error: any) {
      setError(error.message || 'Failed to load AI insights');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="flex items-center justify-center h-64">
          <div className="flex items-center space-x-2 text-orange-600">
            <Brain className="w-8 h-8 animate-pulse" />
            <span className="text-lg font-medium">AI is analyzing job opportunities...</span>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 p-6 ${className}`}>
        <div className="text-center text-red-600">
          <Brain className="w-12 h-12 mx-auto mb-4 opacity-50" />
          <h3 className="text-lg font-medium mb-2">AI Analysis Unavailable</h3>
          <p className="text-sm text-gray-600 dark:text-gray-400">{error}</p>
          <button
            onClick={loadAIData}
            className="mt-4 px-4 py-2 bg-orange-600 hover:bg-orange-700 text-white rounded-lg transition-colors"
          >
            Retry Analysis
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      {/* Header */}
      <div className="p-6 border-b border-gray-200 dark:border-gray-700">
        <div className="flex items-center space-x-3 mb-4">
          <div className="p-2 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
            <Brain className="w-6 h-6 text-orange-600" />
          </div>
          <div>
            <h2 className="text-xl font-bold text-gray-900 dark:text-white">
              AI-Powered Insights
            </h2>
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Personalized job recommendations and market analysis
            </p>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex space-x-1 bg-gray-100 dark:bg-gray-700 rounded-lg p-1">
          <button
            onClick={() => setActiveTab('recommendations')}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'recommendations'
                ? 'bg-white dark:bg-gray-600 text-orange-600 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <Target className="w-4 h-4" />
            <span>Recommendations</span>
          </button>
          <button
            onClick={() => setActiveTab('skills')}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'skills'
                ? 'bg-white dark:bg-gray-600 text-orange-600 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <TrendingUp className="w-4 h-4" />
            <span>Skills Demand</span>
          </button>
          <button
            onClick={() => setActiveTab('salary')}
            className={`flex-1 flex items-center justify-center space-x-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
              activeTab === 'salary'
                ? 'bg-white dark:bg-gray-600 text-orange-600 shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
            }`}
          >
            <DollarSign className="w-4 h-4" />
            <span>Salary Insights</span>
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-6">
        {activeTab === 'recommendations' && (
          <div>
            {recommendations.length > 0 ? (
              <div className="space-y-4">
                <div className="flex items-center justify-between mb-4">
                  <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                    Top Matches for You
                  </h3>
                  <span className="text-sm text-gray-500 dark:text-gray-400">
                    {recommendations.length} recommendations
                  </span>
                </div>
                <div className="grid gap-4 md:grid-cols-2">
                  {recommendations.slice(0, 4).map((job, index) => (
                    <div key={job.id || job._id} className="relative">
                      <JobCard job={job} />
                      {(job as any).match_score && (
                        <div className="absolute top-2 right-2 bg-orange-600 text-white px-2 py-1 rounded-full text-xs font-medium">
                          {Math.round((job as any).match_score * 100)}% match
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <Target className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No Recommendations Available
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Complete your profile to get personalized job recommendations
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'skills' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                In-Demand Skills
              </h3>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Market analysis
              </span>
            </div>
            {skillsDemand.length > 0 ? (
              <div className="space-y-3">
                {skillsDemand.slice(0, 8).map((skill, index) => (
                  <div
                    key={skill.skill}
                    className="flex items-center justify-between p-4 bg-gray-50 dark:bg-gray-700 rounded-lg"
                  >
                    <div className="flex items-center space-x-3">
                      <div className="flex items-center justify-center w-8 h-8 bg-orange-100 dark:bg-orange-900/20 rounded-lg">
                        <span className="text-sm font-bold text-orange-600">
                          #{index + 1}
                        </span>
                      </div>
                      <div>
                        <h4 className="font-medium text-gray-900 dark:text-white">
                          {skill.skill}
                        </h4>
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          {skill.demand_count} jobs • {skill.company_count} companies
                        </p>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className="flex items-center space-x-1 text-green-600">
                        <TrendingUp className="w-4 h-4" />
                        <span className="text-sm font-medium">{skill.trend}</span>
                      </div>
                      {skill.average_salary > 0 && (
                        <p className="text-sm text-gray-600 dark:text-gray-400">
                          Avg: ${skill.average_salary.toLocaleString()}
                        </p>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-center py-12">
                <TrendingUp className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No Skills Data Available
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Skills demand analysis will appear here
                </p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'salary' && (
          <div>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
                Salary Market Insights
              </h3>
              <span className="text-sm text-gray-500 dark:text-gray-400">
                Developer positions
              </span>
            </div>
            {salaryInsights ? (
              <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                  <div className="p-4 bg-orange-50 dark:bg-orange-900/10 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <DollarSign className="w-5 h-5 text-orange-600" />
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        Average Salary
                      </h4>
                    </div>
                    <p className="text-2xl font-bold text-orange-600">
                      ${salaryInsights.average_salary.toLocaleString()}
                    </p>
                  </div>
                  
                  <div className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <MapPin className="w-5 h-5 text-gray-600" />
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        Market Analysis
                      </h4>
                    </div>
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Jobs Analyzed:</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {salaryInsights.total_jobs_analyzed.toLocaleString()}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Companies:</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          {salaryInsights.companies_offering}
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600 dark:text-gray-400">Market Trend:</span>
                        <span className="font-medium text-green-600 capitalize">
                          {salaryInsights.market_trend}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>

                <div className="space-y-4">
                  <div className="p-4 bg-blue-50 dark:bg-blue-900/10 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Star className="w-5 h-5 text-blue-600" />
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        Salary Range
                      </h4>
                    </div>
                    <div className="space-y-2">
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Minimum:</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          ${salaryInsights.salary_range.min?.toLocaleString() || 'N/A'}
                        </span>
                      </div>
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-600 dark:text-gray-400">Maximum:</span>
                        <span className="font-medium text-gray-900 dark:text-white">
                          ${salaryInsights.salary_range.max?.toLocaleString() || 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="p-4 bg-green-50 dark:bg-green-900/10 rounded-lg">
                    <div className="flex items-center space-x-2 mb-2">
                      <Zap className="w-5 h-5 text-green-600" />
                      <h4 className="font-medium text-gray-900 dark:text-white">
                        AI Recommendation
                      </h4>
                    </div>
                    <p className="text-sm text-gray-600 dark:text-gray-400">
                      Based on current market trends, developer salaries are showing strong growth. 
                      Consider highlighting high-demand skills to maximize your earning potential.
                    </p>
                  </div>
                </div>
              </div>
            ) : (
              <div className="text-center py-12">
                <DollarSign className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                <h3 className="text-lg font-medium text-gray-900 dark:text-white mb-2">
                  No Salary Data Available
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Salary insights will appear here when data is available
                </p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default AIJobRecommendations; 