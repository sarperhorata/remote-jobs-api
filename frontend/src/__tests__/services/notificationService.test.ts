import { notificationService } from '../../services/notificationService';

// Mock Notification API
const mockNotification = jest.fn();
const mockRequestPermission = jest.fn();

Object.defineProperty(global, 'Notification', {
  value: mockNotification,
  writable: true
});

Object.defineProperty(global.Notification, 'permission', {
  value: 'default',
  writable: true
});

Object.defineProperty(global.Notification, 'requestPermission', {
  value: mockRequestPermission,
  writable: true
});

// Mock fetch for API calls
global.fetch = jest.fn();

// Mock console methods
global.console = {
  ...console,
  error: jest.fn(),
  log: jest.fn()
};

describe('NotificationService', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    (fetch as jest.Mock).mockClear();
    mockNotification.mockClear();
    mockRequestPermission.mockClear();
    
    // Reset permission state
    Object.defineProperty(global.Notification, 'permission', {
      value: 'default',
      writable: true
    });

    // Clear any existing intervals
    if ((window as any).jobCheckInterval) {
      clearInterval((window as any).jobCheckInterval);
      delete (window as any).jobCheckInterval;
    }
  });

  afterEach(() => {
    // Clean up any intervals
    notificationService.stopPeriodicJobCheck();
  });

  describe('Permission Management', () => {
    it('should check if notifications are supported', () => {
      expect(notificationService.isNotificationSupported()).toBe(true);
    });

    it('should request permission when default', async () => {
      mockRequestPermission.mockResolvedValueOnce('granted');
      
      const result = await notificationService.requestPermission();
      
      expect(mockRequestPermission).toHaveBeenCalled();
      expect(result).toBe('granted');
    });

    it('should return existing permission without requesting', async () => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'granted',
        writable: true
      });
      
      const result = await notificationService.requestPermission();
      
      expect(mockRequestPermission).not.toHaveBeenCalled();
      expect(result).toBe('granted');
    });

    it('should handle permission denial', async () => {
      mockRequestPermission.mockResolvedValueOnce('denied');
      
      const result = await notificationService.requestPermission();
      
      expect(result).toBe('denied');
    });
  });

  describe('Basic Notifications', () => {
    beforeEach(() => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'granted',
        writable: true
      });
    });

    it('should show basic notification when permission granted', async () => {
      const mockNotificationInstance = {
        close: jest.fn()
      };
      mockNotification.mockReturnValueOnce(mockNotificationInstance);
      
      const result = await notificationService.showNotification({
        title: 'Test Title',
        body: 'Test Body'
      });
      
      expect(result).toBe(true);
      expect(mockNotification).toHaveBeenCalledWith('Test Title', {
        body: 'Test Body',
        icon: '/favicon.ico',
        tag: undefined,
        data: undefined
      });
      
      // Check auto-close is set
      expect(setTimeout).toHaveBeenCalledWith(expect.any(Function), 5000);
    });

    it('should not show notification when permission denied', async () => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'denied',
        writable: true
      });
      
      const result = await notificationService.showNotification({
        title: 'Test Title',
        body: 'Test Body'
      });
      
      expect(result).toBe(false);
      expect(mockNotification).not.toHaveBeenCalled();
    });

    it('should handle notification creation errors', async () => {
      mockNotification.mockImplementationOnce(() => {
        throw new Error('Notification failed');
      });
      
      const result = await notificationService.showNotification({
        title: 'Test Title',
        body: 'Test Body'
      });
      
      expect(result).toBe(false);
      expect(console.error).toHaveBeenCalledWith('Error showing notification:', expect.any(Error));
    });

    it('should use custom icon and tag when provided', async () => {
      const mockNotificationInstance = {
        close: jest.fn()
      };
      mockNotification.mockReturnValueOnce(mockNotificationInstance);
      
      await notificationService.showNotification({
        title: 'Test Title',
        body: 'Test Body',
        icon: '/custom-icon.png',
        tag: 'custom-tag',
        data: { customData: 'value' }
      });
      
      expect(mockNotification).toHaveBeenCalledWith('Test Title', {
        body: 'Test Body',
        icon: '/custom-icon.png',
        tag: 'custom-tag',
        data: { customData: 'value' }
      });
    });
  });

  describe('Job Notifications', () => {
    beforeEach(() => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'granted',
        writable: true
      });
    });

    it('should show job notification with correct format', async () => {
      const mockNotificationInstance = {
        close: jest.fn()
      };
      mockNotification.mockReturnValueOnce(mockNotificationInstance);
      
      const job = {
        id: 'job123',
        title: 'Software Engineer',
        company: 'Tech Corp',
        location: 'San Francisco'
      };
      
      const result = await notificationService.showJobNotification(job);
      
      expect(result).toBe(true);
      expect(mockNotification).toHaveBeenCalledWith('New Job: Software Engineer', {
        body: 'Tech Corp in San Francisco',
        icon: '/favicon.ico',
        tag: 'job-job123',
        data: { jobId: 'job123', type: 'job_alert' }
      });
    });

    it('should show multiple job notifications with limits', async () => {
      const mockNotificationInstance = {
        close: jest.fn()
      };
      mockNotification.mockReturnValue(mockNotificationInstance);
      
      const jobs = Array.from({ length: 7 }, (_, i) => ({
        id: `job${i}`,
        title: `Job ${i}`,
        company: `Company ${i}`,
        location: 'Remote'
      }));
      
      await notificationService.showMultipleJobNotifications(jobs, 3);
      
      // Should show 3 individual notifications + 1 summary
      expect(mockNotification).toHaveBeenCalledTimes(4);
      
      // Check summary notification
      expect(mockNotification).toHaveBeenLastCalledWith('7 New Jobs Available', {
        body: '3 shown, 4 more available',
        icon: '/favicon.ico',
        tag: 'job-summary',
        data: undefined
      });
    });

    it('should not show summary notification when jobs are within limit', async () => {
      const mockNotificationInstance = {
        close: jest.fn()
      };
      mockNotification.mockReturnValue(mockNotificationInstance);
      
      const jobs = [
        { id: 'job1', title: 'Job 1', company: 'Company 1', location: 'Remote' },
        { id: 'job2', title: 'Job 2', company: 'Company 2', location: 'Remote' }
      ];
      
      await notificationService.showMultipleJobNotifications(jobs, 5);
      
      // Should show only 2 individual notifications, no summary
      expect(mockNotification).toHaveBeenCalledTimes(2);
    });
  });

  describe('Job Checking', () => {
    beforeEach(() => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'granted',
        writable: true
      });
    });

    it('should fetch recent jobs correctly', async () => {
      const mockJobs = [
        { id: 'job1', title: 'Job 1', company: 'Company 1' },
        { id: 'job2', title: 'Job 2', company: 'Company 2' }
      ];
      
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => mockJobs
      });
      
      const result = await notificationService.checkForNewJobs();
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining('/api/jobs/recent')
      );
      expect(result).toEqual(mockJobs);
    });

    it('should include since parameter when provided', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });
      
      const lastCheckTime = '2023-01-01T00:00:00.000Z';
      await notificationService.checkForNewJobs(lastCheckTime);
      
      expect(fetch).toHaveBeenCalledWith(
        expect.stringContaining(`since=${encodeURIComponent(lastCheckTime)}`)
      );
    });

    it('should handle API errors gracefully', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: false,
        statusText: 'Server Error'
      });
      
      const result = await notificationService.checkForNewJobs();
      
      expect(result).toEqual([]);
      expect(console.error).toHaveBeenCalledWith(
        'Error checking for new jobs:',
        expect.any(Error)
      );
    });

    it('should handle network errors', async () => {
      (fetch as jest.Mock).mockRejectedValueOnce(new Error('Network error'));
      
      const result = await notificationService.checkForNewJobs();
      
      expect(result).toEqual([]);
      expect(console.error).toHaveBeenCalledWith(
        'Error checking for new jobs:',
        expect.any(Error)
      );
    });

    it('should handle non-array responses', async () => {
      (fetch as jest.Mock).mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Not an array' })
      });
      
      const result = await notificationService.checkForNewJobs();
      
      expect(result).toEqual([]);
    });
  });

  describe('Periodic Job Checking', () => {
    beforeEach(() => {
      jest.useFakeTimers();
      Object.defineProperty(global.Notification, 'permission', {
        value: 'granted',
        writable: true
      });
    });

    afterEach(() => {
      jest.useRealTimers();
    });

    it('should start periodic job checking', () => {
      notificationService.startPeriodicJobCheck(1); // 1 minute intervals
      
      expect((window as any).jobCheckInterval).toBeDefined();
      
      // Clean up
      notificationService.stopPeriodicJobCheck();
    });

    it('should stop periodic job checking when permission is denied', () => {
      notificationService.startPeriodicJobCheck(1);
      
      // Change permission to denied
      Object.defineProperty(global.Notification, 'permission', {
        value: 'denied',
        writable: true
      });
      
      // Fast-forward time to trigger the check
      jest.advanceTimersByTime(60000); // 1 minute
      
      // Interval should be cleared
      expect((window as any).jobCheckInterval).toBeUndefined();
    });

    it('should check for new jobs periodically', async () => {
      const mockJobs = [
        { id: 'job1', title: 'New Job', company: 'Tech Corp', location: 'Remote' }
      ];
      
      (fetch as jest.Mock).mockResolvedValue({
        ok: true,
        json: async () => mockJobs
      });
      
      const mockNotificationInstance = { close: jest.fn() };
      mockNotification.mockReturnValue(mockNotificationInstance);
      
      notificationService.startPeriodicJobCheck(1); // 1 minute
      
      // Fast-forward time
      jest.advanceTimersByTime(60000); // 1 minute
      
      // Wait for async operations
      await Promise.resolve();
      
      expect(fetch).toHaveBeenCalled();
      
      // Clean up
      notificationService.stopPeriodicJobCheck();
    });

    it('should stop periodic checking', () => {
      notificationService.startPeriodicJobCheck(1);
      expect((window as any).jobCheckInterval).toBeDefined();
      
      notificationService.stopPeriodicJobCheck();
      expect((window as any).jobCheckInterval).toBeUndefined();
    });

    it('should handle errors in periodic checking gracefully', async () => {
      (fetch as jest.Mock).mockRejectedValue(new Error('Network error'));
      
      notificationService.startPeriodicJobCheck(1);
      
      // Fast-forward time
      jest.advanceTimersByTime(60000);
      
      // Wait for async operations
      await Promise.resolve();
      
      expect(console.error).toHaveBeenCalledWith(
        'Error in periodic job check:',
        expect.any(Error)
      );
      
      // Clean up
      notificationService.stopPeriodicJobCheck();
    });
  });

  describe('Permission Helpers', () => {
    it('should correctly identify granted permission', () => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'granted',
        writable: true
      });
      
      expect(notificationService.isPermissionGranted()).toBe(true);
    });

    it('should correctly identify denied permission', () => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'denied',
        writable: true
      });
      
      expect(notificationService.isPermissionGranted()).toBe(false);
    });

    it('should correctly identify default permission', () => {
      Object.defineProperty(global.Notification, 'permission', {
        value: 'default',
        writable: true
      });
      
      expect(notificationService.isPermissionGranted()).toBe(false);
    });
  });

  describe('Unsupported Environment', () => {
    beforeEach(() => {
      // Mock unsupported environment
      Object.defineProperty(global, 'Notification', {
        value: undefined,
        writable: true
      });
    });

    it('should handle unsupported environment gracefully', () => {
      expect(notificationService.isNotificationSupported()).toBe(false);
    });

    it('should return denied permission for unsupported environment', async () => {
      const result = await notificationService.requestPermission();
      expect(result).toBe('denied');
    });

    it('should not show notifications in unsupported environment', async () => {
      const result = await notificationService.showNotification({
        title: 'Test',
        body: 'Test'
      });
      
      expect(result).toBe(false);
    });
  });
}); 