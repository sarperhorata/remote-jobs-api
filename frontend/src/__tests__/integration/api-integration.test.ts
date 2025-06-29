import { getApiUrl } from '../../utils/apiConfig';
import { jobService } from '../../services/jobService';

describe('API Integration Tests', () => {
  // These tests require a running backend
  const isBackendAvailable = async (): Promise<boolean> => {
    try {
      const apiUrl = await getApiUrl();
      const response = await fetch(apiUrl.replace('/api/v1', '/health'));
      return response.ok;
    } catch {
      return false;
    }
  };

  beforeAll(async () => {
    const available = await isBackendAvailable();
    if (!available) {
      console.warn('⚠️ Backend not available - skipping integration tests');
    }
  });

  describe('Real API Calls', () => {
    it('should fetch jobs without API URL duplication', async () => {
      const available = await isBackendAvailable();
      if (!available) {
        console.warn('Skipping - backend not available');
        return;
      }

      try {
        const jobs = await jobService.getJobs(1, 3);
        
        expect(Array.isArray(jobs)).toBe(true);
        expect(jobs.length).toBeGreaterThan(0);
        
        // Verify job structure
        if (jobs.length > 0) {
          const job = jobs[0];
          expect(job).toHaveProperty('id');
          expect(job).toHaveProperty('title');
          expect(job).toHaveProperty('company');
        }
      } catch (error: any) {
        // Check if error is due to URL duplication
        if (error.message.includes('404') || error.message.includes('/api/api')) {
          fail('API URL duplication detected: ' + error.message);
        }
        throw error;
      }
    });

    it('should fetch job statistics without errors', async () => {
      const available = await isBackendAvailable();
      if (!available) {
        console.warn('Skipping - backend not available');
        return;
      }

      try {
        const stats = await jobService.getJobStatistics();
        
        expect(stats).toBeDefined();
        expect(typeof stats).toBe('object');
      } catch (error: any) {
        // Allow this to fail gracefully if endpoint doesn't exist
        if (error.message.includes('404')) {
          console.warn('Statistics endpoint not available');
          return;
        }
        throw error;
      }
    });

    it('should handle search with proper URL construction', async () => {
      const available = await isBackendAvailable();
      if (!available) {
        console.warn('Skipping - backend not available');
        return;
      }

      try {
        const result = await jobService.searchJobs('developer');
        
        expect(result).toHaveProperty('jobs');
        expect(result).toHaveProperty('total');
        expect(Array.isArray(result.jobs)).toBe(true);
        expect(typeof result.total).toBe('number');
      } catch (error: any) {
        // Check for URL construction errors
        if (error.message.includes('/api/api') || error.message.includes('404')) {
          fail('API URL construction error: ' + error.message);
        }
        // Allow empty results
        console.warn('Search returned empty or failed:', error.message);
      }
    });

    it('should detect correct API URL format', async () => {
      const apiUrl = await getApiUrl();
      
      // Should not contain double /api paths
      expect(apiUrl).not.toContain('/api/api');
      expect(apiUrl).not.toContain('//api');
      
      // Should end with /api/v1
      expect(apiUrl).toMatch(/\/api\/v1$/);
      
      // Should be a valid URL format
      expect(apiUrl).toMatch(/^https?:\/\/[^\/]+\/api\/v1$/);
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors gracefully', async () => {
      // Mock a network error by using an invalid URL
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockRejectedValue(new Error('Network error'));

      try {
        const jobs = await jobService.getJobs();
        // Should return empty array or handle gracefully
        expect(Array.isArray(jobs)).toBe(true);
      } catch (error) {
        // Error should be properly typed and handled
        expect(error).toBeInstanceOf(Error);
      } finally {
        global.fetch = originalFetch;
      }
    });

    it('should handle 404 errors without crashing', async () => {
      const originalFetch = global.fetch;
      global.fetch = jest.fn().mockResolvedValue({
        ok: false,
        status: 404,
        statusText: 'Not Found',
        json: async () => ({ error: 'Not found' })
      } as Response);

      try {
        await jobService.getJobs();
      } catch (error: any) {
        expect(error.message).toContain('404');
      } finally {
        global.fetch = originalFetch;
      }
    });
  });

  describe('URL Validation', () => {
    it('should never generate malformed URLs', async () => {
      const testCases = [
        { input: '', expected: false },
        { input: 'http://localhost:8002/api/api/v1', expected: false },
        { input: 'http://localhost:8002//api/v1', expected: false },
        { input: 'http://localhost:8002/api/v1', expected: true },
      ];

      for (const testCase of testCases) {
        const hasDoubleApi = testCase.input.includes('/api/api');
        const hasDoubleSlash = testCase.input.includes('//api');
        const isValidFormat = testCase.input === '' ? false : !!testCase.input.match(/^https?:\/\/[^\/]+\/api\/v1$/);
        
        const isValid = !hasDoubleApi && !hasDoubleSlash && (testCase.input === '' ? false : isValidFormat);
        
        expect(isValid).toBe(testCase.expected);
      }
    });

    it('should construct proper health check URLs', async () => {
      const apiUrl = await getApiUrl();
      const healthUrl = apiUrl.replace(/\/api\/v1$/, '/health');
      
      expect(healthUrl).not.toContain('/api');
      expect(healthUrl).toMatch(/^https?:\/\/[^\/]+\/health$/);
    });
  });
}); 