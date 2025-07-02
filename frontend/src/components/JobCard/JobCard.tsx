import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../../contexts/AuthContext';
import { Job } from '../../types/job';

interface JobCardProps {
  job: Job;
  onJobClick?: (job: Job) => void;
  onAuthRequired?: () => void;
  isHidden?: boolean;
  onHide?: () => void;
  onReveal?: () => void;
}

interface ToastProps {
  message: string;
  onClose: () => void;
}

const Toast: React.FC<ToastProps> = ({ message, onClose }) => {
  React.useEffect(() => {
    const timer = setTimeout(() => {
      onClose();
    }, 10000); // 10 seconds

    return () => clearTimeout(timer);
  }, [onClose]);

  return (
    <div className="fixed top-4 right-4 bg-orange-500 text-white px-6 py-3 rounded-lg shadow-lg z-50 max-w-sm">
      <div className="flex items-center justify-between">
        <span className="text-sm font-medium">{message}</span>
        <button 
          onClick={onClose}
          className="ml-4 text-white hover:text-gray-200"
        >
          ×
        </button>
      </div>
    </div>
  );
};

const JobCard: React.FC<JobCardProps> = ({ 
  job, 
  onAuthRequired, 
  isHidden = false,
  onHide,
  onReveal 
}) => {
  const { user } = useAuth();
  const [isFavorited, setIsFavorited] = useState(false);
  const [showToast, setShowToast] = useState(false);

  // Helper function to get company name
  const getCompanyName = () => {
    if (typeof job.company === 'string') {
      return job.company;
    }
    return job.company?.name || job.companyName || 'Unknown Company';
  };

  // Helper function to get company logo
  const getCompanyLogo = () => {
    if (typeof job.company === 'object' && job.company?.logo) {
      return job.company.logo;
    }
    return job.company_logo || job.companyLogo;
  };

  const handleFavoriteClick = () => {
    if (!user) {
      // Show toast and trigger auth modal
      setShowToast(true);
      if (onAuthRequired) {
        onAuthRequired();
      }
      return;
    }

    // Toggle favorite status
    setIsFavorited(!isFavorited);
    
    // TODO: Call API to save/remove from favorites
    console.log('Favorite clicked for job:', job._id || job.id);
  };

  const handleHideReveal = () => {
    if (isHidden && onReveal) {
      onReveal();
    } else if (!isHidden && onHide) {
      onHide();
    }
  };

  const companyLogo = getCompanyLogo();

  return (
    <>
      {showToast && (
        <Toast 
          message="You have to be signed in to add a job to favorites!"
          onClose={() => setShowToast(false)}
        />
      )}
      
      <div className={`bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition ${isHidden ? 'opacity-50' : ''}`}>
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-start">
            {companyLogo && (
              <img 
                src={companyLogo} 
                alt={getCompanyName()} 
                className="w-12 h-12 rounded-full mr-4"
              />
            )}
            <div>
              <h3 className="font-semibold text-lg">{job.title}</h3>
              <p className="text-gray-600">{getCompanyName()}</p>
            </div>
          </div>
          
          <div className="flex gap-2">
            {/* Hide/Reveal Button */}
            {(onHide || onReveal) && (
              <button
                onClick={handleHideReveal}
                className={`p-2 rounded-full transition-colors ${
                  isHidden 
                    ? 'text-green-500 hover:text-green-600' 
                    : 'text-gray-400 hover:text-gray-600'
                }`}
                title={isHidden ? 'Show job' : 'Hide job'}
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  {isHidden ? (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  ) : (
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.878 9.878L3 3m6.878 6.878L21 21" />
                  )}
                </svg>
              </button>
            )}
            
            {/* Favorite Button */}
            <button
              onClick={handleFavoriteClick}
              className={`p-2 rounded-full transition-colors ${
                isFavorited 
                  ? 'text-yellow-500 hover:text-yellow-600' 
                  : 'text-gray-400 hover:text-yellow-500'
              }`}
              title={isFavorited ? 'Remove from favorites' : 'Add to favorites'}
            >
              <svg 
                className="w-5 h-5" 
                fill={isFavorited ? 'currentColor' : 'none'} 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path 
                  strokeLinecap="round" 
                  strokeLinejoin="round" 
                  strokeWidth={2} 
                  d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" 
                />
              </svg>
            </button>
          </div>
        </div>
        
        <div className="flex flex-wrap gap-2 mb-4">
          <span className="text-sm text-gray-500">{job.location}</span>
          <span className="text-sm text-gray-500">•</span>
          <span className="text-sm text-gray-500">{job.job_type}</span>
        </div>
        
        <div className="flex flex-wrap gap-2 mb-4">
          {job.skills?.slice(0, 3).map(skill => (
            <span 
              key={skill} 
              className="bg-blue-100 text-blue-800 text-xs px-2 py-1 rounded"
            >
              {skill}
            </span>
          ))}
          {job.skills && job.skills.length > 3 && (
            <span className="text-xs text-gray-500">+{job.skills.length - 3} more</span>
          )}
        </div>
        
        <div className="flex justify-between items-center">
          <Link 
            to={`/jobs/${job._id || job.id}`}
            className="text-blue-600 hover:underline"
          >
            View Details
          </Link>
          <span className="text-xs text-gray-500">
            Posted {job.postedAt ? new Date(job.postedAt).toLocaleDateString() : 'Recently'}
          </span>
        </div>
      </div>
    </>
  );
};

export default JobCard; 