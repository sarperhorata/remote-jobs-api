import React from 'react';
import { 
  Building2, 
  MapPin, 
  Globe, 
  Users, 
  Calendar,
  Star,
  ExternalLink,
  Mail,
  Phone
} from 'lucide-react';

interface Company {
  _id: string;
  name: string;
  logo?: string;
  website?: string;
  location?: string;
  industry?: string;
  founded?: string;
  size?: string;
  description?: string;
  rating?: number;
  reviewCount?: number;
  email?: string;
  phone?: string;
}

interface CompanyHeaderProps {
  company: Company;
  className?: string;
}

const CompanyHeader: React.FC<CompanyHeaderProps> = ({ company, className = '' }) => {
  const formatFoundedYear = (founded: string) => {
    if (!founded) return '';
    const year = new Date(founded).getFullYear();
    return `Founded ${year}`;
  };

  const formatRating = (rating: number) => {
    return rating.toFixed(1);
  };

  return (
    <div className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm border border-gray-200 dark:border-gray-700 ${className}`}>
      <div className="p-6">
        <div className="flex flex-col lg:flex-row lg:items-start lg:justify-between">
          {/* Company Info */}
          <div className="flex-1">
            <div className="flex items-start space-x-4">
              {/* Logo */}
              <div className="flex-shrink-0">
                {company.logo ? (
                  <img
                    src={company.logo}
                    alt={`${company.name} logo`}
                    className="w-16 h-16 rounded-lg object-cover border border-gray-200 dark:border-gray-600"
                  />
                ) : (
                  <div className="w-16 h-16 rounded-lg bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center">
                    <Building2 className="w-8 h-8 text-white" />
                  </div>
                )}
              </div>

              {/* Company Details */}
              <div className="flex-1 min-w-0">
                <div className="flex items-center space-x-3 mb-2">
                  <h1 className="text-2xl font-bold text-gray-900 dark:text-white truncate">
                    {company.name}
                  </h1>
                  {company.rating && (
                    <div className="flex items-center space-x-1">
                      <Star className="w-4 h-4 text-yellow-400 fill-current" />
                      <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                        {formatRating(company.rating)}
                      </span>
                      {company.reviewCount && (
                        <span className="text-sm text-gray-500 dark:text-gray-400">
                          ({company.reviewCount} reviews)
                        </span>
                      )}
                    </div>
                  )}
                </div>

                {/* Company Meta */}
                <div className="flex flex-wrap items-center gap-4 text-sm text-gray-600 dark:text-gray-400 mb-3">
                  {company.industry && (
                    <div className="flex items-center space-x-1">
                      <Building2 className="w-4 h-4" />
                      <span>{company.industry}</span>
                    </div>
                  )}
                  {company.location && (
                    <div className="flex items-center space-x-1">
                      <MapPin className="w-4 h-4" />
                      <span>{company.location}</span>
                    </div>
                  )}
                  {company.size && (
                    <div className="flex items-center space-x-1">
                      <Users className="w-4 h-4" />
                      <span>{company.size}</span>
                    </div>
                  )}
                  {company.founded && (
                    <div className="flex items-center space-x-1">
                      <Calendar className="w-4 h-4" />
                      <span>{formatFoundedYear(company.founded)}</span>
                    </div>
                  )}
                </div>

                {/* Description */}
                {company.description && (
                  <p className="text-gray-700 dark:text-gray-300 text-sm leading-relaxed">
                    {company.description}
                  </p>
                )}
              </div>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex flex-col space-y-3 mt-4 lg:mt-0 lg:ml-6">
            {company.website && (
              <a
                href={company.website}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Globe className="w-4 h-4 mr-2" />
                Visit Website
                <ExternalLink className="w-3 h-3 ml-1" />
              </a>
            )}
            
            {company.email && (
              <a
                href={`mailto:${company.email}`}
                className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Mail className="w-4 h-4 mr-2" />
                Contact
              </a>
            )}

            {company.phone && (
              <a
                href={`tel:${company.phone}`}
                className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
              >
                <Phone className="w-4 h-4 mr-2" />
                Call
              </a>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CompanyHeader; 