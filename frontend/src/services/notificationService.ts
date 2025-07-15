import { getApiUrl } from '../utils/apiConfig';

export interface Notification {
  _id: string;
  user_id: string;
  title: string;
  message: string;
  notification_type: 'info' | 'success' | 'warning' | 'error';
  category: string;
  is_read: boolean;
  is_active: boolean;
  action_url?: string;
  action_text?: string;
  created_at: string;
  read_at?: string;
}

export interface NotificationCount {
  unread_count: number;
}

class NotificationService {
  private listeners: ((count: number) => void)[] = [];
  private notificationListeners: ((notification: Notification) => void)[] = [];
  private jobCheckInterval: NodeJS.Timeout | null = null;

  // Subscribe to notification count changes
  onUnreadCountChange(callback: (count: number) => void) {
    this.listeners.push(callback);
    
    // Return unsubscribe function
    return () => {
      const index = this.listeners.indexOf(callback);
      if (index > -1) {
        this.listeners.splice(index, 1);
      }
    };
  }

  // Subscribe to new notifications
  onNewNotification(callback: (notification: Notification) => void) {
    this.notificationListeners.push(callback);
    
    return () => {
      const index = this.notificationListeners.indexOf(callback);
      if (index > -1) {
        this.notificationListeners.splice(index, 1);
      }
    };
  }

  // Request browser notification permission
  async requestPermission(): Promise<boolean> {
    if (!('Notification' in window)) {
      console.warn('This browser does not support notifications');
      return false;
    }

    if (Notification.permission === 'granted') {
      return true;
    }

    if (Notification.permission !== 'denied') {
      try {
        const permission = await Notification.requestPermission();
        return permission === 'granted';
      } catch (error) {
        console.error('Error requesting notification permission:', error);
        return false;
      }
    }

    return false;
  }

  // Start periodic job checking
  startPeriodicJobCheck(intervalMinutes: number = 30) {
    // Clear existing interval if any
    if (this.jobCheckInterval) {
      clearInterval(this.jobCheckInterval);
    }

    // Set up new interval
    this.jobCheckInterval = setInterval(async () => {
      try {
        await this.checkForNewJobMatches();
      } catch (error) {
        console.error('Error during periodic job check:', error);
      }
    }, intervalMinutes * 60 * 1000); // Convert minutes to milliseconds

    console.log(`Started periodic job check every ${intervalMinutes} minutes`);
  }

  // Stop periodic job checking
  stopPeriodicJobCheck() {
    if (this.jobCheckInterval) {
      clearInterval(this.jobCheckInterval);
      this.jobCheckInterval = null;
      console.log('Stopped periodic job check');
    }
  }

  // Check for new job matches (private implementation)
  private async checkForNewJobMatches() {
    try {
      // This would typically check user preferences and find matching jobs
      // For now, it's a placeholder that could be expanded
      console.log('Checking for new job matches...');
      
      // Placeholder: In the future, this could make API calls to:
      // 1. Get user job preferences
      // 2. Search for new jobs matching those preferences
      // 3. Send browser notifications for relevant matches
    } catch (error) {
      console.error('Error checking for new job matches:', error);
    }
  }

  // Get unread notification count
  async getUnreadCount(): Promise<number> {
    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        return 0; // No auth, no notifications
      }

      const response = await fetch(`${apiUrl}/api/v1/notifications/unread-count`, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired, clear it
          localStorage.removeItem('auth_token');
        }
        return 0;
      }

      const data = await response.json();
      return data.unread_count || 0;
    } catch (error) {
      console.error('Failed to get unread count:', error);
      return 0;
    }
  }

  // Refresh unread count and notify listeners
  async refreshUnreadCount(): Promise<void> {
    const count = await this.getUnreadCount();
    this.notifyCountChange(count);
  }

  // Mark all notifications as read
  async markAllAsRead(): Promise<void> {
    try {
      const apiUrl = await getApiUrl();
      const token = localStorage.getItem('auth_token');
      
      if (!token) {
        return;
      }

      const response = await fetch(`${apiUrl}/api/v1/notifications/mark-all-read`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        this.notifyCountChange(0);
      }
    } catch (error) {
      console.error('Failed to mark all as read:', error);
    }
  }

  // Send browser notification
  sendBrowserNotification(title: string, message: string, options?: NotificationOptions) {
    if (Notification.permission === 'granted') {
      try {
        new Notification(title, {
          body: message,
          icon: '/favicon.ico',
          badge: '/favicon.ico',
          ...options
        });
      } catch (error) {
        console.error('Error sending browser notification:', error);
      }
    }
  }

  // Notify all listeners about count change
  private notifyCountChange(count: number) {
    this.listeners.forEach(callback => {
      try {
        callback(count);
      } catch (error) {
        console.error('Error in notification count listener:', error);
      }
    });
  }

  // Cleanup method
  cleanup() {
    this.stopPeriodicJobCheck();
    this.listeners.length = 0;
    this.notificationListeners.length = 0;
  }
}

// Export singleton instance
export const notificationService = new NotificationService();
export default notificationService; 