import { 
  searchJobs, 
  getJobById, 
  getJobsByCompany, 
  getSavedJobs,
  saveJob,
  unsaveJob,
  applyToJob,
  getJobRecommendations
} from '../../services/jobService';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};

// Mock window.localStorage
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
  writable: true
});

describe('jobService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockFetch.mockClear();
    // Reset localStorage mock
    localStorageMock.getItem.mockReturnValue('mock-token');
    localStorageMock.setItem.mockClear();
    localStorageMock.removeItem.mockClear();
    localStorageMock.clear.mockClear();
  });

  describe('searchJobs', () => {
    test('successfully searches jobs with filters', async () => {
      const mockJobs = [
        {
          id: '1',
          title: 'React Developer',
          company: 'Tech Corp',
          location: 'Remote',
          salary: '$80k - $120k'
        }
      ];

      const mockResponse = {
        jobs: mockJobs,
        total: 1,
        page: 1,
        total_pages: 1
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const filters = {
        query: 'react',
        location: 'remote',
        jobType: 'full-time',
        workType: 'remote'
      };

      const result = await searchJobs(filters, 1);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8001/api/v1/jobs/search'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles search error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' })
      });

      await expect(searchJobs({}, 1)).rejects.toThrow('Internal server error');
    });

    test('handles network error', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(searchJobs({}, 1)).rejects.toThrow('Network error');
    });
  });

  describe('getJobById', () => {
    test('successfully gets job by id', async () => {
      const mockJob = {
        id: '1',
        title: 'React Developer',
        company: 'Tech Corp',
        location: 'Remote',
        salary: '$80k - $120k',
        description: 'We are looking for a React developer...',
        requirements: ['React', 'TypeScript'],
        benefits: ['Health Insurance', '401k']
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockJob
      });

      const result = await getJobById('1');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8001/api/v1/jobs/1'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockJob);
    });

    test('handles job not found error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Job not found' })
      });

      await expect(getJobById('999')).rejects.toThrow('Job not found');
    });
  });

  describe('getJobsByCompany', () => {
    test('successfully gets jobs by company', async () => {
      const mockJobs = [
        {
          id: '1',
          title: 'React Developer',
          company: 'Tech Corp',
          location: 'Remote'
        }
      ];

      const mockResponse = {
        jobs: mockJobs,
        total: 1,
        company: {
          name: 'Tech Corp',
          description: 'A great company'
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await getJobsByCompany('tech-corp');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8001/api/v1/companies/tech-corp/jobs'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles company not found error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Company not found' })
      });

      await expect(getJobsByCompany('nonexistent')).rejects.toThrow('Company not found');
    });
  });

  describe('getSavedJobs', () => {
    test('successfully gets saved jobs', async () => {
      const mockJobs = [
        {
          id: '1',
          title: 'React Developer',
          company: 'Tech Corp',
          saved_at: '2024-01-01T00:00:00Z'
        }
      ];

      const mockResponse = {
        jobs: mockJobs,
        total: 1
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await getSavedJobs();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8001/api/v1/jobs/saved'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles unauthorized error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 401,
        json: async () => ({ detail: 'Unauthorized' })
      });

      await expect(getSavedJobs()).rejects.toThrow('Unauthorized');
    });
  });

  describe('saveJob', () => {
    test('successfully saves job', async () => {
      const mockResponse = {
        message: 'Job saved successfully',
        job_id: '1'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await saveJob('1');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8001/api/v1/jobs/1/save'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles job already saved error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Job already saved' })
      });

      await expect(saveJob('1')).rejects.toThrow('Job already saved');
    });
  });

  describe('unsaveJob', () => {
    test('successfully unsaves job', async () => {
      const mockResponse = {
        message: 'Job removed from saved jobs',
        job_id: '1'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await unsaveJob('1');

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8001/api/v1/jobs/1/unsave'),
        expect.objectContaining({
          method: 'DELETE',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles job not saved error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Job not found in saved jobs' })
      });

      await expect(unsaveJob('1')).rejects.toThrow('Job not found in saved jobs');
    });
  });

  describe('applyToJob', () => {
    test('successfully applies to job', async () => {
      const mockResponse = {
        message: 'Application submitted successfully',
        application_id: 'app-123'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const applicationData = {
        cover_letter: 'I am interested in this position...',
        resume_url: 'https://example.com/resume.pdf'
      };

      const result = await applyToJob('1', applicationData);

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/v1/jobs/1/apply'),
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token',
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(applicationData)
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles already applied error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Already applied to this job' })
      });

      await expect(applyToJob('1', {})).rejects.toThrow('Already applied to this job');
    });
  });

  describe('getJobRecommendations', () => {
    test('successfully gets job recommendations', async () => {
      const mockJobs = [
        {
          id: '1',
          title: 'React Developer',
          company: 'Tech Corp',
          location: 'Remote',
          match_score: 0.95
        }
      ];

      const mockResponse = {
        jobs: mockJobs,
        total: 1
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await getJobRecommendations();

      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('http://localhost:8001/api/v1/jobs/recommendations'),
        expect.objectContaining({
          method: 'GET',
          headers: expect.objectContaining({
            'Authorization': 'Bearer mock-token'
          })
        })
      );

      expect(result).toEqual(mockResponse);
    });

    test('handles no recommendations available', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [], total: 0 })
      });

      const result = await getJobRecommendations();

      expect(result.jobs).toEqual([]);
      expect(result.total).toBe(0);
    });
  });
});