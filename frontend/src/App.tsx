import React, { Suspense, lazy, useEffect } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { HelmetProvider } from 'react-helmet-async';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';
import { AuthCallback } from './pages/AuthCallback';
import { AuthError } from './pages/AuthError';
import { NotFound } from './pages/NotFound';
import PaymentSuccess from './pages/PaymentSuccess';
import { Toaster } from 'react-hot-toast';
import AutocompleteTest from './pages/AutocompleteTest';
import { LazyRoute, PageLoadingSkeleton } from './components/LazyComponent';
import { initializeBundleOptimization, bundleTracker } from './utils/bundleOptimization';

// Critical pages (loaded immediately)
const HomePage = lazy(() => import('./pages/Home'));
const LoginPage = lazy(() => import('./pages/Login'));
const RegisterPage = lazy(() => import('./pages/Register'));

// Secondary pages (loaded on demand)
const JobDetailPage = lazy(() => import('./pages/JobDetailPage'));
const JobSearchResultsPage = lazy(() => import('./pages/JobSearchResults'));
const UserProfilePage = lazy(() => import('./pages/UserProfile'));
const MyProfilePage = lazy(() => import('./pages/MyProfile'));
const ResumeUploadPage = lazy(() => import('./pages/ResumeUpload'));

// Static pages (lowest priority)
const TermsConditionsPage = lazy(() => import('./pages/TermsConditions'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicy'));
const CookiePolicyPage = lazy(() => import('./pages/CookiePolicy'));
const PricingPage = lazy(() => import('./pages/Pricing'));
const SalaryGuidePage = lazy(() => import('./pages/SalaryGuide'));
const HelpPage = lazy(() => import('./pages/Help'));
const RemoteTipsPage = lazy(() => import('./pages/RemoteTips'));
const CareerTipsPage = lazy(() => import('./pages/CareerTips'));
const AboutPage = lazy(() => import('./pages/About'));
const ContactPage = lazy(() => import('./pages/Contact'));
const VisaSponsorshipPage = lazy(() => import('./pages/VisaSponsorship'));
const RelocationGuidePage = lazy(() => import('./pages/RelocationGuide'));

// User-specific pages
const ApplicationsPage = lazy(() => import('./pages/Applications'));
const MyApplicationsPage = lazy(() => import('./pages/MyApplications'));
const FavoritesPage = lazy(() => import('./pages/Favorites'));
const ExternalAPIServicesPage = lazy(() => import('./pages/ExternalAPIServices'));
const SettingsPage = lazy(() => import('./pages/Settings'));

// Auth callback pages
const GoogleCallbackPage = lazy(() => import('./pages/GoogleCallback'));
const LinkedInCallbackPage = lazy(() => import('./pages/LinkedInCallback'));

// Onboarding Pages
const CheckEmailPage = lazy(() => import('./pages/CheckEmail'));
const EmailVerificationPage = lazy(() => import('./pages/EmailVerification'));
const SetPasswordPage = lazy(() => import('./pages/SetPassword'));
const OnboardingProfileSetupPage = lazy(() => import('./pages/OnboardingProfileSetup'));
const OnboardingCompleteProfilePage = lazy(() => import('./pages/OnboardingCompleteProfile'));

// Auth Pages
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPassword'));
const ResetPasswordPage = lazy(() => import('./pages/ResetPassword'));

// Optimized QueryClient with better cache management
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 5 * 60 * 1000, // 5 minutes
      cacheTime: 10 * 60 * 1000, // 10 minutes
      retry: 2,
      refetchOnWindowFocus: false,
    },
  },
});

