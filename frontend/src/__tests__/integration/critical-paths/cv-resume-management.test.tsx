import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../contexts/AuthContext';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import App from '../../../App';
import { resumeService, userService } from '../../../services/AllServices';

// Mock services
jest.mock('../../../services/AllServices', () => ({
  resumeService: {
    uploadResume: jest.fn(),
    getResumes: jest.fn(),
    deleteResume: jest.fn(),
    updateResume: jest.fn(),
    extractSkills: jest.fn(),
    generateResume: jest.fn(),
  },
  userService: {
    updateProfile: jest.fn(),
    getProfile: jest.fn(),
  },
  authService: {
    getCurrentUser: jest.fn(),
  },
}));

const mockResumeService = resumeService as jest.Mocked<typeof resumeService>;
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

// Mock file
const createMockFile = (name: string, type: string, size: number) => {
  const file = new File(['mock content'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
};

describe('CV and Resume Management Critical Path', () => {
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

  describe('Resume Upload Flow', () => {
    it('should complete full resume upload process', async () => {
      // Mock successful upload
      mockResumeService.uploadResume.mockResolvedValue({
        success: true,
        resumeId: 'resume_123',
        filename: 'test-resume.pdf',
        skills: ['React', 'TypeScript', 'Node.js']
      });

      // Mock skills extraction
      mockResumeService.extractSkills.mockResolvedValue({
        skills: ['React', 'TypeScript', 'Node.js', 'JavaScript'],
        confidence: 0.85
      });

      renderApp();

      // 1. Navigate to resume upload page
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const resumeTab = screen.getByText(/CV Yükle/i) || screen.getByText(/Upload Resume/i);
      fireEvent.click(resumeTab);

      // 2. Upload resume file
      const fileInput = screen.getByLabelText(/Dosya Seç/i) || screen.getByLabelText(/Choose File/i);
      const mockFile = createMockFile('test-resume.pdf', 'application/pdf', 1024 * 1024); // 1MB

      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      // 3. Verify file selection
      await waitFor(() => {
        expect(screen.getByText(/test-resume.pdf/i)).toBeInTheDocument();
      });

      // 4. Submit upload
      const uploadButton = screen.getByText(/Yükle/i) || screen.getByText(/Upload/i);
      fireEvent.click(uploadButton);

      // 5. Verify upload processing
      await waitFor(() => {
        expect(mockResumeService.uploadResume).toHaveBeenCalledWith(mockFile);
      });

      // 6. Verify skills extraction
      await waitFor(() => {
        expect(mockResumeService.extractSkills).toHaveBeenCalled();
      });

      // 7. Verify success message
      await waitFor(() => {
        expect(screen.getByText(/CV başarıyla yüklendi/i) || screen.getByText(/Resume uploaded successfully/i)).toBeInTheDocument();
      });

      // 8. Verify extracted skills display
      await waitFor(() => {
        expect(screen.getByText(/React/i)).toBeInTheDocument();
        expect(screen.getByText(/TypeScript/i)).toBeInTheDocument();
        expect(screen.getByText(/Node.js/i)).toBeInTheDocument();
      });
    });

    it('should handle upload errors gracefully', async () => {
      // Mock upload failure
      mockResumeService.uploadResume.mockRejectedValue(new Error('Upload failed'));

      renderApp();

      // Navigate to resume upload
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const resumeTab = screen.getByText(/CV Yükle/i) || screen.getByText(/Upload Resume/i);
      fireEvent.click(resumeTab);

      // Upload invalid file
      const fileInput = screen.getByLabelText(/Dosya Seç/i) || screen.getByLabelText(/Choose File/i);
      const invalidFile = createMockFile('test.txt', 'text/plain', 1024 * 1024);

      fireEvent.change(fileInput, { target: { files: [invalidFile] } });

      const uploadButton = screen.getByText(/Yükle/i) || screen.getByText(/Upload/i);
      fireEvent.click(uploadButton);

      // Verify error handling
      await waitFor(() => {
        expect(screen.getByText(/Geçersiz dosya formatı/i) || screen.getByText(/Invalid file format/i)).toBeInTheDocument();
      });
    });

    it('should validate file size and format', async () => {
      renderApp();

      // Navigate to resume upload
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const resumeTab = screen.getByText(/CV Yükle/i) || screen.getByText(/Upload Resume/i);
      fireEvent.click(resumeTab);

      // Try to upload oversized file
      const fileInput = screen.getByLabelText(/Dosya Seç/i) || screen.getByLabelText(/Choose File/i);
      const oversizedFile = createMockFile('large-resume.pdf', 'application/pdf', 10 * 1024 * 1024); // 10MB

      fireEvent.change(fileInput, { target: { files: [oversizedFile] } });

      // Verify size validation
      await waitFor(() => {
        expect(screen.getByText(/Dosya boyutu çok büyük/i) || screen.getByText(/File size too large/i)).toBeInTheDocument();
      });
    });
  });

  describe('Resume Management', () => {
    beforeEach(() => {
      // Mock existing resumes
      mockResumeService.getResumes.mockResolvedValue([
        {
          id: 'resume_1',
          filename: 'resume-1.pdf',
          uploadedAt: '2024-01-01',
          skills: ['React', 'TypeScript'],
          isPrimary: true
        },
        {
          id: 'resume_2',
          filename: 'resume-2.pdf',
          uploadedAt: '2024-01-02',
          skills: ['Node.js', 'Python'],
          isPrimary: false
        }
      ]);
    });

    it('should manage multiple resumes', async () => {
      renderApp();

      // 1. Navigate to resume management
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const resumeTab = screen.getByText(/CV Yönetimi/i) || screen.getByText(/Resume Management/i);
      fireEvent.click(resumeTab);

      // 2. Verify resume list
      await waitFor(() => {
        expect(mockResumeService.getResumes).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText(/resume-1.pdf/i)).toBeInTheDocument();
        expect(screen.getByText(/resume-2.pdf/i)).toBeInTheDocument();
      });

      // 3. Set primary resume
      const setPrimaryButton = screen.getByText(/Ana CV Yap/i) || screen.getByText(/Set as Primary/i);
      fireEvent.click(setPrimaryButton);

      // 4. Verify primary resume update
      await waitFor(() => {
        expect(screen.getByText(/Ana CV güncellendi/i) || screen.getByText(/Primary resume updated/i)).toBeInTheDocument();
      });
    });

    it('should delete resume', async () => {
      // Mock delete success
      mockResumeService.deleteResume.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to resume management
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const resumeTab = screen.getByText(/CV Yönetimi/i) || screen.getByText(/Resume Management/i);
      fireEvent.click(resumeTab);

      // Wait for resumes to load
      await waitFor(() => {
        expect(screen.getByText(/resume-1.pdf/i)).toBeInTheDocument();
      });

      // Delete resume
      const deleteButton = screen.getByText(/Sil/i) || screen.getByText(/Delete/i);
      fireEvent.click(deleteButton);

      // Confirm deletion
      const confirmButton = screen.getByText(/Evet, Sil/i) || screen.getByText(/Yes, Delete/i);
      fireEvent.click(confirmButton);

      // Verify deletion
      await waitFor(() => {
        expect(mockResumeService.deleteResume).toHaveBeenCalledWith('resume_1');
      });

      await waitFor(() => {
        expect(screen.getByText(/CV silindi/i) || screen.getByText(/Resume deleted/i)).toBeInTheDocument();
      });
    });

    it('should update resume information', async () => {
      // Mock update success
      mockResumeService.updateResume.mockResolvedValue({ success: true });

      renderApp();

      // Navigate to resume management
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const resumeTab = screen.getByText(/CV Yönetimi/i) || screen.getByText(/Resume Management/i);
      fireEvent.click(resumeTab);

      // Wait for resumes to load
      await waitFor(() => {
        expect(screen.getByText(/resume-1.pdf/i)).toBeInTheDocument();
      });

      // Edit resume
      const editButton = screen.getByText(/Düzenle/i) || screen.getByText(/Edit/i);
      fireEvent.click(editButton);

      // Update resume name
      const nameInput = screen.getByLabelText(/CV Adı/i) || screen.getByLabelText(/Resume Name/i);
      fireEvent.change(nameInput, { target: { value: 'Updated Resume' } });

      // Save changes
      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // Verify update
      await waitFor(() => {
        expect(mockResumeService.updateResume).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText(/CV güncellendi/i) || screen.getByText(/Resume updated/i)).toBeInTheDocument();
      });
    });
  });

  describe('Resume Generation and AI Features', () => {
    it('should generate AI-powered resume', async () => {
      // Mock AI resume generation
      mockResumeService.generateResume.mockResolvedValue({
        success: true,
        resumeId: 'ai_resume_123',
        filename: 'ai-generated-resume.pdf',
        content: 'AI generated resume content...'
      });

      renderApp();

      // 1. Navigate to AI resume generation
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const aiResumeTab = screen.getByText(/AI CV Oluştur/i) || screen.getByText(/Generate AI Resume/i);
      fireEvent.click(aiResumeTab);

      // 2. Fill profile information for AI generation
      const experienceInput = screen.getByLabelText(/Deneyim/i) || screen.getByLabelText(/Experience/i);
      const educationInput = screen.getByLabelText(/Eğitim/i) || screen.getByLabelText(/Education/i);
      const skillsInput = screen.getByLabelText(/Yetenekler/i) || screen.getByLabelText(/Skills/i);

      fireEvent.change(experienceInput, { target: { value: '5 years of React development' } });
      fireEvent.change(educationInput, { target: { value: 'Computer Science Degree' } });
      fireEvent.change(skillsInput, { target: { value: 'React, TypeScript, Node.js' } });

      // 3. Generate resume
      const generateButton = screen.getByText(/CV Oluştur/i) || screen.getByText(/Generate Resume/i);
      fireEvent.click(generateButton);

      // 4. Verify AI generation
      await waitFor(() => {
        expect(mockResumeService.generateResume).toHaveBeenCalledWith({
          experience: '5 years of React development',
          education: 'Computer Science Degree',
          skills: 'React, TypeScript, Node.js'
        });
      });

      // 5. Verify success
      await waitFor(() => {
        expect(screen.getByText(/AI CV oluşturuldu/i) || screen.getByText(/AI Resume generated/i)).toBeInTheDocument();
      });
    });

    it('should extract and suggest skills from resume', async () => {
      // Mock skills extraction
      mockResumeService.extractSkills.mockResolvedValue({
        skills: ['React', 'TypeScript', 'Node.js', 'JavaScript', 'CSS'],
        confidence: 0.92,
        suggestions: ['Redux', 'GraphQL', 'Docker']
      });

      renderApp();

      // Navigate to skills extraction
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      const skillsTab = screen.getByText(/Yetenek Analizi/i) || screen.getByText(/Skills Analysis/i);
      fireEvent.click(skillsTab);

      // Upload resume for skills extraction
      const fileInput = screen.getByLabelText(/CV Yükle/i) || screen.getByLabelText(/Upload Resume/i);
      const mockFile = createMockFile('resume.pdf', 'application/pdf', 1024 * 1024);

      fireEvent.change(fileInput, { target: { files: [mockFile] } });

      const analyzeButton = screen.getByText(/Analiz Et/i) || screen.getByText(/Analyze/i);
      fireEvent.click(analyzeButton);

      // Verify skills extraction
      await waitFor(() => {
        expect(mockResumeService.extractSkills).toHaveBeenCalledWith(mockFile);
      });

      // Verify extracted skills display
      await waitFor(() => {
        expect(screen.getByText(/React/i)).toBeInTheDocument();
        expect(screen.getByText(/TypeScript/i)).toBeInTheDocument();
        expect(screen.getByText(/Node.js/i)).toBeInTheDocument();
      });

      // Verify skill suggestions
      await waitFor(() => {
        expect(screen.getByText(/Redux/i)).toBeInTheDocument();
        expect(screen.getByText(/GraphQL/i)).toBeInTheDocument();
        expect(screen.getByText(/Docker/i)).toBeInTheDocument();
      });
    });
  });

  describe('Resume Application Integration', () => {
    it('should apply to job with selected resume', async () => {
      // Mock job application with resume
      const mockJobService = require('../../../services/AllServices').jobService;
      mockJobService.applyToJob = jest.fn().mockResolvedValue({
        success: true,
        applicationId: 'app_123'
      });

      renderApp();

      // 1. Navigate to job detail
      const jobsLink = screen.getByText(/İşler/i) || screen.getByText(/Jobs/i);
      fireEvent.click(jobsLink);

      // Wait for job list
      await waitFor(() => {
        expect(screen.getByText(/React Developer/i)).toBeInTheDocument();
      });

      // Click on job
      const jobCard = screen.getByText(/React Developer/i);
      fireEvent.click(jobCard);

      // 2. Apply to job
      const applyButton = screen.getByText(/Başvur/i) || screen.getByText(/Apply/i);
      fireEvent.click(applyButton);

      // 3. Select resume
      const resumeSelect = screen.getByLabelText(/CV Seç/i) || screen.getByLabelText(/Select Resume/i);
      fireEvent.change(resumeSelect, { target: { value: 'resume_1' } });

      // 4. Submit application
      const submitButton = screen.getByText(/Başvuruyu Gönder/i) || screen.getByText(/Submit Application/i);
      fireEvent.click(submitButton);

      // 5. Verify application with resume
      await waitFor(() => {
        expect(mockJobService.applyToJob).toHaveBeenCalledWith(
          expect.any(String),
          expect.objectContaining({
            resumeId: 'resume_1'
          })
        );
      });

      // 6. Verify success
      await waitFor(() => {
        expect(screen.getByText(/Başvuru başarılı/i) || screen.getByText(/Application successful/i)).toBeInTheDocument();
      });
    });
  });
});