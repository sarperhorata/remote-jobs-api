interface NotificationOptions {
  title: string;
  body: string;
  icon?: string;
  tag?: string;
  data?: any;
}

class NotificationService {
  private permission: NotificationPermission = 'default';
  private isSupported: boolean;

  constructor() {
    this.isSupported = 'Notification' in window;
    if (this.isSupported) {
      this.permission = Notification.permission;
    }
  }

  async requestPermission(): Promise<NotificationPermission> {
    if (!this.isSupported) {
      return 'denied';
    }

    if (this.permission === 'default') {
      this.permission = await Notification.requestPermission();
    }

    return this.permission;
  }

  async showNotification(options: NotificationOptions): Promise<boolean> {
    await this.requestPermission();

    if (this.permission !== 'granted') {
      return false;
    }

    try {
      const notification = new Notification(options.title, {
        body: options.body,
        icon: options.icon || '/favicon.ico',
        tag: options.tag,
        data: options.data,
      });

      // Auto close after 5 seconds
      setTimeout(() => {
        notification.close();
      }, 5000);

      return true;
    } catch (error) {
      console.error('Error showing notification:', error);
      return false;
    }
  }

  async showJobNotification(job: any): Promise<boolean> {
    return this.showNotification({
      title: `New Job: ${job.title}`,
      body: `${job.company} in ${job.location}`,
      tag: `job-${job.id}`,
      data: { jobId: job.id, type: 'job_alert' }
    });
  }

  async showMultipleJobNotifications(jobs: any[], maxNotifications = 5): Promise<void> {
    const limitedJobs = jobs.slice(0, maxNotifications);
    
    for (const job of limitedJobs) {
      await this.showJobNotification(job);
      // Small delay between notifications
      await new Promise(resolve => setTimeout(resolve, 100));
    }

    // If there are more jobs, show a summary notification
    if (jobs.length > maxNotifications) {
      await this.showNotification({
        title: `${jobs.length} New Jobs Available`,
        body: `${maxNotifications} shown, ${jobs.length - maxNotifications} more available`,
        tag: 'job-summary'
      });
    }
  }

  isPermissionGranted(): boolean {
    return this.permission === 'granted';
  }

  isNotificationSupported(): boolean {
    return this.isSupported;
  }

  async checkForNewJobs(lastCheckTime?: string): Promise<any[]> {
    try {
      const url = new URL('/api/jobs/recent', window.location.origin);
      if (lastCheckTime) {
        url.searchParams.set('since', lastCheckTime);
      }

      const response = await fetch(url.toString());
      if (!response.ok) {
        throw new Error(`Failed to fetch recent jobs: ${response.statusText}`);
      }

      const jobs = await response.json();
      return Array.isArray(jobs) ? jobs : [];
    } catch (error) {
      console.error('Error checking for new jobs:', error);
      return [];
    }
  }

  startPeriodicJobCheck(intervalMinutes = 30): void {
    let lastCheckTime = new Date().toISOString();

    const checkInterval = setInterval(async () => {
      if (!this.isPermissionGranted()) {
        clearInterval(checkInterval);
        return;
      }

      try {
        const newJobs = await this.checkForNewJobs(lastCheckTime);
        
        if (newJobs.length > 0) {
          await this.showMultipleJobNotifications(newJobs);
        }

        lastCheckTime = new Date().toISOString();
      } catch (error) {
        console.error('Error in periodic job check:', error);
      }
    }, intervalMinutes * 60 * 1000);

    // Store interval ID for cleanup if needed
    (window as any).jobCheckInterval = checkInterval;
  }

  stopPeriodicJobCheck(): void {
    if ((window as any).jobCheckInterval) {
      clearInterval((window as any).jobCheckInterval);
      delete (window as any).jobCheckInterval;
    }
  }
}

// Create and export singleton instance
export const notificationService = new NotificationService();

// Export class for testing or custom instances
export { NotificationService };
export type { NotificationOptions }; 