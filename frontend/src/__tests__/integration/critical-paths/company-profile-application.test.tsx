import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../contexts/AuthContext';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import App from '../../../App';
import { companyService, jobService, applicationService } from '../../../services/AllServices';

// Mock services
jest.mock('../../../services/AllServices', () => ({
  companyService: {
    getCompanyProfile: jest.fn(),
    getCompanyJobs: jest.fn(),
    followCompany: jest.fn(),
    unfollowCompany: jest.fn(),
    getCompanyReviews: jest.fn(),
    submitCompanyReview: jest.fn(),
  },
  jobService: {
    getJobById: jest.fn(),
    applyToJob: jest.fn(),
    getSimilarJobs: jest.fn(),
    getJobApplications: jest.fn(),
    saveJob: jest.fn(),
    unsaveJob: jest.fn(),
  },
  applicationService: {
    getApplicationStatus: jest.fn(),
    withdrawApplication: jest.fn(),
    updateApplication: jest.fn(),
    getApplicationHistory: jest.fn(),
  },
  authService: {
    getCurrentUser: jest.fn(),
  },
}));

const mockCompanyService = companyService as jest.Mocked<typeof companyService>;
const mockJobService = jobService as jest.Mocked<typeof jobService>;
const mockApplicationService = applicationService as jest.Mocked<typeof applicationService>;

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

