import { jobService } from '../../services/AllServices';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

describe('JobService', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockLocalStorage.getItem.mockClear();
    mockLocalStorage.setItem.mockClear();
    mockLocalStorage.removeItem.mockClear();
  });

  describe('getJobs', () => {
    it('fetches jobs successfully', async () => {
      const mockJobs = [
        {
          _id: '1',
          title: 'Senior Frontend Developer',
          company: { name: 'TechCorp' },
          location: 'Remote',
          job_type: 'Full-time',
          salary_min: 80000,
          salary_max: 120000,
          created_at: '2024-01-15T10:00:00Z'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockJobs
      });

      const result = await jobService.getJobs();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockJobs);
    });

    it('fetches jobs with filters', async () => {
      const filters = {
        keywords: 'React',
        location: 'Remote',
        jobType: 'Full-time',
        experienceLevel: 'Senior',
        salaryMin: 80000,
        salaryMax: 120000,
        isRemote: true,
        skills: ['React', 'TypeScript']
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

      await jobService.getJobs(filters);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs?keywords=React&location=Remote&jobType=Full-time&experienceLevel=Senior&salaryMin=80000&salaryMax=120000&isRemote=true&skills=React,TypeScript'),
        expect.any(Object)
      );
    });

    it('handles API error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(jobService.getJobs()).rejects.toThrow('Network error');
    });

    it('handles non-ok response', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      await expect(jobService.getJobs()).rejects.toThrow('Failed to fetch jobs');
    });
  });

  describe('getJobById', () => {
    it('fetches job by ID successfully', async () => {
      const mockJob = {
        _id: '1',
        title: 'Senior Frontend Developer',
        company: { name: 'TechCorp' },
        location: 'Remote',
        job_type: 'Full-time',
        description: 'We are looking for a senior frontend developer...',
        requirements: ['React', 'TypeScript', '5+ years experience'],
        benefits: ['Health insurance', 'Remote work'],
        created_at: '2024-01-15T10:00:00Z'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockJob
      });

      const result = await jobService.getJobById('1');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/1'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );

      expect(result).toEqual(mockJob);
    });

    it('handles job not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      await expect(jobService.getJobById('999')).rejects.toThrow('Job not found');
    });
  });

  describe('searchJobs', () => {
    it('searches jobs with query', async () => {
      const searchQuery = 'React Developer';
      const mockResults = [
        {
          _id: '1',
          title: 'React Developer',
          company: { name: 'TechCorp' },
          location: 'Remote'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults
      });

      const result = await jobService.searchJobs(searchQuery);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/jobs/search?q=${encodeURIComponent(searchQuery)}`),
        expect.any(Object)
      );

      expect(result).toEqual(mockResults);
    });

    it('handles empty search query', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

      const result = await jobService.searchJobs('');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/search?q='),
        expect.any(Object)
      );

      expect(result).toEqual([]);
    });
  });

  describe('getSimilarJobs', () => {
    it('fetches similar jobs', async () => {
      const jobId = '1';
      const mockSimilarJobs = [
        {
          _id: '2',
          title: 'Frontend Developer',
          company: { name: 'AnotherCorp' },
          location: 'Remote'
        }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSimilarJobs
      });

      const result = await jobService.getSimilarJobs(jobId);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/jobs/${jobId}/similar`),
        expect.any(Object)
      );

      expect(result).toEqual(mockSimilarJobs);
    });
  });

  describe('applyForJob', () => {
    it('applies for job successfully', async () => {
      const jobId = '1';
      const applicationData = {
        coverLetter: 'I am interested in this position...',
        resume: 'resume.pdf',
        portfolio: 'https://example.com/portfolio'
      };

      mockLocalStorage.getItem.mockReturnValue('mock-token');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Application submitted successfully' })
      });

      const result = await jobService.applyForJob(jobId, applicationData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/jobs/${jobId}/apply`),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json',
            'Authorization': 'Bearer mock-token'
          }),
          body: JSON.stringify(applicationData)
        })
      );

      expect(result).toEqual({ message: 'Application submitted successfully' });
    });

    it('handles unauthorized application', async () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      await expect(jobService.applyForJob('1', {})).rejects.toThrow('Authentication required');
    });

    it('handles application error', async () => {
      mockLocalStorage.getItem.mockReturnValue('mock-token');

      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ error: 'Invalid application data' })
      });

      await expect(jobService.applyForJob('1', {})).rejects.toThrow('Invalid application data');
    });
  });

  describe('saveJob', () => {
    it('saves job successfully', async () => {
      const jobId = '1';
      mockLocalStorage.getItem.mockReturnValue('mock-token');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Job saved successfully' })
      });

      const result = await jobService.saveJob(jobId);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/jobs/${jobId}/save`),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual({ message: 'Job saved successfully' });
    });

    it('handles unauthorized save', async () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      await expect(jobService.saveJob('1')).rejects.toThrow('Authentication required');
    });
  });

  describe('unsaveJob', () => {
    it('unsaves job successfully', async () => {
      const jobId = '1';
      mockLocalStorage.getItem.mockReturnValue('mock-token');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Job unsaved successfully' })
      });

      const result = await jobService.unsaveJob(jobId);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining(`/api/jobs/${jobId}/save`),
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual({ message: 'Job unsaved successfully' });
    });
  });

  describe('getSavedJobs', () => {
    it('fetches saved jobs successfully', async () => {
      const mockSavedJobs = [
        {
          _id: '1',
          title: 'Senior Frontend Developer',
          company: { name: 'TechCorp' },
          location: 'Remote'
        }
      ];

      mockLocalStorage.getItem.mockReturnValue('mock-token');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSavedJobs
      });

      const result = await jobService.getSavedJobs();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/saved'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockSavedJobs);
    });

    it('handles unauthorized access', async () => {
      mockLocalStorage.getItem.mockReturnValue(null);

      await expect(jobService.getSavedJobs()).rejects.toThrow('Authentication required');
    });
  });

  describe('getAppliedJobs', () => {
    it('fetches applied jobs successfully', async () => {
      const mockAppliedJobs = [
        {
          _id: '1',
          title: 'Senior Frontend Developer',
          company: { name: 'TechCorp' },
          location: 'Remote',
          applicationStatus: 'pending'
        }
      ];

      mockLocalStorage.getItem.mockReturnValue('mock-token');

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockAppliedJobs
      });

      const result = await jobService.getAppliedJobs();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/applied'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockAppliedJobs);
    });
  });

  describe('getJobStats', () => {
    it('fetches job statistics', async () => {
      const mockStats = {
        totalJobs: 1000,
        remoteJobs: 500,
        fullTimeJobs: 800,
        averageSalary: 85000
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      });

      const result = await jobService.getJobStats();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/stats'),
        expect.any(Object)
      );

      expect(result).toEqual(mockStats);
    });
  });

  describe('getJobCategories', () => {
    it('fetches job categories', async () => {
      const mockCategories = [
        { name: 'Technology', count: 500 },
        { name: 'Marketing', count: 200 },
        { name: 'Sales', count: 150 }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockCategories
      });

      const result = await jobService.getJobCategories();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/categories'),
        expect.any(Object)
      );

      expect(result).toEqual(mockCategories);
    });
  });

  describe('getJobLocations', () => {
    it('fetches job locations', async () => {
      const mockLocations = [
        { name: 'Remote', count: 500 },
        { name: 'New York, NY', count: 200 },
        { name: 'San Francisco, CA', count: 150 }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockLocations
      });

      const result = await jobService.getJobLocations();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/locations'),
        expect.any(Object)
      );

      expect(result).toEqual(mockLocations);
    });
  });

  describe('getJobSkills', () => {
    it('fetches job skills', async () => {
      const mockSkills = [
        { name: 'React', count: 300 },
        { name: 'JavaScript', count: 250 },
        { name: 'Python', count: 200 }
      ];

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockSkills
      });

      const result = await jobService.getJobSkills();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/skills'),
        expect.any(Object)
      );

      expect(result).toEqual(mockSkills);
    });
  });
});