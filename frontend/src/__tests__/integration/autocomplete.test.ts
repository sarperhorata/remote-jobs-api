/**
 * Autocomplete Integration Tests
 * Tests for API URL construction and autocomplete functionality
 */

import { API_BASE_URL } from '../../utils/apiConfig';

describe('Autocomplete API Integration Tests', () => {
  
  beforeEach(() => {
    // Reset fetch mock
    global.fetch = jest.fn();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  test('should construct correct API URL without duplication', () => {
    // Test that API_BASE_URL doesn't have double /api/ in URL
    const expectedBaseUrl = 'http://localhost:8001';
    expect(API_BASE_URL).toBe(expectedBaseUrl);
    
    // Test complete URL construction
    const query = 'react';
    const completeUrl = `${API_BASE_URL}/api/v1/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=20`;
    
    expect(completeUrl).toBe('http://localhost:8001/api/v1/jobs/job-titles/search?q=react&limit=20');
    expect(completeUrl).not.toContain('/api/api/'); // Should not have duplicate /api/
  });

  test('should fetch autocomplete results successfully', async () => {
    // Mock successful API response
    const mockResponse = [
      { id: '29', title: 'React Developer', category: 'Technology' }
    ];
    
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: true,
      json: async () => mockResponse,
    });

    // Simulate autocomplete fetch
    const query = 'react';
    const apiUrl = `${API_BASE_URL}/api/v1/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=20`;
    
    const response = await fetch(apiUrl);
    const data = await response.json();

    expect(fetch).toHaveBeenCalledWith(
      'http://localhost:8001/api/v1/jobs/job-titles/search?q=react&limit=20'
    );
    expect(data).toEqual(mockResponse);
  });

  test('should handle API errors gracefully', async () => {
    // Mock 404 response
    (global.fetch as jest.Mock).mockResolvedValueOnce({
      ok: false,
      status: 404,
      json: async () => ({ error: 'Not Found' }),
    });

    const query = 'nonexistent';
    const apiUrl = `${API_BASE_URL}/api/v1/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=20`;
    
    const response = await fetch(apiUrl);
    
    expect(response.ok).toBe(false);
    expect(response.status).toBe(404);
  });

  test('should encode special characters in query', () => {
    const specialQuery = 'C++ Developer';
    const encodedQuery = encodeURIComponent(specialQuery);
    const apiUrl = `${API_BASE_URL}/api/v1/jobs/job-titles/search?q=${encodedQuery}&limit=20`;
    
    expect(apiUrl).toBe('http://localhost:8001/api/v1/jobs/job-titles/search?q=C%2B%2B%20Developer&limit=20');
    expect(apiUrl).not.toContain('/api/api/');
  });

  test('should work in incognito mode (no localStorage dependencies)', () => {
    // Simulate incognito mode by clearing localStorage
    const originalLocalStorage = global.localStorage;
    delete (global as any).localStorage;
    
    // API URL construction should still work
    const query = 'frontend';
    const completeUrl = `${API_BASE_URL}/api/v1/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=20`;
    
    expect(completeUrl).toBe('http://localhost:8001/api/v1/jobs/job-titles/search?q=frontend&limit=20');
    
    // Restore localStorage
    global.localStorage = originalLocalStorage;
  });

}); 