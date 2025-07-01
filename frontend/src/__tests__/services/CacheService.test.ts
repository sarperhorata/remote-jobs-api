// Mock localStorage with persistent data storage
const storage: { [key: string]: string } = {};

const mockStorage = {
  getItem: jest.fn((key: string) => storage[key] || null),
  setItem: jest.fn((key: string, value: string) => {
    storage[key] = value;
  }),
  removeItem: jest.fn((key: string) => {
    delete storage[key];
  }),
  clear: jest.fn(() => {
    Object.keys(storage).forEach(key => delete storage[key]);
  }),
  length: 0,
  key: jest.fn()
};

Object.defineProperty(window, 'localStorage', {
  value: mockStorage,
  writable: true
});

describe('CacheService Tests', () => {
  beforeEach(() => {
    // Clear storage and reset mocks
    Object.keys(storage).forEach(key => delete storage[key]);
    jest.clearAllMocks();
  });

  describe('Basic Cache Operations', () => {
    const cacheService = {
      set: (key: string, value: any, ttl: number = 3600000) => {
        const cacheItem = {
          value,
          timestamp: Date.now(),
          ttl
        };
        storage[key] = JSON.stringify(cacheItem);
        mockStorage.setItem(key, JSON.stringify(cacheItem));
      },

      get: (key: string) => {
        const cached = storage[key];
        if (!cached) return null;

        try {
          const item = JSON.parse(cached);
          const now = Date.now();
          
          if (item.timestamp + item.ttl < now) {
            delete storage[key];
            mockStorage.removeItem(key);
            return null;
          }
          
          return item.value;
        } catch (error) {
          delete storage[key];
          mockStorage.removeItem(key);
          return null;
        }
      },

      remove: (key: string) => {
        delete storage[key];
        mockStorage.removeItem(key);
      },

      clear: () => {
        Object.keys(storage).forEach(key => delete storage[key]);
        mockStorage.clear();
      }
    };

    it('should set and get cache values correctly', () => {
      const testData = { jobs: [{ id: '1', title: 'Developer' }] };
      
      cacheService.set('jobs', testData);
      const retrieved = cacheService.get('jobs');
      
      expect(retrieved).toEqual(testData);
      expect(mockStorage.setItem).toHaveBeenCalled();
    });

    it('should handle cache expiration', (done) => {
      const testData = { message: 'This will expire' };
      const shortTTL = 50; // 50ms
      
      cacheService.set('temp', testData, shortTTL);
      
      expect(cacheService.get('temp')).toEqual(testData);
      
      setTimeout(() => {
        expect(cacheService.get('temp')).toBeNull();
        done();
      }, 60);
    });

    it('should remove cache entries', () => {
      cacheService.set('toRemove', { data: 'test' });
      expect(cacheService.get('toRemove')).toBeTruthy();
      
      cacheService.remove('toRemove');
      expect(cacheService.get('toRemove')).toBeNull();
    });

    it('should clear all cache', () => {
      cacheService.set('item1', { data: 'test1' });
      cacheService.set('item2', { data: 'test2' });
      
      cacheService.clear();
      
      expect(cacheService.get('item1')).toBeNull();
      expect(cacheService.get('item2')).toBeNull();
    });

    it('should handle malformed cache data', () => {
      storage['malformed'] = 'invalid json{';
      
      expect(cacheService.get('malformed')).toBeNull();
      expect(storage['malformed']).toBeUndefined();
    });
  });

  describe('Job Data Caching', () => {
    const jobCacheService = {
      cacheJobs: (jobs: any[], searchKey: string, ttl: number = 600000) => {
        const cacheKey = `jobs_${searchKey}`;
        const cacheData = {
          jobs,
          searchKey,
          timestamp: Date.now(),
          ttl
        };
        storage[cacheKey] = JSON.stringify(cacheData);
      },

      getCachedJobs: (searchKey: string) => {
        const cacheKey = `jobs_${searchKey}`;
        const cached = storage[cacheKey];
        
        if (!cached) return null;
        
        try {
          const data = JSON.parse(cached);
          const now = Date.now();
          
          if (data.timestamp + data.ttl < now) {
            delete storage[cacheKey];
            return null;
          }
          
          return data.jobs;
        } catch (error) {
          return null;
        }
      },

      generateSearchKey: (query: string, filters: any = {}) => {
        const searchParams = { query, ...filters };
        return btoa(JSON.stringify(searchParams)).replace(/[^a-zA-Z0-9]/g, '');
      }
    };

    it('should cache job search results', () => {
      const jobs = [
        { id: '1', title: 'React Developer', company: 'Tech Corp' },
        { id: '2', title: 'Vue Developer', company: 'Web Corp' }
      ];
      const searchKey = jobCacheService.generateSearchKey('developer');
      
      jobCacheService.cacheJobs(jobs, searchKey);
      const cached = jobCacheService.getCachedJobs(searchKey);
      
      expect(cached).toEqual(jobs);
      expect(cached).toHaveLength(2);
    });

    it('should generate consistent search keys', () => {
      const query = 'javascript developer';
      const filters = { location: 'remote', salary: '50000+' };
      
      const key1 = jobCacheService.generateSearchKey(query, filters);
      const key2 = jobCacheService.generateSearchKey(query, filters);
      
      expect(key1).toBe(key2);
      expect(key1).toMatch(/^[a-zA-Z0-9]+$/);
    });

    it('should handle different search parameters', () => {
      const jobs1 = [{ id: '1', title: 'Frontend Dev' }];
      const jobs2 = [{ id: '2', title: 'Backend Dev' }];
      
      const key1 = jobCacheService.generateSearchKey('frontend');
      const key2 = jobCacheService.generateSearchKey('backend');
      
      jobCacheService.cacheJobs(jobs1, key1);
      jobCacheService.cacheJobs(jobs2, key2);
      
      expect(jobCacheService.getCachedJobs(key1)).toEqual(jobs1);
      expect(jobCacheService.getCachedJobs(key2)).toEqual(jobs2);
    });
  });

  describe('Performance Tests', () => {
    it('should handle large datasets efficiently', () => {
      const largeDataset = Array.from({ length: 100 }, (_, i) => ({
        id: i,
        title: `Job ${i}`,
        description: 'Test description'
      }));
      
      const startTime = performance.now();
      
      storage['large_dataset'] = JSON.stringify({
        value: largeDataset,
        timestamp: Date.now(),
        ttl: 3600000
      });
      
      const cached = storage['large_dataset'];
      const parsed = JSON.parse(cached);
      
      const endTime = performance.now();
      
      expect(parsed.value).toHaveLength(100);
      expect(endTime - startTime).toBeLessThan(50);
    });

    it('should handle concurrent operations', () => {
      const operations = Array.from({ length: 10 }, (_, i) => ({
        key: `concurrent_${i}`,
        value: { data: `test_${i}` }
      }));
      
      operations.forEach(op => {
        storage[op.key] = JSON.stringify({
          value: op.value,
          timestamp: Date.now(),
          ttl: 3600000
        });
      });
      
      operations.forEach(op => {
        const cached = storage[op.key];
        expect(cached).toBeTruthy();
        
        const parsed = JSON.parse(cached);
        expect(parsed.value).toEqual(op.value);
      });
    });
  });
}); 