const App: React.FC = () => {
  useEffect(() => {
    // Initialize bundle optimization
    initializeBundleOptimization();
    
    // Track initial page load
    bundleTracker.trackPageLoad('App');
  }, []);

  return (
    <HelmetProvider>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ThemeProvider>
            <Router future={{ v7_relativeSplatPath: true, v7_startTransition: true }}>
              <Toaster 
                position="top-center" 
                reverseOrder={false}
                toastOptions={{
                  duration: 10000,
                  style: {
                    background: '#1f2937',
                    color: '#f3f4f6',
                    border: '1px solid #374151',
                    borderRadius: '8px',
                    fontSize: '14px',
                    fontWeight: '500',
                    maxWidth: '500px',
                  },
                  success: {
                    style: {
                      background: '#065f46',
                      color: '#d1fae5',
                      border: '1px solid #047857',
                    },
                  },
                  error: {
                    style: {
                      background: '#7f1d1d',
                      color: '#fed7d7',
                      border: '1px solid #dc2626',
                    },
                  },
                }}
              />
              
              <Routes>
                {/* Critical routes with optimized loading */}
                <Route path="/" element={<LazyRoute component={HomePage} />} />
                <Route path="/login" element={<LazyRoute component={LoginPage} />} />
                <Route path="/register" element={<LazyRoute component={RegisterPage} />} />
                
                {/* Job-related routes */}
                <Route path="/jobs" element={<LazyRoute component={JobSearchResultsPage} />} />
                <Route path="/jobs/:id" element={<LazyRoute component={JobDetailPage} />} />
                <Route path="/job/:id" element={<LazyRoute component={JobDetailPage} />} />
                <Route path="/search" element={<LazyRoute component={JobSearchResultsPage} />} />
                
                {/* User routes with authentication */}
                <Route path="/profile" element={
                  <ProtectedRoute>
                    <LazyRoute component={UserProfilePage} />
                  </ProtectedRoute>
                } />
                <Route path="/myprofile" element={
                  <ProtectedRoute>
                    <LazyRoute component={MyProfilePage} />
                  </ProtectedRoute>
                } />
                <Route path="/resume-upload" element={
                  <ProtectedRoute>
                    <LazyRoute component={ResumeUploadPage} />
                  </ProtectedRoute>
                } />
                <Route path="/applications" element={
                  <ProtectedRoute>
                    <LazyRoute component={ApplicationsPage} />
                  </ProtectedRoute>
                } />
                <Route path="/my-applications" element={
                  <ProtectedRoute>
                    <LazyRoute component={MyApplicationsPage} />
                  </ProtectedRoute>
                } />
                <Route path="/favorites" element={
                  <ProtectedRoute>
                    <LazyRoute component={FavoritesPage} />
                  </ProtectedRoute>
                } />
                <Route path="/settings" element={
                  <ProtectedRoute>
                    <LazyRoute component={SettingsPage} />
                  </ProtectedRoute>
                } />
                
                {/* Static pages with lower priority loading */}
                <Route path="/pricing" element={<LazyRoute component={PricingPage} />} />
                <Route path="/salary-guide" element={<LazyRoute component={SalaryGuidePage} />} />
                <Route path="/help" element={<LazyRoute component={HelpPage} />} />
                <Route path="/remote-tips" element={<LazyRoute component={RemoteTipsPage} />} />
                <Route path="/career-tips" element={<LazyRoute component={CareerTipsPage} />} />
                <Route path="/about" element={<LazyRoute component={AboutPage} />} />
                <Route path="/contact" element={<LazyRoute component={ContactPage} />} />
                <Route path="/visa-sponsorship" element={<LazyRoute component={VisaSponsorshipPage} />} />
                <Route path="/relocation-guide" element={<LazyRoute component={RelocationGuidePage} />} />
                
                {/* Legal pages */}
                <Route path="/terms" element={<LazyRoute component={TermsConditionsPage} />} />
                <Route path="/privacy" element={<LazyRoute component={PrivacyPolicyPage} />} />
                <Route path="/cookies" element={<LazyRoute component={CookiePolicyPage} />} />
                
                {/* Auth flow pages */}
                <Route path="/auth/callback" element={<AuthCallback />} />
                <Route path="/auth/error" element={<AuthError />} />
                <Route path="/auth/google/callback" element={<LazyRoute component={GoogleCallbackPage} />} />
                <Route path="/auth/linkedin/callback" element={<LazyRoute component={LinkedInCallbackPage} />} />
                <Route path="/forgot-password" element={<LazyRoute component={ForgotPasswordPage} />} />
                <Route path="/reset-password" element={<LazyRoute component={ResetPasswordPage} />} />
                
                {/* Onboarding flow */}
                <Route path="/check-email" element={<LazyRoute component={CheckEmailPage} />} />
                <Route path="/verify-email" element={<LazyRoute component={EmailVerificationPage} />} />
                <Route path="/set-password" element={<LazyRoute component={SetPasswordPage} />} />
                <Route path="/onboarding/profile-setup" element={<LazyRoute component={OnboardingProfileSetupPage} />} />
                <Route path="/onboarding/complete-profile" element={<LazyRoute component={OnboardingCompleteProfilePage} />} />
                
                {/* Payment and external services */}
                <Route path="/payment/success" element={<PaymentSuccess />} />
                <Route path="/external-api-services" element={
                  <ProtectedRoute>
                    <LazyRoute component={ExternalAPIServicesPage} />
                  </ProtectedRoute>
                } />
                
                {/* Test routes */}
                <Route path="/autocomplete-test" element={<AutocompleteTest />} />
                
                {/* 404 page */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Router>
          </ThemeProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
};

export default App;
