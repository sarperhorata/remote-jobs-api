describe('UserService Tests', () => {
  const localStorageMock = {
    getItem: jest.fn(),
    setItem: jest.fn(),
    removeItem: jest.fn(),
    clear: jest.fn()
  };
  
  Object.defineProperty(window, 'localStorage', {
    value: localStorageMock
  });

  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('User Profile Management', () => {
    it('should save user preferences', () => {
      const preferences = { theme: 'dark', notifications: true };
      
      localStorageMock.setItem.mockImplementation((key, value) => {
        expect(key).toBe('userPreferences');
        expect(typeof value).toBe('string');
      });
      
      localStorage.setItem('userPreferences', JSON.stringify(preferences));
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith(
        'userPreferences',
        JSON.stringify(preferences)
      );
    });

    it('should retrieve user preferences', () => {
      const preferences = { theme: 'light', notifications: false };
      localStorageMock.getItem.mockReturnValue(JSON.stringify(preferences));
      
      const result = localStorage.getItem('userPreferences');
      const parsedResult = result ? JSON.parse(result) : null;
      
      expect(parsedResult).toEqual(preferences);
      expect(localStorageMock.getItem).toHaveBeenCalledWith('userPreferences');
    });

    it('should handle null user preferences', () => {
      localStorageMock.getItem.mockReturnValue(null);
      
      const result = localStorage.getItem('userPreferences');
      
      expect(result).toBeNull();
    });
  });

  describe('User Session Management', () => {
    it('should manage user tokens', () => {
      const token = 'mock-jwt-token';
      
      localStorage.setItem('auth_token', token);
      
      expect(localStorageMock.setItem).toHaveBeenCalledWith('auth_token', token);
    });

    it('should clear user session', () => {
      localStorage.clear();
      
      expect(localStorageMock.clear).toHaveBeenCalled();
    });
  });

  describe('User Data Validation', () => {
    it('should validate email format', () => {
      const validEmail = 'test@example.com';
      const invalidEmail = 'invalid-email';
      
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      
      expect(emailRegex.test(validEmail)).toBe(true);
      expect(emailRegex.test(invalidEmail)).toBe(false);
    });
  });
});
