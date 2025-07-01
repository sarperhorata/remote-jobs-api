describe('Cache Service Tests', () => {
  // Mock localStorage for caching
  const mockStorage = {
    data: new Map<string, string>(),
    getItem: jest.fn((key: string) => mockStorage.data.get(key) || null),
    setItem: jest.fn((key: string, value: string) => {
      mockStorage.data.set(key, value);
    }),
    removeItem: jest.fn((key: string) => {
      mockStorage.data.delete(key);
    }),
    clear: jest.fn(() => {
      mockStorage.data.clear();
    })
  };

  Object.defineProperty(window, 'localStorage', {
    value: mockStorage,
    writable: true
  });

  beforeEach(() => {
    mockStorage.data.clear();
    jest.clearAllMocks();
  });

  describe('Basic Cache Operations', () => {
    const cacheService = {
      set: (key: string, value: any, ttl?: number) => {
        const cacheItem = {
          value,
          timestamp: Date.now(),
          ttl: ttl || 3600000 // Default 1 hour
        };
        mockStorage.setItem(key, JSON.stringify(cacheItem));
      },

      get: (key: string) => {
        const cached = mockStorage.getItem(key);
        if (!cached) return null;

        try {
          const item = JSON.parse(cached);
          const now = Date.now();
          
          if (item.timestamp + item.ttl < now) {
            mockStorage.removeItem(key);
            return null;
          }
          
          return item.value;
        } catch (error) {
          mockStorage.removeItem(key);
          return null;
        }
      },

      remove: (key: string) => {
        mockStorage.removeItem(key);
      },

      clear: () => {
        mockStorage.clear();
      }
    };

    // ... existing code ...
  });
}); 