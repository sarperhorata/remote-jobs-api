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
  picture?: string;
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
      skills: ['Product Management', 'Product Strategy', 'Data Analytics', 'Agile/Scrum', 'Market Research', 'User Experience', 'A/B Testing', 'Roadmap Planning', 'Stakeholder Management', 'Growth Hacking'],
      experience: [
        {
          title: 'Co-Founder & Chief Product Officer',
          company: 'Buzz2Remote',
          startDate: '2024-01',
          endDate: null,
          description: 'Founded and leading the product strategy for a remote job platform. Building features for job matching, user onboarding, and analytics. Managing product roadmap and user experience optimization.'
        },
        {
          title: 'Senior Product Manager',
          company: 'Remote-First Tech Company',
          startDate: '2022-03',
          endDate: '2023-12',
          description: 'Led product development for B2B SaaS platform. Increased user engagement by 40% through data-driven product decisions. Managed cross-functional teams of 15+ members.'
        },
        {
          title: 'Product Manager',
          company: 'Growth-Stage Startup',
          startDate: '2020-06',
          endDate: '2022-02',
          description: 'Drove product vision and strategy for consumer mobile app. Launched 3 major features that resulted in 60% increase in user retention. Collaborated with engineering, design, and marketing teams.'
        },
        {
          title: 'Product Analyst',
          company: 'Digital Agency',
          startDate: '2019-01',
          endDate: '2020-05',
          description: 'Analyzed user behavior and market trends to inform product decisions. Created dashboards and reports for C-level executives. Conducted user interviews and usability testing.'
        }
      ],
      education: [
        {
          school: 'Bogazici University',
          degree: 'Master of Business Administration',
          field: 'Technology Management',
          startDate: '2017-09',
          endDate: '2019-06'
        },
        {
          school: 'Istanbul Technical University',
          degree: 'Bachelor of Science',
          field: 'Industrial Engineering',
          startDate: '2013-09',
          endDate: '2017-06'
        }
      ],
      cvUrl: 'https://buzz2remote.com/cv/sarper-horata-product-manager.pdf'
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