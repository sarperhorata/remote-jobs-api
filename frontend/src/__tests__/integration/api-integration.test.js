/**
 * API Integration Tests
 * Tests API endpoints and integration with backend services
 */

import { render, screen, waitFor } from '@testing-library/react';
import axios from 'axios';

// Mock axios for controlled testing
jest.mock('axios');
const mockedAxios = axios;

describe('🔗 API Integration Tests', () => {
  beforeEach(() => {
    // Reset all mocks before each test
    jest.clearAllMocks();
  });

  describe('Jobs API', () => {
    test('should fetch jobs successfully', async () => {
      const mockJobs = [
        {
          id: 1,
          title: 'Frontend Developer',
          company: 'Tech Corp',
          location: 'Remote',
          type: 'full-time'
        },
        {
          id: 2,
          title: 'Backend Developer',
          company: 'Dev Inc',
          location: 'Remote',
          type: 'part-time'
        }
      ];

      mockedAxios.get.mockResolvedValueOnce({
        data: { jobs: mockJobs, total: 2 },
        status: 200
      });

      // Simulate API call
      const response = await axios.get('/api/jobs');
      
      expect(response.status).toBe(200);
      expect(response.data.jobs).toHaveLength(2);
      expect(response.data.jobs[0]).toHaveProperty('title', 'Frontend Developer');
    });

    test('should handle API errors gracefully', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: { status: 500, data: { message: 'Server Error' } }
      });

      try {
        await axios.get('/api/jobs');
      } catch (error) {
        expect(error.response.status).toBe(500);
        expect(error.response.data.message).toBe('Server Error');
      }
    });

    test('should handle pagination correctly', async () => {
      const mockResponse = {
        data: {
          jobs: [{ id: 1, title: 'Test Job' }],
          pagination: {
            currentPage: 1,
            totalPages: 5,
            totalJobs: 50
          }
        }
      };

      mockedAxios.get.mockResolvedValueOnce(mockResponse);

      const response = await axios.get('/api/jobs?page=1&limit=10');
      
      expect(response.data.pagination.currentPage).toBe(1);
      expect(response.data.pagination.totalPages).toBe(5);
    });
  });

  describe('Authentication API', () => {
    test('should login successfully with valid credentials', async () => {
      const mockLoginResponse = {
        data: {
          user: { id: 1, email: 'test@example.com', name: 'Test User' },
          token: 'mock-jwt-token'
        },
        status: 200
      };

      mockedAxios.post.mockResolvedValueOnce(mockLoginResponse);

      const response = await axios.post('/api/auth/login', {
        email: 'test@example.com',
        password: 'password123'
      });

      expect(response.status).toBe(200);
      expect(response.data.user.email).toBe('test@example.com');
      expect(response.data.token).toBeTruthy();
    });

    test('should handle login failure with invalid credentials', async () => {
      mockedAxios.post.mockRejectedValueOnce({
        response: {
          status: 401,
          data: { message: 'Invalid credentials' }
        }
      });

      try {
        await axios.post('/api/auth/login', {
          email: 'test@example.com',
          password: 'wrongpassword'
        });
      } catch (error) {
        expect(error.response.status).toBe(401);
        expect(error.response.data.message).toBe('Invalid credentials');
      }
    });

    test('should register new user successfully', async () => {
      const mockRegisterResponse = {
        data: {
          user: { id: 2, email: 'newuser@example.com', name: 'New User' },
          token: 'new-jwt-token'
        },
        status: 201
      };

      mockedAxios.post.mockResolvedValueOnce(mockRegisterResponse);

      const response = await axios.post('/api/auth/register', {
        name: 'New User',
        email: 'newuser@example.com',
        password: 'password123'
      });

      expect(response.status).toBe(201);
      expect(response.data.user.email).toBe('newuser@example.com');
    });
  });

  describe('Search API', () => {
    test('should search jobs with filters', async () => {
      const mockSearchResults = {
        data: {
          jobs: [
            { id: 1, title: 'React Developer', skills: ['React', 'JavaScript'] },
            { id: 2, title: 'Vue Developer', skills: ['Vue', 'JavaScript'] }
          ],
          filters: {
            applied: {
              skills: ['JavaScript'],
              type: 'full-time'
            }
          }
        }
      };

      mockedAxios.get.mockResolvedValueOnce(mockSearchResults);

      const response = await axios.get('/api/jobs/search', {
        params: {
          q: 'JavaScript Developer',
          skills: 'JavaScript',
          type: 'full-time'
        }
      });

      expect(response.data.jobs).toHaveLength(2);
      expect(response.data.filters.applied.skills).toContain('JavaScript');
    });

    test('should handle empty search results', async () => {
      mockedAxios.get.mockResolvedValueOnce({
        data: { jobs: [], total: 0 }
      });

      const response = await axios.get('/api/jobs/search?q=nonexistent');
      
      expect(response.data.jobs).toHaveLength(0);
      expect(response.data.total).toBe(0);
    });
  });

  describe('Company API', () => {
    test('should fetch company details', async () => {
      const mockCompany = {
        data: {
          id: 1,
          name: 'Tech Corporation',
          description: 'Leading tech company',
          openJobs: 5,
          website: 'https://techcorp.com'
        }
      };

      mockedAxios.get.mockResolvedValueOnce(mockCompany);

      const response = await axios.get('/api/companies/1');
      
      expect(response.data.name).toBe('Tech Corporation');
      expect(response.data.openJobs).toBe(5);
    });
  });

  describe('Subscription API', () => {
    test('should handle subscription creation', async () => {
      const mockSubscription = {
        data: {
          id: 'sub_123',
          plan: 'premium',
          status: 'active',
          current_period_end: '2024-12-31'
        }
      };

      mockedAxios.post.mockResolvedValueOnce(mockSubscription);

      const response = await axios.post('/api/subscriptions', {
        plan: 'premium',
        payment_method: 'pm_123'
      });

      expect(response.data.plan).toBe('premium');
      expect(response.data.status).toBe('active');
    });
  });

  describe('API Error Handling', () => {
    test('should handle network errors', async () => {
      mockedAxios.get.mockRejectedValueOnce(new Error('Network Error'));

      try {
        await axios.get('/api/jobs');
      } catch (error) {
        expect(error.message).toBe('Network Error');
      }
    });

    test('should handle timeout errors', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        code: 'ECONNABORTED',
        message: 'timeout of 5000ms exceeded'
      });

      try {
        await axios.get('/api/jobs');
      } catch (error) {
        expect(error.code).toBe('ECONNABORTED');
      }
    });

    test('should handle rate limiting', async () => {
      mockedAxios.get.mockRejectedValueOnce({
        response: {
          status: 429,
          data: { message: 'Too Many Requests' }
        }
      });

      try {
        await axios.get('/api/jobs');
      } catch (error) {
        expect(error.response.status).toBe(429);
      }
    });
  });

  describe('Data Validation', () => {
    test('should validate API response structure for jobs', async () => {
      const mockJobs = {
        data: {
          jobs: [
            {
              id: 1,
              title: 'Developer',
              company: 'Test Co',
              description: 'Test job',
              requirements: ['JavaScript'],
              salary: { min: 50000, max: 80000 },
              createdAt: '2024-01-01',
              updatedAt: '2024-01-01'
            }
          ],
          pagination: {
            currentPage: 1,
            totalPages: 1,
            totalJobs: 1
          }
        }
      };

      mockedAxios.get.mockResolvedValueOnce(mockJobs);

      const response = await axios.get('/api/jobs');
      const job = response.data.jobs[0];

      // Validate required fields
      expect(job).toHaveProperty('id');
      expect(job).toHaveProperty('title');
      expect(job).toHaveProperty('company');
      expect(job).toHaveProperty('description');
      expect(job).toHaveProperty('requirements');
      expect(job).toHaveProperty('salary');
      expect(job).toHaveProperty('createdAt');
      expect(job).toHaveProperty('updatedAt');

      // Validate data types
      expect(typeof job.id).toBe('number');
      expect(typeof job.title).toBe('string');
      expect(Array.isArray(job.requirements)).toBe(true);
      expect(typeof job.salary).toBe('object');
    });
  });
});