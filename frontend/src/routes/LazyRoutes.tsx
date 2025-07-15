import React, { Suspense, lazy } from 'react';
import { Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';

// Inline lazyWithRetry function to avoid import issues
const lazyWithRetry = <T extends React.ComponentType<any>>(
  componentImport: () => Promise<{ default: T }>,
  retries = 3
): React.ComponentType<any> => {
  return lazy(() => {
    return new Promise<{ default: T }>((resolve, reject) => {
      let attempts = 0;
      
      const attemptImport = async () => {
        try {
          const component = await componentImport();
          resolve(component);
        } catch (error) {
          attempts++;
          if (attempts >= retries) {
            reject(error);
          } else {
            setTimeout(attemptImport, Math.pow(2, attempts) * 1000);
          }
        }
      };
      
      attemptImport();
    });
  });
};

// Inline loading component
const createLoadingComponent = (message = 'Loading...') => () => (
  <div className="flex items-center justify-center p-8">
    <div className="flex items-center space-x-2">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      <span className="text-gray-600">{message}</span>
    </div>
  </div>
);

// Lazy load pages - only existing files
const Home = lazyWithRetry(() => import('../pages/Home'));
const Login = lazyWithRetry(() => import('../pages/Login'));
const Register = lazyWithRetry(() => import('../pages/Register'));
const ForgotPassword = lazyWithRetry(() => import('../pages/ForgotPassword'));
const Jobs = lazyWithRetry(() => import('../pages/Jobs'));
const JobDetailPage = lazyWithRetry(() => import('../pages/JobDetailPage'));
const JobDetail = lazyWithRetry(() => import('../pages/JobDetail'));
const MyApplications = lazyWithRetry(() => import('../pages/MyApplications'));
const Profile = lazyWithRetry(() => import('../pages/Profile'));
const Favorites = lazyWithRetry(() => import('../pages/Favorites'));
const Companies = lazyWithRetry(() => import('../pages/Companies'));
const MyProfile = lazyWithRetry(() => import('../pages/MyProfile'));
const Notifications = lazyWithRetry(() => import('../pages/Notifications'));
const Help = lazyWithRetry(() => import('../pages/Help'));
const CheckEmail = lazyWithRetry(() => import('../pages/CheckEmail'));
const GoogleCallback = lazyWithRetry(() => import('../pages/GoogleCallback'));
const LinkedInCallback = lazyWithRetry(() => import('../pages/LinkedInCallback'));
const Dashboard = lazyWithRetry(() => import('../pages/Dashboard'));
const ResetPassword = lazyWithRetry(() => import('../pages/ResetPassword'));
const PrivacyPolicy = lazyWithRetry(() => import('../pages/PrivacyPolicy'));
const TermsConditions = lazyWithRetry(() => import('../pages/TermsConditions'));
const NotFound = lazyWithRetry(() => import('../pages/NotFound'));
const Pricing = lazyWithRetry(() => import('../pages/Pricing'));
const AdminDashboard = lazyWithRetry(() => import('../pages/AdminDashboard'));
const Admin = lazyWithRetry(() => import('../pages/Admin'));
const OnboardingCompleteProfile = lazyWithRetry(() => import('../pages/OnboardingCompleteProfile'));
const ProfileSetup = lazyWithRetry(() => import('../pages/ProfileSetup'));
const EmailVerification = lazyWithRetry(() => import('../pages/EmailVerification'));

// Loading components for different sections
const PageLoader = () => (
  <div className="min-h-screen flex items-center justify-center">
    <div className="flex items-center space-x-2">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      <span className="text-gray-600">Loading page...</span>
    </div>
  </div>
);

const ComponentLoader = () => (
  <div className="flex items-center justify-center p-4">
    <div className="flex items-center space-x-2">
      <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600"></div>
      <span className="text-gray-600">Loading...</span>
    </div>
  </div>
);

// Error fallback component
const PageErrorFallback = ({ error, resetErrorBoundary }: { error: Error; resetErrorBoundary: () => void }) => (
  <div className="flex flex-col items-center justify-center p-8 text-center min-h-screen">
    <div className="bg-red-50 border border-red-200 rounded-lg p-6 max-w-md">
      <svg
        className="w-12 h-12 text-red-500 mx-auto mb-4"
        fill="none"
        stroke="currentColor"
        viewBox="0 0 24 24"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          strokeWidth={2}
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z"
        />
      </svg>
      <h3 className="text-lg font-semibold text-red-800 mb-2">Error Loading Page</h3>
      <p className="text-red-600 mb-4">Failed to load page. Please try again.</p>
      <button
        onClick={resetErrorBoundary}
        className="px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
      >
        Try Again
      </button>
    </div>
  </div>
);

const LazyRoutes: React.FC = () => {
  return (
    <ErrorBoundary FallbackComponent={PageErrorFallback}>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Home />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/jobs/:id" element={<JobDetailPage />} />
          <Route path="/companies" element={<Companies />} />
          <Route path="/pricing" element={<Pricing />} />
          <Route path="/help" element={<Help />} />
          <Route path="/privacy" element={<PrivacyPolicy />} />
          <Route path="/terms" element={<TermsConditions />} />

          {/* Auth routes */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/forgot-password" element={<ForgotPassword />} />
          <Route path="/reset-password" element={<ResetPassword />} />
          <Route path="/verify-email" element={<CheckEmail />} />

          {/* Protected routes */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/applications" element={<MyApplications />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<MyProfile />} />

          {/* Onboarding */}
          <Route path="/onboarding/complete-profile" element={<OnboardingCompleteProfile />} />
          <Route path="/profile-setup" element={<ProfileSetup />} />

          {/* Admin routes */}
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/admin/*" element={<Admin />} />

          {/* 404 */}
          <Route path="*" element={<NotFound />} />
        </Routes>
      </Suspense>
    </ErrorBoundary>
  );
};

export default LazyRoutes; 