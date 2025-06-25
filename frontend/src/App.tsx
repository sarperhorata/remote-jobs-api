import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';
import { AuthCallback } from './pages/AuthCallback';
import { AuthError } from './pages/AuthError';
import { NotFound } from './pages/NotFound';
import PaymentSuccess from './pages/PaymentSuccess';

// Page Components (Lazy loading for better performance)
const HomePage = lazy(() => import('./pages/Home'));
const LoginPage = lazy(() => import('./pages/Login'));
const RegisterPage = lazy(() => import('./pages/Register'));

const JobDetailPage = lazy(() => import('./pages/JobDetailPage'));
const JobSearchResultsPage = lazy(() => import('./pages/JobSearchResults'));
const UserProfilePage = lazy(() => import('./pages/UserProfile'));
const ResumeUploadPage = lazy(() => import('./pages/ResumeUpload'));
const TermsConditionsPage = lazy(() => import('./pages/TermsConditions'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicy'));

const PricingPage = lazy(() => import('./pages/Pricing'));
const HelpPage = lazy(() => import('./pages/Help'));
const ApplicationsPage = lazy(() => import('./pages/Applications'));
const ExternalAPIServicesPage = lazy(() => import('./pages/ExternalAPIServices'));
const GoogleCallbackPage = lazy(() => import('./pages/GoogleCallback'));

// Onboarding Pages
const CheckEmailPage = lazy(() => import('./pages/CheckEmail'));
const EmailVerificationPage = lazy(() => import('./pages/EmailVerification'));
const SetPasswordPage = lazy(() => import('./pages/SetPassword'));
const OnboardingProfileSetupPage = lazy(() => import('./pages/OnboardingProfileSetup'));
const OnboardingCompleteProfilePage = lazy(() => import('./pages/OnboardingCompleteProfile'));

// Auth Pages
const ForgotPasswordPage = lazy(() => import('./pages/ForgotPassword'));
const ResetPasswordPage = lazy(() => import('./pages/ResetPassword'));

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <Router>
            <Suspense fallback={<div className="flex justify-center items-center h-screen text-xl font-semibold">Loading Buzz2Remote...</div>}>
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                
                <Route path="/jobs/:id" element={<JobDetailPage />} />
                <Route path="/jobs/search" element={<JobSearchResultsPage />} />
                
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/terms" element={<TermsConditionsPage />} />
                <Route path="/terms-conditions" element={<TermsConditionsPage />} />
                <Route path="/privacy" element={<PrivacyPolicyPage />} />
                <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
                <Route path="/help" element={<HelpPage />} />
                <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
                <Route path="/auth/callback" element={<AuthCallback />} />
                <Route path="/auth/error" element={<AuthError />} />
                <Route path="/payment/success" element={<PaymentSuccess />} />

                {/* Auth Routes */}
                <Route path="/forgot-password" element={<ForgotPasswordPage />} />
                <Route path="/reset-password" element={<ResetPasswordPage />} />

                {/* Onboarding Routes */}
                <Route path="/onboarding/check-email" element={<CheckEmailPage />} />
                <Route path="/onboarding/verify-email" element={<EmailVerificationPage />} />
                <Route path="/onboarding/set-password" element={<SetPasswordPage />} />
                <Route path="/onboarding/profile-setup" element={<OnboardingProfileSetupPage />} />
                <Route path="/onboarding/complete-profile" element={<OnboardingCompleteProfilePage />} />

                {/* Protected Routes (Require Authentication) */}
                <Route 
                  path="/profile" 
                  element={
                    <ProtectedRoute>
                      <UserProfilePage />
                    </ProtectedRoute>
                  }
                />
                <Route 
                  path="/profile/resume-upload" 
                  element={
                    <ProtectedRoute>
                      <ResumeUploadPage />
                    </ProtectedRoute>
                  }
                />
                <Route 
                  path="/applications" 
                  element={
                    <ProtectedRoute>
                      <ApplicationsPage />
                    </ProtectedRoute>
                  }
                />
                <Route 
                  path="/admin/external-api-services" 
                  element={
                    <ProtectedRoute>
                      <ExternalAPIServicesPage />
                    </ProtectedRoute>
                  }
                />

                {/* Fallback for unmatched routes */}
                <Route path="*" element={<NotFound />} />
              </Routes>
            </Suspense>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
