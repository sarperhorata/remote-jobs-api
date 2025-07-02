import React from 'react';

interface QuickSearchButtonProps {
  title: string;
  onClick: () => void;
}

const QuickSearchButton: React.FC<QuickSearchButtonProps> = ({ title, onClick }) => {
  return (
    <button
      onClick={onClick}
      className="px-4 py-2 bg-white dark:bg-slate-800 border border-gray-200 dark:border-slate-600 rounded-lg hover:bg-blue-50 dark:hover:bg-slate-700 hover:border-blue-300 dark:hover:border-blue-500 transition-colors duration-200 text-sm font-medium text-gray-700 dark:text-gray-300 hover:text-blue-600 dark:hover:text-blue-400"
    >
      {title}
    </button>
  );
};

export default QuickSearchButton; 