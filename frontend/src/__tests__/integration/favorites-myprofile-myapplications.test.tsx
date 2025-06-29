import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import '@testing-library/jest-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import Favorites from '../../pages/Favorites';
import MyProfile from '../../pages/MyProfile';
import MyApplications from '../../pages/MyApplications';
import { AuthContext } from '../../contexts/AuthContext';

// Mock components and services
jest.mock('../../components/Header', () => {
  return function MockHeader() {
    return <div data-testid="header">Header</div>;
  };
});

jest.mock('../../services/jobService', () => ({
  jobService: {
    getJobById: jest.fn(),
    unsaveJob: jest.fn(),
    saveJob: jest.fn(),
    searchJobs: jest.fn(),
    getMyApplications: jest.fn(),
  }
}));

// Mock localStorage
const mockLocalStorage = (() => {
  let store: Record<string, string> = {};
  return {
    getItem: (key: string) => store[key] || null,
    setItem: (key: string, value: string) => { store[key] = value; },
    removeItem: (key: string) => { delete store[key]; },
    clear: () => { store = {}; }
  };
})();

Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

// Import after mocking
import { jobService } from '../../services/jobService';

const mockJobService = jobService as jest.Mocked<typeof jobService>;

// Mock authenticated user
const mockUser = {
  id: 'user1',
  name: 'Test User',
  email: 'test@example.com',
  profilePicture: 'https://example.com/avatar.jpg'
};

const mockAuthContextValue = {
  user: mockUser,
  isAuthenticated: true,
  login: jest.fn(),
  logout: jest.fn(),
  register: jest.fn(),
  loading: false
};

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    <AuthContext.Provider value={mockAuthContextValue}>
      {children}
    </AuthContext.Provider>
  </BrowserRouter>
);

describe('Favorites Page Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
  });

  it('renders favorites page with saved jobs', async () => {
    const mockJobs = [
      {
        id: '1',
        title: 'Software Engineer',
        company: 'Test Company',
        location: 'Remote',
        salary_range: '$70k-$90k',
        type: 'Full-time',
        url: 'https://example.com/job1'
      }
    ];

    // Mock localStorage with saved jobs
    mockLocalStorage.setItem('savedJobs', JSON.stringify(mockJobs));
    mockJobService.getJobById.mockResolvedValue(mockJobs[0]);

    render(
      <TestWrapper>
        <Favorites />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('My Saved Jobs')).toBeInTheDocument();
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
    });
  });

  it('handles removing jobs from favorites', async () => {
    const mockJobs = [
      {
        id: '1',
        title: 'Software Engineer',
        company: 'Test Company',
        location: 'Remote',
        salary_range: '$70k-$90k',
        type: 'Full-time',
        url: 'https://example.com/job1'
      }
    ];

    mockLocalStorage.setItem('savedJobs', JSON.stringify(mockJobs));
    mockJobService.getJobById.mockResolvedValue(mockJobs[0]);
    mockJobService.unsaveJob.mockResolvedValue(undefined);

    render(
      <TestWrapper>
        <Favorites />
      </TestWrapper>
    );

    await waitFor(() => {
      const removeButton = screen.getByLabelText('Remove from favorites');
      fireEvent.click(removeButton);
    });

    await waitFor(() => {
      expect(mockJobService.unsaveJob).toHaveBeenCalledWith('user1', '1');
    });
  });

  it('shows empty state when no saved jobs', () => {
    render(
      <TestWrapper>
        <Favorites />
      </TestWrapper>
    );

    expect(screen.getByText('No saved jobs yet')).toBeInTheDocument();
  });
});

describe('MyProfile Page Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders profile page with user data', () => {
    render(
      <TestWrapper>
        <MyProfile />
      </TestWrapper>
    );

    expect(screen.getByText('My Profile')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
    expect(screen.getByDisplayValue('test@example.com')).toBeInTheDocument();
  });

  it('allows editing profile information', async () => {
    render(
      <TestWrapper>
        <MyProfile />
      </TestWrapper>
    );

    const editButton = screen.getByText('Edit Profile');
    fireEvent.click(editButton);

    await waitFor(() => {
      expect(screen.getByText('Save Changes')).toBeInTheDocument();
    });

    const nameInput = screen.getByDisplayValue('Test User');
    fireEvent.change(nameInput, { target: { value: 'Updated Name' } });

    const saveButton = screen.getByText('Save Changes');
    fireEvent.click(saveButton);

    await waitFor(() => {
      expect(screen.getByText('Edit Profile')).toBeInTheDocument();
    });
  });

  it('handles profile picture upload', async () => {
    render(
      <TestWrapper>
        <MyProfile />
      </TestWrapper>
    );

    const editButton = screen.getByText('Edit Profile');
    fireEvent.click(editButton);

    const fileInput = screen.getByLabelText('Change Photo');
    const file = new File(['test'], 'test.jpg', { type: 'image/jpeg' });
    
    fireEvent.change(fileInput, { target: { files: [file] } });

    await waitFor(() => {
      expect(fileInput.files?.[0]).toBe(file);
    });
  });
});

