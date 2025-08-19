import React, { useState, useEffect } from 'react';
import { FaTachometerAlt, FaClock, FaServer, FaExclamationTriangle, FaCheckCircle, FaChartLine, FaSync, FaLightbulb, FaArrowUp, FaArrowDown } from 'react-icons/fa';
import Layout from '../components/Layout';
import { performanceService, PerformanceMetrics } from '../services/performanceService';

interface SentryError {
  id: string;
  title: string;
  level: 'error' | 'warning' | 'info';
  count: number;
  lastSeen: Date;
  project: string;
}

const PerformanceDashboard: React.FC = () => {
  const [metrics, setMetrics] = useState<PerformanceMetrics | null>(null);
  const [sentryErrors, setSentryErrors] = useState<SentryError[]>([]);
  const [loading, setLoading] = useState(true);
  const [lastRefresh, setLastRefresh] = useState<Date>(new Date());
  const [recommendations, setRecommendations] = useState<string[]>([]);

  useEffect(() => {
    fetchPerformanceData();
    const interval = setInterval(fetchPerformanceData, 30000); // Refresh every 30 seconds
    return () => clearInterval(interval);
  }, []);

  const fetchPerformanceData = async () => {
    try {
      setLoading(true);
      
      // Backend'den gerçek performans metriklerini al
      const backendMetrics = await performanceService.fetchBackendMetrics();
      
      // Local performans metriklerini hesapla
      const localMetrics = performanceService.calculateMetrics();
      
      // Backend metrikleri varsa onları kullan, yoksa local'den
      const finalMetrics = backendMetrics || localMetrics;
      
      // Performans raporu oluştur
      const report = performanceService.generateReport();
      
      // Mock Sentry errors (gerçek implementasyonda Sentry API'den gelecek)
      const mockSentryErrors: SentryError[] = [
        {
          id: '1',
          title: 'API timeout error in job search',
          level: 'error',
          count: 15,
          lastSeen: new Date(Date.now() - 1000 * 60 * 30),
          project: 'frontend'
        },
        {
          id: '2',
          title: 'Database connection failed',
          level: 'error',
          count: 8,
          lastSeen: new Date(Date.now() - 1000 * 60 * 60),
          project: 'backend'
        },
        {
          id: '3',
          title: 'Memory usage high',
          level: 'warning',
          count: 25,
          lastSeen: new Date(Date.now() - 1000 * 60 * 15),
          project: 'backend'
        },
        {
          id: '4',
          title: 'Slow page load detected',
          level: 'warning',
          count: 12,
          lastSeen: new Date(Date.now() - 1000 * 60 * 45),
          project: 'frontend'
        }
      ];
      
      setMetrics(finalMetrics);
      setSentryErrors(mockSentryErrors);
      setRecommendations(report.recommendations);
      setLastRefresh(new Date());
      
      // Performans önerilerini console'a yazdır
      if (report.recommendations.length > 0) {
        console.log('🚀 Performance Recommendations:', report.recommendations);
      }
    } catch (error) {
      console.error('Error fetching performance data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'healthy': return 'text-green-600 bg-green-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'error': return 'text-red-600 bg-red-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy': return <FaCheckCircle className="w-4 h-4" />;
      case 'warning': return <FaExclamationTriangle className="w-4 h-4" />;
      case 'error': return <FaExclamationTriangle className="w-4 h-4" />;
      default: return <FaServer className="w-4 h-4" />;
    }
  };

  const getErrorLevelColor = (level: string) => {
    switch (level) {
      case 'error': return 'text-red-600 bg-red-100';
      case 'warning': return 'text-yellow-600 bg-yellow-100';
      case 'info': return 'text-blue-600 bg-blue-100';
      default: return 'text-gray-600 bg-gray-100';
    }
  };

  const formatTime = (date: Date) => {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
  };

  const formatRelativeTime = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const minutes = Math.floor(diff / (1000 * 60));
    const hours = Math.floor(diff / (1000 * 60 * 60));
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));

    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  if (loading && !metrics) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="flex justify-center items-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Performance Dashboard
              </h1>
              <p className="text-gray-600">
                Real-time monitoring of system performance and error tracking
              </p>
            </div>
            <button
              onClick={fetchPerformanceData}
              disabled={loading}
              className="flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 transition-colors"
            >
              <FaSync className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Refresh
            </button>
          </div>

          {/* Last Updated */}
          <div className="mb-6 text-sm text-gray-500">
            Last updated: {lastRefresh ? formatTime(lastRefresh) : 'Never'}
          </div>

          {metrics && (
            <>
              {/* Key Metrics */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                {/* Page Load Time */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                        <FaClock className="w-5 h-5 text-blue-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-600">Page Load Time</h3>
                        <p className="text-2xl font-bold text-gray-900">
                          {metrics.pageLoadTime.toFixed(2)}s
                        </p>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      metrics.pageLoadTime < 2 ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
                    }`}>
                      {metrics.pageLoadTime < 2 ? 'Good' : 'Slow'}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Target: &lt;2s
                  </div>
                </div>

                {/* API Response Time */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                        <FaTachometerAlt className="w-5 h-5 text-green-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-600">API Response</h3>
                        <p className="text-2xl font-bold text-gray-900">
                          {metrics.apiResponseTime.toFixed(0)}ms
                        </p>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      metrics.apiResponseTime < 500 ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
                    }`}>
                      {metrics.apiResponseTime < 500 ? 'Fast' : 'Slow'}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Target: &lt;500ms
                  </div>
                </div>

                {/* Uptime */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                        <FaServer className="w-5 h-5 text-purple-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-600">Uptime</h3>
                        <p className="text-2xl font-bold text-gray-900">
                          {metrics.uptime.toFixed(3)}%
                        </p>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${
                      metrics.uptime >= 99.9 ? 'text-green-600 bg-green-100' : 'text-red-600 bg-red-100'
                    }`}>
                      {metrics.uptime >= 99.9 ? 'Excellent' : 'Poor'}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    Target: 99.9%+
                  </div>
                </div>

                {/* Server Status */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-orange-100 rounded-lg flex items-center justify-center">
                        <FaServer className="w-5 h-5 text-orange-600" />
                      </div>
                      <div>
                        <h3 className="text-sm font-medium text-gray-600">Server Status</h3>
                        <p className="text-2xl font-bold text-gray-900 capitalize">
                          {metrics.serverStatus}
                        </p>
                      </div>
                    </div>
                    <div className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(metrics.serverStatus)}`}>
                      {getStatusIcon(metrics.serverStatus)}
                    </div>
                  </div>
                  <div className="text-xs text-gray-500">
                    {metrics.activeUsers.toLocaleString()} active users
                  </div>
                </div>
              </div>

              {/* Performance Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-8">
                {/* Performance Trend */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <FaChartLine className="w-5 h-5 text-blue-600" />
                    Performance Trend (Last 24h)
                  </h3>
                  <div className="h-64 bg-gray-50 rounded-lg flex items-center justify-center">
                    <p className="text-gray-500">Chart visualization would go here</p>
                  </div>
                </div>

                {/* Error Rate */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <FaExclamationTriangle className="w-5 h-5 text-red-600" />
                    Error Rate
                  </h3>
                  <div className="text-center">
                    <div className="text-4xl font-bold text-gray-900 mb-2">
                      {metrics.errorRate.toFixed(3)}%
                    </div>
                    <div className="text-sm text-gray-600">
                      {metrics.errorRate < 0.1 ? 'Excellent' : metrics.errorRate < 0.5 ? 'Good' : 'Needs attention'}
                    </div>
                  </div>
                </div>
              </div>

              {/* Sentry Errors */}
              <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                  <FaExclamationTriangle className="w-5 h-5 text-red-600" />
                  Recent Errors (Sentry)
                </h3>
                
                {sentryErrors.length === 0 ? (
                  <div className="text-center py-8">
                    <FaCheckCircle className="w-12 h-12 text-green-400 mx-auto mb-4" />
                    <p className="text-gray-600">No errors reported</p>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {sentryErrors.map((error) => (
                      <div key={error.id} className="border border-gray-200 rounded-lg p-4">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-3 mb-2">
                              <span className={`px-2 py-1 rounded-full text-xs font-medium ${getErrorLevelColor(error.level)}`}>
                                {error.level.toUpperCase()}
                              </span>
                              <span className="text-sm text-gray-500">
                                {error.project}
                              </span>
                            </div>
                            <h4 className="font-medium text-gray-900 mb-1">
                              {error.title}
                            </h4>
                            <div className="flex items-center gap-4 text-sm text-gray-500">
                              <span>{error.count} occurrences</span>
                              <span>Last seen: {formatRelativeTime(error.lastSeen)}</span>
                            </div>
                          </div>
                          <button className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                            View Details
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Performance Recommendations */}
              {recommendations.length > 0 && (
                <div className="mt-8 bg-gradient-to-r from-yellow-50 to-orange-50 rounded-lg p-6 border border-yellow-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4 flex items-center gap-2">
                    <FaLightbulb className="w-5 h-5 text-yellow-600" />
                    Performance Recommendations
                  </h3>
                  <div className="space-y-3">
                    {recommendations.map((recommendation, index) => (
                      <div key={index} className="flex items-start gap-3 p-3 bg-white rounded-lg border border-yellow-200">
                        <FaLightbulb className="w-4 h-4 text-yellow-600 mt-0.5 flex-shrink-0" />
                        <p className="text-sm text-gray-700">{recommendation}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* System Health Summary */}
              <div className="mt-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-lg p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">
                  System Health Summary
                </h3>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      metrics.pageLoadTime < 2 && metrics.apiResponseTime < 500 ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span className="text-sm text-gray-700">Performance</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      metrics.uptime >= 99.9 ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span className="text-sm text-gray-700">Availability</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${
                      sentryErrors.filter(e => e.level === 'error').length === 0 ? 'bg-green-500' : 'bg-red-500'
                    }`}></div>
                    <span className="text-sm text-gray-700">Error Rate</span>
                  </div>
                </div>
              </div>
            </>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default PerformanceDashboard; 