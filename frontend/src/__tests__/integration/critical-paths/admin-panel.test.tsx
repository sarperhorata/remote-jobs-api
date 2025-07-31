import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../contexts/AuthContext';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import App from '../../../App';
import { adminService, userService, jobService, analyticsService } from '../../../services/AllServices';

// Mock services
jest.mock('../../../services/AllServices', () => ({
  adminService: {
    getDashboardStats: jest.fn(),
    getUsers: jest.fn(),
    getUserDetails: jest.fn(),
    updateUserStatus: jest.fn(),
    deleteUser: jest.fn(),
    getJobs: jest.fn(),
    getJobDetails: jest.fn(),
    approveJob: jest.fn(),
    rejectJob: jest.fn(),
    deleteJob: jest.fn(),
    getApplications: jest.fn(),
    getApplicationDetails: jest.fn(),
    updateApplicationStatus: jest.fn(),
    getAnalytics: jest.fn(),
    getSystemLogs: jest.fn(),
    clearLogs: jest.fn(),
    getSettings: jest.fn(),
    updateSettings: jest.fn(),
  },
  userService: {
    getProfile: jest.fn(),
  },
  jobService: {
    getJobById: jest.fn(),
  },
  analyticsService: {
    getMetrics: jest.fn(),
    exportData: jest.fn(),
  },
  authService: {
    getCurrentUser: jest.fn(),
  },
}));

const mockAdminService = adminService as jest.Mocked<typeof adminService>;
const mockUserService = userService as jest.Mocked<typeof userService>;
const mockJobService = jobService as jest.Mocked<typeof jobService>;
const mockAnalyticsService = analyticsService as jest.Mocked<typeof analyticsService>;

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