describe('MyApplications Page Integration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockJobService.getMyApplications.mockResolvedValue([]);
  });

  it('renders applications page', async () => {
    render(
      <TestWrapper>
        <MyApplications />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('My Applications')).toBeInTheDocument();
    });
  });

  it('displays application statistics', async () => {
    const mockApplications = [
      {
        id: '1',
        jobTitle: 'Software Engineer',
        company: 'Test Company',
        status: 'pending',
        appliedDate: '2024-01-15',
        jobId: 'job1'
      },
      {
        id: '2',
        jobTitle: 'Product Manager',
        company: 'Another Company',
        status: 'interview',
        appliedDate: '2024-01-10',
        jobId: 'job2'
      }
    ];

    mockJobService.getMyApplications.mockResolvedValue(mockApplications);

    render(
      <TestWrapper>
        <MyApplications />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('2 Total Applications')).toBeInTheDocument();
      expect(screen.getByText('1 Pending')).toBeInTheDocument();
      expect(screen.getByText('1 Interview')).toBeInTheDocument();
    });
  });

  it('filters applications by status', async () => {
    const mockApplications = [
      {
        id: '1',
        jobTitle: 'Software Engineer',
        company: 'Test Company',
        status: 'pending',
        appliedDate: '2024-01-15',
        jobId: 'job1'
      },
      {
        id: '2',
        jobTitle: 'Product Manager',
        company: 'Another Company',
        status: 'interview',
        appliedDate: '2024-01-10',
        jobId: 'job2'
      }
    ];

    mockJobService.getMyApplications.mockResolvedValue(mockApplications);

    render(
      <TestWrapper>
        <MyApplications />
      </TestWrapper>
    );

    await waitFor(() => {
      const pendingFilter = screen.getByText('Pending (1)');
      fireEvent.click(pendingFilter);
    });

    await waitFor(() => {
      expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      expect(screen.queryByText('Product Manager')).not.toBeInTheDocument();
    });
  });

  it('handles application status updates', async () => {
    const mockApplications = [
      {
        id: '1',
        jobTitle: 'Software Engineer',
        company: 'Test Company',
        status: 'pending',
        appliedDate: '2024-01-15',
        jobId: 'job1'
      }
    ];

    mockJobService.getMyApplications.mockResolvedValue(mockApplications);

    render(
      <TestWrapper>
        <MyApplications />
      </TestWrapper>
    );

    await waitFor(() => {
      const statusBadge = screen.getByText('Pending');
      expect(statusBadge).toBeInTheDocument();
    });
  });
});

describe('Cross-page Integration', () => {
  it('maintains user context across pages', () => {
    const { rerender } = render(
      <TestWrapper>
        <Favorites />
      </TestWrapper>
    );

    expect(screen.getByText('My Saved Jobs')).toBeInTheDocument();

    rerender(
      <TestWrapper>
        <MyProfile />
      </TestWrapper>
    );

    expect(screen.getByText('My Profile')).toBeInTheDocument();
    expect(screen.getByDisplayValue('Test User')).toBeInTheDocument();
  });

  it('handles authentication state changes', () => {
    const unauthenticatedContext = {
      ...mockAuthContextValue,
      isAuthenticated: false,
      user: null
    };

    render(
      <BrowserRouter>
        <AuthContext.Provider value={unauthenticatedContext}>
          <Favorites />
        </AuthContext.Provider>
      </BrowserRouter>
    );

    expect(screen.getByText('Please log in to view your saved jobs')).toBeInTheDocument();
  });
});

