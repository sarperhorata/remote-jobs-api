import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout';
import { 
  Bell, 
  Check, 
  Trash2, 
  Info, 
  AlertCircle, 
  CheckCircle, 
  XCircle,
  Filter,
  Search,
  Clock,
  ExternalLink
} from 'lucide-react';

interface Notification {
  _id: string;
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

const Notifications: React.FC = () => {
  const { isAuthenticated, user } = useAuth();
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'unread' | 'read'>('all');
  const [category, setCategory] = useState<string>('all');
  const [searchTerm, setSearchTerm] = useState('');
  const [unreadCount, setUnreadCount] = useState(0);

  useEffect(() => {
    if (isAuthenticated) {
      loadNotifications();
      loadUnreadCount();
    } else {
      setLoading(false);
    }
  }, [isAuthenticated, filter, category]);

  const loadNotifications = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem('token');
      
      let url = `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/notifications?limit=50`;
      
      if (filter === 'unread') {
        url += '&is_read=false';
      } else if (filter === 'read') {
        url += '&is_read=true';
      }
      
      if (category !== 'all') {
        url += `&category=${category}`;
      }

      const response = await fetch(url, {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        setNotifications(data);
      } else {
        console.error('Failed to load notifications');
      }
    } catch (error) {
      console.error('Error loading notifications:', error);
    } finally {
      setLoading(false);
    }
  };

