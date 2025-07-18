import React, { useState, useEffect } from 'react';
import { salaryEstimationService, SalaryEstimationRequest, SalaryEstimationResponse } from '../services/salaryEstimationService';

interface SalaryEstimationProps {
  jobTitle: string;
  location?: string;
  companySize?: string;
  experienceLevel?: string;
  onEstimationComplete?: (estimation: SalaryEstimationResponse) => void;
  showDetails?: boolean;
  className?: string;
}

const SalaryEstimation: React.FC<SalaryEstimationProps> = ({
  jobTitle,
  location,
  companySize,
  experienceLevel,
  onEstimationComplete,
  showDetails = false,
  className = ''
}) => {
  const [estimation, setEstimation] = useState<SalaryEstimationResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [showEstimation, setShowEstimation] = useState(false);

  useEffect(() => {
    if (jobTitle && showEstimation) {
      estimateSalary();
    }
  }, [jobTitle, location, companySize, experienceLevel, showEstimation]);

  const estimateSalary = async () => {
    if (!jobTitle.trim()) return;

    setLoading(true);
    setError(null);

    try {
      const request: SalaryEstimationRequest = {
        job_title: jobTitle,
        location,
        company_size: companySize,
        experience_level: experienceLevel,
      };

      const result = await salaryEstimationService.estimateSalary(request);
      setEstimation(result);
      
      if (onEstimationComplete) {
        onEstimationComplete(result);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Maaş tahmini yapılamadı');
    } finally {
      setLoading(false);
    }
  };

  const handleEstimateClick = () => {
    setShowEstimation(true);
  };

  if (!showEstimation) {
    return (
      <div className={`${className}`}>
        <button
          onClick={handleEstimateClick}
          className="inline-flex items-center px-3 py-1.5 text-sm font-medium text-blue-600 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 hover:border-blue-300 transition-colors"
        >
          <svg className="w-4 h-4 mr-1.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
          </svg>
          Maaş Tahmini Yap
        </button>
      </div>
    );
  }

  if (loading) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center space-x-2 text-gray-600">
          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
          <span className="text-sm">Maaş tahmini yapılıyor...</span>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className={`${className}`}>
        <div className="flex items-center space-x-2 text-red-600">
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <span className="text-sm">{error}</span>
        </div>
      </div>
    );
  }

  if (!estimation) {
    return (
      <div className={`${className}`}>
        <div className="text-sm text-gray-500">
          Maaş tahmini için yeterli veri bulunamadı.
        </div>
      </div>
    );
  }

  return (
    <div className={`${className}`}>
      <div className="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-4">
        <div className="flex items-center justify-between mb-3">
          <h4 className="text-sm font-semibold text-gray-900 flex items-center">
            <svg className="w-4 h-4 mr-1.5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8c-1.657 0-3 .895-3 2s1.343 2 3 2 3 .895 3 2-1.343 2-3 2m0-8c1.11 0 2.08.402 2.599 1M12 8V7m0 1v8m0 0v1m0-1c-1.11 0-2.08-.402-2.599-1" />
            </svg>
            Tahmini Maaş Aralığı
          </h4>
          {estimation.is_estimated && (
            <span className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-yellow-100 text-yellow-800">
              <svg className="w-3 h-3 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              Tahmin
            </span>
          )}
        </div>

        <div className="text-lg font-bold text-gray-900 mb-2">
          {salaryEstimationService.formatSalaryRange(
            estimation.min_salary,
            estimation.max_salary,
            estimation.currency,
            estimation.period,
            estimation.is_estimated
          )}
        </div>

        {showDetails && (
          <div className="space-y-2 text-sm text-gray-600">
            {estimation.confidence_score && (
              <div className="flex items-center justify-between">
                <span>Güven Skoru:</span>
                <span className={`font-medium ${salaryEstimationService.getConfidenceColorClass(estimation.confidence_score)}`}>
                  {salaryEstimationService.formatConfidenceScore(estimation.confidence_score)}
                </span>
              </div>
            )}
            
            {estimation.data_points && (
              <div className="flex items-center justify-between">
                <span>Veri Noktası:</span>
                <span className="font-medium">{estimation.data_points}</span>
              </div>
            )}
            
            {estimation.similar_jobs_count && (
              <div className="flex items-center justify-between">
                <span>Benzer İş Sayısı:</span>
                <span className="font-medium">{estimation.similar_jobs_count}</span>
              </div>
            )}
            
            {estimation.mean_salary && (
              <div className="flex items-center justify-between">
                <span>Ortalama Maaş:</span>
                <span className="font-medium">
                  {salaryEstimationService.formatSalary(estimation.mean_salary, estimation.currency, estimation.period)}
                </span>
              </div>
            )}
          </div>
        )}

        <div className="mt-3 pt-3 border-t border-blue-200">
          <p className="text-xs text-gray-500">
            Bu tahmin, benzer pozisyonların maaş verilerine dayanarak yapılmıştır ve 
            {estimation.is_estimated ? ' kesin değildir' : ' gerçek maaş bilgilerine dayanmaktadır'}.
          </p>
        </div>
      </div>
    </div>
  );
};

export default SalaryEstimation; 