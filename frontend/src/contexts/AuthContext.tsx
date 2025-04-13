import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

interface UserProfile {
  name: string;
  email: string;
  phone: string;
  location: string;
  cvUrl: string;
  skills: string[];
  experience: {
    title: string;
    company: string;
    startDate: string;
    endDate: string | null;
    description: string;
  }[];
  education: {
    school: string;
    degree: string;
    field: string;
    startDate: string;
    endDate: string | null;
  }[];
}

interface User {
  id: string;
  name: string;
  email: string;
  profilePicture?: string;
  profile?: UserProfile;
}

interface AuthContextType {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  signup: (name: string, email: string, password: string) => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

interface AuthProviderProps {
  children: ReactNode;
}

export function AuthProvider({ children }: AuthProviderProps) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  // Mock user for demo purposes
  const mockUser: User = {
    id: 'user-1',
    name: 'Sarper Horata',
    email: 'sarperhorata@gmail.com',
    profilePicture: 'https://via.placeholder.com/150',
    profile: {
      name: 'Sarper Horata',
      email: 'sarperhorata@gmail.com',
      phone: '+90 555 123 4567',
      location: 'Istanbul, Turkey',
      cvUrl: 'https://example.com/cv.pdf',
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
      ]
    }
  };

  // Sabit kullanıcı bilgisi - referansı değişmeyecek
  // eslint-disable-next-line react-hooks/exhaustive-deps
  const staticMockUser = React.useMemo(() => mockUser, []);

  useEffect(() => {
    // Simulate loading user from localStorage or session
    const loadUser = async () => {
      setIsLoading(true);
      try {
        // In a real app, check if user is logged in from token/localStorage
        await new Promise(resolve => setTimeout(resolve, 500));
        setUser(staticMockUser); // Always logged in for demo
      } catch (error) {
        console.error('Failed to load user:', error);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    };

    loadUser();
  }, [staticMockUser]); // Sabit kullanıcı referansını bağımlılık olarak kullan

  const login = async (email: string, password: string) => {
    setIsLoading(true);
    try {
      // In a real app, make API call to authenticate
      await new Promise(resolve => setTimeout(resolve, 1000));
      setUser(staticMockUser);
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const logout = () => {
    // In a real app, clear tokens/localStorage
    setUser(null);
  };

  const signup = async (name: string, email: string, password: string) => {
    setIsLoading(true);
    try {
      // In a real app, make API call to create account
      await new Promise(resolve => setTimeout(resolve, 1000));
      setUser({
        id: 'new-user',
        name,
        email,
      });
    } catch (error) {
      console.error('Signup failed:', error);
      throw error;
    } finally {
      setIsLoading(false);
    }
  };

  const value = {
    user,
    isAuthenticated: !!user,
    isLoading,
    login,
    logout,
    signup,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 