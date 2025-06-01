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
const UserProfilePage = lazy(() => import('./pages/UserProfile'));
const ResumeUploadPage = lazy(() => import('./pages/ResumeUpload'));
const TermsConditionsPage = lazy(() => import('./pages/TermsConditions'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicy'));

const PricingPage = lazy(() => import('./pages/Pricing'));
const HelpPage = lazy(() => import('./pages/Help'));
const ApplicationsPage = lazy(() => import('./pages/Applications'));
const ExternalAPIServicesPage = lazy(() => import('./pages/ExternalAPIServices'));
const GoogleCallbackPage = lazy(() => import('./pages/GoogleCallback'));

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
                
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/terms" element={<TermsConditionsPage />} />
                <Route path="/privacy" element={<PrivacyPolicyPage />} />
                <Route path="/help" element={<HelpPage />} />
                <Route path="/auth/google/callback" element={<GoogleCallbackPage />} />
                <Route path="/auth/callback" element={<AuthCallback />} />
                <Route path="/auth/error" element={<AuthError />} />
                <Route path="/payment/success" element={<PaymentSuccess />} />

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
