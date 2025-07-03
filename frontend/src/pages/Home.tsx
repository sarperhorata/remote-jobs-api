import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Layout from '../components/Layout';
import AuthModal from '../components/AuthModal';
import Onboarding from '../components/Onboarding';
import MultiJobAutocomplete from '../components/MultiJobAutocomplete';
import { jobService } from '../services/jobService';
import type { Job } from '../types/job';

// Simple icon components
const Search = () => <span>🔍</span>;

interface Position {
  title: string;
  count: number;
  category?: string;
}

const Home: React.FC = () => {
  const navigate = useNavigate();
  const [showAuthModal, setShowAuthModal] = useState(false);
  const [showOnboarding, setShowOnboarding] = useState(false);
  const [selectedPositions, setSelectedPositions] = useState<Position[]>([]);
  const [statistics, setStatistics] = useState({
    total_jobs: 0,
    active_jobs: 0
  });
  const [recentJobs, setRecentJobs] = useState<Job[]>([]);

  // Simple fallback positions
  const fallbackPositions: Position[] = [
    { title: "Software Engineer", count: 1523, category: "Engineering" },
    { title: "Product Manager", count: 892, category: "Product" },
    { title: "Frontend Developer", count: 745, category: "Engineering" },
    { title: "Backend Developer", count: 654, category: "Engineering" },
    { title: "Data Scientist", count: 432, category: "Data" },
    { title: "DevOps Engineer", count: 321, category: "Engineering" }
  ];

  useEffect(() => {
    // Load statistics
    const loadStats = async () => {
      try {
        const stats = await jobService.getJobStatistics();
        setStatistics(stats);
      } catch (error) {
        console.error('Error loading statistics:', error);
        setStatistics({ total_jobs: 38345, active_jobs: 38345 });
      }
    };

    // Load recent jobs
    const loadRecentJobs = async () => {
      try {
        const jobs = await jobService.searchJobs({ q: '', page: 1, per_page: 6 });
        setRecentJobs(jobs.jobs || []);
      } catch (error) {
        console.error('Error loading recent jobs:', error);
      }
    };

    loadStats();
    loadRecentJobs();
  }, []);

  const handlePositionSelect = (position: Position) => {
    setSelectedPositions([position]);
    navigate(`/jobs?q=${encodeURIComponent(position.title)}`);
  };

  const handleSearch = (positions: Position[]) => {
    if (positions.length > 0) {
      const query = positions.map(p => p.title).join(' ');
      navigate(`/jobs?q=${encodeURIComponent(query)}`);
    }
  };

  return (
    <Layout>
      <div className="min-h-screen bg-white dark:bg-gray-900">
        {/* Hero Section */}
        <section className="py-20 px-4">
          <div className="max-w-6xl mx-auto text-center">
            <h1 className="text-4xl md:text-6xl font-bold text-gray-900 dark:text-white mb-6">
              Uzaktan Çalışma Hayallerini <br />
              <span className="text-blue-600 dark:text-blue-400">Gerçeğe Dönüştür</span>
            </h1>
            
            <p className="text-xl text-gray-600 dark:text-gray-300 mb-12 max-w-3xl mx-auto">
              Dünyanın her yerinden remote iş fırsatlarını keşfet. 
              {statistics.total_jobs ? `${statistics.total_jobs.toLocaleString()}+` : '38,000+'} aktif iş ilanı arasından sana uygun olanı bul.
            </p>

            {/* Search Section */}
            <div className="max-w-2xl mx-auto mb-16">
              <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
                <MultiJobAutocomplete
                  onSelect={handlePositionSelect}
                  placeholder="Hangi pozisyonu arıyorsun? (örn: Frontend Developer)"
                  className="w-full text-lg"
                />
                
                <div className="mt-6 flex flex-wrap gap-2 justify-center">
                  {fallbackPositions.slice(0, 6).map((position) => (
                    <button
                      key={position.title}
                      onClick={() => handlePositionSelect(position)}
                      className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full text-sm hover:bg-blue-100 dark:hover:bg-blue-900 transition-colors"
                    >
                      {position.title}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-20">
              <div className="text-center">
                <div className="text-3xl font-bold text-blue-600 dark:text-blue-400">
                  {statistics.total_jobs ? statistics.total_jobs.toLocaleString() : '38,345'}+
                </div>
                <div className="text-gray-600 dark:text-gray-400">Toplam İş İlanı</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-green-600 dark:text-green-400">
                  {statistics.active_jobs ? statistics.active_jobs.toLocaleString() : '38,345'}+
                </div>
                <div className="text-gray-600 dark:text-gray-400">Aktif İlan</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-purple-600 dark:text-purple-400">2,500+</div>
                <div className="text-gray-600 dark:text-gray-400">Şirket</div>
              </div>
              <div className="text-center">
                <div className="text-3xl font-bold text-orange-600 dark:text-orange-400">100%</div>
                <div className="text-gray-600 dark:text-gray-400">Remote</div>
              </div>
            </div>
          </div>
        </section>

        {/* Recent Jobs */}
        {recentJobs.length > 0 && (
          <section className="py-16 px-4 bg-gray-50 dark:bg-gray-800">
            <div className="max-w-6xl mx-auto">
              <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
                Son Eklenen İş İlanları
              </h2>
              
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                {recentJobs.slice(0, 6).map((job) => (
                  <div key={job._id || job.id} className="bg-white dark:bg-gray-900 rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
                    <h3 className="font-bold text-lg text-gray-900 dark:text-white mb-2">
                      {job.title}
                    </h3>
                    <p className="text-blue-600 dark:text-blue-400 mb-2">
                      {typeof job.company === 'string' ? job.company : job.company?.name || 'Şirket'}
                    </p>
                    <p className="text-gray-600 dark:text-gray-400 mb-4">{job.location}</p>
                    <div className="flex flex-wrap gap-2 mb-4">
                      {job.skills?.slice(0, 3).map((skill, index) => (
                        <span key={index} className="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-xs rounded">
                          {skill}
                        </span>
                      ))}
                    </div>
                    <Link
                      to={`/jobs/${job._id || job.id}`}
                      className="text-blue-600 dark:text-blue-400 hover:underline text-sm"
                    >
                      Detayları Gör →
                    </Link>
                  </div>
                ))}
              </div>

              <div className="text-center mt-12">
                <Link
                  to="/jobs"
                  className="inline-flex items-center px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
                >
                  Tüm İş İlanlarını Gör
                  <span className="ml-2">→</span>
                </Link>
              </div>
            </div>
          </section>
        )}

        {/* Features */}
        <section className="py-16 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-3xl font-bold text-center text-gray-900 dark:text-white mb-12">
              Neden Buzz2Remote?
            </h2>
            
            <div className="grid md:grid-cols-3 gap-8">
              <div className="text-center">
                <div className="text-4xl mb-4">🌍</div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Global Fırsatlar
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Dünyanın her yerinden remote iş fırsatlarına erişin
                </p>
              </div>
              
              <div className="text-center">
                <div className="text-4xl mb-4">⚡</div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Hızlı Başvuru
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Tek tıkla direkt şirketlerin sayfalarına yönlendirme
                </p>
              </div>
              
              <div className="text-center">
                <div className="text-4xl mb-4">🔍</div>
                <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">
                  Akıllı Filtreleme
                </h3>
                <p className="text-gray-600 dark:text-gray-400">
                  Gelişmiş filtreleme ile tam istediğin işi bul
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Modals */}
        {showAuthModal && (
          <AuthModal 
            isOpen={showAuthModal}
            onClose={() => setShowAuthModal(false)} 
          />
        )}
        
        {showOnboarding && (
          <Onboarding 
            isOpen={showOnboarding}
            onClose={() => setShowOnboarding(false)}
            onComplete={() => {
              setShowOnboarding(false);
              navigate('/jobs');
            }}
          />
        )}
      </div>
    </Layout>
  );
};

export default Home; 