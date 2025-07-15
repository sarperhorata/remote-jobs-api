import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { API_URL } from '../config';
import { formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';
import Layout from '../components/Layout';
import { FileText, Clock, CheckCircle, XCircle, AlertCircle, ExternalLink } from 'lucide-react';

interface Application {
  _id: string;
  job: {
    _id: string;
    title: string;
    company: string;
    location: string;
    type: string;
  };
  status: 'pending' | 'reviewed' | 'accepted' | 'rejected';
  appliedAt: string;
  updatedAt: string;
  notes?: string;
}

const Applications: React.FC = () => {
  const { user, isAuthenticated } = useAuth();
  const [filter, setFilter] = useState<string>('all');
  const [applications, setApplications] = useState<Application[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchApplications = async () => {
      if (!user) return;
      
      try {
        setIsLoading(true);
        const response = await fetch(`${API_URL}/applications`, {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`
          }
        });
        if (!response.ok) throw new Error('Failed to fetch applications');
        const data = await response.json();
        setApplications(data);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'An error occurred');
      } finally {
        setIsLoading(false);
      }
    };

    fetchApplications();
    
    // Refetch every 30 seconds
    const interval = setInterval(fetchApplications, 30000);
    return () => clearInterval(interval);
  }, [user]);

  const filteredApplications = applications?.filter(app => {
    if (filter === 'all') return true;
    return app.status === filter;
  });

  const getStatusConfig = (status: string) => {
    switch (status) {
      case 'pending':
        return {
          icon: Clock,
          color: 'text-yellow-600 dark:text-yellow-400',
          bg: 'bg-yellow-100 dark:bg-yellow-900/30',
          label: 'İnceleniyor'
        };
      case 'reviewed':
        return {
          icon: AlertCircle,
          color: 'text-blue-600 dark:text-blue-400',
          bg: 'bg-blue-100 dark:bg-blue-900/30',
          label: 'İncelendi'
        };
      case 'accepted':
        return {
          icon: CheckCircle,
          color: 'text-green-600 dark:text-green-400',
          bg: 'bg-green-100 dark:bg-green-900/30',
          label: 'Kabul Edildi'
        };
      case 'rejected':
        return {
          icon: XCircle,
          color: 'text-red-600 dark:text-red-400',
          bg: 'bg-red-100 dark:bg-red-900/30',
          label: 'Reddedildi'
        };
      default:
        return {
          icon: Clock,
          color: 'text-gray-600 dark:text-gray-400',
          bg: 'bg-gray-100 dark:bg-gray-900/30',
          label: status
        };
    }
  };

  const getApplicationStats = () => {
    const stats = {
      total: applications.length,
      pending: applications.filter(app => app.status === 'pending').length,
      reviewed: applications.filter(app => app.status === 'reviewed').length,
      accepted: applications.filter(app => app.status === 'accepted').length,
      rejected: applications.filter(app => app.status === 'rejected').length,
    };
    return stats;
  };

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="max-w-md mx-auto">
            <FileText className="w-16 h-16 text-gray-400 dark:text-gray-500 mx-auto mb-4" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-4">Giriş Yapın</h1>
            <p className="text-gray-600 dark:text-gray-300">Başvurularınızı görüntülemek için giriş yapmanız gerekiyor.</p>
          </div>
        </div>
      </Layout>
    );
  }

  if (isLoading) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600 dark:text-gray-300">Başvurularınız yükleniyor...</p>
        </div>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-16 text-center">
          <div className="max-w-md mx-auto">
            <div className="text-red-600 dark:text-red-400">
              <XCircle className="h-12 w-12 mx-auto" />
            </div>
            <h3 className="mt-2 text-lg font-medium text-gray-900 dark:text-white">Bir hata oluştu</h3>
            <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">Başvurularınız yüklenirken bir sorun oluştu. Lütfen daha sonra tekrar deneyin.</p>
          </div>
        </div>
      </Layout>
    );
  }

  const stats = getApplicationStats();

  return (
    <Layout>
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
            <FileText className="w-8 h-8 text-blue-500" />
            Başvurularım
          </h1>
          <p className="text-gray-600 dark:text-gray-300 mt-2">
            İş başvurularınızı takip edin ve durumlarını görüntüleyin
          </p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4 mb-8">
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-gray-900 dark:text-white">{stats.total}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Toplam</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-yellow-600 dark:text-yellow-400">{stats.pending}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">İnceleniyor</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">{stats.reviewed}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">İncelendi</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-green-600 dark:text-green-400">{stats.accepted}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Kabul Edildi</div>
          </div>
          <div className="bg-white dark:bg-slate-800 rounded-lg p-4 text-center border border-gray-200 dark:border-slate-600">
            <div className="text-2xl font-bold text-red-600 dark:text-red-400">{stats.rejected}</div>
            <div className="text-xs text-gray-600 dark:text-gray-300">Reddedildi</div>
          </div>
        </div>

        {/* Filtreler */}
        <div className="mb-6 flex flex-wrap gap-2">
          <button
            onClick={() => setFilter('all')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'all'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-600'
            }`}
          >
            Tümü
          </button>
          <button
            onClick={() => setFilter('pending')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'pending'
                ? 'bg-yellow-600 text-white'
                : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-600'
            }`}
          >
            İnceleniyor
          </button>
          <button
            onClick={() => setFilter('reviewed')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'reviewed'
                ? 'bg-blue-600 text-white'
                : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-600'
            }`}
          >
            İncelendi
          </button>
          <button
            onClick={() => setFilter('accepted')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'accepted'
                ? 'bg-green-600 text-white'
                : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-600'
            }`}
          >
            Kabul Edildi
          </button>
          <button
            onClick={() => setFilter('rejected')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === 'rejected'
                ? 'bg-red-600 text-white'
                : 'bg-white dark:bg-slate-800 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-slate-700 border border-gray-200 dark:border-slate-600'
            }`}
          >
            Reddedildi
          </button>
        </div>

        {/* Başvuru Listesi */}
        <div className="space-y-4">
          {filteredApplications?.length === 0 ? (
            <div className="text-center py-12">
              <FileText className="mx-auto h-12 w-12 text-gray-400 dark:text-gray-500" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">Başvuru bulunamadı</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {filter === 'all'
                  ? 'Henüz hiç başvuru yapmamışsınız.'
                  : 'Bu kategoride başvuru bulunamadı.'}
              </p>
            </div>
          ) : (
            filteredApplications?.map((application) => {
              const statusConfig = getStatusConfig(application.status);
              const StatusIcon = statusConfig.icon;
              
              return (
                <div
                  key={application._id}
                  className="bg-white dark:bg-slate-800 shadow-sm rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-200 border border-gray-200 dark:border-slate-600"
                >
                  <div className="p-6">
                    <div className="flex items-start justify-between">
                      <div className="flex-1">
                        <div className="flex items-start gap-4">
                          {/* Company Logo Placeholder */}
                          <div className="w-12 h-12 rounded-lg bg-gray-100 dark:bg-slate-700 flex items-center justify-center flex-shrink-0">
                            <div className="w-12 h-12 rounded-lg bg-gray-200 dark:bg-slate-600 flex items-center justify-center text-gray-500 dark:text-gray-400 text-sm font-semibold">
                              {application.job.company.charAt(0)}
                            </div>
                          </div>
                          
                          <div className="flex-1 min-w-0">
                            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-1">
                              {application.job.title}
                            </h3>
                            <p className="text-blue-600 dark:text-blue-400 font-medium mb-1">
                              {application.job.company}
                            </p>
                            <p className="text-gray-600 dark:text-gray-300 text-sm mb-2">
                              {application.job.location} • {application.job.type}
                            </p>
                            
                            <div className="flex items-center gap-4 text-sm text-gray-500 dark:text-gray-400">
                              <span>
                                Başvuru: {formatDistanceToNow(new Date(application.appliedAt), { addSuffix: true, locale: tr })}
                              </span>
                              <span>
                                Son Güncelleme: {formatDistanceToNow(new Date(application.updatedAt), { addSuffix: true, locale: tr })}
                              </span>
                            </div>
                            
                            {application.notes && (
                              <div className="mt-3 p-3 bg-gray-50 dark:bg-slate-700 rounded-md">
                                <p className="text-sm text-gray-700 dark:text-gray-300">{application.notes}</p>
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                      
                      <div className="ml-4 flex flex-col items-end gap-3">
                        <span className={`inline-flex items-center gap-1 px-3 py-1 rounded-full text-sm font-medium ${statusConfig.bg} ${statusConfig.color}`}>
                          <StatusIcon className="w-4 h-4" />
                          {statusConfig.label}
                        </span>
                        
                        <a
                          href={`/jobs/${application.job._id}`}
                          className="p-2 text-gray-400 dark:text-gray-500 hover:text-blue-500 dark:hover:text-blue-400 hover:bg-blue-50 dark:hover:bg-blue-900/30 rounded-full transition-colors"
                          title="İlanı Görüntüle"
                        >
                          <ExternalLink className="w-5 h-5" />
                        </a>
                      </div>
                    </div>
                  </div>
                </div>
              );
            })
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Applications; 