describe('User Profile Pages Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockLocalStorage.clear();
    mockLocalStorage.getItem.mockImplementation((key: string) => {
      switch (key) {
        case 'savedJobs':
          return JSON.stringify(['test-job-1', 'test-job-2']);
        case 'myApplications':
          return JSON.stringify([
            {
              id: '1',
              job_id: 'job-1',
              job_title: 'Senior React Developer',
              company: 'TechCorp Inc.',
              location: 'Remote',
              salary: '$80,000 - $120,000',
              job_type: 'Full-time',
              work_type: 'Remote',
              applied_at: new Date().toISOString(),
              status: 'reviewing',
              application_url: 'https://example.com/application/1'
            }
          ]);
        case 'userPreferences':
          return JSON.stringify({
            location: 'San Francisco, CA',
            bio: 'Experienced developer',
            job_titles: ['Frontend Developer', 'React Developer'],
            skills: ['JavaScript', 'React', 'TypeScript'],
            experience_levels: ['Mid Level'],
            work_types: ['Remote'],
            salary_ranges: ['$60,000 - $80,000']
          });
        default:
          return null;
      }
    });
  });

  describe('Favorites Page', () => {
    test('renders favorites page with saved jobs', async () => {
      render(
        <TestWrapper>
          <Favorites />
        </TestWrapper>
      );

      expect(screen.getByText('My Favorite Jobs')).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getByText('2 jobs in your favorites')).toBeInTheDocument();
      });
    });

    test('shows login prompt when not authenticated', () => {
      const unauthenticatedContext = {
        ...mockAuthContextValue,
        isAuthenticated: false,
        user: null
      };

      jest.mocked(require('../../contexts/AuthContext').useAuth).mockReturnValue(unauthenticatedContext);

      render(
        <TestWrapper>
          <Favorites />
        </TestWrapper>
      );

      expect(screen.getByText('Please Login')).toBeInTheDocument();
      expect(screen.getByText('You need to be logged in to view your favorite jobs.')).toBeInTheDocument();
    });

    test('removes job from favorites when remove button clicked', async () => {
      render(
        <TestWrapper>
          <Favorites />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test Job')).toBeInTheDocument();
      });

      const removeButton = screen.getByTitle('Remove from Favorites');
      fireEvent.click(removeButton);

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'savedJobs',
        expect.stringContaining('"test-job-2"')
      );
    });

    test('shows empty state when no favorites', () => {
      mockLocalStorage.getItem.mockImplementation((key: string) => {
        if (key === 'savedJobs') return JSON.stringify([]);
        return null;
      });

      render(
        <TestWrapper>
          <Favorites />
        </TestWrapper>
      );

      expect(screen.getByText('No Favorite Jobs Yet')).toBeInTheDocument();
      expect(screen.getByText('Start adding jobs to your favorites to see them here.')).toBeInTheDocument();
    });

    test('applies dark mode styles correctly', () => {
      render(
        <TestWrapper>
          <div className="dark">
            <Favorites />
          </div>
        </TestWrapper>
      );

      const container = screen.getByText('My Favorite Jobs').closest('div');
      expect(container).toHaveClass('dark:bg-slate-900');
    });

    it('handles job removal with backend sync', async () => {
      const mockJob = {
        id: 'job-1',
        _id: 'job-1',
        title: 'Software Engineer',
        company: 'Tech Corp',
        location: 'Remote',
      };

      mockLocalStorage.setItem('savedJobs', JSON.stringify(['job-1']));
      mockJobService.getJobById.mockResolvedValue(mockJob);
      mockJobService.unsaveJob.mockResolvedValue(undefined);

      render(
        <TestWrapper>
          <Favorites />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      });

      const removeButton = screen.getByTitle('Remove from Favorites');
      fireEvent.click(removeButton);

      await waitFor(() => {
        expect(mockJobService.unsaveJob).toHaveBeenCalledWith('user1', 'job-1');
      });
    });

    it('handles unsaveJob API failure gracefully', async () => {
      const mockJob = {
        id: 'job-1',
        _id: 'job-1',
        title: 'Software Engineer',
        company: 'Tech Corp',
      };

      mockLocalStorage.setItem('savedJobs', JSON.stringify(['job-1']));
      mockJobService.getJobById.mockResolvedValue(mockJob);
      mockJobService.unsaveJob.mockRejectedValue(new Error('Network error'));

      const consoleSpy = jest.spyOn(console, 'error').mockImplementation(() => {});

      render(
        <TestWrapper>
          <Favorites />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Software Engineer')).toBeInTheDocument();
      });

      const removeButton = screen.getByTitle('Remove from Favorites');
      fireEvent.click(removeButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Error removing favorite:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });
  });

  describe('My Profile Page', () => {
    test('renders profile page with user information', async () => {
      render(
        <TestWrapper>
          <MyProfile />
        </TestWrapper>
      );

      expect(screen.getByText('Test User')).toBeInTheDocument();
      expect(screen.getByText('test@example.com')).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getByText('Activity Stats')).toBeInTheDocument();
      });
    });

    test('shows edit form when edit button clicked', () => {
      render(
        <TestWrapper>
          <MyProfile />
        </TestWrapper>
      );

      const editButton = screen.getByText('Edit Profile');
      fireEvent.click(editButton);

      expect(screen.getByText('Save')).toBeInTheDocument();
      expect(screen.getByText('Cancel')).toBeInTheDocument();
    });

    test('saves profile changes when save button clicked', () => {
      render(
        <TestWrapper>
          <MyProfile />
        </TestWrapper>
      );

      const editButton = screen.getByText('Edit Profile');
      fireEvent.click(editButton);

      const bioTextarea = screen.getByPlaceholderText('Tell us about yourself...');
      fireEvent.change(bioTextarea, { target: { value: 'Updated bio' } });

      const saveButton = screen.getByText('Save');
      fireEvent.click(saveButton);

      expect(mockLocalStorage.setItem).toHaveBeenCalledWith(
        'userPreferences',
        expect.stringContaining('"bio":"Updated bio"')
      );
    });

    test('shows user preferences and skills', async () => {
      render(
        <TestWrapper>
          <MyProfile />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
        expect(screen.getByText('React Developer')).toBeInTheDocument();
        expect(screen.getByText('JavaScript')).toBeInTheDocument();
        expect(screen.getByText('React')).toBeInTheDocument();
        expect(screen.getByText('TypeScript')).toBeInTheDocument();
      });
    });

    it('saves profile with user properties correctly', async () => {
      mockLocalStorage.setItem('userPreferences', JSON.stringify({
        location: 'Test Location',
        bio: 'Test Bio',
      }));

      render(
        <TestWrapper>
          <MyProfile />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Test User')).toBeInTheDocument();
        expect(screen.getByText('test@example.com')).toBeInTheDocument();
      });
    });
  });

  describe('My Applications Page', () => {
    test('renders applications page with application history', async () => {
      render(
        <TestWrapper>
          <MyApplications />
        </TestWrapper>
      );

      expect(screen.getByText('My Applications')).toBeInTheDocument();
      
      await waitFor(() => {
        expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
        expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
      });
    });

    test('shows application statistics', async () => {
      render(
        <TestWrapper>
          <MyApplications />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('1')).toBeInTheDocument(); // Total applications
        expect(screen.getByText('Total')).toBeInTheDocument();
        expect(screen.getByText('Review')).toBeInTheDocument();
      });
    });

    test('filters applications by status', async () => {
      render(
        <TestWrapper>
          <MyApplications />
        </TestWrapper>
      );

      await waitFor(() => {
        expect(screen.getByText('Under Review')).toBeInTheDocument();
      });

      const reviewingButton = screen.getByText('Under Review (1)');
      fireEvent.click(reviewingButton);

      expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
    });

    test('shows status badges correctly', async () => {
      render(
        <TestWrapper>
          <MyApplications />
        </TestWrapper>
      );

      await waitFor(() => {
        const statusBadge = screen.getByText('Under Review');
        expect(statusBadge).toHaveClass('text-blue-600');
      });
    });

    test('shows empty state when no applications', () => {
      mockLocalStorage.getItem.mockImplementation((key: string) => {
        if (key === 'myApplications') return JSON.stringify([]);
        return null;
      });

      render(
        <TestWrapper>
          <MyApplications />
        </TestWrapper>
      );

      expect(screen.getByText('No Applications Yet')).toBeInTheDocument();
      expect(screen.getByText('Start applying to jobs to see them here.')).toBeInTheDocument();
    });
  });

  describe('Dark Mode Compatibility', () => {
    test('all pages support dark mode', () => {
      const pages = [
        { component: <Favorites />, name: 'Favorites' },
        { component: <MyProfile />, name: 'MyProfile' },
        { component: <MyApplications />, name: 'MyApplications' }
      ];

      pages.forEach(({ component, name }) => {
        const { container } = render(
          <TestWrapper>
            <div className="dark">
              {component}
            </div>
          </TestWrapper>
        );

        // Check if dark mode classes are applied
        const darkElements = container.querySelectorAll('.dark\\:bg-slate-900, .dark\\:bg-slate-800, .dark\\:text-white');
        expect(darkElements.length).toBeGreaterThan(0);
      });
    });
  });

  describe('Responsive Design', () => {
    test('pages are responsive and mobile-friendly', () => {
      // Mock mobile viewport
      Object.defineProperty(window, 'innerWidth', {
        writable: true,
        configurable: true,
        value: 375,
      });

      render(
        <TestWrapper>
          <MyProfile />
        </TestWrapper>
      );

      // Check for responsive grid classes
      const responsiveElements = document.querySelectorAll('.grid-cols-1, .md\\:grid-cols-2, .lg\\:grid-cols-3');
      expect(responsiveElements.length).toBeGreaterThan(0);
    });
  });

  describe('Accessibility', () => {
    test('pages have proper ARIA labels and semantic markup', () => {
      render(
        <TestWrapper>
          <MyApplications />
        </TestWrapper>
      );

      // Check for semantic headings
      expect(screen.getByRole('heading', { level: 1 })).toBeInTheDocument();
      
      // Check for buttons with proper labels
      const buttons = screen.getAllByRole('button');
      buttons.forEach(button => {
        expect(button).toHaveAccessibleName();
      });
    });
  });
}); 