import { authService } from "../../services/authService";

describe("AuthService Comprehensive Tests", () => {
  let localStorageMock: any;

  beforeEach(() => {
    localStorageMock = {
      getItem: jest.fn(),
      setItem: jest.fn(), 
      removeItem: jest.fn(),
      clear: jest.fn(),
    };
    Object.defineProperty(window, "localStorage", {
      value: localStorageMock,
      writable: true,
    });
    
    global.fetch = jest.fn();
    jest.clearAllMocks();
  });

  describe("Validation Functions", () => {
    it("should validate email correctly", () => {
      expect(authService.validateEmail("test@example.com")).toBe(true);
      expect(authService.validateEmail("invalid-email")).toBe(false);
      expect(authService.validateEmail("")).toBe(false);
    });

    it("should validate password correctly", () => {
      expect(authService.validatePassword("password123")).toBe(true);
      expect(authService.validatePassword("short")).toBe(false);
      expect(authService.validatePassword("")).toBe(false);
    });
  });

  describe("Token Management", () => {
    it("should check if user is authenticated", () => {
      localStorageMock.getItem.mockReturnValue("valid-token");
      expect(authService.isAuthenticated()).toBe(true);
      
      localStorageMock.getItem.mockReturnValue(null);
      expect(authService.isAuthenticated()).toBe(false);
    });

    it("should get stored auth token", () => {
      localStorageMock.getItem.mockReturnValue("stored-token");
      const token = authService.getToken();
      
      expect(localStorageMock.getItem).toHaveBeenCalledWith("auth_token");
      expect(token).toBe("stored-token");
    });
  });

  describe("Authentication Flow", () => {
    it("should handle login validation errors", async () => {
      await expect(authService.login("invalid-email", "pass")).rejects.toThrow("Invalid email format");
      await expect(authService.login("test@example.com", "short")).rejects.toThrow("Password must be at least 6 characters");
    });

    it("should handle logout", async () => {
      localStorageMock.getItem.mockReturnValue("test-token");
      (global.fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
      });

      await authService.logout();
      
      expect(localStorageMock.removeItem).toHaveBeenCalledWith("auth_token");
      expect(localStorageMock.removeItem).toHaveBeenCalledWith("user_data");
    });
  });
});
