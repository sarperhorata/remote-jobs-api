import React, { Suspense } from 'react';
import { Routes, Route } from 'react-router-dom';
import { ErrorBoundary } from 'react-error-boundary';
import { lazyWithRetry, createLoadingComponent, createErrorFallback } from '../utils/lazyUtils';

// Lazy load pages with retry functionality
const Home = lazyWithRetry(() => import('../pages/Home'));
const Jobs = lazyWithRetry(() => import('../pages/Jobs'));
const JobDetail = lazyWithRetry(() => import('../pages/JobDetail'));
const Companies = lazyWithRetry(() => import('../pages/Companies'));
const MyApplications = lazyWithRetry(() => import('../pages/MyApplications'));
const Notifications = lazyWithRetry(() => import('../pages/Notifications'));
const Dashboard = lazyWithRetry(() => import('../pages/Dashboard'));
const Profile = lazyWithRetry(() => import('../pages/Profile'));
const Settings = lazyWithRetry(() => import('../pages/MyProfile'));
const Help = lazyWithRetry(() => import('../pages/Help'));
const Login = lazyWithRetry(() => import('../pages/Login'));
const Register = lazyWithRetry(() => import('../pages/Register'));
const ForgotPassword = lazyWithRetry(() => import('../pages/ForgotPassword'));
const ResetPassword = lazyWithRetry(() => import('../pages/ResetPassword'));
const EmailVerification = lazyWithRetry(() => import('../pages/EmailVerification'));

// Admin pages
const AdminDashboard = lazyWithRetry(() => import('../pages/AdminDashboard'));
const Admin = lazyWithRetry(() => import('../pages/Admin'));

// Onboarding
const OnboardingCompleteProfile = lazyWithRetry(() => import('../pages/OnboardingCompleteProfile'));
const ProfileSetup = lazyWithRetry(() => import('../pages/ProfileSetup'));

// Other pages
const Pricing = lazyWithRetry(() => import('../pages/Pricing'));
const PrivacyPolicy = lazyWithRetry(() => import('../pages/PrivacyPolicy'));
const TermsConditions = lazyWithRetry(() => import('../pages/TermsConditions'));
const NotFound = lazyWithRetry(() => import('../pages/NotFound'));

// Loading components for different sections
const PageLoader = createLoadingComponent('Loading page...', 'min-h-screen flex items-center justify-center');
const ComponentLoader = createLoadingComponent('Loading...', 'flex items-center justify-center p-4');

// Error fallback
const PageErrorFallback = createErrorFallback('Failed to load page. Please try again.');

const LazyRoutes: React.FC = () => {
  return (
    <ErrorBoundary FallbackComponent={PageErrorFallback}>
      <Suspense fallback={<PageLoader />}>
        <Routes>
          {/* Public routes */}
          <Route path="/" element={<Home />} />
          <Route path="/jobs" element={<Jobs />} />
          <Route path="/jobs/:id" element={<JobDetail />} />
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
          <Route path="/verify-email" element={<EmailVerification />} />

          {/* Protected routes */}
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/applications" element={<MyApplications />} />
          <Route path="/notifications" element={<Notifications />} />
          <Route path="/profile" element={<Profile />} />
          <Route path="/settings" element={<Settings />} />

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