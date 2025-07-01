describe('Local Storage Service Tests', () => {
  // Simple mock implementation that works
  let storageData: { [key: string]: string } = {};
  
  const mockStorage = {
    getItem: (key: string) => storageData[key] || null,
    setItem: (key: string, value: string) => {
      storageData[key] = value;
    },
    removeItem: (key: string) => {
      delete storageData[key];
    },
    clear: () => {
      storageData = {};
    }
  };

  Object.defineProperty(window, 'localStorage', {
    value: mockStorage,
    writable: true
  });

  beforeEach(() => {
    storageData = {};
  });

  describe('Basic Storage Operations', () => {
    const storageService = {
      set: (key: string, value: any) => {
        const serialized = JSON.stringify(value);
        mockStorage.setItem(key, serialized);
      },
      
      get: (key: string) => {
        const item = mockStorage.getItem(key);
        if (!item) return null;
        try {
          return JSON.parse(item);
        } catch {
          return item;
        }
      },
      
      remove: (key: string) => {
        mockStorage.removeItem(key);
      },
      
      clear: () => {
        mockStorage.clear();
      }
    };

    test('should store and retrieve string values', () => {
      storageService.set('test-key', 'test-value');
      expect(storageService.get('test-key')).toBe('test-value');
    });

    test('should store and retrieve object values', () => {
      const testObject = { name: 'John', age: 30 };
      storageService.set('user', testObject);
      expect(storageService.get('user')).toEqual(testObject);
    });

    test('should store and retrieve array values', () => {
      const testArray = [1, 2, 3, 'test'];
      storageService.set('numbers', testArray);
      expect(storageService.get('numbers')).toEqual(testArray);
    });

    test('should return null for non-existent keys', () => {
      expect(storageService.get('non-existent')).toBeNull();
    });

    test('should remove items correctly', () => {
      storageService.set('temp', 'value');
      expect(storageService.get('temp')).toBe('value');
      
      storageService.remove('temp');
      expect(storageService.get('temp')).toBeNull();
    });

    test('should clear all items', () => {
      storageService.set('key1', 'value1');
      storageService.set('key2', 'value2');
      
      storageService.clear();
      expect(storageService.get('key1')).toBeNull();
      expect(storageService.get('key2')).toBeNull();
    });
  });

  describe('User Preferences Storage', () => {
    const preferencesService = {
      saveUserPreferences: (preferences: any) => {
        const existingPrefs = mockStorage.getItem('userPreferences');
        const currentPrefs = existingPrefs ? JSON.parse(existingPrefs) : {};
        const updatedPrefs = { ...currentPrefs, ...preferences };
        mockStorage.setItem('userPreferences', JSON.stringify(updatedPrefs));
      },
      
      getUserPreferences: () => {
        const prefs = mockStorage.getItem('userPreferences');
        return prefs ? JSON.parse(prefs) : {};
      }
    };

    test('should save and retrieve user preferences', () => {
      const preferences = {
        theme: 'dark',
        notifications: true,
        language: 'en'
      };

      preferencesService.saveUserPreferences(preferences);
      const retrieved = preferencesService.getUserPreferences();
      
      expect(retrieved).toEqual(preferences);
    });

    test('should merge preferences with existing ones', () => {
      preferencesService.saveUserPreferences({ theme: 'light', notifications: false });
      preferencesService.saveUserPreferences({ language: 'tr' });
      
      const preferences = preferencesService.getUserPreferences();
      expect(preferences).toEqual({
        theme: 'light',
        notifications: false,
        language: 'tr'
      });
    });

    test('should return empty object for no preferences', () => {
      const preferences = preferencesService.getUserPreferences();
      expect(preferences).toEqual({});
    });
  });

  describe('Search History Management', () => {
    const searchHistoryService = {
      addSearch: (searchTerm: string) => {
        const history = mockStorage.getItem('searchHistory');
        const searches = history ? JSON.parse(history) : [];
        
        // Remove if already exists and add to beginning
        const filtered = searches.filter((term: string) => term !== searchTerm);
        const updated = [searchTerm, ...filtered].slice(0, 10); // Keep last 10
        
        mockStorage.setItem('searchHistory', JSON.stringify(updated));
      },
      
      getSearchHistory: () => {
        const history = mockStorage.getItem('searchHistory');
        return history ? JSON.parse(history) : [];
      },
      
      clearSearchHistory: () => {
        mockStorage.removeItem('searchHistory');
      },
      
      removeSearchTerm: (searchTerm: string) => {
        const history = mockStorage.getItem('searchHistory');
        if (history) {
          const searches = JSON.parse(history);
          const filtered = searches.filter((term: string) => term !== searchTerm);
          mockStorage.setItem('searchHistory', JSON.stringify(filtered));
        }
      }
    };

    test('should add search terms to history', () => {
      searchHistoryService.addSearch('React Developer');
      searchHistoryService.addSearch('Python Engineer');
      
      const history = searchHistoryService.getSearchHistory();
      expect(history).toEqual(['Python Engineer', 'React Developer']);
    });

    test('should move existing search to top', () => {
      searchHistoryService.addSearch('React');
      searchHistoryService.addSearch('Python');
      searchHistoryService.addSearch('JavaScript');
      searchHistoryService.addSearch('React'); // Should move to top
      
      const history = searchHistoryService.getSearchHistory();
      expect(history[0]).toBe('React');
      expect(history.length).toBe(3);
    });

    test('should limit history to 10 items', () => {
      // Add 12 search terms
      for (let i = 0; i < 12; i++) {
        searchHistoryService.addSearch(`Search ${i}`);
      }
      
      const history = searchHistoryService.getSearchHistory();
      expect(history.length).toBe(10);
      expect(history[0]).toBe('Search 11'); // Most recent
    });

    test('should remove specific search terms', () => {
      searchHistoryService.addSearch('Keep This');
      searchHistoryService.addSearch('Remove This');
      searchHistoryService.addSearch('Keep This Too');
      
      searchHistoryService.removeSearchTerm('Remove This');
      
      const history = searchHistoryService.getSearchHistory();
      expect(history).not.toContain('Remove This');
      expect(history).toContain('Keep This');
      expect(history).toContain('Keep This Too');
    });

    test('should clear all search history', () => {
      searchHistoryService.addSearch('Test 1');
      searchHistoryService.addSearch('Test 2');
      
      searchHistoryService.clearSearchHistory();
      
      const history = searchHistoryService.getSearchHistory();
      expect(history).toEqual([]);
    });
  });

  describe('Session Management', () => {
    const sessionService = {
      setSession: (token: string, expiresIn: number) => {
        const expirationTime = Date.now() + (expiresIn * 1000);
        const sessionData = {
          token,
          expiresAt: expirationTime
        };
        mockStorage.setItem('session', JSON.stringify(sessionData));
      },
      
      getSession: () => {
        const session = mockStorage.getItem('session');
        if (!session) return null;
        
        const sessionData = JSON.parse(session);
        
        // Check if session is expired
        if (Date.now() > sessionData.expiresAt) {
          mockStorage.removeItem('session');
          return null;
        }
        
        return sessionData;
      },
      
      clearSession: () => {
        mockStorage.removeItem('session');
      },
      
      isSessionValid: () => {
        const session = sessionService.getSession();
        return session !== null;
      }
    };

    test('should store and retrieve valid session', () => {
      const token = 'test-token-123';
      const expiresIn = 3600; // 1 hour
      
      sessionService.setSession(token, expiresIn);
      const session = sessionService.getSession();
      
      expect(session).toBeTruthy();
      expect(session.token).toBe(token);
    });

    test('should return null for expired session', () => {
      const token = 'expired-token';
      const expiresIn = -1; // Already expired
      
      sessionService.setSession(token, expiresIn);
      const session = sessionService.getSession();
      
      expect(session).toBeNull();
    });

    test('should validate session correctly', () => {
      // Valid session
      sessionService.setSession('valid-token', 3600);
      expect(sessionService.isSessionValid()).toBe(true);
      
      // Expired session
      sessionService.setSession('expired-token', -1);
      expect(sessionService.isSessionValid()).toBe(false);
      
      // No session
      sessionService.clearSession();
      expect(sessionService.isSessionValid()).toBe(false);
    });

    test('should clear session correctly', () => {
      sessionService.setSession('test-token', 3600);
      expect(sessionService.isSessionValid()).toBe(true);
      
      sessionService.clearSession();
      expect(sessionService.isSessionValid()).toBe(false);
    });
  });
});
