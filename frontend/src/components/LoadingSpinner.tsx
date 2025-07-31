import React from 'react';

interface LoadingSpinnerProps {
  size?: 'sm' | 'md' | 'lg' | 'xl';
  color?: 'blue' | 'green' | 'red';
  text?: string;
  className?: string;
  fullScreen?: boolean;
}

export const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'md',
  color = 'blue',
  text,
  className = '',
  fullScreen = false
}) => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-6 h-6',
    lg: 'w-8 h-8',
    xl: 'w-12 h-12'
  };

  const colorClasses = {
    blue: 'text-blue-500',
    green: 'text-green-500',
    red: 'text-red-500'
  };

  const spinner = (
    <div
      role="status"
      aria-label={text || 'Loading...'}
      aria-live="polite"
      className={`animate-spin rounded-full border-b-2 ${sizeClasses[size]} ${colorClasses[color]} ${className}`}
    />
  );

  if (fullScreen) {
    return (
      <div
        data-testid="loading-overlay"
        className="fixed inset-0 bg-black bg-opacity-50 flex justify-center items-center z-50"
      >
        <div className="flex flex-col items-center space-y-4">
          {spinner}
          {text && <p className="text-white">{text}</p>}
        </div>
      </div>
    );
  }

  return (
    <div className="flex justify-center items-center py-8">
      <div className="flex flex-col items-center space-y-4">
        {spinner}
        {text && <p className="text-gray-600">{text}</p>}
      </div>
    </div>
  );
}; 