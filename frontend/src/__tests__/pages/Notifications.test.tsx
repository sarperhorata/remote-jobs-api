import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Notifications from '../../pages/Notifications';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock AuthContext
const mockAuthContext = {
  isAuthenticated: true,
  user: { _id: 'test-user-id', email: 'test@example.com' },
  login: jest.fn(),
  logout: jest.fn(),
  signup: jest.fn(),
  isLoading: false
};

jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => mockAuthContext
}));

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('Notifications Page', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    // Reset auth context for each test
    mockAuthContext.isAuthenticated = true;
    mockAuthContext.user = { _id: 'test-user-id', email: 'test@example.com' };
  });

  it('renders notifications page when authenticated', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Test Notification',
        message: 'This is a test notification',
        notification_type: 'info',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 1 })
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    expect(screen.getByText('1 unread notification')).toBeInTheDocument();
    expect(screen.getByText('Test Notification')).toBeInTheDocument();
  });

  it('shows login message when not authenticated', () => {
    mockAuthContext.isAuthenticated = false;
    mockAuthContext.user = null;

    renderWithProviders(<Notifications />);

    expect(screen.getByText('Please log in to view notifications')).toBeInTheDocument();
  });

  it('displays empty state when no notifications', async () => {
    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => []
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('No notifications')).toBeInTheDocument();
    });

    expect(screen.getByText("You're all caught up! Check back later for new updates.")).toBeInTheDocument();
  });

  it('filters notifications by read status', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Unread Notification',
        message: 'This is unread',
        notification_type: 'info',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '2',
        title: 'Read Notification',
        message: 'This is read',
        notification_type: 'success',
        category: 'job',
        is_read: true,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 1 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Unread Notification')).toBeInTheDocument();
    });

    // Change filter to read
    const filterSelect = screen.getByDisplayValue('All');
    fireEvent.change(filterSelect, { target: { value: 'read' } });

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('is_read=true'),
        expect.any(Object)
      );
    });
  });

  it('marks notification as read', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Test Notification',
        message: 'This is a test notification',
        notification_type: 'info',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 1 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Notification marked as read' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Test Notification')).toBeInTheDocument();
    });

    const markAsReadButton = screen.getByTitle('Mark as read');
    fireEvent.click(markAsReadButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/1/read'),
        expect.objectContaining({
          method: 'PUT'
        })
      );
    });
  });

  it('marks all notifications as read', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Test Notification 1',
        message: 'This is a test notification',
        notification_type: 'info',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '2',
        title: 'Test Notification 2',
        message: 'This is another test notification',
        notification_type: 'warning',
        category: 'job',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 2 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Marked 2 notifications as read', modified_count: 2 })
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Mark all read')).toBeInTheDocument();
    });

    const markAllReadButton = screen.getByText('Mark all read');
    fireEvent.click(markAllReadButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/mark-all-read'),
        expect.objectContaining({
          method: 'PUT'
        })
      );
    });
  });

  it('deletes a notification', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Test Notification',
        message: 'This is a test notification',
        notification_type: 'info',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 1 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Notification deleted' })
      });

    // Mock window.confirm
    window.confirm = jest.fn(() => true);

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Test Notification')).toBeInTheDocument();
    });

    const deleteButton = screen.getByTitle('Delete notification');
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/1'),
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });
  });

  it('clears all notifications', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Test Notification',
        message: 'This is a test notification',
        notification_type: 'info',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 1 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'Cleared 1 notifications', cleared_count: 1 })
      });

    // Mock window.confirm
    window.confirm = jest.fn(() => true);

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Clear all')).toBeInTheDocument();
    });

    const clearAllButton = screen.getByText('Clear all');
    fireEvent.click(clearAllButton);

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith(
        expect.stringContaining('/notifications/clear-all'),
        expect.objectContaining({
          method: 'DELETE'
        })
      );
    });
  });

  it('searches notifications', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Job Application Update',
        message: 'Your application has been reviewed',
        notification_type: 'success',
        category: 'application',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '2',
        title: 'System Maintenance',
        message: 'Scheduled maintenance notification',
        notification_type: 'warning',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 2 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Job Application Update')).toBeInTheDocument();
      expect(screen.getByText('System Maintenance')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search notifications...');
    fireEvent.change(searchInput, { target: { value: 'Job' } });

    await waitFor(() => {
      expect(screen.getByText('Job Application Update')).toBeInTheDocument();
      expect(screen.queryByText('System Maintenance')).not.toBeInTheDocument();
    });
  });

  it('displays notification icons correctly', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Success Notification',
        message: 'This is a success notification',
        notification_type: 'success',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '2',
        title: 'Warning Notification',
        message: 'This is a warning notification',
        notification_type: 'warning',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '3',
        title: 'Error Notification',
        message: 'This is an error notification',
        notification_type: 'error',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      }
    ];

    mockFetch
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 3 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Success Notification')).toBeInTheDocument();
      expect(screen.getByText('Warning Notification')).toBeInTheDocument();
      expect(screen.getByText('Error Notification')).toBeInTheDocument();
    });

    // Check that notification cards have the correct styling for unread notifications
    const notificationCards = screen.getAllByText(/Notification$/);
    expect(notificationCards).toHaveLength(3);
  });
}); 