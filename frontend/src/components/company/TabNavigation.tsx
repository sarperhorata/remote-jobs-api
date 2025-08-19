import React from 'react';

interface Tab {
  id: string;
  label: string;
  icon?: React.ReactNode;
  count?: number;
}

interface TabNavigationProps {
  tabs: Tab[];
  activeTab: string;
  onTabChange: (tabId: string) => void;
  className?: string;
}

const TabNavigation: React.FC<TabNavigationProps> = ({
  tabs,
  activeTab,
  onTabChange,
  className = ''
}) => {
  return (
    <div className={`border-b border-gray-200 dark:border-gray-700 ${className}`}>
      <nav className="-mb-px flex space-x-8" aria-label="Tabs">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => onTabChange(tab.id)}
            className={`
              group relative min-w-0 flex-1 overflow-hidden py-4 px-1 text-center text-sm font-medium hover:text-gray-700 dark:hover:text-gray-300 focus:z-10 focus:outline-none
              ${
                activeTab === tab.id
                  ? 'border-b-2 border-blue-500 text-blue-600 dark:text-blue-400'
                  : 'border-b-2 border-transparent text-gray-500 dark:text-gray-400 hover:border-gray-300 dark:hover:border-gray-600'
              }
            `}
          >
            <div className="flex items-center justify-center space-x-2">
              {tab.icon && <span className="flex-shrink-0">{tab.icon}</span>}
              <span className="truncate">{tab.label}</span>
              {tab.count !== undefined && (
                <span
                  className={`
                    ml-2 rounded-full py-0.5 px-2.5 text-xs font-medium
                    ${
                      activeTab === tab.id
                        ? 'bg-blue-100 text-blue-600 dark:bg-blue-900 dark:text-blue-400'
                        : 'bg-gray-100 text-gray-900 dark:bg-gray-700 dark:text-gray-300'
                    }
                  `}
                >
                  {tab.count}
                </span>
              )}
            </div>
            <span
              aria-hidden="true"
              className={`
                absolute inset-x-0 bottom-0 h-0.5
                ${
                  activeTab === tab.id
                    ? 'bg-blue-500'
                    : 'bg-transparent'
                }
              `}
            />
          </button>
        ))}
      </nav>
    </div>
  );
};

export default TabNavigation; 