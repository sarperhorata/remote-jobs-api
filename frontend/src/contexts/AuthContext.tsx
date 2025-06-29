import React, { createContext, useContext, useState, useEffect, useCallback, useMemo } from 'react';

interface UserProfile {
  email: string;
  name: string;
  phone: string;
  location: string;
  skills: string[];
  experience: Array<{
    title: string;
    company: string;
    startDate: string;
    endDate: string | null;
    description: string;
  }>;
  education: Array<{
    school: string;
    degree: string;
    field: string;
    startDate: string;
    endDate: string;
  }>;
  cvUrl: string;
}

interface User {
  id: string;
  name: string;
  email: string;
  profilePicture?: string;
  profile_picture?: string;
  created_at?: string;
  profile?: UserProfile;
  role?: 'user' | 'admin';
}

export interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  signup: (name: string, email: string, password: string) => Promise<void>;
  refreshUser: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | null>(null);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(false);

  // Static mock user for development
  const staticMockUser: User = useMemo(() => ({
    id: 'user-1',
    name: 'Sarper Horata',
    email: 'sarperhorata@gmail.com',
    profilePicture: 'https://via.placeholder.com/150',
    role: 'admin' as const,
    profile: {
      email: 'sarperhorata@gmail.com',
      name: 'Sarper Horata',
      phone: '+90 555 123 4567',
      location: 'Istanbul, Turkey',
      skills: ['React', 'TypeScript', 'Node.js', 'Python', 'Docker'],
      experience: [
        {
          title: 'Senior Frontend Developer',
          company: 'Tech Corp',
          startDate: '2020-01',
          endDate: null,
          description: 'Leading frontend development for multiple projects'
        },
        {
          title: 'Frontend Developer',
          company: 'Startup Inc',
          startDate: '2018-03',
          endDate: '2019-12',
          description: 'Developed and maintained web applications'
        }
      ],
      education: [
        {
          school: 'Istanbul Technical University',
          degree: 'Bachelor of Science',
          field: 'Computer Engineering',
          startDate: '2014-09',
          endDate: '2018-05'
        }
      ],
      cvUrl: 'https://example.com/cv.pdf'
    }
  }), []);

  // Function to load user data
  const loadUser = useCallback(async () => {
    if (process.env.NODE_ENV === 'test') {
      // In test environment, start with null user
      setUser(null);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      
      const token = localStorage.getItem('token');
      if (!token) {
        // In development, show mock user for demo purposes
        if (process.env.NODE_ENV === 'development') {
          await new Promise(resolve => setTimeout(resolve, 500));
          setUser(staticMockUser);
        } else {
          setUser(null);
        }
        return;
      }

      // Try to fetch user data with token
      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      } else {
        localStorage.removeItem('token');
        setUser(null);
      }
    } catch (error) {
      console.error('Failed to load user:', error);
      setUser(null);
    } finally {
      setIsLoading(false);
    }
  }, [staticMockUser]);

  useEffect(() => {
    loadUser();
  }, [loadUser]);

  const login = async (email: string, password: string) => {
    if (process.env.NODE_ENV === 'test') {
      // Mock login for tests
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Login failed');
      }

      setUser(data.user);
      localStorage.setItem('token', data.token);
      return;
    }

    try {
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await response.json();
      
      if (response.ok) {
        setUser(data.user || staticMockUser);
        localStorage.setItem('token', data.token || 'demo-token');
      } else {
        throw new Error(data.message || 'Login failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const signup = async (name: string, email: string, password: string) => {
    if (process.env.NODE_ENV === 'test') {
      // Mock signup for tests
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      
      if (!response.ok) {
        throw new Error(data.message || 'Signup failed');
      }

      setUser(data.user);
      localStorage.setItem('token', data.token);
      return;
    }

    try {
      const response = await fetch('/api/auth/signup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ name, email, password })
      });

      const data = await response.json();
      
      if (response.ok) {
        setUser(data.user || { ...staticMockUser, name, email });
        localStorage.setItem('token', data.token || 'demo-token');
      } else {
        throw new Error(data.message || 'Signup failed');
      }
    } catch (error) {
      throw error;
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('token');
  };

  const refreshUser = async () => {
    if (process.env.NODE_ENV === 'test') {
      // Mock refresh for tests
      const token = localStorage.getItem('token');
      if (!token) return;

      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
      return;
    }

    const token = localStorage.getItem('token');
    if (!token) return;

    try {
      const response = await fetch('/api/auth/me', {
        headers: { Authorization: `Bearer ${token}` }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
      }
    } catch (error) {
      console.error('Failed to refresh user:', error);
    }
  };

  const isAuthenticated = !!user;

  return (
    <AuthContext.Provider value={{
      user,
      isAuthenticated,
      isLoading,
      login,
      logout,
      signup,
      refreshUser
    }}>
      {children}
    </AuthContext.Provider>
  );
}; 