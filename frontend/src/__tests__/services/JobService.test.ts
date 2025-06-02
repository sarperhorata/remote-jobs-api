import { JobService } from '../../services/jobService';

// Mock fetch globally
global.fetch = jest.fn();

describe('JobService', () => {
  beforeEach(() => {
    (fetch as jest.Mock).mockClear();
  });

  describe('getJobs', () => {
    it('should fetch jobs successfully', async () => {
      const mockJobs = [
        { id: '1', title: 'Software Engineer', company: 'TechCorp' },
        { id: '2', title: 'Product Manager', company: 'StartupCo' },
      ];
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ jobs: mockJobs }),
      } as any);

      const result = await JobService.getJobs();
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/?page=1&per_page=10',
        expect.any(Object)
      );
      expect(result).toEqual(mockJobs);
    });

    it('should handle fetch error', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));

      await expect(JobService.getJobs()).rejects.toThrow('Network error');
    });

    it('should handle non-200 response', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 500,
        statusText: 'Internal Server Error'
      });

      await expect(JobService.getJobs()).rejects.toThrow('HTTP 500: Internal Server Error');
    });

    it('should pass filters correctly', async () => {
      const filters = {
        location: 'Remote',
        company: 'TechCorp',
        search: 'developer'
      };

      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ jobs: [] }),
      } as any);

      await JobService.getJobs(1, 10, filters);
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/?page=1&per_page=10&location=Remote&company=TechCorp&search=developer',
        expect.any(Object)
      );
    });

    it('should handle empty response body', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => null
      });

      const result = await JobService.getJobs();
      expect(result).toEqual([]);
    });
  });

  describe('getJobById', () => {
    it('should fetch job by ID successfully', async () => {
      const mockJob = { id: '1', title: 'Software Engineer', company: 'TechCorp' };
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue(mockJob),
      } as any);

      const result = await JobService.getJobById('1');
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/1',
        expect.any(Object)
      );
      expect(result).toEqual(mockJob);
    });

    it('should handle job not found', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      await expect(JobService.getJobById('999')).rejects.toThrow('HTTP 404: Not Found');
    });
  });

  describe('searchJobs', () => {
    it('should search jobs successfully', async () => {
      const mockJobs = [
        { id: '1', title: 'React Developer', company: 'TechCorp' },
      ];
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ jobs: mockJobs, total: 1 }),
      } as any);

      const result = await JobService.searchJobs('react');
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/search?q=react',
        expect.any(Object)
      );
      expect(result).toEqual({ jobs: mockJobs, total: 1 });
    });

    it('should handle empty search query', async () => {
      const result = await JobService.searchJobs('');
      expect(result).toEqual({ jobs: [], total: 0 });
    });
  });

  describe('getJobStatistics', () => {
    it('should fetch job statistics successfully', async () => {
      const mockStats = {
        total_jobs: 1000,
        active_jobs: 800,
        positions: [
          { title: 'Software Engineer', count: 100 }
        ]
      };
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue(mockStats),
      } as any);

      const result = await JobService.getJobStatistics();
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/statistics',
        expect.any(Object)
      );
      expect(result).toEqual(mockStats);
    });
  });

  describe('createJob', () => {
    it('should create job successfully', async () => {
      const jobData = {
        title: 'New Job',
        company: 'New Company',
        description: 'Job description'
      };
      
      const mockResponse = { ...jobData, id: '1' };
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await JobService.createJob(jobData);
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(jobData)
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle creation error', async () => {
      const jobData = { title: '', company: '', description: '' };

      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 422,
        statusText: 'Validation Error'
      });

      await expect(JobService.createJob(jobData)).rejects.toThrow('HTTP 422: Validation Error');
    });
  });

  describe('updateJob', () => {
    it('should update job successfully', async () => {
      const jobData = { title: 'Updated Title' };
      const mockResponse = { id: '1', ...jobData };
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await JobService.updateJob('1', jobData);
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/1',
        expect.objectContaining({
          method: 'PUT',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(jobData)
        })
      );
      expect(result).toEqual(mockResponse);
    });
  });

  describe('deleteJob', () => {
    it('should delete job successfully', async () => {
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({}),
      } as any);

      await JobService.deleteJob('1');
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/1',
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });

    it('should handle delete error', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        status: 404,
        statusText: 'Not Found'
      });

      await expect(JobService.deleteJob('999')).rejects.toThrow('HTTP 404: Not Found');
    });
  });

  describe('applyToJob', () => {
    it('should apply to job successfully', async () => {
      const applicationData = {
        coverLetter: 'I am interested in this position.',
        resume: 'Resume content'
      };
      
      const mockResponse = { id: '1', status: 'submitted' };
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue(mockResponse),
      } as any);

      const result = await JobService.applyToJob('1', applicationData);
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/1/apply',
        expect.objectContaining({
          method: 'POST',
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          }),
          body: JSON.stringify(applicationData)
        })
      );
      expect(result.status).toBe('submitted');
    });
  });

  describe('getMyApplications', () => {
    it('should fetch user applications successfully', async () => {
      const mockApplications = [
        { id: '1', job_id: '1', status: 'pending' },
        { id: '2', job_id: '2', status: 'approved' },
      ];
      
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ applications: mockApplications }),
      } as any);

      const result = await JobService.getMyApplications();
      
      expect(fetch).toHaveBeenCalledWith(
        'http://localhost:8001/api/jobs/applications',
        expect.any(Object)
      );
      expect(result.applications).toEqual(mockApplications);
    });
  });

  describe('error handling', () => {
    it('should handle network timeout', async () => {
      (fetch as jest.Mock).mockImplementationOnce(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Request timeout')), 100)
        )
      );

      await expect(JobService.getJobs()).rejects.toThrow('Request timeout');
    });

    it('should handle malformed JSON response', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => {
          throw new Error('Invalid JSON');
        }
      });

      await expect(JobService.getJobs()).rejects.toThrow('Invalid JSON');
    });
  });

  describe('API endpoint configuration', () => {
    it('should include correct headers', async () => {
      // Mock successful response
      (fetch as jest.MockedFunction<typeof fetch>).mockResolvedValue({
        ok: true,
        json: jest.fn().mockResolvedValue({ jobs: [] })
      } as any);

      await JobService.getJobs();

      expect(fetch).toHaveBeenCalledWith(
        expect.any(String),
        expect.objectContaining({
          headers: expect.objectContaining({
            'Content-Type': 'application/json'
          })
        })
      );
    });
  });
}); 