import { getApiUrl, clearApiUrlCache, checkBackendHealth, API_BASE_URL } from '../../utils/apiConfig';

// Mock fetch
global.fetch = jest.fn();
const mockFetch = fetch as jest.MockedFunction<typeof fetch>;

describe('API Configuration', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    clearApiUrlCache();
    // Mock console to avoid noise
    jest.spyOn(console, 'log').mockImplementation(() => {});
    jest.spyOn(console, 'warn').mockImplementation(() => {});
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('getApiUrl', () => {
    it('should return correct API URL format', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      } as Response);

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toMatch(/^http:\/\/localhost:\d+\/api\/v1$/);
      expect(apiUrl).not.toContain('/api/api/v1');
      expect(apiUrl).not.toContain('//api');
    });

    it('should not contain double /api paths', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      } as Response);

      const apiUrl = await getApiUrl();
      
      // Ensure no double /api paths
      expect(apiUrl).not.toContain('/api/api');
      expect(apiUrl).not.toContain('api/v1/api');
      
      // Ensure proper format
      expect(apiUrl.split('/api/v1')).toHaveLength(2);
    });

    it('should use environment variable when available', async () => {
      const originalEnv = process.env.REACT_APP_API_URL;
      process.env.REACT_APP_API_URL = 'http://custom-api.com';

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toBe('http://custom-api.com/api/v1');
      
      process.env.REACT_APP_API_URL = originalEnv;
    });

    it('should handle environment variable with /api/v1 suffix', async () => {
      const originalEnv = process.env.REACT_APP_API_URL;
      process.env.REACT_APP_API_URL = 'http://custom-api.com/api/v1';

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toBe('http://custom-api.com/api/v1');
      expect(apiUrl).not.toContain('/api/v1/api/v1');
      
      process.env.REACT_APP_API_URL = originalEnv;
    });

    it('should cache API URL after first detection', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      } as Response);

      const url1 = await getApiUrl();
      const url2 = await getApiUrl();
      
      expect(url1).toBe(url2);
      expect(mockFetch).toHaveBeenCalledTimes(1); // Only one health check
    });

    it('should test multiple ports in order', async () => {
      // Mock first few ports to fail, last one to succeed
      mockFetch
        .mockRejectedValueOnce(new Error('Connection refused'))
        .mockRejectedValueOnce(new Error('Connection refused'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'healthy' }),
        } as Response);

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toMatch(/^http:\/\/localhost:\d+\/api\/v1$/);
      expect(mockFetch).toHaveBeenCalledTimes(3);
    });

    it('should fall back to default port when all ports fail', async () => {
      mockFetch.mockRejectedValue(new Error('Connection refused'));

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toBe('http://localhost:8001/api/v1');
      expect(console.warn).toHaveBeenCalledWith(
        expect.stringContaining('No backend found, using default URL')
      );
    });

    it('should handle test environment correctly', async () => {
      // Test environment is already set by Jest
      // Skip this test or adjust expectations
      const apiUrl = await getApiUrl();
      
      // In test environment, it should return the fallback URL
      expect(apiUrl).toMatch(/^http:\/\/localhost:\d+\/api\/v1$/);
    });
  });

  describe('clearApiUrlCache', () => {
    it('should clear cached API URL', async () => {
      mockFetch.mockResolvedValue({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      } as Response);

      // First call
      await getApiUrl();
      expect(mockFetch).toHaveBeenCalledTimes(1);

      // Second call should use cache
      await getApiUrl();
      expect(mockFetch).toHaveBeenCalledTimes(1);

      // Clear cache
      clearApiUrlCache();

      // Third call should make new request
      await getApiUrl();
      expect(mockFetch).toHaveBeenCalledTimes(2);
    });
  });

  describe('checkBackendHealth', () => {
    it('should return true for healthy backend', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      } as Response);

      const isHealthy = await checkBackendHealth('http://localhost:8002/api/v1');
      
      expect(isHealthy).toBe(true);
      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8002/health',
        expect.objectContaining({
          method: 'GET'
        })
      );
    });

    it('should return false for unhealthy backend', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
      } as Response);

      const isHealthy = await checkBackendHealth('http://localhost:8002/api/v1');
      
      expect(isHealthy).toBe(false);
    });

    it('should return false for network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      const isHealthy = await checkBackendHealth('http://localhost:8002/api/v1');
      
      expect(isHealthy).toBe(false);
      expect(console.error).toHaveBeenCalledWith(
        'Backend health check failed:',
        expect.any(Error)
      );
    });

    it('should use detected API URL when no URL provided', async () => {
      mockFetch
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'healthy' }),
        } as Response)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'healthy' }),
        } as Response);

      const isHealthy = await checkBackendHealth();
      
      expect(isHealthy).toBe(true);
      expect(mockFetch).toHaveBeenCalledTimes(2); // One for getApiUrl, one for health check
    });
  });

  describe('API_BASE_URL constant', () => {
    it('should have correct fallback value', () => {
      expect(API_BASE_URL).toBe('http://localhost:8001');
      expect(API_BASE_URL).not.toContain('/api/v1');
    });
  });

  describe('URL Construction Edge Cases', () => {
    it('should handle URLs with trailing slashes', async () => {
      const originalEnv = process.env.REACT_APP_API_URL;
      process.env.REACT_APP_API_URL = 'http://custom-api.com/';

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toBe('http://custom-api.com/api/v1');
      expect(apiUrl).not.toContain('//api');
      
      process.env.REACT_APP_API_URL = originalEnv;
    });

    it('should handle URLs without trailing slashes', async () => {
      const originalEnv = process.env.REACT_APP_API_URL;
      process.env.REACT_APP_API_URL = 'http://custom-api.com';

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toBe('http://custom-api.com/api/v1');
      
      process.env.REACT_APP_API_URL = originalEnv;
    });

    it('should handle malformed environment URLs', async () => {
      const originalEnv = process.env.REACT_APP_API_URL;
      process.env.REACT_APP_API_URL = 'not-a-url';

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toBe('not-a-url/api/v1');
      
      process.env.REACT_APP_API_URL = originalEnv;
    });
  });

  describe('Concurrent Requests', () => {
    it('should handle concurrent getApiUrl calls', async () => {
      let resolvePromise: (value: any) => void;
      const mockPromise = new Promise((resolve) => {
        resolvePromise = resolve;
      });

      mockFetch.mockReturnValueOnce(mockPromise);

      // Start multiple concurrent requests
      const promise1 = getApiUrl();
      const promise2 = getApiUrl();
      const promise3 = getApiUrl();

      // Resolve the mock
      resolvePromise!({
        ok: true,
        json: async () => ({ status: 'healthy' }),
      } as Response);

      const [url1, url2, url3] = await Promise.all([promise1, promise2, promise3]);
      
      expect(url1).toBe(url2);
      expect(url2).toBe(url3);
      expect(mockFetch).toHaveBeenCalledTimes(1); // Only one actual request
    });
  });

  describe('Error Recovery', () => {
    it('should recover from temporary network errors', async () => {
      mockFetch
        .mockRejectedValueOnce(new Error('Temporary network error'))
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'healthy' }),
        } as Response);

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toMatch(/^http:\/\/localhost:\d+\/api\/v1$/);
    });

    it('should handle timeout errors', async () => {
      const timeoutError = new Error('Request timeout');
      timeoutError.name = 'AbortError';
      
      mockFetch
        .mockRejectedValueOnce(timeoutError)
        .mockResolvedValueOnce({
          ok: true,
          json: async () => ({ status: 'healthy' }),
        } as Response);

      const apiUrl = await getApiUrl();
      
      expect(apiUrl).toMatch(/^http:\/\/localhost:\d+\/api\/v1$/);
    });
  });
}); 