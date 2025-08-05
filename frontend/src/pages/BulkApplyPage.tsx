import React from 'react';
import { Helmet } from 'react-helmet-async';
import BulkApplyManager from '../components/BulkApplyManager';
import { useAuth } from '../contexts/AuthContext';

const BulkApplyPage: React.FC = () => {
  const { user } = useAuth();

  return (
    <>
      <Helmet>
        <title>Bulk Job Application - Buzz2Remote</title>
        <meta name="description" content="Apply to multiple jobs automatically with our intelligent bulk application system. Save time and increase your chances of getting hired." />
        <meta name="keywords" content="bulk job application, automatic job application, multiple job apply, job search automation" />
      </Helmet>

      <div className="min-h-screen bg-gradient-to-br from-purple-50 via-white to-blue-50">
        <div className="container mx-auto px-4 py-8">
          <div className="max-w-6xl mx-auto">
            {/* Header */}
            <div className="text-center mb-8">
              <h1 className="text-4xl font-bold text-gray-900 mb-4">
                Bulk Job Application
              </h1>
              <p className="text-xl text-gray-600 max-w-3xl mx-auto">
                Apply to multiple jobs automatically with our intelligent form filling system. 
                Save time and increase your chances of getting hired.
              </p>
            </div>

            {/* Features */}
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Selection</h3>
                <p className="text-gray-600">Select multiple jobs that match your profile and preferences</p>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v10a2 2 0 002 2h8a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Auto Fill Forms</h3>
                <p className="text-gray-600">Automatically fill application forms using your profile data</p>
              </div>

              <div className="bg-white rounded-xl p-6 shadow-lg border border-gray-100">
                <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center mb-4">
                  <svg className="w-6 h-6 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                  </svg>
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Queue</h3>
                <p className="text-gray-600">Intelligent rate limiting and error handling for optimal results</p>
              </div>
            </div>

            {/* Main Component */}
            <div className="bg-white rounded-2xl shadow-xl border border-gray-100 overflow-hidden">
              <BulkApplyManager />
            </div>

            {/* User Info */}
            {user && (
              <div className="mt-8 bg-blue-50 rounded-xl p-6 border border-blue-200">
                <div className="flex items-center gap-4">
                  <div className="w-12 h-12 bg-blue-100 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                    </svg>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-900">
                      Welcome back, {user.name || user.email}!
                    </h3>
                    <p className="text-gray-600">
                      Your profile data will be used to automatically fill application forms.
                    </p>
                  </div>
                </div>
              </div>
            )}

            {/* Tips */}
            <div className="mt-8 bg-yellow-50 rounded-xl p-6 border border-yellow-200">
              <div className="flex items-start gap-4">
                <div className="w-8 h-8 bg-yellow-100 rounded-full flex items-center justify-center flex-shrink-0 mt-1">
                  <svg className="w-5 h-5 text-yellow-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <div>
                  <h3 className="text-lg font-semibold text-gray-900 mb-2">Pro Tips</h3>
                  <ul className="text-gray-700 space-y-1">
                    <li>• Update your profile and resume before starting bulk applications</li>
                    <li>• Review each job description to ensure it matches your skills</li>
                    <li>• Monitor the application progress and handle any errors manually</li>
                    <li>• Keep track of your applications in the My Applications section</li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default BulkApplyPage; 