import React, { Suspense, lazy } from 'react';
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
// TestAutocomplete removed

// Page Components (Lazy loading for better performance)
const HomePage = lazy(() => import('./pages/Home'));
const LoginPage = lazy(() => import('./pages/Login'));
const RegisterPage = lazy(() => import('./pages/Register'));

const JobDetailPage = lazy(() => import('./pages/JobDetailPage'));
const JobSearchResultsPage = lazy(() => import('./pages/JobSearchResults'));
const UserProfilePage = lazy(() => import('./pages/UserProfile'));
const MyProfilePage = lazy(() => import('./pages/MyProfile'));
const ResumeUploadPage = lazy(() => import('./pages/ResumeUpload'));
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
const ApplicationsPage = lazy(() => import('./pages/Applications'));
const MyApplicationsPage = lazy(() => import('./pages/MyApplications'));
const FavoritesPage = lazy(() => import('./pages/Favorites'));
const ExternalAPIServicesPage = lazy(() => import('./pages/ExternalAPIServices'));
const SettingsPage = lazy(() => import('./pages/Settings'));
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

const queryClient = new QueryClient();

const App: React.FC = () => {
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
                      border: '1px solid #10b981',
                    },
                    iconTheme: {
                      primary: '#10b981',
                      secondary: '#d1fae5',
                    },
                  },
                  error: {
                    style: {
                      background: '#7f1d1d',
                      color: '#fecaca',
                      border: '1px solid #ef4444',
                    },
                    iconTheme: {
                      primary: '#ef4444',
                      secondary: '#fecaca',
                    },
                  },
                }}
              />
              <Suspense fallback={<div className="flex justify-center items-center h-screen text-xl font-semibold">Loading Buzz2Remote...</div>}>
                <Routes>
                  {/* Public Routes */}
                  <Route path="/" element={<HomePage />} />
                  <Route path="/login" element={<LoginPage />} />
                  <Route path="/register" element={<RegisterPage />} />
                  
                  <Route path="/jobs/:id" element={<JobDetailPage />} />
                  <Route path="/jobs/search" element={<JobSearchResultsPage />} />
                  
                  <Route path="/pricing" element={<PricingPage />} />
                  <Route path="/salary-guide" element={<SalaryGuidePage />} />
                  <Route path="/terms" element={<TermsConditionsPage />} />
                  <Route path="/terms-conditions" element={<TermsConditionsPage />} />
                  <Route path="/privacy" element={<PrivacyPolicyPage />} />
                  <Route path="/privacy-policy" element={<PrivacyPolicyPage />} />
                  <Route path="/cookie-policy" element={<CookiePolicyPage />} />
                  <Route path="/help" element={<HelpPage />} />
                  <Route path="/remote-tips" element={<RemoteTipsPage />} />
                  <Route path="/career-tips" element={<CareerTipsPage />} />
                  <Route path="/about" element={<AboutPage />} />
                  <Route path="/contact" element={<ContactPage />} />
                  <Route path="/visa-sponsorship" element={<VisaSponsorshipPage />} />
                  <Route path="/relocation-guide" element={<RelocationGuidePage />} />
                  <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
                  <Route path="/auth/linkedin/callback" element={<LinkedInCallbackPage />} />
                  <Route path="/auth/callback" element={<AuthCallback />} />
                  <Route path="/auth/error" element={<AuthError />} />
                  <Route path="/payment/success" element={<PaymentSuccess />} />
                  <Route path="/autocomplete-test" element={<AutocompleteTest />} />

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
                    path="/my-profile" 
                    element={
                      <ProtectedRoute>
                        <MyProfilePage />
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
                    path="/favorites" 
                    element={
                      <ProtectedRoute>
                        <FavoritesPage />
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
                    path="/my-applications" 
                    element={
                      <ProtectedRoute>
                        <MyApplicationsPage />
                      </ProtectedRoute>
                    }
                  />
                  <Route 
                    path="/settings" 
                    element={
                      <ProtectedRoute>
                        <SettingsPage />
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

                  {/* Testing Routes */}
                  <Route path="/autocomplete-test" element={<AutocompleteTest />} />
                  {/* TestAutocomplete route removed */}

                  {/* Fallback for unmatched routes */}
                  <Route path="*" element={<NotFound />} />
                </Routes>
              </Suspense>
            </Router>
          </ThemeProvider>
        </AuthProvider>
      </QueryClientProvider>
    </HelmetProvider>
  );
};

export default App;