describe('Company Profile and Application Critical Path', () => {
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

  describe('Company Profile Exploration', () => {
    beforeEach(() => {
      // Mock company profile
      mockCompanyService.getCompanyProfile.mockResolvedValue({
        id: 'company_1',
        name: 'TechCorp',
        logo: 'techcorp-logo.png',
        description: 'Leading technology company',
        industry: 'Technology',
        size: '500-1000',
        location: 'San Francisco, CA',
        website: 'https://techcorp.com',
        founded: 2010,
        benefits: ['Health Insurance', 'Remote Work', 'Stock Options'],
        culture: 'Innovative and collaborative environment',
        rating: 4.5,
        reviewCount: 150
      });

      // Mock company jobs
      mockCompanyService.getCompanyJobs.mockResolvedValue({
        jobs: [
          {
            id: 'job_1',
            title: 'Senior React Developer',
            location: 'Remote',
            type: 'Full-time',
            salary: '80000-120000',
            postedAt: '2024-01-01',
            skills: ['React', 'TypeScript', 'Node.js']
          },
          {
            id: 'job_2',
            title: 'Product Manager',
            location: 'San Francisco',
            type: 'Full-time',
            salary: '100000-150000',
            postedAt: '2024-01-02',
            skills: ['Product Management', 'Agile', 'Analytics']
          }
        ],
        total: 2
      });
    });

    it('should explore company profile and view jobs', async () => {
      renderApp();

      // 1. Navigate to companies page
      const companiesLink = screen.getByText(/Şirketler/i) || screen.getByText(/Companies/i);
      fireEvent.click(companiesLink);

      // 2. Search for company
      const searchInput = screen.getByPlaceholderText(/Şirket ara/i) || screen.getByPlaceholderText(/Search companies/i);
      fireEvent.change(searchInput, { target: { value: 'TechCorp' } });

      const searchButton = screen.getByText(/Ara/i) || screen.getByText(/Search/i);
      fireEvent.click(searchButton);

      // 3. Click on company
      await waitFor(() => {
        expect(screen.getByText(/TechCorp/i)).toBeInTheDocument();
      });

      const companyCard = screen.getByText(/TechCorp/i);
      fireEvent.click(companyCard);

      // 4. Verify company profile
      await waitFor(() => {
        expect(mockCompanyService.getCompanyProfile).toHaveBeenCalledWith('company_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/Leading technology company/i)).toBeInTheDocument();
        expect(screen.getByText(/San Francisco, CA/i)).toBeInTheDocument();
        expect(screen.getByText(/500-1000/i)).toBeInTheDocument();
      });

      // 5. View company jobs
      const jobsTab = screen.getByText(/İş İlanları/i) || screen.getByText(/Job Listings/i);
      fireEvent.click(jobsTab);

      // 6. Verify company jobs
      await waitFor(() => {
        expect(mockCompanyService.getCompanyJobs).toHaveBeenCalledWith('company_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/Senior React Developer/i)).toBeInTheDocument();
        expect(screen.getByText(/Product Manager/i)).toBeInTheDocument();
      });
    });

    it('should follow/unfollow company', async () => {
      // Mock follow success
      mockCompanyService.followCompany.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to company profile
      const companiesLink = screen.getByText(/Şirketler/i) || screen.getByText(/Companies/i);
      fireEvent.click(companiesLink);

      const companyCard = screen.getByText(/TechCorp/i);
      fireEvent.click(companyCard);

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText(/TechCorp/i)).toBeInTheDocument();
      });

      // Follow company
      const followButton = screen.getByText(/Takip Et/i) || screen.getByText(/Follow/i);
      fireEvent.click(followButton);

      // Verify follow action
      await waitFor(() => {
        expect(mockCompanyService.followCompany).toHaveBeenCalledWith('company_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/Takip ediliyor/i) || screen.getByText(/Following/i)).toBeInTheDocument();
      });

      // Unfollow company
      mockCompanyService.unfollowCompany.mockResolvedValue({ success: true });
      const unfollowButton = screen.getByText(/Takibi Bırak/i) || screen.getByText(/Unfollow/i);
      fireEvent.click(unfollowButton);

      // Verify unfollow action
      await waitFor(() => {
        expect(mockCompanyService.unfollowCompany).toHaveBeenCalledWith('company_1');
      });
    });

    it('should view and submit company reviews', async () => {
      // Mock company reviews
      mockCompanyService.getCompanyReviews.mockResolvedValue([
        {
          id: 'review_1',
          rating: 5,
          comment: 'Great company to work for!',
          author: 'John Doe',
          date: '2024-01-01',
          pros: 'Good benefits, remote work',
          cons: 'Sometimes long hours'
        }
      ]);

      // Mock review submission
      mockCompanyService.submitCompanyReview.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to company profile
      const companiesLink = screen.getByText(/Şirketler/i) || screen.getByText(/Companies/i);
      fireEvent.click(companiesLink);

      const companyCard = screen.getByText(/TechCorp/i);
      fireEvent.click(companyCard);

      // Wait for profile to load
      await waitFor(() => {
        expect(screen.getByText(/TechCorp/i)).toBeInTheDocument();
      });

      // View reviews
      const reviewsTab = screen.getByText(/Değerlendirmeler/i) || screen.getByText(/Reviews/i);
      fireEvent.click(reviewsTab);

      // Verify reviews display
      await waitFor(() => {
        expect(mockCompanyService.getCompanyReviews).toHaveBeenCalledWith('company_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/Great company to work for!/i)).toBeInTheDocument();
        expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
      });

      // Submit new review
      const addReviewButton = screen.getByText(/Değerlendirme Ekle/i) || screen.getByText(/Add Review/i);
      fireEvent.click(addReviewButton);

      // Fill review form
      const ratingInput = screen.getByLabelText(/Puan/i) || screen.getByLabelText(/Rating/i);
      const commentInput = screen.getByLabelText(/Yorum/i) || screen.getByLabelText(/Comment/i);
      const prosInput = screen.getByLabelText(/Artılar/i) || screen.getByLabelText(/Pros/i);
      const consInput = screen.getByLabelText(/Eksiler/i) || screen.getByLabelText(/Cons/i);

      fireEvent.change(ratingInput, { target: { value: '4' } });
      fireEvent.change(commentInput, { target: { value: 'Good work environment' } });
      fireEvent.change(prosInput, { target: { value: 'Flexible hours' } });
      fireEvent.change(consInput, { target: { value: 'Limited growth' } });

      // Submit review
      const submitButton = screen.getByText(/Gönder/i) || screen.getByText(/Submit/i);
      fireEvent.click(submitButton);

      // Verify review submission
      await waitFor(() => {
        expect(mockCompanyService.submitCompanyReview).toHaveBeenCalledWith('company_1', {
          rating: 4,
          comment: 'Good work environment',
          pros: 'Flexible hours',
          cons: 'Limited growth'
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/Değerlendirme gönderildi/i) || screen.getByText(/Review submitted/i)).toBeInTheDocument();
      });
    });
  });

  describe('Job Application Process', () => {
    beforeEach(() => {
      // Mock job details
      mockJobService.getJobById.mockResolvedValue({
        id: 'job_1',
        title: 'Senior React Developer',
        company: {
          id: 'company_1',
          name: 'TechCorp',
          logo: 'techcorp-logo.png'
        },
        location: 'Remote',
        type: 'Full-time',
        salary: '80000-120000',
        description: 'We are looking for an experienced React developer...',
        requirements: [
          '5+ years of React experience',
          'Strong TypeScript skills',
          'Experience with Node.js'
        ],
        benefits: [
          'Health insurance',
          'Remote work',
          'Stock options'
        ],
        skills: ['React', 'TypeScript', 'Node.js'],
        postedAt: '2024-01-01',
        applicationDeadline: '2024-02-01'
      });

      // Mock similar jobs
      mockJobService.getSimilarJobs.mockResolvedValue([
        {
          id: 'job_2',
          title: 'React Developer',
          company: { name: 'OtherCorp' },
          location: 'Remote',
          salary: '70000-100000'
        }
      ]);
    });

    it('should complete full job application process', async () => {
      // Mock successful application
      mockJobService.applyToJob.mockResolvedValue({
        success: true,
        applicationId: 'app_123',
        message: 'Application submitted successfully'
      });

      renderApp();

      // 1. Navigate to job detail
      const jobsLink = screen.getByText(/İşler/i) || screen.getByText(/Jobs/i);
      fireEvent.click(jobsLink);

      // Wait for job list
      await waitFor(() => {
        expect(screen.getByText(/Senior React Developer/i)).toBeInTheDocument();
      });

      // Click on job
      const jobCard = screen.getByText(/Senior React Developer/i);
      fireEvent.click(jobCard);

      // 2. Verify job details
      await waitFor(() => {
        expect(mockJobService.getJobById).toHaveBeenCalledWith('job_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/TechCorp/i)).toBeInTheDocument();
        expect(screen.getByText(/Remote/i)).toBeInTheDocument();
        expect(screen.getByText(/80000-120000/i)).toBeInTheDocument();
      });

      // 3. Apply to job
      const applyButton = screen.getByText(/Başvur/i) || screen.getByText(/Apply/i);
      fireEvent.click(applyButton);

      // 4. Fill application form
      const nameInput = screen.getByLabelText(/Ad Soyad/i) || screen.getByLabelText(/Full Name/i);
      const emailInput = screen.getByLabelText(/E-posta/i) || screen.getByLabelText(/Email/i);
      const phoneInput = screen.getByLabelText(/Telefon/i) || screen.getByLabelText(/Phone/i);
      const coverLetterInput = screen.getByLabelText(/Ön Yazı/i) || screen.getByLabelText(/Cover Letter/i);

      fireEvent.change(nameInput, { target: { value: 'Test User' } });
      fireEvent.change(emailInput, { target: { value: 'test@example.com' } });
      fireEvent.change(phoneInput, { target: { value: '+1234567890' } });
      fireEvent.change(coverLetterInput, { target: { value: 'I am interested in this position...' } });

      // 5. Submit application
      const submitButton = screen.getByText(/Başvuruyu Gönder/i) || screen.getByText(/Submit Application/i);
      fireEvent.click(submitButton);

      // 6. Verify application submission
      await waitFor(() => {
        expect(mockJobService.applyToJob).toHaveBeenCalledWith('job_1', {
          name: 'Test User',
          email: 'test@example.com',
          phone: '+1234567890',
          coverLetter: 'I am interested in this position...'
        });
      });

      // 7. Verify success message
      await waitFor(() => {
        expect(screen.getByText(/Başvuru başarılı/i) || screen.getByText(/Application successful/i)).toBeInTheDocument();
      });

      // 8. View similar jobs
      const similarJobsSection = screen.getByText(/Benzer İşler/i) || screen.getByText(/Similar Jobs/i);
      expect(similarJobsSection).toBeInTheDocument();

      await waitFor(() => {
        expect(mockJobService.getSimilarJobs).toHaveBeenCalledWith('job_1');
      });
    });

    it('should save and unsave jobs', async () => {
      // Mock save job
      mockJobService.saveJob.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to job detail
      const jobsLink = screen.getByText(/İşler/i) || screen.getByText(/Jobs/i);
      fireEvent.click(jobsLink);

      const jobCard = screen.getByText(/Senior React Developer/i);
      fireEvent.click(jobCard);

      // Wait for job details
      await waitFor(() => {
        expect(screen.getByText(/TechCorp/i)).toBeInTheDocument();
      });

      // Save job
      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // Verify save action
      await waitFor(() => {
        expect(mockJobService.saveJob).toHaveBeenCalledWith('job_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/Kaydedildi/i) || screen.getByText(/Saved/i)).toBeInTheDocument();
      });

      // Unsave job
      mockJobService.unsaveJob.mockResolvedValue({ success: true });
      const unsaveButton = screen.getByText(/Kaydetmeyi Kaldır/i) || screen.getByText(/Unsave/i);
      fireEvent.click(unsaveButton);

      // Verify unsave action
      await waitFor(() => {
        expect(mockJobService.unsaveJob).toHaveBeenCalledWith('job_1');
      });
    });
  });

  describe('Application Management', () => {
    beforeEach(() => {
      // Mock application status
      mockApplicationService.getApplicationStatus.mockResolvedValue({
        status: 'under_review',
        applicationId: 'app_123',
        submittedAt: '2024-01-01',
        lastUpdated: '2024-01-05',
        notes: 'Application is being reviewed'
      });

      // Mock application history
      mockApplicationService.getApplicationHistory.mockResolvedValue([
        {
          id: 'app_1',
          jobTitle: 'Senior React Developer',
          company: 'TechCorp',
          status: 'under_review',
          appliedAt: '2024-01-01',
          lastUpdated: '2024-01-05'
        },
        {
          id: 'app_2',
          jobTitle: 'Product Manager',
          company: 'OtherCorp',
          status: 'rejected',
          appliedAt: '2023-12-15',
          lastUpdated: '2023-12-20'
        }
      ]);
    });

    it('should track application status', async () => {
      renderApp();

      // 1. Navigate to applications
      const applicationsLink = screen.getByText(/Başvurularım/i) || screen.getByText(/My Applications/i);
      fireEvent.click(applicationsLink);

      // 2. Verify application history
      await waitFor(() => {
        expect(mockApplicationService.getApplicationHistory).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText(/Senior React Developer/i)).toBeInTheDocument();
        expect(screen.getByText(/Product Manager/i)).toBeInTheDocument();
      });

      // 3. View application details
      const viewDetailsButton = screen.getByText(/Detayları Gör/i) || screen.getByText(/View Details/i);
      fireEvent.click(viewDetailsButton);

      // 4. Verify application status
      await waitFor(() => {
        expect(mockApplicationService.getApplicationStatus).toHaveBeenCalledWith('app_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/İnceleniyor/i) || screen.getByText(/Under Review/i)).toBeInTheDocument();
        expect(screen.getByText(/Application is being reviewed/i)).toBeInTheDocument();
      });
    });

    it('should withdraw application', async () => {
      // Mock withdrawal success
      mockApplicationService.withdrawApplication.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to applications
      const applicationsLink = screen.getByText(/Başvurularım/i) || screen.getByText(/My Applications/i);
      fireEvent.click(applicationsLink);

      // Wait for applications to load
      await waitFor(() => {
        expect(screen.getByText(/Senior React Developer/i)).toBeInTheDocument();
      });

      // Withdraw application
      const withdrawButton = screen.getByText(/Başvuruyu Geri Çek/i) || screen.getByText(/Withdraw/i);
      fireEvent.click(withdrawButton);

      // Confirm withdrawal
      const confirmButton = screen.getByText(/Evet, Geri Çek/i) || screen.getByText(/Yes, Withdraw/i);
      fireEvent.click(confirmButton);

      // Verify withdrawal
      await waitFor(() => {
        expect(mockApplicationService.withdrawApplication).toHaveBeenCalledWith('app_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/Başvuru geri çekildi/i) || screen.getByText(/Application withdrawn/i)).toBeInTheDocument();
      });
    });

    it('should update application', async () => {
      // Mock update success
      mockApplicationService.updateApplication.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to applications
      const applicationsLink = screen.getByText(/Başvurularım/i) || screen.getByText(/My Applications/i);
      fireEvent.click(applicationsLink);

      // Wait for applications to load
      await waitFor(() => {
        expect(screen.getByText(/Senior React Developer/i)).toBeInTheDocument();
      });

      // Edit application
      const editButton = screen.getByText(/Düzenle/i) || screen.getByText(/Edit/i);
      fireEvent.click(editButton);

      // Update cover letter
      const coverLetterInput = screen.getByLabelText(/Ön Yazı/i) || screen.getByLabelText(/Cover Letter/i);
      fireEvent.change(coverLetterInput, { target: { value: 'Updated cover letter...' } });

      // Save changes
      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // Verify update
      await waitFor(() => {
        expect(mockApplicationService.updateApplication).toHaveBeenCalledWith('app_1', {
          coverLetter: 'Updated cover letter...'
        });
      });

      await waitFor(() => {
        expect(screen.getByText(/Başvuru güncellendi/i) || screen.getByText(/Application updated/i)).toBeInTheDocument();
      });
    });
  });
});