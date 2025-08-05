import React, { lazy, Suspense } from 'react';
import { Routes, Route, Navigate } from 'react-router-dom';
import LoadingScreen from '../components/common/LoadingScreen';
import SalaryGuide from '../pages/SalaryGuide';
import VisaSponsorship from '../pages/VisaSponsorship';
import RelocationGuide from '../pages/RelocationGuide';

// Lazy loaded components
const Home = lazy(() => import('../pages/Home'));
const Jobs = lazy(() => import('../pages/Jobs'));
const JobDetail = lazy(() => import('../pages/JobDetail')); 
const Login = lazy(() => import('../pages/Login'));
const Register = lazy(() => import('../pages/Register'));
const Profile = lazy(() => import('../pages/Profile'));
const Settings = lazy(() => import('../pages/Settings'));
const SavedJobs = lazy(() => import('../pages/SavedJobs'));
const Notifications = lazy(() => import('../pages/Notifications'));
const NotFound = lazy(() => import('../pages/NotFound'));
const SearchResults = lazy(() => import('../pages/SearchResults'));
const RemoteTips = lazy(() => import('../pages/RemoteTips'));
const CareerTips = lazy(() => import('../pages/CareerTips'));
const RemoteHints = lazy(() => import('../pages/RemoteHints'));
const Pricing = lazy(() => import('../pages/Pricing'));
const CompanyProfile = lazy(() => import('../pages/CompanyProfile'));

// Protected route component
const ProtectedRoute = ({ children }) => {
  const isAuthenticated = localStorage.getItem('token') !== null;
  return isAuthenticated ? children : <Navigate to="/login" />;
};

const AppRoutes = () => {
  return (
    <Suspense fallback={<LoadingScreen />}>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/jobs" element={<Jobs />} />
        <Route path="/search" element={<SearchResults />} />
        <Route path="/jobs/:id" element={<JobDetail />} />
        <Route path="/companies/:companyId" element={<CompanyProfile />} />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="/remote-tips" element={<RemoteTips />} />
        <Route path="/career-tips" element={<CareerTips />} />
        <Route path="/remote-hints" element={<RemoteHints />} />
        <Route path="/pricing" element={<Pricing />} />
        <Route path="/salary-guide" element={<SalaryGuide />} />
        <Route path="/visa-sponsorship" element={<VisaSponsorship />} />
        <Route path="/relocation-guide" element={<RelocationGuide />} />
        <Route 
          path="/profile" 
          element={
            <ProtectedRoute>
              <Profile />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/settings" 
          element={
            <ProtectedRoute>
              <Settings />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/saved-jobs" 
          element={
            <ProtectedRoute>
              <SavedJobs />
            </ProtectedRoute>
          } 
        />
        <Route 
          path="/notifications" 
          element={
            <ProtectedRoute>
              <Notifications />
            </ProtectedRoute>
          } 
        />
        <Route path="*" element={<NotFound />} />
      </Routes>
    </Suspense>
  );
};

export default AppRoutes; 