  const loadUnreadCount = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/notifications/unread-count`,
        {
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        const data = await response.json();
        setUnreadCount(data.unread_count);
      }
    } catch (error) {
      console.error('Error loading unread count:', error);
    }
  };

  const markAsRead = async (notificationId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/notifications/${notificationId}/read`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        // Update local state
        setNotifications(prev => 
          prev.map(notification => 
            notification._id === notificationId 
              ? { ...notification, is_read: true, read_at: new Date().toISOString() }
              : notification
          )
        );
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error marking notification as read:', error);
    }
  };

  const markAllAsRead = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/notifications/mark-all-read`,
        {
          method: 'PUT',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        setNotifications(prev => 
          prev.map(notification => ({
            ...notification,
            is_read: true,
            read_at: new Date().toISOString()
          }))
        );
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Error marking all notifications as read:', error);
    }
  };

  const deleteNotification = async (notificationId: string) => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/notifications/${notificationId}`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        setNotifications(prev => prev.filter(n => n._id !== notificationId));
        loadUnreadCount();
      }
    } catch (error) {
      console.error('Error deleting notification:', error);
    }
  };

  const clearAllNotifications = async () => {
    if (!window.confirm('Are you sure you want to clear all notifications?')) {
      return;
    }

    try {
      const token = localStorage.getItem('token');
      const response = await fetch(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8001'}/api/v1/notifications/clear-all`,
        {
          method: 'DELETE',
          headers: {
            'Authorization': `Bearer ${token}`,
            'Content-Type': 'application/json'
          }
        }
      );

      if (response.ok) {
        setNotifications([]);
        setUnreadCount(0);
      }
    } catch (error) {
      console.error('Error clearing all notifications:', error);
    }
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'success':
        return <CheckCircle className="w-5 h-5 text-green-500" />;
      case 'warning':
        return <AlertCircle className="w-5 h-5 text-yellow-500" />;
      case 'error':
        return <XCircle className="w-5 h-5 text-red-500" />;
      default:
        return <Info className="w-5 h-5 text-blue-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      return 'Just now';
    } else if (diffInHours < 24) {
      return `${diffInHours}h ago`;
    } else {
      const diffInDays = Math.floor(diffInHours / 24);
      return `${diffInDays}d ago`;
    }
  };

  const filteredNotifications = notifications.filter(notification => {
    if (searchTerm) {
      const searchLower = searchTerm.toLowerCase();
      return (
        notification.title.toLowerCase().includes(searchLower) ||
        notification.message.toLowerCase().includes(searchLower)
      );
    }
    return true;
  });

  if (!isAuthenticated) {
    return (
      <Layout>
        <div className="container mx-auto px-4 py-8">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-gray-900 mb-4">Please log in to view notifications</h1>
            <p className="text-gray-600">You need to be logged in to access your notifications.</p>
          </div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      
      <div className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <Bell className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
                <p className="text-gray-600">
                  {unreadCount > 0 ? `${unreadCount} unread notification${unreadCount > 1 ? 's' : ''}` : 'All caught up!'}
                </p>
              </div>
            </div>
            
            <div className="flex items-center space-x-2">
              {unreadCount > 0 && (
                <button
                  onClick={markAllAsRead}
                  className="flex items-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition-colors"
                >
                  <Check className="w-4 h-4" />
                  <span>Mark all read</span>
                </button>
              )}
              
              {notifications.length > 0 && (
                <button
                  onClick={clearAllNotifications}
                  className="flex items-center space-x-2 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-colors"
                >
                  <Trash2 className="w-4 h-4" />
                  <span>Clear all</span>
                </button>
              )}
            </div>
          </div>

          {/* Filters */}
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
            <div className="flex flex-col lg:flex-row lg:items-center lg:justify-between space-y-4 lg:space-y-0 lg:space-x-4">
              {/* Search */}
              <div className="relative flex-1 max-w-md">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <input
                  type="text"
                  placeholder="Search notifications..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                />
              </div>

              {/* Filter buttons */}
              <div className="flex items-center space-x-2">
                <select
                  value={filter}
                  onChange={(e) => setFilter(e.target.value as 'all' | 'unread' | 'read')}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All</option>
                  <option value="unread">Unread</option>
                  <option value="read">Read</option>
                </select>

                <select
                  value={category}
                  onChange={(e) => setCategory(e.target.value)}
                  className="px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                >
                  <option value="all">All Categories</option>
                  <option value="general">General</option>
                  <option value="job">Job</option>
                  <option value="application">Application</option>
                  <option value="system">System</option>
                </select>
              </div>
            </div>
          </div>

          {/* Notifications List */}
          {loading ? (
            <div className="flex justify-center items-center py-12">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredNotifications.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="w-16 h-16 text-gray-300 mx-auto mb-4" />
              <h3 className="text-lg font-medium text-gray-900 mb-2">No notifications</h3>
              <p className="text-gray-600">
                {searchTerm || filter !== 'all' || category !== 'all' 
                  ? 'No notifications match your filters.' 
                  : 'You\'re all caught up! Check back later for new updates.'}
              </p>
            </div>
          ) : (
            <div className="space-y-4">
              {filteredNotifications.map((notification) => (
                <div
                  key={notification._id}
                  className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 transition-all hover:shadow-md ${
                    !notification.is_read ? 'border-l-4 border-l-blue-500' : ''
                  }`}
                >
                  <div className="flex items-start space-x-4">
                    <div className="flex-shrink-0 mt-1">
                      {getNotificationIcon(notification.notification_type)}
                    </div>
                    
                    <div className="flex-1 min-w-0">
                      <div className="flex items-start justify-between">
                        <div className="flex-1">
                          <h3 className={`text-lg font-medium ${!notification.is_read ? 'text-gray-900' : 'text-gray-700'}`}>
                            {notification.title}
                          </h3>
                          <p className="text-gray-600 mt-1">{notification.message}</p>
                          
                          <div className="flex items-center space-x-4 mt-3 text-sm text-gray-500">
                            <div className="flex items-center space-x-1">
                              <Clock className="w-4 h-4" />
                              <span>{formatDate(notification.created_at)}</span>
                            </div>
                            
                            <span className="px-2 py-1 bg-gray-100 rounded-full text-xs">
                              {notification.category}
                            </span>
                          </div>
                        </div>
                        
                        <div className="flex items-center space-x-2 ml-4">
                          {notification.action_url && notification.action_text && (
                            <a
                              href={notification.action_url}
                              target="_blank"
                              rel="noopener noreferrer"
                              className="flex items-center space-x-1 px-3 py-1 bg-blue-100 text-blue-700 rounded-lg hover:bg-blue-200 transition-colors text-sm"
                            >
                              <span>{notification.action_text}</span>
                              <ExternalLink className="w-3 h-3" />
                            </a>
                          )}
                          
                          {!notification.is_read && (
                            <button
                              onClick={() => markAsRead(notification._id)}
                              className="p-2 text-gray-400 hover:text-green-600 hover:bg-green-50 rounded-lg transition-colors"
                              title="Mark as read"
                            >
                              <Check className="w-4 h-4" />
                            </button>
                          )}
                          
                          <button
                            onClick={() => deleteNotification(notification._id)}
                            className="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors"
                            title="Delete notification"
                          >
                            <Trash2 className="w-4 h-4" />
                          </button>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default Notifications; 