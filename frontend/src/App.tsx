import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from 'react-query';
import Home from './pages/Home';
import Jobs from './pages/Jobs';
import JobDetail from './pages/JobDetail';
import Profile from './pages/Profile';
import Status from './pages/Status';
import Dashboard from './pages/Dashboard';
import Navigation from './components/Navigation';
import { AuthProvider } from './contexts/AuthContext';
import { ThemeProvider } from './contexts/theme/ThemeContext';
import './App.css';

const queryClient = new QueryClient();

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <ThemeProvider>
          <Router>
            <div className="min-h-screen">
              <Navigation />
              <main>
                <Routes>
                  <Route path="/" element={<Home />} />
                  <Route path="/dashboard" element={<Dashboard />} />
                  <Route path="/jobs" element={<Jobs />} />
                  <Route path="/jobs/:id" element={<JobDetail />} />
                  <Route path="/my-skills" element={<Profile />} />
                  <Route path="/my-resumes" element={<Profile />} />
                  <Route path="/my-jobs" element={<Profile />} />
                  <Route path="/profile" element={<Profile />} />
                  <Route path="/status" element={<Status />} />
                </Routes>
              </main>
            </div>
          </Router>
        </ThemeProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
};

export default App;
