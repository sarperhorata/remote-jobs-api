import React, { useState } from 'react';
import { useQuery } from 'react-query';
import { API_URL } from '../config';
import { formatDistanceToNow } from 'date-fns';
import { tr } from 'date-fns/locale';

interface Company {
  _id: string;
  name: string;
  logo: string;
  description: string;
  website: string;
  location: string;
  size: string;
  industry: string;
  founded: number;
  jobs: {
    _id: string;
    title: string;
    type: string;
    location: string;
    postedAt: string;
  }[];
}

const Companies: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [industryFilter, setIndustryFilter] = useState('all');
  const [sizeFilter, setSizeFilter] = useState('all');

  const { data: companies, isLoading, error } = useQuery<Company[]>(
    'companies',
    async () => {
      const response = await fetch(`${API_URL}/companies`);
      if (!response.ok) throw new Error('Failed to fetch companies');
      return response.json();
    }
  );

  const filteredCompanies = companies?.filter(company => {
    const matchesSearch = company.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         company.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesIndustry = industryFilter === 'all' || company.industry === industryFilter;
    const matchesSize = sizeFilter === 'all' || company.size === sizeFilter;
    return matchesSearch && matchesIndustry && matchesSize;
  });

  const industries = Array.from(new Set(companies?.map(c => c.industry) || []));
  const sizes = Array.from(new Set(companies?.map(c => c.size) || []));

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600 mx-auto"></div>
            <p className="mt-4 text-gray-600">Şirketler yükleniyor...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          <div className="text-center">
            <div className="text-red-600">
              <svg className="h-12 w-12 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
            </div>
            <h3 className="mt-2 text-lg font-medium text-gray-900">Bir hata oluştu</h3>
            <p className="mt-1 text-sm text-gray-500">Şirketler yüklenirken bir sorun oluştu. Lütfen daha sonra tekrar deneyin.</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        <div className="text-center">
          <h1 className="text-3xl font-extrabold text-gray-900 sm:text-4xl">
            Şirketler
          </h1>
          <p className="mt-4 text-lg text-gray-500">
            Uzaktan çalışma fırsatları sunan şirketleri keşfedin
          </p>
        </div>

        {/* Filtreler */}
        <div className="mt-8 space-y-4">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <input
                type="text"
                placeholder="Şirket ara..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>
            <select
              value={industryFilter}
              onChange={(e) => setIndustryFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">Tüm Sektörler</option>
              {industries.map(industry => (
                <option key={industry} value={industry}>{industry}</option>
              ))}
            </select>
            <select
              value={sizeFilter}
              onChange={(e) => setSizeFilter(e.target.value)}
              className="px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-indigo-500"
            >
              <option value="all">Tüm Boyutlar</option>
              {sizes.map(size => (
                <option key={size} value={size}>{size}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Şirket Listesi */}
        <div className="mt-8 space-y-6">
          {filteredCompanies?.length === 0 ? (
            <div className="text-center py-12">
              <svg
                className="mx-auto h-12 w-12 text-gray-400"
                fill="none"
                viewBox="0 0 24 24"
                stroke="currentColor"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4"
                />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Şirket bulunamadı</h3>
              <p className="mt-1 text-sm text-gray-500">
                Arama kriterlerinize uygun şirket bulunamadı.
              </p>
            </div>
          ) : (
            filteredCompanies?.map((company) => (
              <div
                key={company._id}
                className="bg-white shadow rounded-lg overflow-hidden hover:shadow-md transition-shadow duration-200"
              >
                <div className="p-6">
                  <div className="flex items-center">
                    {company.logo && (
                      <img
                        src={company.logo}
                        alt={`${company.name} logo`}
                        className="h-16 w-16 object-contain rounded-lg"
                      />
                    )}
                    <div className="ml-4">
                      <h3 className="text-lg font-medium text-gray-900">
                        {company.name}
                      </h3>
                      <p className="mt-1 text-sm text-gray-500">
                        {company.industry} • {company.size} • {company.location}
                      </p>
                    </div>
                  </div>
                  <p className="mt-4 text-gray-500">{company.description}</p>
                  <div className="mt-4 flex flex-wrap gap-2">
                    <a
                      href={company.website}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-indigo-100 text-indigo-800 hover:bg-indigo-200"
                    >
                      Website
                    </a>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-gray-100 text-gray-800">
                      {company.founded} yılından beri
                    </span>
                  </div>
                  {company.jobs && company.jobs.length > 0 && (
                    <div className="mt-6">
                      <h4 className="text-sm font-medium text-gray-900">Açık Pozisyonlar</h4>
                      <div className="mt-2 space-y-2">
                        {company.jobs.map((job) => (
                          <a
                            key={job._id}
                            href={`/jobs/${job._id}`}
                            className="block p-3 bg-gray-50 rounded-md hover:bg-gray-100"
                          >
                            <div className="flex items-center justify-between">
                              <div>
                                <p className="text-sm font-medium text-gray-900">{job.title}</p>
                                <p className="text-sm text-gray-500">
                                  {job.type} • {job.location}
                                </p>
                              </div>
                              <p className="text-sm text-gray-500">
                                {formatDistanceToNow(new Date(job.postedAt), { addSuffix: true, locale: tr })}
                              </p>
                            </div>
                          </a>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default Companies; 