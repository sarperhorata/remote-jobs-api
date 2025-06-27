import { jobService } from '../../services/jobService';

jest.mock('../../utils/apiConfig', () => ({
  getApiUrl: jest.fn().mockResolvedValue('http://localhost:8001/api')
}));

let mockFetch = jest.fn();
global.fetch = mockFetch;

describe('jobService', () => {
  beforeEach(() => {
    (mockFetch as jest.Mock).mockClear();
    // Reset the mock to always return the correct URL
    (mockFetch as jest.Mock).mockResolvedValue('http://localhost:8001/api');
  });

  describe('getJobs', () => {
    it('should fetch jobs successfully with default parameters', async () => {
      const mockJobs = {
        jobs: [{ id: '1', title: 'Software Engineer', company: 'TechCorp' }],
        total: 1,
        page: 1,
        pages: 1
      };

      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockJobs
      });

      const result = await jobService.getJobs();
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/?page=1&per_page=10',
        expect.any(Object)
      );
      expect(result).toEqual(mockJobs.jobs);
    });

    it('should handle network errors', async () => {
      (mockFetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(jobService.getJobs()).rejects.toThrow('Network error');
    });

    it('should handle API errors', async () => {
      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      await expect(jobService.getJobs()).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    it('should pass filters correctly', async () => {
      const filters = {
        location: 'Remote',
        company: 'TechCorp',
        search: 'developer'
      };

      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: [], total: 0, page: 1, pages: 0 })
      });

      await jobService.getJobs(1, 10, filters);
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/?page=1&per_page=10&location=Remote&company=TechCorp&search=developer',
        expect.any(Object)
      );
    });
  });

  describe('getJobById', () => {
    it('should fetch a single job successfully', async () => {
      const mockJob = { id: '1', title: 'Software Engineer', company: 'TechCorp' };

      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockJob
      });

      const result = await jobService.getJobById('1');
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/1',
        expect.any(Object)
      );
      expect(result).toEqual(mockJob);
    });

    it('should handle job not found', async () => {
      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      await expect(jobService.getJobById('999')).rejects.toThrow('HTTP 404: Not Found');
    });
  });

  describe('searchJobs', () => {
    it('should search jobs successfully', async () => {
      const mockResults = {
        jobs: [{ id: '1', title: 'React Developer' }],
        total: 1
      };

      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResults
      });

      const result = await jobService.searchJobs('react');
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/search?q=react',
        expect.any(Object)
      );
      expect(result).toEqual(mockResults);
    });
  });

  describe('getJobStatistics', () => {
    it('should fetch job statistics successfully', async () => {
      const mockStats = {
        total_jobs: 100,
        total_companies: 50,
        locations: ['Remote', 'New York'],
        categories: ['Engineering', 'Design']
      };

      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockStats
      });

      const result = await jobService.getJobStatistics();
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/statistics',
        expect.any(Object)
      );
      expect(result).toEqual(mockStats);
    });
  });

  describe('getFeaturedJobs', () => {
    it('should fetch featured jobs successfully', async () => {
      const mockJobs = [
        { id: '1', title: 'Senior Engineer', featured: true },
        { id: '2', title: 'Tech Lead', featured: true }
      ];

      // Mock getJobs function response
      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ jobs: mockJobs })
      });

      const result = await jobService.getFeaturedJobs();
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/?limit=3'
      );
      expect(result).toEqual(mockJobs);
    });
  });

  describe('applyToJob', () => {
    it('should apply to job successfully', async () => {
      const applicationData = {
        coverLetter: 'I am interested in this position...',
        resume: 'resume.pdf'
      };
      const mockResponse = { success: true, applicationId: '123' };

      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await jobService.applyToJob('1', applicationData);
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/1/apply',
        expect.objectContaining({
          method: 'POST',
          body: JSON.stringify(applicationData)
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('getMyApplications', () => {
    it('should fetch user applications successfully', async () => {
      const mockApplications = [
        { id: '1', jobId: '1', status: 'pending' },
        { id: '2', jobId: '2', status: 'reviewed' }
      ];

      (mockFetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ applications: mockApplications })
      });

      const result = await jobService.getMyApplications();
      
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/applications',
        expect.any(Object)
      );
      expect(result).toEqual({ applications: mockApplications });
    });
  });

  describe('config', () => {
    it('should have correct base URL', async () => {
      const baseURL = await jobService.getBaseURL();
      expect(baseURL).toBe('http://localhost:8001/api');
    });
  });
}); 