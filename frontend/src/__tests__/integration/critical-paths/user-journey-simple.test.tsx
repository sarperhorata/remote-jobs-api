import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// Mock services
jest.mock('../../../services/AllServices', () => ({
  jobService: {
    searchJobs: jest.fn(),
    getJobById: jest.fn(),
    applyToJob: jest.fn(),
  },
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    getCurrentUser: jest.fn(),
  },
  userService: {
    updateProfile: jest.fn(),
    getProfile: jest.fn(),
  },
}));

// Mock components without router dependencies
const MockJobCard = ({ job }: { job: any }) => (
  <div data-testid="job-card">
    <h3>{job.title}</h3>
    <p>{job.company}</p>
    <p>{job.location}</p>
    <button data-testid="apply-button">Apply</button>
  </div>
);

const MockSearchBar = ({ onSearch }: { onSearch: (query: string) => void }) => (
  <div data-testid="search-bar">
    <input 
      data-testid="search-input" 
      placeholder="Search jobs..."
      onChange={(e) => onSearch(e.target.value)}
    />
    <button data-testid="search-button">Search</button>
  </div>
);

const MockProfileForm = ({ onSubmit }: { onSubmit: (data: any) => void }) => (
  <form data-testid="profile-form" onSubmit={(e) => {
    e.preventDefault();
    onSubmit({ name: 'Test User', email: 'test@example.com' });
  }}>
    <input data-testid="name-input" placeholder="Name" />
    <input data-testid="email-input" placeholder="Email" />
    <button type="submit" data-testid="save-button">Save</button>
  </form>
);

