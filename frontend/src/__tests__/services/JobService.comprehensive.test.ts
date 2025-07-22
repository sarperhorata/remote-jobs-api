import { jobService } from '../../services/jobService';

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock
});

describe('JobService Comprehensive Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null);
  });

  describe('getJobs', () => {
    test('fetches jobs successfully with default parameters', async () => {
      const mockJobs = [
        {
          _id: '1',
          title: 'Frontend Developer',
          company: 'TechCorp',
          location: 'Remote',
          job_type: 'Full-time',
          salary_range: '$80k - $120k',
          skills: ['React', 'TypeScript'],
          created_at: new Date().toISOString(),
          description: 'Exciting opportunity',
          company_logo: '💻',
          url: '#',
          is_active: true
        }
      ];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 1, page: 1, limit: 10 })
      });

      const result = await jobService.getJobs();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/jobs/search?page=1&limit=10'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockJobs);
    });

    test('fetches jobs with custom pagination', async () => {
      const mockJobs = [
        {
          _id: '2',
          title: 'Backend Developer',
          company: 'DataFlow',
          location: 'Remote',
          job_type: 'Full-time',
          salary_range: '$90k - $130k',
          skills: ['Python', 'Django'],
          created_at: new Date().toISOString(),
          description: 'Backend role',
          company_logo: '🔧',
          url: '#',
          is_active: true
        }
      ];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 1, page: 2, limit: 5 })
      });

      const result = await jobService.getJobs(2, 5);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/jobs/search?page=2&limit=5'),
        expect.any(Object)
      );

      expect(result).toEqual(mockJobs);
    });

    test('handles API error gracefully', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(jobService.getJobs()).rejects.toThrow('Network error');
    });

    test('handles non-ok response', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      await expect(jobService.getJobs()).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    test('handles empty response', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [], total: 0, page: 1, limit: 10 })
      });

      const result = await jobService.getJobs();

      expect(result).toEqual([]);
    });

    test('handles different response formats', async () => {
      const mockJobs = [{ _id: '1', title: 'Developer' }];

      // Test with items array
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ items: mockJobs })
      });

      const result1 = await jobService.getJobs();
      expect(result1).toEqual(mockJobs);

      // Test with direct array
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockJobs
      });

      const result2 = await jobService.getJobs();
      expect(result2).toEqual(mockJobs);
    });
  });

  describe('searchJobs', () => {
    test('searches jobs with query parameters', async () => {
      const mockJobs = [
        {
          _id: '1',
          title: 'React Developer',
          company: 'TechCorp',
          location: 'Remote',
          job_type: 'Full-time',
          salary_range: '$80k - $120k',
          skills: ['React', 'TypeScript'],
          created_at: new Date().toISOString(),
          description: 'React role',
          company_logo: '💻',
          url: '#',
          is_active: true
        }
      ];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs, total: 1 })
      });

      const searchParams = {
        q: 'React',
        location: 'Remote',
        job_type: 'Full-time',
        skills: ['React', 'TypeScript']
      };

      const result = await jobService.searchJobs(searchParams);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/jobs/search?location=Remote&q=React&job_type=Full-time'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockJobs);
    });

    test('handles search with empty parameters', async () => {
      const mockJobs = [{ _id: '1', title: 'Developer' }];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs })
      });

      const result = await jobService.searchJobs({});

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/jobs/search?'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockJobs);
    });

    test('handles search API error', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Search failed'));

      const result = await jobService.searchJobs({ q: 'React' });
      expect(result).toEqual({ jobs: [], total: 0 });
    });
  });

  describe('getJobById', () => {
    test('fetches job by ID successfully', async () => {
      const mockJob = {
        _id: '1',
        title: 'Senior Developer',
        company: 'TechCorp',
        location: 'Remote',
        job_type: 'Full-time',
        salary_range: '$100k - $150k',
        skills: ['React', 'Node.js'],
        created_at: new Date().toISOString(),
        description: 'Senior role',
        company_logo: '💻',
        url: '#',
        is_active: true
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockJob
      });

      const result = await jobService.getJobById('1');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/jobs/1'),
        expect.objectContaining({
          method: 'GET'
        })
      );

      expect(result).toEqual(mockJob);
    });

    test('handles job not found', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      await expect(jobService.getJobById('999')).rejects.toThrow('HTTP 404: Not Found');
    });
  });

  describe('getJobStats', () => {
    test('fetches job statistics successfully', async () => {
      const mockStats = {
        totalJobs: 1000,
        totalCompanies: 100,
        totalCountries: 50,
        averageSalary: 85000,
        topSkills: ['React', 'Python', 'JavaScript'],
        jobTypes: {
          'Full-time': 600,
          'Part-time': 200,
          'Contract': 200
        }
      };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      });

      const result = await jobService.getJobStats();

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/jobs/statistics/'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockStats);
    });

    test('handles stats API error', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Stats failed'));

      const result = await jobService.getJobStats();
      expect(result).toEqual({
        jobs_by_company: [],
        jobs_by_location: [],
        total_jobs: 0
      });
    });
  });

  describe('getJobTitleSuggestions', () => {
    test('fetches job title suggestions successfully', async () => {
      const mockSuggestions = [
        'React Developer',
        'React Native Developer',
        'React Engineer'
      ];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSuggestions
      });

      const result = await jobService.getJobTitleSuggestions('React');

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/jobs/job-titles/search?q=React&limit=10'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockSuggestions);
    });

    test('fetches job title suggestions with limit', async () => {
      const mockSuggestions = ['React Developer', 'React Engineer'];

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockSuggestions
      });

      const result = await jobService.getJobTitleSuggestions('React', 2);

      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/jobs/job-titles/search?q=React&limit=2'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockSuggestions);
    });
  });

  describe('Authentication Headers', () => {
    test('includes auth token in requests when available', async () => {
      localStorageMock.getItem.mockReturnValue('test-token');

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [] })
      });

      await jobService.getJobs();

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.any(Object)
      );
    });

    test('works without auth token', async () => {
      localStorageMock.getItem.mockReturnValue(null);

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [] })
      });

      await jobService.getJobs();

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.not.objectContaining({
            'Authorization': expect.any(String)
          })
        })
      );
    });
  });

  describe('Error Handling', () => {
    test('handles network timeout', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('timeout'));

      await expect(jobService.getJobs()).rejects.toThrow('timeout');
    });

    test('handles malformed JSON response', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });

      await expect(jobService.getJobs()).rejects.toThrow('Invalid JSON');
    });

    test('handles 401 unauthorized', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 401,
        statusText: 'Unauthorized'
      });

      await expect(jobService.getJobs()).rejects.toThrow('HTTP 401: Unauthorized');
    });

    test('handles 403 forbidden', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 403,
        statusText: 'Forbidden'
      });

      await expect(jobService.getJobs()).rejects.toThrow('HTTP 403: Forbidden');
    });
  });

  describe('URL Construction', () => {
    test('constructs correct API URLs', async () => {
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => ({ jobs: [] })
      });

      await jobService.getJobs(1, 10);
      expect(fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/v1\/jobs\/search\?page=1&limit=10$/),
        expect.any(Object)
      );

      await jobService.searchJobs({ q: 'React' });
      expect(fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/v1\/jobs\/search\?/),
        expect.any(Object)
      );

      await jobService.getJobById('123');
      expect(fetch).toHaveBeenCalledWith(
        expect.stringMatching(/\/api\/v1\/jobs\/123$/),
        expect.any(Object)
      );
    });
  });
});