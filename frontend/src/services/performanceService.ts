import { trackPageLoad, trackApiCall, reportError } from '../config/sentry';

export interface PerformanceMetrics {
  pageLoadTime: number;
  apiResponseTime: number;
  uptime: number;
  errorRate: number;
  activeUsers: number;
  serverStatus: 'healthy' | 'warning' | 'error';
  lastUpdated: Date;
}

export interface ApiMetrics {
  endpoint: string;
  responseTime: number;
  statusCode: number;
  timestamp: Date;
}

class PerformanceService {
  private metrics: PerformanceMetrics[] = [];
  private apiMetrics: ApiMetrics[] = [];
  private startTime: number = Date.now();

  // Sayfa yükleme süresini izle
  trackPageLoad(pageName: string): number {
    const loadTime = performance.now();
    
    // Sentry'ye gönder
    trackPageLoad(pageName, loadTime);
    
    // Local storage'a kaydet
    this.savePageLoadMetric(pageName, loadTime);
    
    return loadTime;
  }

  // API çağrı süresini izle
  trackApiCall(endpoint: string, responseTime: number, statusCode: number): void {
    const apiMetric: ApiMetrics = {
      endpoint,
      responseTime,
      statusCode,
      timestamp: new Date()
    };

    // Sentry'ye gönder
    trackApiCall(endpoint, responseTime, statusCode < 400);

    // Local storage'a kaydet
    this.apiMetrics.push(apiMetric);
    this.saveApiMetrics();
  }

  // Performans metriklerini hesapla
  calculateMetrics(): PerformanceMetrics {
    const now = new Date();
    const uptime = this.calculateUptime();
    const avgPageLoadTime = this.calculateAveragePageLoadTime();
    const avgApiResponseTime = this.calculateAverageApiResponseTime();
    const errorRate = this.calculateErrorRate();
    const serverStatus = this.determineServerStatus();

    const metrics: PerformanceMetrics = {
      pageLoadTime: avgPageLoadTime,
      apiResponseTime: avgApiResponseTime,
      uptime,
      errorRate,
      activeUsers: this.estimateActiveUsers(),
      serverStatus,
      lastUpdated: now
    };

    this.metrics.push(metrics);
    this.saveMetrics();

    return metrics;
  }

  // Uptime hesapla
  private calculateUptime(): number {
    const totalTime = Date.now() - this.startTime;
    const downtime = this.calculateDowntime();
    return Math.max(0, 100 - (downtime / totalTime) * 100);
  }

  // Ortalama sayfa yükleme süresi
  private calculateAveragePageLoadTime(): number {
    const pageLoads = this.getPageLoadMetrics();
    if (pageLoads.length === 0) return 0;
    
    const total = pageLoads.reduce((sum, metric) => sum + metric.loadTime, 0);
    return total / pageLoads.length;
  }

  // Ortalama API response süresi
  private calculateAverageApiResponseTime(): number {
    if (this.apiMetrics.length === 0) return 0;
    
    const total = this.apiMetrics.reduce((sum, metric) => sum + metric.responseTime, 0);
    return total / this.apiMetrics.length;
  }

  // Hata oranı hesapla
  private calculateErrorRate(): number {
    if (this.apiMetrics.length === 0) return 0;
    
    const errors = this.apiMetrics.filter(metric => metric.statusCode >= 400).length;
    return (errors / this.apiMetrics.length) * 100;
  }

  // Server durumu belirle
  private determineServerStatus(): 'healthy' | 'warning' | 'error' {
    const errorRate = this.calculateErrorRate();
    const avgResponseTime = this.calculateAverageApiResponseTime();

    if (errorRate > 5 || avgResponseTime > 1000) {
      return 'error';
    } else if (errorRate > 2 || avgResponseTime > 500) {
      return 'warning';
    } else {
      return 'healthy';
    }
  }

  // Aktif kullanıcı sayısını tahmin et
  private estimateActiveUsers(): number {
    // Basit tahmin - gerçek implementasyonda analytics'ten gelecek
    const baseUsers = 500;
    const timeMultiplier = Math.sin(Date.now() / (24 * 60 * 60 * 1000)) * 0.3 + 1;
    return Math.floor(baseUsers * timeMultiplier);
  }

  // Downtime hesapla (basit implementasyon)
  private calculateDowntime(): number {
    // Gerçek implementasyonda monitoring servisinden gelecek
    return 0;
  }

