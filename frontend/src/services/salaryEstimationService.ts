import apiConfig from '../utils/apiConfig';

export interface SalaryEstimationRequest {
  job_title: string;
  location?: string;
  company_size?: string;
  experience_level?: string;
}

export interface SalaryEstimationResponse {
  min_salary: number;
  max_salary: number;
  currency: string;
  period: string;
  is_estimated: boolean;
  confidence_score?: number;
  data_points?: number;
  similar_jobs_count?: number;
  mean_salary?: number;
  median_salary?: number;
}

export interface SimilarJob {
  _id: string;
  title: string;
  company: string;
  location: string;
  salary_min: number;
  salary_max: number;
  salary_currency: string;
  salary_period: string;
  is_estimated?: boolean;
}

export interface SalaryStatistics {
  total_jobs: number;
  jobs_with_salary: number;
  estimated_salary_jobs: number;
  salary_coverage_percentage: number;
  currency_distribution: Array<{
    _id: string;
    count: number;
  }>;
}

class SalaryEstimationService {
  private async getBaseUrl(): Promise<string> {
    const apiUrl = await apiConfig.getApiUrl();
    return `${apiUrl.replace('/api/v1', '')}/salary`;
  }

  /**
   * Maaş tahmini yap
   */
  async estimateSalary(request: SalaryEstimationRequest): Promise<SalaryEstimationResponse> {
    try {
      const baseUrl = await this.getBaseUrl();
      const response = await fetch(`${baseUrl}/estimate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Maaş tahmini yapılamadı');
      }

      return await response.json();
    } catch (error) {
      console.error('Salary estimation error:', error);
      throw error;
    }
  }

  /**
   * Metinden maaş bilgisini çıkar
   */
  async extractSalaryFromText(text: string): Promise<any> {
    try {
      const baseUrl = await this.getBaseUrl();
      const response = await fetch(`${baseUrl}/extract-from-text`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Maaş bilgisi çıkarılamadı');
      }

      return await response.json();
    } catch (error) {
      console.error('Salary extraction error:', error);
      throw error;
    }
  }

  /**
   * Benzer işleri getir
   */
  async getSimilarJobs(
    jobTitle: string,
    location?: string,
    companySize?: string,
    experienceLevel?: string
  ): Promise<{ job_title: string; similar_jobs_count: number; similar_jobs: SimilarJob[] }> {
    try {
      const baseUrl = await this.getBaseUrl();
      const params = new URLSearchParams({
        job_title: jobTitle,
        ...(location && { location }),
        ...(companySize && { company_size: companySize }),
        ...(experienceLevel && { experience_level: experienceLevel }),
      });

      const response = await fetch(`${baseUrl}/similar-jobs/${encodeURIComponent(jobTitle)}?${params}`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Benzer işler bulunamadı');
      }

      return await response.json();
    } catch (error) {
      console.error('Similar jobs error:', error);
      throw error;
    }
  }

  /**
   * İş verisini işle ve maaş bilgisini ekle
   */
  async processJobSalary(jobData: any): Promise<any> {
    try {
      const baseUrl = await this.getBaseUrl();
      const response = await fetch(`${baseUrl}/process-job`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(jobData),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'İş verisi işlenemedi');
      }

      return await response.json();
    } catch (error) {
      console.error('Job processing error:', error);
      throw error;
    }
  }

  /**
   * Maaş istatistiklerini getir
   */
  async getSalaryStatistics(): Promise<SalaryStatistics> {
    try {
      const baseUrl = await this.getBaseUrl();
      const response = await fetch(`${baseUrl}/statistics`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'İstatistikler alınamadı');
      }

      return await response.json();
    } catch (error) {
      console.error('Salary statistics error:', error);
      throw error;
    }
  }

  /**
   * Maaş formatını düzenle
   */
  formatSalary(salary: number, currency: string, period: string, isEstimated: boolean = false): string {
    const formatter = new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });

    const formattedSalary = formatter.format(salary);
    const periodText = this.getPeriodText(period);
    const estimatedText = isEstimated ? ' (est.)' : '';

    return `${formattedSalary}${periodText}${estimatedText}`;
  }

  /**
   * Maaş aralığını formatla
   */
  formatSalaryRange(
    minSalary: number,
    maxSalary: number,
    currency: string,
    period: string,
    isEstimated: boolean = false
  ): string {
    const formatter = new Intl.NumberFormat('tr-TR', {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    });

    const formattedMin = formatter.format(minSalary);
    const formattedMax = formatter.format(maxSalary);
    const periodText = this.getPeriodText(period);
    const estimatedText = isEstimated ? ' (est.)' : '';

    return `${formattedMin} - ${formattedMax}${periodText}${estimatedText}`;
  }

  /**
   * Periyot metnini getir
   */
  private getPeriodText(period: string): string {
    switch (period.toLowerCase()) {
      case 'yearly':
      case 'annual':
        return '/yıl';
      case 'monthly':
        return '/ay';
      case 'hourly':
        return '/saat';
      default:
        return '';
    }
  }

  /**
   * Güven skorunu yüzde olarak formatla
   */
  formatConfidenceScore(score: number): string {
    return `${Math.round(score * 100)}%`;
  }

  /**
   * Güven skoruna göre renk sınıfı getir
   */
  getConfidenceColorClass(score: number): string {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  }

  /**
   * Maaş bilgisini kullanıcı dostu formatta göster
   */
  getSalaryDisplayText(
    minSalary?: number,
    maxSalary?: number,
    currency?: string,
    period?: string,
    isEstimated?: boolean
  ): string {
    if (!minSalary || !maxSalary || !currency || !period) {
      return 'Maaş bilgisi mevcut değil';
    }

    if (minSalary === maxSalary) {
      return this.formatSalary(minSalary, currency, period, isEstimated);
    } else {
      return this.formatSalaryRange(minSalary, maxSalary, currency, period, isEstimated);
    }
  }
}

export const salaryEstimationService = new SalaryEstimationService(); 