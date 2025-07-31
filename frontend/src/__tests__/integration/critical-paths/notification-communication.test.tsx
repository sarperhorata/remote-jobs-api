import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../contexts/AuthContext';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import App from '../../../App';
import { notificationService, communicationService, userService } from '../../../services/AllServices';

// Mock services
jest.mock('../../../services/AllServices', () => ({
  notificationService: {
    getNotifications: jest.fn(),
    markAsRead: jest.fn(),
    markAllAsRead: jest.fn(),
    deleteNotification: jest.fn(),
    updateNotificationSettings: jest.fn(),
    getNotificationSettings: jest.fn(),
    subscribeToNotifications: jest.fn(),
    unsubscribeFromNotifications: jest.fn(),
  },
  communicationService: {
    sendMessage: jest.fn(),
    getMessages: jest.fn(),
    getConversations: jest.fn(),
    markMessageAsRead: jest.fn(),
    deleteMessage: jest.fn(),
    blockUser: jest.fn(),
    unblockUser: jest.fn(),
  },
  userService: {
    getProfile: jest.fn(),
    updateProfile: jest.fn(),
  },
  authService: {
    getCurrentUser: jest.fn(),
  },
}));

const mockNotificationService = notificationService as jest.Mocked<typeof notificationService>;
const mockCommunicationService = communicationService as jest.Mocked<typeof communicationService>;
const mockUserService = userService as jest.Mocked<typeof userService>;