  // Local storage işlemleri
  private savePageLoadMetric(pageName: string, loadTime: number): void {
    try {
      const metrics = JSON.parse(localStorage.getItem('pageLoadMetrics') || '[]');
      metrics.push({ pageName, loadTime, timestamp: Date.now() });
      
      // Son 100 metrik tut
      if (metrics.length > 100) {
        metrics.splice(0, metrics.length - 100);
      }
      
      localStorage.setItem('pageLoadMetrics', JSON.stringify(metrics));
    } catch (error) {
      reportError(error as Error, { context: 'savePageLoadMetric' });
    }
  }

  private getPageLoadMetrics(): Array<{ pageName: string; loadTime: number; timestamp: number }> {
    try {
      return JSON.parse(localStorage.getItem('pageLoadMetrics') || '[]');
    } catch (error) {
      reportError(error as Error, { context: 'getPageLoadMetrics' });
      return [];
    }
  }

  private saveApiMetrics(): void {
    try {
      // Son 100 API metrik tut
      if (this.apiMetrics.length > 100) {
        this.apiMetrics = this.apiMetrics.slice(-100);
      }
      
      localStorage.setItem('apiMetrics', JSON.stringify(this.apiMetrics));
    } catch (error) {
      reportError(error as Error, { context: 'saveApiMetrics' });
    }
  }

  private saveMetrics(): void {
    try {
      // Son 50 performans metrik tut
      if (this.metrics.length > 50) {
        this.metrics = this.metrics.slice(-50);
      }
      
      localStorage.setItem('performanceMetrics', JSON.stringify(this.metrics));
    } catch (error) {
      reportError(error as Error, { context: 'saveMetrics' });
    }
  }

  // API wrapper - tüm API çağrılarını izle
  async apiCall<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const startTime = performance.now();
    
    try {
      const response = await fetch(endpoint, options);
      const responseTime = performance.now() - startTime;
      
      this.trackApiCall(endpoint, responseTime, response.status);
      
      if (!response.ok) {
        throw new Error(`API Error: ${response.status} ${response.statusText}`);
      }
      
      return await response.json();
    } catch (error) {
      const responseTime = performance.now() - startTime;
      this.trackApiCall(endpoint, responseTime, 500);
      throw error;
    }
  }

  // Backend'den performans metriklerini al
  async fetchBackendMetrics(): Promise<PerformanceMetrics | null> {
    try {
      const response = await this.apiCall<PerformanceMetrics>('/api/performance/metrics');
      return response;
    } catch (error) {
      console.error('Error fetching backend metrics:', error);
      return null;
    }
  }

  // Backend'den sistem sağlık durumunu al
  async fetchHealthStatus(): Promise<any> {
    try {
      const response = await this.apiCall<any>('/api/performance/health');
      return response;
    } catch (error) {
      console.error('Error fetching health status:', error);
      return null;
    }
  }

  // Performans raporu oluştur
  generateReport(): {
    summary: PerformanceMetrics;
    trends: {
      pageLoadTrend: number[];
      apiResponseTrend: number[];
      errorRateTrend: number[];
    };
    recommendations: string[];
  } {
    const summary = this.calculateMetrics();
    
    // Trend analizi (son 10 metrik)
    const recentMetrics = this.metrics.slice(-10);
    const pageLoadTrend = recentMetrics.map(m => m.pageLoadTime);
    const apiResponseTrend = recentMetrics.map(m => m.apiResponseTime);
    const errorRateTrend = recentMetrics.map(m => m.errorRate);

    // Öneriler
    const recommendations: string[] = [];
    
    if (summary.pageLoadTime > 2000) {
      recommendations.push('Sayfa yükleme süresi 2 saniyeyi aşıyor. Bundle optimizasyonu gerekli.');
    }
    
    if (summary.apiResponseTime > 500) {
      recommendations.push('API response süresi 500ms\'i aşıyor. Backend optimizasyonu gerekli.');
    }
    
    if (summary.errorRate > 1) {
      recommendations.push('Hata oranı %1\'i aşıyor. Hata analizi ve düzeltme gerekli.');
    }

    return {
      summary,
      trends: {
        pageLoadTrend,
        apiResponseTrend,
        errorRateTrend
      },
      recommendations
    };
  }
}

export const performanceService = new PerformanceService(); 