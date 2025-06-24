// Jest automatically provides describe, it, expect globals
// For mocking, we use jest.fn() instead of vi
import { onboardingService } from '../../services/onboardingService';

// Mock fetch globally
const mockFetch = jest.fn();
global.fetch = mockFetch;

describe('OnboardingService', () => {
  beforeEach(() => {
    mockFetch.mockClear();
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('registerWithEmail', () => {
    it('should register user with email successfully', async () => {
      const mockResponse = {
        message: 'Kayıt başarılı! Email adresinizi kontrol edin',
        user_id: 'test-user-id',
        onboarding_step: 0,
        next_step: 'email_verification'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.registerWithEmail('test@example.com');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/register-email',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test@example.com' })
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle registration error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Email zaten kayıtlı' })
      });

      await expect(onboardingService.registerWithEmail('existing@example.com'))
        .rejects.toThrow('Email zaten kayıtlı');
    });

    it('should validate email format', async () => {
      await expect(onboardingService.registerWithEmail('invalid-email'))
        .rejects.toThrow();
    });
  });

  describe('verifyEmail', () => {
    it('should verify email with valid token', async () => {
      const mockResponse = {
        message: 'Email başarıyla doğrulandı',
        onboarding_step: 1,
        next_step: 'set_password'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.verifyEmail('valid-token');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/verify-email',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ token: 'valid-token' })
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle invalid token', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Geçersiz veya süresi dolmuş token' })
      });

      await expect(onboardingService.verifyEmail('invalid-token'))
        .rejects.toThrow('Geçersiz veya süresi dolmuş token');
    });
  });

  describe('setPassword', () => {
    it('should set password successfully', async () => {
      const mockResponse = {
        message: 'Şifre başarıyla belirlendi',
        onboarding_step: 2,
        next_step: 'profile_setup'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.setPassword(
        'valid-token',
        'SecurePass123!',
        'SecurePass123!'
      );

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/set-password',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: 'valid-token',
            password: 'SecurePass123!',
            confirm_password: 'SecurePass123!'
          })
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle password mismatch', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Şifreler eşleşmiyor' })
      });

      await expect(onboardingService.setPassword(
        'valid-token',
        'password1',
        'password2'
      )).rejects.toThrow('Şifreler eşleşmiyor');
    });

    it('should validate password strength', async () => {
      await expect(onboardingService.setPassword(
        'valid-token',
        'weak',
        'weak'
      )).rejects.toThrow();
    });
  });

  describe('getLinkedInAuthUrl', () => {
    it('should get LinkedIn auth URL', async () => {
      const mockResponse = {
        auth_url: 'https://linkedin.com/oauth/authorize?client_id=123&state=xyz',
        state: 'xyz'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.getLinkedInAuthUrl();

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/linkedin-auth-url'
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle LinkedIn configuration error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'LinkedIn konfigürasyonu eksik' })
      });

      await expect(onboardingService.getLinkedInAuthUrl())
        .rejects.toThrow('LinkedIn konfigürasyonu eksik');
    });
  });

  describe('handleLinkedInCallback', () => {
    it('should handle LinkedIn callback successfully', async () => {
      const mockResponse = {
        message: 'LinkedIn başarıyla bağlandı',
        onboarding_step: 3,
        next_step: 'complete_profile',
        linkedin_profile: {
          id: 'linkedin-123',
          firstName: { en_US: 'John' },
          lastName: { en_US: 'Doe' }
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.handleLinkedInCallback(
        'auth-code',
        'state-value',
        'user-id'
      );

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/linkedin-callback',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            code: 'auth-code',
            state: 'state-value',
            user_id: 'user-id'
          })
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle LinkedIn API error', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'LinkedIn bağlantısında hata oluştu' })
      });

      await expect(onboardingService.handleLinkedInCallback(
        'invalid-code',
        'state',
        'user-id'
      )).rejects.toThrow('LinkedIn bağlantısında hata oluştu');
    });
  });

  describe('uploadCV', () => {
    it('should upload CV successfully', async () => {
      const mockResponse = {
        message: 'CV başarıyla yüklendi',
        file_url: '/uploads/cv/test-uuid.pdf'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const mockFile = new File(['pdf content'], 'test.pdf', { type: 'application/pdf' });
      
      const result = await onboardingService.uploadCV('user-id', mockFile);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/upload-cv',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle invalid file type', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Sadece PDF, DOC, DOCX dosyaları kabul edilir' })
      });

      const mockFile = new File(['text content'], 'test.txt', { type: 'text/plain' });

      await expect(onboardingService.uploadCV('user-id', mockFile))
        .rejects.toThrow('Sadece PDF, DOC, DOCX dosyaları kabul edilir');
    });

    it('should handle file size limit', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Dosya boyutu 5MB\'dan küçük olmalıdır' })
      });

      // Create a large file (6MB)
      const largeContent = new Array(6 * 1024 * 1024).fill('x').join('');
      const mockFile = new File([largeContent], 'large.pdf', { type: 'application/pdf' });

      await expect(onboardingService.uploadCV('user-id', mockFile))
        .rejects.toThrow('Dosya boyutu 5MB\'dan küçük olmalıdır');
    });
  });

  describe('uploadCVWithParsing', () => {
    it('should upload and parse CV successfully', async () => {
      const mockResponse = {
        message: 'CV başarıyla yüklendi ve analiz edildi',
        file_url: '/uploads/cv/test-uuid.pdf',
        parsed_data: {
          name: 'John Doe',
          email: 'john.doe@example.com',
          title: 'Software Engineer',
          skills: ['Python', 'JavaScript', 'React'],
          experience_years: 5
        }
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const mockFile = new File(['pdf content'], 'john_cv.pdf', { type: 'application/pdf' });
      
      const result = await onboardingService.uploadCVWithParsing('user-id', mockFile, true);

      const expectedFormData = new FormData();
      expectedFormData.append('user_id', 'user-id');
      expectedFormData.append('file', mockFile);
      expectedFormData.append('parse', 'true');
      expectedFormData.append('auto_fill', 'true');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/upload-cv',
        expect.objectContaining({
          method: 'POST',
          body: expect.any(FormData)
        })
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle parsing error gracefully', async () => {
      const mockResponse = {
        message: 'CV yüklendi ancak analiz edilemedi',
        file_url: '/uploads/cv/test-uuid.pdf',
        parsing_error: 'PDF\'den metin çıkarılamadı'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const mockFile = new File(['corrupted pdf'], 'corrupted.pdf', { type: 'application/pdf' });
      
      const result = await onboardingService.uploadCVWithParsing('user-id', mockFile, false);

      expect(result).toEqual(mockResponse);
      expect(result.parsing_error).toBeDefined();
    });
  });

  describe('completeProfile', () => {
    it('should complete profile successfully', async () => {
      const mockResponse = {
        message: 'Profil başarıyla tamamlandı',
        onboarding_step: 4,
        next_step: 'dashboard',
        access_token: 'jwt-token'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const profileData = {
        name: 'John Doe',
        bio: 'Software Engineer',
        location: 'Istanbul',
        skills: ['Python', 'React'],
        experience_years: 5
      };

      const result = await onboardingService.completeProfile('user-id', profileData);

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/complete-profile?user_id=user-id',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(profileData)
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle missing required fields', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'İsim alanı zorunludur' })
      });

      await expect(onboardingService.completeProfile('user-id', {}))
        .rejects.toThrow('İsim alanı zorunludur');
    });
  });

  describe('getOnboardingStatus', () => {
    it('should get onboarding status successfully', async () => {
      const mockResponse = {
        user_id: 'user-id',
        onboarding_step: 2,
        next_step: 'profile_setup',
        email_verified: true,
        onboarding_completed: false,
        has_linkedin: false,
        has_resume: true
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.getOnboardingStatus('user-id');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/onboarding/status/user-id'
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle user not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Kullanıcı bulunamadı' })
      });

      await expect(onboardingService.getOnboardingStatus('invalid-user-id'))
        .rejects.toThrow('Kullanıcı bulunamadı');
    });
  });

  describe('forgotPassword', () => {
    it('should send forgot password email successfully', async () => {
      const mockResponse = {
        message: 'Şifre sıfırlama bağlantısı email adresinize gönderildi'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.forgotPassword('test@example.com');

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/forgot-password',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email: 'test@example.com' })
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle email not found', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 404,
        json: async () => ({ detail: 'Bu email adresi ile kayıtlı kullanıcı bulunamadı' })
      });

      await expect(onboardingService.forgotPassword('notfound@example.com'))
        .rejects.toThrow('Bu email adresi ile kayıtlı kullanıcı bulunamadı');
    });
  });

  describe('resetPassword', () => {
    it('should reset password successfully', async () => {
      const mockResponse = {
        message: 'Şifre başarıyla sıfırlandı'
      };

      mockFetch.mockResolvedValueOnce({
        ok: true,
        json: async () => mockResponse
      });

      const result = await onboardingService.resetPassword(
        'reset-token',
        'NewPassword123!',
        'NewPassword123!'
      );

      expect(mockFetch).toHaveBeenCalledWith(
        'http://localhost:8000/api/auth/reset-password',
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            token: 'reset-token',
            new_password: 'NewPassword123!',
            confirm_password: 'NewPassword123!'
          })
        }
      );
      expect(result).toEqual(mockResponse);
    });

    it('should handle invalid reset token', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => ({ detail: 'Geçersiz veya süresi dolmuş token' })
      });

      await expect(onboardingService.resetPassword(
        'invalid-token',
        'password',
        'password'
      )).rejects.toThrow('Geçersiz veya süresi dolmuş token');
    });
  });

  describe('Error Handling', () => {
    it('should handle network errors', async () => {
      mockFetch.mockRejectedValueOnce(new Error('Network error'));

      await expect(onboardingService.registerWithEmail('test@example.com'))
        .rejects.toThrow('Network error');
    });

    it('should handle server errors', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 500,
        json: async () => ({ detail: 'Internal server error' })
      });

      await expect(onboardingService.registerWithEmail('test@example.com'))
        .rejects.toThrow('Internal server error');
    });

    it('should handle malformed JSON responses', async () => {
      mockFetch.mockResolvedValueOnce({
        ok: false,
        status: 400,
        json: async () => { throw new Error('Invalid JSON'); }
      });

      await expect(onboardingService.registerWithEmail('test@example.com'))
        .rejects.toThrow('Invalid JSON');
    });
  });
}); 