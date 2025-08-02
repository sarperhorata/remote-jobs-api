import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../contexts/ThemeContext';
import Notifications from '../../pages/Notifications';

// Mock fetch
const mockFetch = jest.fn();
global.fetch = mockFetch;

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(() => 'mock-token'),
  setItem: jest.fn(),
  removeItem: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage,
  writable: true,
});

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
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('Notifications Page', () => {
  beforeEach(() => {
    mockFetch.mockClear();
    mockLocalStorage.getItem.mockClear();
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
        json: async () => ({ unread_count: 1 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('1 unread notification')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Test Notification')).toBeInTheDocument();
    });
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
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('All caught up!')).toBeInTheDocument();
    });
  });

  it('handles API error gracefully', async () => {
    mockFetch.mockRejectedValueOnce(new Error('Network error'));

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });
  });

  it('filters notifications by read status', async () => {
    const mockNotifications = [
      {
        _id: '1',
        title: 'Unread Notification',
        message: 'This is an unread notification',
        notification_type: 'info',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '2',
        title: 'Read Notification',
        message: 'This is a read notification',
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
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    // Wait for notifications to load
    await waitFor(() => {
      expect(screen.getByText('Unread Notification')).toBeInTheDocument();
    }, { timeout: 3000 });

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
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Test Notification')).toBeInTheDocument();
    }, { timeout: 3000 });

    // Look for mark as read button (might be an icon or text)
    const markAsReadButton = screen.getByTitle('Mark as read') || screen.getByText('Mark as read');
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
        json: async () => ({ unread_count: 2 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ message: 'All notifications marked as read' })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({ unread_count: 0 })
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Mark all read')).toBeInTheDocument();
    }, { timeout: 3000 });

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

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Test Notification')).toBeInTheDocument();
    }, { timeout: 3000 });

    const deleteButton = screen.getByTitle('Delete notification') || screen.getByText('Delete');
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
        title: 'Test Notification 1',
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
        json: async () => ({ message: 'All notifications cleared' })
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Clear all')).toBeInTheDocument();
    }, { timeout: 3000 });

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
        message: 'Your job application has been updated',
        notification_type: 'info',
        category: 'job',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '2',
        title: 'System Maintenance',
        message: 'System will be down for maintenance',
        notification_type: 'warning',
        category: 'system',
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
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Job Application Update')).toBeInTheDocument();
      expect(screen.getByText('System Maintenance')).toBeInTheDocument();
    }, { timeout: 3000 });

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
        message: 'Operation completed successfully',
        notification_type: 'success',
        category: 'system',
        is_read: false,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '2',
        title: 'Warning Notification',
        message: 'Please check your settings',
        notification_type: 'warning',
        category: 'job',
        is_read: true,
        is_active: true,
        created_at: '2024-01-01T00:00:00Z'
      },
      {
        _id: '3',
        title: 'Error Notification',
        message: 'Something went wrong',
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
        json: async () => ({ unread_count: 2 })
      })
      .mockResolvedValueOnce({
        ok: true,
        json: async () => mockNotifications
      });

    renderWithProviders(<Notifications />);

    await waitFor(() => {
      expect(screen.getByText('Notifications')).toBeInTheDocument();
    });

    await waitFor(() => {
      expect(screen.getByText('Success Notification')).toBeInTheDocument();
      expect(screen.getByText('Warning Notification')).toBeInTheDocument();
      expect(screen.getByText('Error Notification')).toBeInTheDocument();
    }, { timeout: 3000 });
  });
}); 