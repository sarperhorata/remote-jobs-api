import React from 'react';

const Admin: React.FC = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
          Admin Panel
        </h1>
        
        <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-4">
              Welcome to Buzz2Remote Admin Panel
            </h2>
            <p className="text-gray-600 dark:text-gray-400">
              Access the full admin dashboard and documentation.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 gap-6">
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">
                Admin Dashboard
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Manage users, jobs, and system settings.
              </p>
              <a
                href="/admin/dashboard"
                className="inline-block bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                Open Dashboard
              </a>
            </div>
            
            <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-2">
                API Documentation
              </h3>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Explore the complete API documentation.
              </p>
              <a
                href="/docs"
                className="inline-block bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
              >
                View Docs
              </a>
            </div>
          </div>
          
          <div className="mt-8 border-t border-gray-200 dark:border-gray-700 pt-6">
            <h3 className="text-lg font-medium text-gray-800 dark:text-gray-200 mb-4">
              Quick Stats
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-blue-50 dark:bg-blue-900/30 p-4 rounded-lg">
                <div className="text-2xl font-bold text-blue-600 dark:text-blue-400">
                  21,000+
                </div>
                <div className="text-sm text-blue-800 dark:text-blue-300">
                  Jobs Processed
                </div>
              </div>
              <div className="bg-green-50 dark:bg-green-900/30 p-4 rounded-lg">
                <div className="text-2xl font-bold text-green-600 dark:text-green-400">
                  471+
                </div>
                <div className="text-sm text-green-800 dark:text-green-300">
                  Companies
                </div>
              </div>
              <div className="bg-purple-50 dark:bg-purple-900/30 p-4 rounded-lg">
                <div className="text-2xl font-bold text-purple-600 dark:text-purple-400">
                  99.9%
                </div>
                <div className="text-sm text-purple-800 dark:text-purple-300">
                  Uptime
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Admin; 