describe('Admin Panel Critical Path', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
    
    // Mock admin user
    localStorage.setItem('authToken', 'admin-token');
    localStorage.setItem('user', JSON.stringify({
      id: 'admin_1',
      name: 'Admin User',
      email: 'admin@buzz2remote.com',
      role: 'admin',
      permissions: ['manage_users', 'manage_jobs', 'manage_applications', 'view_analytics']
    }));
  });

  describe('Admin Dashboard', () => {
    beforeEach(() => {
      // Mock dashboard stats
      mockAdminService.getDashboardStats.mockResolvedValue({
        totalUsers: 1250,
        totalJobs: 450,
        totalApplications: 3200,
        activeUsers: 890,
        pendingJobs: 25,
        pendingApplications: 150,
        revenue: 15000,
        growthRate: 12.5
      });

      // Mock analytics
      mockAnalyticsService.getMetrics.mockResolvedValue({
        userGrowth: [120, 135, 150, 165, 180, 195],
        jobPostings: [45, 52, 48, 60, 55, 62],
        applications: [320, 350, 380, 400, 420, 450],
        revenue: [12000, 13500, 14200, 14800, 15200, 15800]
      });
    });

    it('should display admin dashboard with statistics', async () => {
      renderApp();

      // 1. Navigate to admin panel
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      // 2. Verify admin dashboard loads
      await waitFor(() => {
        expect(mockAdminService.getDashboardStats).toHaveBeenCalled();
      });

      // 3. Verify dashboard statistics display
      await waitFor(() => {
        expect(screen.getByText(/1250/i)).toBeInTheDocument(); // Total users
        expect(screen.getByText(/450/i)).toBeInTheDocument(); // Total jobs
        expect(screen.getByText(/3200/i)).toBeInTheDocument(); // Total applications
        expect(screen.getByText(/15000/i)).toBeInTheDocument(); // Revenue
      });

      // 4. Verify analytics charts
      await waitFor(() => {
        expect(mockAnalyticsService.getMetrics).toHaveBeenCalled();
      });

      // 5. Verify pending items
      expect(screen.getByText(/25/i)).toBeInTheDocument(); // Pending jobs
      expect(screen.getByText(/150/i)).toBeInTheDocument(); // Pending applications
    });

    it('should export dashboard data', async () => {
      // Mock export success
      mockAnalyticsService.exportData.mockResolvedValue({
        success: true,
        downloadUrl: 'https://example.com/export.csv'
      });

      renderApp();

      // Navigate to admin dashboard
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      // Wait for dashboard to load
      await waitFor(() => {
        expect(screen.getByText(/1250/i)).toBeInTheDocument();
      });

      // Export data
      const exportButton = screen.getByText(/Veri Dışa Aktar/i) || screen.getByText(/Export Data/i);
      fireEvent.click(exportButton);

      // Verify export
      await waitFor(() => {
        expect(mockAnalyticsService.exportData).toHaveBeenCalledWith('dashboard');
      });

      await waitFor(() => {
        expect(screen.getByText(/Dışa aktarma başarılı/i) || screen.getByText(/Export successful/i)).toBeInTheDocument();
      });
    });
  });

  describe('User Management', () => {
    beforeEach(() => {
      // Mock users list
      mockAdminService.getUsers.mockResolvedValue({
        users: [
          {
            id: 'user_1',
            name: 'John Doe',
            email: 'john@example.com',
            status: 'active',
            role: 'user',
            createdAt: '2024-01-01',
            lastLogin: '2024-01-15',
            applicationsCount: 5
          },
          {
            id: 'user_2',
            name: 'Jane Smith',
            email: 'jane@example.com',
            status: 'suspended',
            role: 'user',
            createdAt: '2024-01-02',
            lastLogin: '2024-01-10',
            applicationsCount: 2
          }
        ],
        total: 2,
        page: 1,
        limit: 10
      });

      // Mock user details
      mockAdminService.getUserDetails.mockResolvedValue({
        id: 'user_1',
        name: 'John Doe',
        email: 'john@example.com',
        status: 'active',
        role: 'user',
        profile: {
          bio: 'Experienced developer',
          location: 'Istanbul',
          skills: ['React', 'TypeScript']
        },
        applications: [
          {
            id: 'app_1',
            jobTitle: 'React Developer',
            company: 'TechCorp',
            status: 'under_review',
            appliedAt: '2024-01-10'
          }
        ],
        createdAt: '2024-01-01',
        lastLogin: '2024-01-15'
      });
    });

    it('should manage users list', async () => {
      renderApp();

      // 1. Navigate to user management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const usersTab = screen.getByText(/Kullanıcılar/i) || screen.getByText(/Users/i);
      fireEvent.click(usersTab);

      // 2. Verify users list loads
      await waitFor(() => {
        expect(mockAdminService.getUsers).toHaveBeenCalled();
      });

      // 3. Verify users display
      await waitFor(() => {
        expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
        expect(screen.getByText(/Jane Smith/i)).toBeInTheDocument();
        expect(screen.getByText(/active/i)).toBeInTheDocument();
        expect(screen.getByText(/suspended/i)).toBeInTheDocument();
      });

      // 4. Search users
      const searchInput = screen.getByPlaceholderText(/Kullanıcı ara/i) || screen.getByPlaceholderText(/Search users/i);
      fireEvent.change(searchInput, { target: { value: 'John' } });

      const searchButton = screen.getByText(/Ara/i) || screen.getByText(/Search/i);
      fireEvent.click(searchButton);

      // 5. Verify search results
      await waitFor(() => {
        expect(mockAdminService.getUsers).toHaveBeenCalledWith(
          expect.objectContaining({ search: 'John' })
        );
      });
    });

    it('should view and manage user details', async () => {
      renderApp();

      // Navigate to user management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const usersTab = screen.getByText(/Kullanıcılar/i) || screen.getByText(/Users/i);
      fireEvent.click(usersTab);

      // Wait for users to load
      await waitFor(() => {
        expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      });

      // View user details
      const viewDetailsButton = screen.getByText(/Detayları Gör/i) || screen.getByText(/View Details/i);
      fireEvent.click(viewDetailsButton);

      // Verify user details load
      await waitFor(() => {
        expect(mockAdminService.getUserDetails).toHaveBeenCalledWith('user_1');
      });

      // Verify user details display
      await waitFor(() => {
        expect(screen.getByText(/john@example.com/i)).toBeInTheDocument();
        expect(screen.getByText(/Experienced developer/i)).toBeInTheDocument();
        expect(screen.getByText(/Istanbul/i)).toBeInTheDocument();
        expect(screen.getByText(/React Developer/i)).toBeInTheDocument();
      });

      // Update user status
      const statusSelect = screen.getByLabelText(/Durum/i) || screen.getByLabelText(/Status/i);
      fireEvent.change(statusSelect, { target: { value: 'suspended' } });

      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // Verify status update
      await waitFor(() => {
        expect(mockAdminService.updateUserStatus).toHaveBeenCalledWith('user_1', 'suspended');
      });
    });

    it('should delete user', async () => {
      // Mock delete success
      mockAdminService.deleteUser.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to user management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const usersTab = screen.getByText(/Kullanıcılar/i) || screen.getByText(/Users/i);
      fireEvent.click(usersTab);

      // Wait for users to load
      await waitFor(() => {
        expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      });

      // Delete user
      const deleteButton = screen.getByText(/Sil/i) || screen.getByText(/Delete/i);
      fireEvent.click(deleteButton);

      const confirmDeleteButton = screen.getByText(/Evet, Sil/i) || screen.getByText(/Yes, Delete/i);
      fireEvent.click(confirmDeleteButton);

      // Verify user deletion
      await waitFor(() => {
        expect(mockAdminService.deleteUser).toHaveBeenCalledWith('user_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/Kullanıcı silindi/i) || screen.getByText(/User deleted/i)).toBeInTheDocument();
      });
    });
  });

  describe('Job Management', () => {
    beforeEach(() => {
      // Mock jobs list
      mockAdminService.getJobs.mockResolvedValue({
        jobs: [
          {
            id: 'job_1',
            title: 'React Developer',
            company: 'TechCorp',
            status: 'pending',
            postedAt: '2024-01-01',
            applicationsCount: 15,
            createdBy: 'user_1'
          },
          {
            id: 'job_2',
            title: 'Product Manager',
            company: 'OtherCorp',
            status: 'approved',
            postedAt: '2024-01-02',
            applicationsCount: 8,
            createdBy: 'user_2'
          }
        ],
        total: 2,
        page: 1,
        limit: 10
      });

      // Mock job details
      mockAdminService.getJobDetails.mockResolvedValue({
        id: 'job_1',
        title: 'React Developer',
        company: 'TechCorp',
        status: 'pending',
        description: 'We are looking for a React developer...',
        requirements: ['React', 'TypeScript', 'Node.js'],
        location: 'Remote',
        salary: '80000-120000',
        applications: [
          {
            id: 'app_1',
            applicantName: 'John Doe',
            status: 'under_review',
            appliedAt: '2024-01-10'
          }
        ],
        postedAt: '2024-01-01',
        createdBy: 'user_1'
      });
    });

    it('should manage jobs list', async () => {
      renderApp();

      // 1. Navigate to job management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const jobsTab = screen.getByText(/İş İlanları/i) || screen.getByText(/Job Listings/i);
      fireEvent.click(jobsTab);

      // 2. Verify jobs list loads
      await waitFor(() => {
        expect(mockAdminService.getJobs).toHaveBeenCalled();
      });

      // 3. Verify jobs display
      await waitFor(() => {
        expect(screen.getByText(/React Developer/i)).toBeInTheDocument();
        expect(screen.getByText(/Product Manager/i)).toBeInTheDocument();
        expect(screen.getByText(/pending/i)).toBeInTheDocument();
        expect(screen.getByText(/approved/i)).toBeInTheDocument();
      });

      // 4. Filter by status
      const statusFilter = screen.getByLabelText(/Durum Filtresi/i) || screen.getByLabelText(/Status Filter/i);
      fireEvent.change(statusFilter, { target: { value: 'pending' } });

      // 5. Verify filtered results
      await waitFor(() => {
        expect(mockAdminService.getJobs).toHaveBeenCalledWith(
          expect.objectContaining({ status: 'pending' })
        );
      });
    });

    it('should approve and reject jobs', async () => {
      // Mock approve success
      mockAdminService.approveJob.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to job management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const jobsTab = screen.getByText(/İş İlanları/i) || screen.getByText(/Job Listings/i);
      fireEvent.click(jobsTab);

      // Wait for jobs to load
      await waitFor(() => {
        expect(screen.getByText(/React Developer/i)).toBeInTheDocument();
      });

      // Approve job
      const approveButton = screen.getByText(/Onayla/i) || screen.getByText(/Approve/i);
      fireEvent.click(approveButton);

      // Verify job approval
      await waitFor(() => {
        expect(mockAdminService.approveJob).toHaveBeenCalledWith('job_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/İş ilanı onaylandı/i) || screen.getByText(/Job approved/i)).toBeInTheDocument();
      });

      // Reject job
      mockAdminService.rejectJob.mockResolvedValue({ success: true });
      const rejectButton = screen.getByText(/Reddet/i) || screen.getByText(/Reject/i);
      fireEvent.click(rejectButton);

      const rejectReasonInput = screen.getByLabelText(/Red Nedeni/i) || screen.getByLabelText(/Rejection Reason/i);
      fireEvent.change(rejectReasonInput, { target: { value: 'Inappropriate content' } });

      const confirmRejectButton = screen.getByText(/Reddetmeyi Onayla/i) || screen.getByText(/Confirm Rejection/i);
      fireEvent.click(confirmRejectButton);

      // Verify job rejection
      await waitFor(() => {
        expect(mockAdminService.rejectJob).toHaveBeenCalledWith('job_1', 'Inappropriate content');
      });
    });

    it('should view job details and applications', async () => {
      renderApp();

      // Navigate to job management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const jobsTab = screen.getByText(/İş İlanları/i) || screen.getByText(/Job Listings/i);
      fireEvent.click(jobsTab);

      // Wait for jobs to load
      await waitFor(() => {
        expect(screen.getByText(/React Developer/i)).toBeInTheDocument();
      });

      // View job details
      const viewDetailsButton = screen.getByText(/Detayları Gör/i) || screen.getByText(/View Details/i);
      fireEvent.click(viewDetailsButton);

      // Verify job details load
      await waitFor(() => {
        expect(mockAdminService.getJobDetails).toHaveBeenCalledWith('job_1');
      });

      // Verify job details display
      await waitFor(() => {
        expect(screen.getByText(/TechCorp/i)).toBeInTheDocument();
        expect(screen.getByText(/Remote/i)).toBeInTheDocument();
        expect(screen.getByText(/80000-120000/i)).toBeInTheDocument();
        expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      });
    });
  });

  describe('Application Management', () => {
    beforeEach(() => {
      // Mock applications list
      mockAdminService.getApplications.mockResolvedValue({
        applications: [
          {
            id: 'app_1',
            jobTitle: 'React Developer',
            company: 'TechCorp',
            applicantName: 'John Doe',
            status: 'under_review',
            appliedAt: '2024-01-10',
            priority: 'high'
          },
          {
            id: 'app_2',
            jobTitle: 'Product Manager',
            company: 'OtherCorp',
            applicantName: 'Jane Smith',
            status: 'approved',
            appliedAt: '2024-01-09',
            priority: 'normal'
          }
        ],
        total: 2,
        page: 1,
        limit: 10
      });

      // Mock application details
      mockAdminService.getApplicationDetails.mockResolvedValue({
        id: 'app_1',
        jobTitle: 'React Developer',
        company: 'TechCorp',
        applicant: {
          name: 'John Doe',
          email: 'john@example.com',
          phone: '+1234567890',
          resume: 'resume.pdf'
        },
        coverLetter: 'I am interested in this position...',
        status: 'under_review',
        appliedAt: '2024-01-10',
        reviewedAt: null,
        notes: ''
      });
    });

    it('should manage applications', async () => {
      renderApp();

      // 1. Navigate to application management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const applicationsTab = screen.getByText(/Başvurular/i) || screen.getByText(/Applications/i);
      fireEvent.click(applicationsTab);

      // 2. Verify applications list loads
      await waitFor(() => {
        expect(mockAdminService.getApplications).toHaveBeenCalled();
      });

      // 3. Verify applications display
      await waitFor(() => {
        expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
        expect(screen.getByText(/Jane Smith/i)).toBeInTheDocument();
        expect(screen.getByText(/under_review/i)).toBeInTheDocument();
        expect(screen.getByText(/approved/i)).toBeInTheDocument();
      });

      // 4. Update application status
      const statusSelect = screen.getByLabelText(/Durum/i) || screen.getByLabelText(/Status/i);
      fireEvent.change(statusSelect, { target: { value: 'approved' } });

      const notesInput = screen.getByLabelText(/Notlar/i) || screen.getByLabelText(/Notes/i);
      fireEvent.change(notesInput, { target: { value: 'Strong candidate' } });

      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // 5. Verify status update
      await waitFor(() => {
        expect(mockAdminService.updateApplicationStatus).toHaveBeenCalledWith('app_1', {
          status: 'approved',
          notes: 'Strong candidate'
        });
      });
    });
  });

  describe('System Management', () => {
    beforeEach(() => {
      // Mock system logs
      mockAdminService.getSystemLogs.mockResolvedValue([
        {
          id: 'log_1',
          level: 'info',
          message: 'User registered successfully',
          timestamp: '2024-01-01T10:00:00Z',
          userId: 'user_1',
          action: 'user_registration'
        },
        {
          id: 'log_2',
          level: 'error',
          message: 'Payment processing failed',
          timestamp: '2024-01-01T09:00:00Z',
          userId: 'user_2',
          action: 'payment_error'
        }
      ]);

      // Mock system settings
      mockAdminService.getSettings.mockResolvedValue({
        maintenance: false,
        registrationEnabled: true,
        maxApplicationsPerUser: 10,
        autoApproveJobs: false,
        emailNotifications: true
      });
    });

    it('should view system logs', async () => {
      renderApp();

      // 1. Navigate to system management
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const systemTab = screen.getByText(/Sistem/i) || screen.getByText(/System/i);
      fireEvent.click(systemTab);

      // 2. Verify system logs load
      await waitFor(() => {
        expect(mockAdminService.getSystemLogs).toHaveBeenCalled();
      });

      // 3. Verify logs display
      await waitFor(() => {
        expect(screen.getByText(/User registered successfully/i)).toBeInTheDocument();
        expect(screen.getByText(/Payment processing failed/i)).toBeInTheDocument();
        expect(screen.getByText(/info/i)).toBeInTheDocument();
        expect(screen.getByText(/error/i)).toBeInTheDocument();
      });

      // 4. Clear logs
      const clearLogsButton = screen.getByText(/Logları Temizle/i) || screen.getByText(/Clear Logs/i);
      fireEvent.click(clearLogsButton);

      const confirmClearButton = screen.getByText(/Evet, Temizle/i) || screen.getByText(/Yes, Clear/i);
      fireEvent.click(confirmClearButton);

      // 5. Verify logs cleared
      await waitFor(() => {
        expect(mockAdminService.clearLogs).toHaveBeenCalled();
      });
    });

    it('should manage system settings', async () => {
      renderApp();

      // 1. Navigate to system settings
      const adminLink = screen.getByText(/Admin/i) || screen.getByText(/Yönetim/i);
      fireEvent.click(adminLink);

      const settingsTab = screen.getByText(/Ayarlar/i) || screen.getByText(/Settings/i);
      fireEvent.click(settingsTab);

      // 2. Verify settings load
      await waitFor(() => {
        expect(mockAdminService.getSettings).toHaveBeenCalled();
      });

      // 3. Update settings
      const maintenanceToggle = screen.getByLabelText(/Bakım Modu/i) || screen.getByLabelText(/Maintenance Mode/i);
      fireEvent.click(maintenanceToggle);

      const maxApplicationsInput = screen.getByLabelText(/Maksimum Başvuru/i) || screen.getByLabelText(/Max Applications/i);
      fireEvent.change(maxApplicationsInput, { target: { value: '15' } });

      const autoApproveToggle = screen.getByLabelText(/Otomatik Onay/i) || screen.getByLabelText(/Auto Approve/i);
      fireEvent.click(autoApproveToggle);

      // 4. Save settings
      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // 5. Verify settings update
      await waitFor(() => {
        expect(mockAdminService.updateSettings).toHaveBeenCalledWith({
          maintenance: true,
          registrationEnabled: true,
          maxApplicationsPerUser: 15,
          autoApproveJobs: true,
          emailNotifications: true
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/Ayarlar kaydedildi/i) || screen.getByText(/Settings saved/i)).toBeInTheDocument();
      });
    });
  });
});