import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import App from '../../App';
import { jobService } from '../../services/AllServices';

// Mock services
jest.mock('../../services/AllServices', () => ({
  jobService: {
    searchJobs: jest.fn(),
    getJobById: jest.fn(),
    applyToJob: jest.fn(),
    getFavorites: jest.fn(),
    addToFavorites: jest.fn(),
    removeFromFavorites: jest.fn(),
  },
  authService: {
    login: jest.fn(),
    register: jest.fn(),
    logout: jest.fn(),
    getCurrentUser: jest.fn(),
  },
}));

const mockJobService = jobService as jest.Mocked<typeof jobService>;

const renderApp = () => {
  return render(
    <ThemeProvider>
      <AuthProvider>
        <App />
      </AuthProvider>
    </ThemeProvider>
  );
};

describe('Complete User Journey Integration Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
  });

  describe('New User Registration and Onboarding', () => {
    it('should complete full registration and onboarding flow', async () => {
      renderApp();

      // 1. Visit homepage
      expect(screen.getByText(/Uzaktan Çalışma Hayallerini/i)).toBeInTheDocument();

      // 2. Click register button
      const registerButton = screen.getByText(/Kayıt Ol/i);
      fireEvent.click(registerButton);

      // 3. Fill registration form
      const nameInput = screen.getByLabelText(/Ad Soyad/i);
      const emailInput = screen.getByLabelText(/E-posta/i);
      const passwordInput = screen.getByLabelText(/Şifre/i);

      fireEvent.change(nameInput, { target: { value: 'Test User' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(passwordInput, { target: { value: 'StrongPassword123!' } });

      // 4. Submit registration
      const submitButton = screen.getByText(/Kayıt Ol/i);
      fireEvent.click(submitButton);

      // 5. Verify registration success
      await waitFor(() => {
        expect(screen.getByText(/Kayıt başarılı/i)).toBeInTheDocument();
      });

      // 6. Complete profile setup
      const profileSetupButton = screen.getByText(/Profil Oluştur/i);
      fireEvent.click(profileSetupButton);

      // 7. Fill profile information
      const bioInput = screen.getByLabelText(/Hakkımda/i);
      const locationInput = screen.getByLabelText(/Konum/i);
      const skillsInput = screen.getByLabelText(/Yetenekler/i);

      fireEvent.change(bioInput, { target: { value: 'Experienced developer' } });
      fireEvent.change(locationInput, { target: { value: 'Istanbul' } });
      fireEvent.change(skillsInput, { target: { value: 'React, TypeScript, Node.js' } });

      // 8. Save profile
      const saveProfileButton = screen.getByText(/Kaydet/i);
      fireEvent.click(saveProfileButton);

      // 9. Verify profile completion
      await waitFor(() => {
        expect(screen.getByText(/Profil tamamlandı/i)).toBeInTheDocument();
      });
    });
  });

  describe('Job Search and Application Flow', () => {
    beforeEach(() => {
      // Mock successful login
      localStorage.setItem('authToken', 'mock-token');
      localStorage.setItem('user', JSON.stringify({
        id: '1',
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    it('should complete full job search and application process', async () => {
      // Mock job search results
      mockJobService.searchJobs.mockResolvedValue({
        jobs: [
          {
            id: '1',
            title: 'React Developer',
            company: { name: 'Tech Corp', logo: 'logo.png' },
            location: 'Remote',
            type: 'Full-time',
            salary: '50000-70000',
            description: 'We are looking for a React developer...',
            skills: ['React', 'TypeScript', 'Node.js'],
            postedAt: '2024-01-01'
          }
        ],
        total: 1,
        page: 1,
        limit: 10
      });

      // Mock job details
      mockJobService.getJobById.mockResolvedValue({
        id: '1',
        title: 'React Developer',
        company: { name: 'Tech Corp', logo: 'logo.png' },
        location: 'Remote',
        type: 'Full-time',
        salary: '50000-70000',
        description: 'We are looking for a React developer...',
        skills: ['React', 'TypeScript', 'Node.js'],
        postedAt: '2024-01-01'
      });

      // Mock successful application
      mockJobService.applyToJob.mockResolvedValue({
        success: true,
        applicationId: 'app-123'
      });

      renderApp();

      // 1. Search for jobs
      const searchInput = screen.getByPlaceholderText(/Search jobs/i);
      fireEvent.change(searchInput, { target: { value: 'React Developer' } });
      
      const searchButton = screen.getByText(/Search/i);
      fireEvent.click(searchButton);

      // 2. Wait for search results
      await waitFor(() => {
        expect(mockJobService.searchJobs).toHaveBeenCalledWith({
          query: 'React Developer',
          page: 1,
          limit: 10
        });
      });

      // 3. Click on a job
      const jobCard = screen.getByText(/React Developer/i);
      fireEvent.click(jobCard);

      // 4. Verify job details page
      await waitFor(() => {
        expect(screen.getByText(/Tech Corp/i)).toBeInTheDocument();
        expect(screen.getByText(/Remote/i)).toBeInTheDocument();
      });

      // 5. Apply for the job
      const applyButton = screen.getByText(/Başvur/i);
      fireEvent.click(applyButton);

      // 6. Fill application form
      const nameInput = screen.getByLabelText(/Ad Soyad/i);
      const emailInput = screen.getByLabelText(/E-posta/i);
      const coverLetterInput = screen.getByLabelText(/Ön Yazı/i);

      fireEvent.change(nameInput, { target: { value: 'Test User' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(coverLetterInput, { target: { value: 'I am interested in this position...' } });

      // 7. Submit application
      const submitButton = screen.getByText(/Başvuruyu Gönder/i);
      fireEvent.click(submitButton);

      // 8. Verify application success
      await waitFor(() => {
        expect(mockJobService.applyToJob).toHaveBeenCalledWith('1', {
          name: 'Test User',
          email: 'test@example.com',
          coverLetter: 'I am interested in this position...'
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/Başvuru başarılı/i)).toBeInTheDocument();
      });
    });
  });

  describe('Favorites and Job Management', () => {
    beforeEach(() => {
      localStorage.setItem('authToken', 'mock-token');
      localStorage.setItem('user', JSON.stringify({
        id: '1',
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    it('should manage favorites and track applications', async () => {
      // Mock favorites
      mockJobService.getFavorites.mockResolvedValue([
        {
          id: '1',
          title: 'React Developer',
          company: { name: 'Tech Corp' },
          location: 'Remote'
        }
      ]);

      // Mock add to favorites
      mockJobService.addToFavorites.mockResolvedValue({ success: true });

      renderApp();

      // 1. Navigate to favorites
      const favoritesLink = screen.getByText(/Favorites/i);
      fireEvent.click(favoritesLink);

      // 2. Verify favorites page
      await waitFor(() => {
        expect(mockJobService.getFavorites).toHaveBeenCalled();
      });

      // 3. Add job to favorites
      const addToFavoritesButton = screen.getByText(/Favorilere Ekle/i);
      fireEvent.click(addToFavoritesButton);

      // 4. Verify job added to favorites
      await waitFor(() => {
        expect(mockJobService.addToFavorites).toHaveBeenCalledWith('1');
      });

      // 5. Navigate to applications
      const applicationsLink = screen.getByText(/Başvurularım/i);
      fireEvent.click(applicationsLink);

      // 6. Verify applications page
      expect(screen.getByText(/Başvuru Geçmişi/i)).toBeInTheDocument();
    });
  });

  describe('Profile Management and Settings', () => {
    beforeEach(() => {
      localStorage.setItem('authToken', 'mock-token');
      localStorage.setItem('user', JSON.stringify({
        id: '1',
        name: 'Test User',
        email: 'test@example.com'
      }));
    });

    it('should update profile and manage settings', async () => {
      renderApp();

      // 1. Navigate to profile
      const profileLink = screen.getByText(/Profil/i);
      fireEvent.click(profileLink);

      // 2. Edit profile
      const editButton = screen.getByText(/Düzenle/i);
      fireEvent.click(editButton);

      // 3. Update profile information
      const bioInput = screen.getByLabelText(/Hakkımda/i);
      const locationInput = screen.getByLabelText(/Konum/i);

      fireEvent.change(bioInput, { target: { value: 'Updated bio' } });
      fireEvent.change(locationInput, { target: { value: 'Ankara' } });

      // 4. Save changes
      const saveButton = screen.getByText(/Kaydet/i);
      fireEvent.click(saveButton);

      // 5. Verify profile updated
      await waitFor(() => {
        expect(screen.getByText(/Profil güncellendi/i)).toBeInTheDocument();
      });

      // 6. Navigate to settings
      const settingsLink = screen.getByText(/Ayarlar/i);
      fireEvent.click(settingsLink);

      // 7. Update notification preferences
      const emailNotifications = screen.getByLabelText(/E-posta Bildirimleri/i);
      fireEvent.click(emailNotifications);

      // 8. Save settings
      const saveSettingsButton = screen.getByText(/Ayarları Kaydet/i);
      fireEvent.click(saveSettingsButton);

      // 9. Verify settings saved
      await waitFor(() => {
        expect(screen.getByText(/Ayarlar kaydedildi/i)).toBeInTheDocument();
      });
    });
  });

  describe('Error Handling and Recovery', () => {
    it('should handle network errors gracefully', async () => {
      // Mock network error
      mockJobService.searchJobs.mockRejectedValue(new Error('Network error'));

      renderApp();

      // 1. Try to search jobs
      const searchInput = screen.getByPlaceholderText(/İş ara/i);
      fireEvent.change(searchInput, { target: { value: 'React Developer' } });
      
      const searchButton = screen.getByText(/Ara/i);
      fireEvent.click(searchButton);

      // 2. Verify error message
      await waitFor(() => {
        expect(screen.getByText(/Bir hata oluştu/i)).toBeInTheDocument();
      });

      // 3. Try retry
      const retryButton = screen.getByText(/Tekrar Dene/i);
      fireEvent.click(retryButton);

      // 4. Verify retry attempt
      await waitFor(() => {
        expect(mockJobService.searchJobs).toHaveBeenCalledTimes(2);
      });
    });

    it('should handle authentication errors', async () => {
      // Mock expired token
      localStorage.setItem('authToken', 'expired-token');

      renderApp();

      // 1. Try to access protected route
      const profileLink = screen.getByText(/Profil/i);
      fireEvent.click(profileLink);

      // 2. Verify redirect to login
      await waitFor(() => {
        expect(screen.getByText(/Giriş Yap/i)).toBeInTheDocument();
      });
    });
  });

  describe('Performance and Responsiveness', () => {
    it('should handle large job lists efficiently', async () => {
      // Mock large job list
      const largeJobList = Array.from({ length: 100 }, (_, i) => ({
        id: `${i}`,
        title: `Job ${i}`,
        company: { name: `Company ${i}` },
        location: 'Remote',
        type: 'Full-time'
      }));

      mockJobService.searchJobs.mockResolvedValue({
        jobs: largeJobList,
        total: 100,
        page: 1,
        limit: 10
      });

      renderApp();

      // 1. Search for jobs
      const searchInput = screen.getByPlaceholderText(/İş ara/i);
      fireEvent.change(searchInput, { target: { value: 'Developer' } });
      
      const searchButton = screen.getByText(/Ara/i);
      fireEvent.click(searchButton);

      // 2. Verify pagination works
      await waitFor(() => {
        expect(screen.getByText(/1-10/i)).toBeInTheDocument();
      });

      // 3. Navigate to next page
      const nextPageButton = screen.getByText(/Sonraki/i);
      fireEvent.click(nextPageButton);

      // 4. Verify page change
      await waitFor(() => {
        expect(mockJobService.searchJobs).toHaveBeenCalledWith({
          query: 'Developer',
          page: 2,
          limit: 10
        });
      });
    });
  });
});