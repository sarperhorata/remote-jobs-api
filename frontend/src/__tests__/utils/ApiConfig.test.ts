import { API_BASE_URL } from '../../utils/apiConfig';

describe('API Configuration Tests', () => {
  it('should have a valid API base URL', () => {
    expect(API_BASE_URL).toBeDefined();
    expect(typeof API_BASE_URL).toBe('string');
    expect(API_BASE_URL.length).toBeGreaterThan(0);
  });

  it('should be a valid URL format', () => {
    expect(API_BASE_URL).toMatch(/^https?:\/\/.+/);
  });

  it('should not end with a slash', () => {
    expect(API_BASE_URL).not.toMatch(/\/$/);
  });
});

describe('Utils Functions Tests', () => {
  it('should test environment detection', () => {
    const isDev = process.env.NODE_ENV === 'development';
    const isTest = process.env.NODE_ENV === 'test';
    
    expect(typeof isDev).toBe('boolean');
    expect(typeof isTest).toBe('boolean');
  });
});
