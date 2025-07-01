import { API_BASE_URL } from '../../utils/apiConfig';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Simple API service for testing
class ApiService {
  static async get(endpoint: string) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`);
    return response.json();
  }

  static async post(endpoint: string, data: any) {
    const response = await fetch(`${API_BASE_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
    });
    return response.json();
  }
}

describe('API Service Tests', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  it('should make GET requests correctly', async () => {
    const mockData = { message: 'success' };
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: jest.fn().mockResolvedValue(mockData),
    });

    const result = await ApiService.get('/test');

    expect(mockFetch).toHaveBeenCalledWith(`${API_BASE_URL}/test`);
    expect(result).toEqual(mockData);
  });

  it('should make POST requests correctly', async () => {
    const mockData = { id: 1, title: 'Test Job' };
    const postData = { title: 'New Job' };
    
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: jest.fn().mockResolvedValue(mockData),
    });

    const result = await ApiService.post('/jobs', postData);

    expect(mockFetch).toHaveBeenCalledWith(`${API_BASE_URL}/jobs`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(postData),
    });
    expect(result).toEqual(mockData);
  });

  it('should handle API errors gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    await expect(ApiService.get('/error')).rejects.toThrow('Network error');
  });
});
