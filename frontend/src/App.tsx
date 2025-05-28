import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider } from './contexts/AuthContext';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';

// Page Components (Lazy loading for better performance)
const HomePage = lazy(() => import('./pages/Home'));
const LoginPage = lazy(() => import('./pages/Login'));
const RegisterPage = lazy(() => import('./pages/Register'));
const JobsListPage = lazy(() => import('./pages/JobsList'));
const JobDetailPage = lazy(() => import('./pages/JobDetailPage'));
const UserProfilePage = lazy(() => import('./pages/UserProfile'));
const ResumeUploadPage = lazy(() => import('./pages/ResumeUpload'));
const AIQuestionHelperPage = lazy(() => import('./pages/AIQuestionHelper'));
const StatusPage = lazy(() => import('./pages/Status'));
const TermsConditionsPage = lazy(() => import('./pages/TermsConditions'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicy'));
const CompaniesPage = lazy(() => import('./pages/Companies'));
const PricingPage = lazy(() => import('./pages/Pricing'));
const HelpPage = lazy(() => import('./pages/Help'));
const ApplicationsPage = lazy(() => import('./pages/Applications'));

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
                <Route path="/jobs" element={<JobsListPage />} />
                <Route path="/jobs/:id" element={<JobDetailPage />} />
                <Route path="/companies" element={<CompaniesPage />} />
                <Route path="/status" element={<StatusPage />} />
                <Route path="/pricing" element={<PricingPage />} />
                <Route path="/terms" element={<TermsConditionsPage />} />
                <Route path="/privacy" element={<PrivacyPolicyPage />} />
                <Route path="/help" element={<HelpPage />} />

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
                  path="/ai-helper"
                  element={
                    <ProtectedRoute>
                      <AIQuestionHelperPage />
                    </ProtectedRoute>
                  }
                />

                {/* Fallback for unmatched routes */}
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </Suspense>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