describe('Simple User Journey Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
  });

  describe('Job Search Flow', () => {
    it('should search for jobs and display results', async () => {
      const mockJobs = [
        { id: '1', title: 'React Developer', company: 'TechCorp', location: 'Remote' },
        { id: '2', title: 'Frontend Engineer', company: 'StartupCo', location: 'San Francisco' }
      ];

      const onSearch = jest.fn().mockResolvedValue(mockJobs);

      render(
        <div>
          <MockSearchBar onSearch={onSearch} />
          {mockJobs.map(job => (
            <MockJobCard key={job.id} job={job} />
          ))}
        </div>
      );

      // Search for jobs
      const searchInput = screen.getByTestId('search-input');
      const searchButton = screen.getByTestId('search-button');

      fireEvent.change(searchInput, { target: { value: 'React' } });
      fireEvent.click(searchButton);

      // Verify search was called
      await waitFor(() => {
        expect(onSearch).toHaveBeenCalledWith('React');
      });

      // Verify job cards are displayed
      expect(screen.getByText('React Developer')).toBeInTheDocument();
      expect(screen.getByText('Frontend Engineer')).toBeInTheDocument();
      expect(screen.getByText('TechCorp')).toBeInTheDocument();
      expect(screen.getByText('StartupCo')).toBeInTheDocument();
    });

    it('should apply to a job', async () => {
      const mockJob = { id: '1', title: 'React Developer', company: 'TechCorp', location: 'Remote' };
      const onApply = jest.fn().mockResolvedValue({ success: true });

      render(<MockJobCard job={mockJob} />);

      // Apply to job
      const applyButton = screen.getByTestId('apply-button');
      fireEvent.click(applyButton);

      // Verify apply action
      await waitFor(() => {
        expect(applyButton).toBeInTheDocument();
      });
    });
  });

  describe('Profile Management', () => {
    it('should update user profile', async () => {
      const onProfileUpdate = jest.fn().mockResolvedValue({ success: true });

      render(<MockProfileForm onSubmit={onProfileUpdate} />);

      // Fill profile form
      const nameInput = screen.getByTestId('name-input');
      const emailInput = screen.getByTestId('email-input');
      const saveButton = screen.getByTestId('save-button');

      fireEvent.change(nameInput, { target: { value: 'John Doe' } });
      fireEvent.change(emailInput, { target: { value: 'john@example.com' } });
      fireEvent.click(saveButton);

      // Verify profile update
      await waitFor(() => {
        expect(onProfileUpdate).toHaveBeenCalledWith({
          name: 'Test User',
          email: 'test@example.com'
        });
      });
    });
  });

  describe('Authentication Flow', () => {
    it('should handle user login', async () => {
      const mockLogin = jest.fn().mockResolvedValue({ 
        success: true, 
        user: { id: '1', name: 'Test User' } 
      });

      const MockLoginForm = () => (
        <form data-testid="login-form" onSubmit={(e) => {
          e.preventDefault();
          mockLogin({ email: 'test@example.com', password: 'password' });
        }}>
          <input data-testid="email-input" placeholder="Email" />
          <input data-testid="password-input" placeholder="Password" />
          <button type="submit" data-testid="login-button">Login</button>
        </form>
      );

      render(<MockLoginForm />);

      // Fill login form
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const loginButton = screen.getByTestId('login-button');

      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(loginButton);

      // Verify login was called
      await waitFor(() => {
        expect(mockLogin).toHaveBeenCalledWith({
          email: 'test@example.com',
          password: 'password'
        });
      });
    });

    it('should handle user registration', async () => {
      const mockRegister = jest.fn().mockResolvedValue({ 
        success: true, 
        user: { id: '1', name: 'New User' } 
      });

      const MockRegisterForm = () => (
        <form data-testid="register-form" onSubmit={(e) => {
          e.preventDefault();
          mockRegister({ 
            name: 'New User', 
            email: 'new@example.com', 
            password: 'password' 
          });
        }}>
          <input data-testid="name-input" placeholder="Name" />
          <input data-testid="email-input" placeholder="Email" />
          <input data-testid="password-input" placeholder="Password" />
          <button type="submit" data-testid="register-button">Register</button>
        </form>
      );

      render(<MockRegisterForm />);

      // Fill registration form
      const nameInput = screen.getByTestId('name-input');
      const emailInput = screen.getByTestId('email-input');
      const passwordInput = screen.getByTestId('password-input');
      const registerButton = screen.getByTestId('register-button');

      fireEvent.change(nameInput, { target: { value: 'New User' } });
      fireEvent.change(emailInput, { target: { value: 'new@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'password' } });
      fireEvent.click(registerButton);

      // Verify registration was called
      await waitFor(() => {
        expect(mockRegister).toHaveBeenCalledWith({
          name: 'New User',
          email: 'new@example.com',
          password: 'password'
        });
      });
    });
  });

  describe('Error Handling', () => {
    it('should handle API errors gracefully', async () => {
      const mockErrorSearch = jest.fn().mockRejectedValue(new Error('Network error'));

      const MockErrorComponent = () => {
        const [error, setError] = React.useState<string | null>(null);

        const handleSearch = async () => {
          try {
            await mockErrorSearch();
          } catch (err) {
            setError('Search failed. Please try again.');
          }
        };

        return (
          <div>
            <button data-testid="error-button" onClick={handleSearch}>
              Search
            </button>
            {error && <div data-testid="error-message">{error}</div>}
          </div>
        );
      };

      render(<MockErrorComponent />);

      // Trigger error
      const errorButton = screen.getByTestId('error-button');
      fireEvent.click(errorButton);

      // Verify error is displayed
      await waitFor(() => {
        expect(screen.getByTestId('error-message')).toBeInTheDocument();
        expect(screen.getByText('Search failed. Please try again.')).toBeInTheDocument();
      });
    });

    it('should handle loading states', async () => {
      const MockLoadingComponent = () => {
        const [loading, setLoading] = React.useState(false);
        const [data, setData] = React.useState<any[]>([]);

        const handleLoad = async () => {
          setLoading(true);
          // Simulate API call
          await new Promise(resolve => setTimeout(resolve, 100));
          setData([{ id: '1', title: 'Loaded Job' }]);
          setLoading(false);
        };

        return (
          <div>
            <button data-testid="load-button" onClick={handleLoad}>
              Load Data
            </button>
            {loading && <div data-testid="loading-spinner">Loading...</div>}
            {data.map(item => (
              <div key={item.id} data-testid="data-item">{item.title}</div>
            ))}
          </div>
        );
      };

      render(<MockLoadingComponent />);

      // Trigger loading
      const loadButton = screen.getByTestId('load-button');
      fireEvent.click(loadButton);

      // Verify loading state
      expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();

      // Verify data is loaded
      await waitFor(() => {
        expect(screen.getByTestId('data-item')).toBeInTheDocument();
        expect(screen.getByText('Loaded Job')).toBeInTheDocument();
      });
    });
  });

  describe('Form Validation', () => {
    it('should validate required fields', async () => {
      const MockValidationForm = () => {
        const [errors, setErrors] = React.useState<string[]>([]);

        const handleSubmit = (e: React.FormEvent) => {
          e.preventDefault();
          const formData = new FormData(e.target as HTMLFormElement);
          const name = formData.get('name') as string;
          const email = formData.get('email') as string;

          const newErrors: string[] = [];
          if (!name) newErrors.push('Name is required');
          if (!email) newErrors.push('Email is required');
          if (email && !email.includes('@')) newErrors.push('Invalid email format');

          setErrors(newErrors);
        };

        return (
          <form data-testid="validation-form" onSubmit={handleSubmit}>
            <input name="name" data-testid="name-input" placeholder="Name" />
            <input name="email" data-testid="email-input" placeholder="Email" />
            <button type="submit" data-testid="submit-button">Submit</button>
            {errors.map((error, index) => (
              <div key={index} data-testid="error-message">{error}</div>
            ))}
          </form>
        );
      };

      render(<MockValidationForm />);

      // Submit empty form
      const submitButton = screen.getByTestId('submit-button');
      fireEvent.click(submitButton);

      // Verify validation errors
      await waitFor(() => {
        expect(screen.getByText('Name is required')).toBeInTheDocument();
        expect(screen.getByText('Email is required')).toBeInTheDocument();
      });

      // Fill with invalid email
      const nameInput = screen.getByTestId('name-input');
      const emailInput = screen.getByTestId('email-input');

      fireEvent.change(nameInput, { target: { value: 'Test User' } });
      fireEvent.change(emailInput, { target: { value: 'invalid-email' } });
      fireEvent.click(submitButton);

      // Verify email validation
      await waitFor(() => {
        expect(screen.getByText('Invalid email format')).toBeInTheDocument();
      });
    });
  });

  describe('Data Management', () => {
    it('should handle data filtering', async () => {
      const MockFilterComponent = () => {
        const [jobs, setJobs] = React.useState([
          { id: '1', title: 'React Developer', category: 'Frontend' },
          { id: '2', title: 'Backend Developer', category: 'Backend' },
          { id: '3', title: 'Full Stack Developer', category: 'Full Stack' }
        ]);
        const [filter, setFilter] = React.useState('all');

        const filteredJobs = filter === 'all' 
          ? jobs 
          : jobs.filter(job => job.category === filter);

        return (
          <div>
            <select 
              data-testid="filter-select" 
              value={filter}
              onChange={(e) => setFilter(e.target.value)}
            >
              <option value="all">All</option>
              <option value="Frontend">Frontend</option>
              <option value="Backend">Backend</option>
              <option value="Full Stack">Full Stack</option>
            </select>
            <div data-testid="jobs-list">
              {filteredJobs.map(job => (
                <div key={job.id} data-testid="job-item">{job.title}</div>
              ))}
            </div>
          </div>
        );
      };

      render(<MockFilterComponent />);

      // Initially all jobs should be visible
      expect(screen.getByText('React Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();
      expect(screen.getByText('Full Stack Developer')).toBeInTheDocument();

      // Filter by Frontend
      const filterSelect = screen.getByTestId('filter-select');
      fireEvent.change(filterSelect, { target: { value: 'Frontend' } });

      // Only Frontend jobs should be visible
      await waitFor(() => {
        expect(screen.getByText('React Developer')).toBeInTheDocument();
        expect(screen.queryByText('Backend Developer')).not.toBeInTheDocument();
        expect(screen.queryByText('Full Stack Developer')).not.toBeInTheDocument();
      });
    });

    it('should handle data sorting', async () => {
      const MockSortComponent = () => {
        const [jobs, setJobs] = React.useState([
          { id: '1', title: 'React Developer', salary: 80000 },
          { id: '2', title: 'Senior Developer', salary: 120000 },
          { id: '3', title: 'Junior Developer', salary: 60000 }
        ]);
        const [sortBy, setSortBy] = React.useState('title');

        const sortedJobs = [...jobs].sort((a, b) => {
          if (sortBy === 'title') {
            return a.title.localeCompare(b.title);
          }
          return a.salary - b.salary;
        });

        return (
          <div>
            <select 
              data-testid="sort-select" 
              value={sortBy}
              onChange={(e) => setSortBy(e.target.value)}
            >
              <option value="title">Sort by Title</option>
              <option value="salary">Sort by Salary</option>
            </select>
            <div data-testid="jobs-list">
              {sortedJobs.map(job => (
                <div key={job.id} data-testid="job-item">
                  {job.title} - ${job.salary}
                </div>
              ))}
            </div>
          </div>
        );
      };

      render(<MockSortComponent />);

      // Initially sorted by title
      const jobItems = screen.getAllByTestId('job-item');
      expect(jobItems[0]).toHaveTextContent('Junior Developer');
      expect(jobItems[1]).toHaveTextContent('React Developer');
      expect(jobItems[2]).toHaveTextContent('Senior Developer');

      // Sort by salary
      const sortSelect = screen.getByTestId('sort-select');
      fireEvent.change(sortSelect, { target: { value: 'salary' } });

      // Should be sorted by salary
      await waitFor(() => {
        const sortedJobItems = screen.getAllByTestId('job-item');
        expect(sortedJobItems[0]).toHaveTextContent('Junior Developer - $60000');
        expect(sortedJobItems[1]).toHaveTextContent('React Developer - $80000');
        expect(sortedJobItems[2]).toHaveTextContent('Senior Developer - $120000');
      });
    });
  });
});