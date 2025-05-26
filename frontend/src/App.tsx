import React, { Suspense, lazy } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import Home from './pages/Home';
import Jobs from './pages/Jobs';
import JobDetail from './pages/JobDetail';
import Profile from './pages/Profile';
import Status from './pages/Status';
import Login from './pages/Login';
import Signup from './pages/Signup';
import Pricing from './pages/Pricing';
import Admin from './pages/Admin';
import Docs from './pages/Docs';
import Navigation from './components/Navigation';
import Header from './components/Header';
import ProtectedRoute from './components/ProtectedRoute';
import { ThemeProvider } from './contexts/ThemeContext';
import './App.css';

// Layouts (Eğer varsa, yoksa direkt sayfaları çağırın)
// import MainLayout from './components/Layout/MainLayout'; 

// Page Components (Lazy loading for better performance)
const HomePage = lazy(() => import('./pages/Home'));
const LoginPage = lazy(() => import('./pages/Login'));
const RegisterPage = lazy(() => import('./pages/Signup'));
const JobsListPage = lazy(() => import('./pages/JobsList'));
const JobDetailPage = lazy(() => import('./pages/JobDetailPage'));
const UserProfilePage = lazy(() => import('./pages/UserProfile'));
const ResumeUploadPage = lazy(() => import('./pages/ResumeUpload'));
const AIQuestionHelperPage = lazy(() => import('./pages/AIQuestionHelper'));
const StatusPage = lazy(() => import('./pages/Status'));
const TermsConditionsPage = lazy(() => import('./pages/TermsConditions'));
const PrivacyPolicyPage = lazy(() => import('./pages/PrivacyPolicy'));
const CompaniesPage = lazy(() => import('./pages/Companies')); // Assuming you'll create this
const PricingPage = lazy(() => import('./pages/Pricing'));   // Assuming you'll create this
const HelpPage = lazy(() => import('./pages/Help'));       // Assuming you'll create this
const ApplicationsPage = lazy(() => import('./pages/Applications')); // Assuming you'll create this

// Admin Pages (Example)
// const AdminDashboard = lazy(() => import('./pages/Admin/Dashboard'));

const queryClient = new QueryClient();

interface ProtectedRouteProps {
  children: JSX.Element;
}

const ProtectedRoute: React.FC<ProtectedRouteProps> = ({ children }) => {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return <div>Loading authentication status...</div>; // Or a proper spinner component
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <Router>
            <Suspense fallback={<div>Loading page...</div>}> {/* Global fallback for lazy loaded components */}
              {/* <MainLayout> Optional: If you have a consistent layout across pages */}
              <Routes>
                {/* Public Routes */}
                <Route path="/" element={<HomePage />} />
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/jobs" element={<JobsListPage />} />
                <Route path="/jobs/:id" element={<JobDetailPage />} />
                <Route path="/companies" element={<CompaniesPage />} /> {/* Placeholder */}
                <Route path="/status" element={<StatusPage />} />
                <Route path="/pricing" element={<PricingPage />} /> {/* Placeholder */}
                <Route path="/terms" element={<TermsConditionsPage />} />
                <Route path="/privacy" element={<PrivacyPolicyPage />} />
                <Route path="/help" element={<HelpPage />} /> {/* Placeholder */}

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
                
                {/* Example Admin Route */}
                {/* <Route 
                  path="/admin/dashboard" 
                  element={
                    <ProtectedRoute>
                      <AdminDashboard />
                    </ProtectedRoute>
                  }
                /> */}

                {/* Fallback for unmatched routes */}
                <Route path="*" element={<Navigate to="/" replace />} /> 
              </Routes>
              {/* </MainLayout> */}
            </Suspense>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