const renderApp = () => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        <AuthProvider>
          <App />
        </AuthProvider>
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Notification and Communication Critical Path', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
    
    // Mock authenticated user
    localStorage.setItem('authToken', 'mock-token');
    localStorage.setItem('user', JSON.stringify({
      id: '1',
      name: 'Test User',
      email: 'test@example.com'
    }));
  });

  describe('Notification Management', () => {
    beforeEach(() => {
      // Mock notifications
      mockNotificationService.getNotifications.mockResolvedValue([
        {
          id: 'notif_1',
          type: 'application_update',
          title: 'Application Status Updated',
          message: 'Your application for Senior React Developer has been reviewed',
          isRead: false,
          createdAt: '2024-01-01T10:00:00Z',
          data: {
            jobId: 'job_1',
            applicationId: 'app_1',
            status: 'under_review'
          }
        },
        {
          id: 'notif_2',
          type: 'new_job',
          title: 'New Job Match',
          message: 'A new React Developer position matches your profile',
          isRead: true,
          createdAt: '2024-01-01T09:00:00Z',
          data: {
            jobId: 'job_2',
            companyName: 'TechCorp'
          }
        },
        {
          id: 'notif_3',
          type: 'message',
          title: 'New Message',
          message: 'You have a new message from TechCorp HR',
          isRead: false,
          createdAt: '2024-01-01T08:00:00Z',
          data: {
            senderId: 'user_2',
            conversationId: 'conv_1'
          }
        }
      ]);

      // Mock notification settings
      mockNotificationService.getNotificationSettings.mockResolvedValue({
        email: {
          application_updates: true,
          new_jobs: true,
          messages: false,
          marketing: false
        },
        push: {
          application_updates: true,
          new_jobs: true,
          messages: true,
          marketing: false
        },
        sms: {
          application_updates: false,
          new_jobs: false,
          messages: false,
          marketing: false
        }
      });
    });

    it('should display and manage notifications', async () => {
      renderApp();

      // 1. Navigate to notifications
      const notificationsLink = screen.getByText(/Bildirimler/i) || screen.getByText(/Notifications/i);
      fireEvent.click(notificationsLink);

      // 2. Verify notifications load
      await waitFor(() => {
        expect(mockNotificationService.getNotifications).toHaveBeenCalled();
      });

      // 3. Verify notification display
      await waitFor(() => {
        expect(screen.getByText(/Application Status Updated/i)).toBeInTheDocument();
        expect(screen.getByText(/New Job Match/i)).toBeInTheDocument();
        expect(screen.getByText(/New Message/i)).toBeInTheDocument();
      });

      // 4. Mark notification as read
      const unreadNotification = screen.getByText(/Application Status Updated/i);
      fireEvent.click(unreadNotification);

      await waitFor(() => {
        expect(mockNotificationService.markAsRead).toHaveBeenCalledWith('notif_1');
      });

      // 5. Mark all as read
      const markAllReadButton = screen.getByText(/Tümünü Okundu İşaretle/i) || screen.getByText(/Mark All as Read/i);
      fireEvent.click(markAllReadButton);

      await waitFor(() => {
        expect(mockNotificationService.markAllAsRead).toHaveBeenCalled();
      });

      // 6. Delete notification
      const deleteButton = screen.getByText(/Sil/i) || screen.getByText(/Delete/i);
      fireEvent.click(deleteButton);

      const confirmDeleteButton = screen.getByText(/Evet, Sil/i) || screen.getByText(/Yes, Delete/i);
      fireEvent.click(confirmDeleteButton);

      await waitFor(() => {
        expect(mockNotificationService.deleteNotification).toHaveBeenCalledWith('notif_1');
      });
    });

    it('should manage notification settings', async () => {
      renderApp();

      // 1. Navigate to notification settings
      const settingsLink = screen.getByText(/Ayarlar/i) || screen.getByText(/Settings/i);
      fireEvent.click(settingsLink);

      const notificationSettingsTab = screen.getByText(/Bildirim Ayarları/i) || screen.getByText(/Notification Settings/i);
      fireEvent.click(notificationSettingsTab);

      // 2. Verify current settings
      await waitFor(() => {
        expect(mockNotificationService.getNotificationSettings).toHaveBeenCalled();
      });

      // 3. Update email notification settings
      const emailApplicationUpdates = screen.getByLabelText(/E-posta - Başvuru Güncellemeleri/i) || screen.getByLabelText(/Email - Application Updates/i);
      fireEvent.click(emailApplicationUpdates); // Toggle off

      const emailNewJobs = screen.getByLabelText(/E-posta - Yeni İşler/i) || screen.getByLabelText(/Email - New Jobs/i);
      fireEvent.click(emailNewJobs); // Toggle off

      // 4. Update push notification settings
      const pushMessages = screen.getByLabelText(/Push - Mesajlar/i) || screen.getByLabelText(/Push - Messages/i);
      fireEvent.click(pushMessages); // Toggle off

      // 5. Save settings
      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // 6. Verify settings update
      await waitFor(() => {
        expect(mockNotificationService.updateNotificationSettings).toHaveBeenCalledWith({
          email: {
            application_updates: false,
            new_jobs: false,
            messages: false,
            marketing: false
          },
          push: {
            application_updates: true,
            new_jobs: true,
            messages: false,
            marketing: false
          },
          sms: {
            application_updates: false,
            new_jobs: false,
            messages: false,
            marketing: false
          }
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/Ayarlar kaydedildi/i) || screen.getByText(/Settings saved/i)).toBeInTheDocument();
      });
    });

    it('should handle notification subscriptions', async () => {
      renderApp();

      // Navigate to notification settings
      const settingsLink = screen.getByText(/Ayarlar/i) || screen.getByText(/Settings/i);
      fireEvent.click(settingsLink);

      const notificationSettingsTab = screen.getByText(/Bildirim Ayarları/i) || screen.getByText(/Notification Settings/i);
      fireEvent.click(notificationSettingsTab);

      // Subscribe to notifications
      const subscribeButton = screen.getByText(/Bildirimlere Abone Ol/i) || screen.getByText(/Subscribe to Notifications/i);
      fireEvent.click(subscribeButton);

      await waitFor(() => {
        expect(mockNotificationService.subscribeToNotifications).toHaveBeenCalled();
      });

      // Unsubscribe from notifications
      const unsubscribeButton = screen.getByText(/Bildirimlerden Çık/i) || screen.getByText(/Unsubscribe from Notifications/i);
      fireEvent.click(unsubscribeButton);

      await waitFor(() => {
        expect(mockNotificationService.unsubscribeFromNotifications).toHaveBeenCalled();
      });
    });
  });

  describe('Communication and Messaging', () => {
    beforeEach(() => {
      // Mock conversations
      mockCommunicationService.getConversations.mockResolvedValue([
        {
          id: 'conv_1',
          participants: [
            { id: '1', name: 'Test User' },
            { id: '2', name: 'TechCorp HR' }
          ],
          lastMessage: {
            id: 'msg_1',
            content: 'Thank you for your application',
            senderId: '2',
            createdAt: '2024-01-01T10:00:00Z',
            isRead: false
          },
          unreadCount: 1,
          updatedAt: '2024-01-01T10:00:00Z'
        },
        {
          id: 'conv_2',
          participants: [
            { id: '1', name: 'Test User' },
            { id: '3', name: 'OtherCorp Recruiter' }
          ],
          lastMessage: {
            id: 'msg_2',
            content: 'When can you start?',
            senderId: '3',
            createdAt: '2024-01-01T09:00:00Z',
            isRead: true
          },
          unreadCount: 0,
          updatedAt: '2024-01-01T09:00:00Z'
        }
      ]);

      // Mock messages for conversation
      mockCommunicationService.getMessages.mockResolvedValue([
        {
          id: 'msg_1',
          content: 'Hi, thank you for your application',
          senderId: '2',
          senderName: 'TechCorp HR',
          createdAt: '2024-01-01T10:00:00Z',
          isRead: false
        },
        {
          id: 'msg_2',
          content: 'Thank you! I am very interested in the position',
          senderId: '1',
          senderName: 'Test User',
          createdAt: '2024-01-01T10:30:00Z',
          isRead: true
        }
      ]);
    });

    it('should manage conversations and messages', async () => {
      renderApp();

      // 1. Navigate to messages
      const messagesLink = screen.getByText(/Mesajlar/i) || screen.getByText(/Messages/i);
      fireEvent.click(messagesLink);

      // 2. Verify conversations load
      await waitFor(() => {
        expect(mockCommunicationService.getConversations).toHaveBeenCalled();
      });

      // 3. Verify conversation list
      await waitFor(() => {
        expect(screen.getByText(/TechCorp HR/i)).toBeInTheDocument();
        expect(screen.getByText(/OtherCorp Recruiter/i)).toBeInTheDocument();
      });

      // 4. Open conversation
      const conversation = screen.getByText(/TechCorp HR/i);
      fireEvent.click(conversation);

      // 5. Verify messages load
      await waitFor(() => {
        expect(mockCommunicationService.getMessages).toHaveBeenCalledWith('conv_1');
      });

      // 6. Verify messages display
      await waitFor(() => {
        expect(screen.getByText(/Hi, thank you for your application/i)).toBeInTheDocument();
        expect(screen.getByText(/Thank you! I am very interested in the position/i)).toBeInTheDocument();
      });

      // 7. Send new message
      const messageInput = screen.getByPlaceholderText(/Mesajınızı yazın/i) || screen.getByPlaceholderText(/Type your message/i);
      const sendButton = screen.getByText(/Gönder/i) || screen.getByText(/Send/i);

      fireEvent.change(messageInput, { target: { value: 'I would love to discuss this opportunity further' } });
      fireEvent.click(sendButton);

      // 8. Verify message sent
      await waitFor(() => {
        expect(mockCommunicationService.sendMessage).toHaveBeenCalledWith('conv_1', {
          content: 'I would love to discuss this opportunity further'
        });
      });
    });

    it('should mark messages as read', async () => {
      renderApp();

      // Navigate to messages
      const messagesLink = screen.getByText(/Mesajlar/i) || screen.getByText(/Messages/i);
      fireEvent.click(messagesLink);

      // Open conversation with unread messages
      const conversation = screen.getByText(/TechCorp HR/i);
      fireEvent.click(conversation);

      // Wait for messages to load
      await waitFor(() => {
        expect(screen.getByText(/Hi, thank you for your application/i)).toBeInTheDocument();
      });

      // Mark message as read
      await waitFor(() => {
        expect(mockCommunicationService.markMessageAsRead).toHaveBeenCalledWith('msg_1');
      });
    });

    it('should delete messages', async () => {
      renderApp();

      // Navigate to messages
      const messagesLink = screen.getByText(/Mesajlar/i) || screen.getByText(/Messages/i);
      fireEvent.click(messagesLink);

      // Open conversation
      const conversation = screen.getByText(/TechCorp HR/i);
      fireEvent.click(conversation);

      // Wait for messages to load
      await waitFor(() => {
        expect(screen.getByText(/Hi, thank you for your application/i)).toBeInTheDocument();
      });

      // Delete message
      const deleteButton = screen.getByText(/Sil/i) || screen.getByText(/Delete/i);
      fireEvent.click(deleteButton);

      const confirmDeleteButton = screen.getByText(/Evet, Sil/i) || screen.getByText(/Yes, Delete/i);
      fireEvent.click(confirmDeleteButton);

      // Verify message deletion
      await waitFor(() => {
        expect(mockCommunicationService.deleteMessage).toHaveBeenCalledWith('msg_1');
      });
    });

    it('should block and unblock users', async () => {
      renderApp();

      // Navigate to messages
      const messagesLink = screen.getByText(/Mesajlar/i) || screen.getByText(/Messages/i);
      fireEvent.click(messagesLink);

      // Open conversation
      const conversation = screen.getByText(/TechCorp HR/i);
      fireEvent.click(conversation);

      // Wait for conversation to load
      await waitFor(() => {
        expect(screen.getByText(/Hi, thank you for your application/i)).toBeInTheDocument();
      });

      // Block user
      const blockButton = screen.getByText(/Engelle/i) || screen.getByText(/Block/i);
      fireEvent.click(blockButton);

      const confirmBlockButton = screen.getByText(/Evet, Engelle/i) || screen.getByText(/Yes, Block/i);
      fireEvent.click(confirmBlockButton);

      // Verify user blocked
      await waitFor(() => {
        expect(mockCommunicationService.blockUser).toHaveBeenCalledWith('2');
      });

      // Unblock user
      const unblockButton = screen.getByText(/Engeli Kaldır/i) || screen.getByText(/Unblock/i);
      fireEvent.click(unblockButton);

      // Verify user unblocked
      await waitFor(() => {
        expect(mockCommunicationService.unblockUser).toHaveBeenCalledWith('2');
      });
    });
  });

  describe('Real-time Notifications', () => {
    it('should handle real-time notification updates', async () => {
      // Mock WebSocket connection
      const mockWebSocket = {
        onmessage: jest.fn(),
        send: jest.fn(),
        close: jest.fn(),
        readyState: 1
      };

      global.WebSocket = jest.fn(() => mockWebSocket) as any;

      renderApp();

      // 1. Navigate to notifications
      const notificationsLink = screen.getByText(/Bildirimler/i) || screen.getByText(/Notifications/i);
      fireEvent.click(notificationsLink);

      // 2. Simulate real-time notification
      const realTimeNotification = {
        type: 'new_notification',
        data: {
          id: 'notif_realtime',
          type: 'application_update',
          title: 'Real-time Update',
          message: 'Your application status has changed',
          isRead: false,
          createdAt: new Date().toISOString()
        }
      };

      // Simulate WebSocket message
      mockWebSocket.onmessage({ data: JSON.stringify(realTimeNotification) });

      // 3. Verify real-time notification appears
      await waitFor(() => {
        expect(screen.getByText(/Real-time Update/i)).toBeInTheDocument();
      });

      // 4. Verify notification count updates
      const notificationCount = screen.getByText(/3/i); // Should show updated count
      expect(notificationCount).toBeInTheDocument();
    });

    it('should handle real-time message updates', async () => {
      // Mock WebSocket connection
      const mockWebSocket = {
        onmessage: jest.fn(),
        send: jest.fn(),
        close: jest.fn(),
        readyState: 1
      };

      global.WebSocket = jest.fn(() => mockWebSocket) as any;

      renderApp();

      // 1. Navigate to messages
      const messagesLink = screen.getByText(/Mesajlar/i) || screen.getByText(/Messages/i);
      fireEvent.click(messagesLink);

      // 2. Open conversation
      const conversation = screen.getByText(/TechCorp HR/i);
      fireEvent.click(conversation);

      // 3. Simulate real-time message
      const realTimeMessage = {
        type: 'new_message',
        data: {
          id: 'msg_realtime',
          content: 'Real-time message from HR',
          senderId: '2',
          senderName: 'TechCorp HR',
          createdAt: new Date().toISOString(),
          isRead: false
        }
      };

      // Simulate WebSocket message
      mockWebSocket.onmessage({ data: JSON.stringify(realTimeMessage) });

      // 4. Verify real-time message appears
      await waitFor(() => {
        expect(screen.getByText(/Real-time message from HR/i)).toBeInTheDocument();
      });

      // 5. Verify unread count updates
      const unreadCount = screen.getByText(/2/i); // Should show updated unread count
      expect(unreadCount).toBeInTheDocument();
    });
  });

  describe('Notification Preferences and Integration', () => {
    it('should integrate with job applications', async () => {
      // Mock job application with notification
      const mockJobService = require('../../../services/AllServices').jobService;
      mockJobService.applyToJob = jest.fn().mockResolvedValue({
        success: true,
        applicationId: 'app_123'
      });

      renderApp();

      // 1. Apply to job
      const jobsLink = screen.getByText(/İşler/i) || screen.getByText(/Jobs/i);
      fireEvent.click(jobsLink);

      // Wait for job list
      await waitFor(() => {
        expect(screen.getByText(/React Developer/i)).toBeInTheDocument();
      });

      const jobCard = screen.getByText(/React Developer/i);
      fireEvent.click(jobCard);

      const applyButton = screen.getByText(/Başvur/i) || screen.getByText(/Apply/i);
      fireEvent.click(applyButton);

      // Fill application form
      const nameInput = screen.getByLabelText(/Ad Soyad/i) || screen.getByLabelText(/Full Name/i);
      const emailInput = screen.getByLabelText(/E-posta/i) || screen.getByLabelText(/Email/i);

      fireEvent.change(nameInput, { target: { value: 'Test User' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });

      const submitButton = screen.getByText(/Başvuruyu Gönder/i) || screen.getByText(/Submit Application/i);
      fireEvent.click(submitButton);

      // 2. Verify application submitted
      await waitFor(() => {
        expect(mockJobService.applyToJob).toHaveBeenCalled();
      });

      // 3. Check for notification about application
      const notificationsLink = screen.getByText(/Bildirimler/i) || screen.getByText(/Notifications/i);
      fireEvent.click(notificationsLink);

      await waitFor(() => {
        expect(screen.getByText(/Başvuru gönderildi/i) || screen.getByText(/Application submitted/i)).toBeInTheDocument();
      });
    });

    it('should handle notification preferences based on user activity', async () => {
      renderApp();

      // 1. Navigate to profile
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      // 2. Update notification preferences based on activity
      const notificationPreferencesButton = screen.getByText(/Bildirim Tercihleri/i) || screen.getByText(/Notification Preferences/i);
      fireEvent.click(notificationPreferencesButton);

      // 3. Set activity-based preferences
      const activeJobSeekerToggle = screen.getByLabelText(/Aktif İş Arayan/i) || screen.getByLabelText(/Active Job Seeker/i);
      fireEvent.click(activeJobSeekerToggle);

      // 4. Save preferences
      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // 5. Verify preferences updated
      await waitFor(() => {
        expect(mockNotificationService.updateNotificationSettings).toHaveBeenCalledWith(
          expect.objectContaining({
            email: expect.objectContaining({
              new_jobs: true,
              application_updates: true
            })
          })
        );
      });
    });
  });
});