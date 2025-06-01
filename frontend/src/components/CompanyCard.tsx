import React from 'react';
import { Company } from '../types/Company';

interface CompanyCardProps {
  company: Company;
}

export const CompanyCard: React.FC<CompanyCardProps> = ({ company }) => {
  return (
    <div className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start space-x-4">
        <div className="flex-shrink-0">
          {company.logo ? (
            <img
              className="h-12 w-12 rounded-lg object-cover"
              src={company.logo}
              alt={`${company.name} logo`}
            />
          ) : (
            <div className="h-12 w-12 rounded-lg bg-gray-200 flex items-center justify-center">
              <span className="text-gray-500 font-medium text-lg">
                {company.name.charAt(0)}
              </span>
            </div>
          )}
        </div>
        
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold text-gray-900 truncate">
            {company.name}
          </h3>
          <p className="text-sm text-gray-600 mb-2">{company.industry}</p>
          <p className="text-sm text-gray-700 line-clamp-2">
            {company.description}
          </p>
        </div>
      </div>
      
      <div className="mt-4 flex items-center justify-between">
        <div className="flex items-center space-x-4 text-sm text-gray-500">
          <span>{company.size} employees</span>
          <span>{company.location}</span>
        </div>
        
        <div className="flex space-x-2">
          {company.website && (
            <a
              href={company.website}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 hover:text-blue-800 text-sm font-medium"
            >
              Website
            </a>
          )}
        </div>
      </div>
      
      {company.techStack && company.techStack.length > 0 && (
        <div className="mt-4 pt-4 border-t border-gray-200">
          <div className="flex flex-wrap gap-2">
            {company.techStack.slice(0, 5).map((tech) => (
              <span
                key={tech}
                className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
              >
                {tech}
              </span>
            ))}
            {company.techStack.length > 5 && (
              <span className="text-xs text-gray-500">
                +{company.techStack.length - 5} more
              </span>
            )}
          </div>
        </div>
      )}
    </div>
  );
}; 