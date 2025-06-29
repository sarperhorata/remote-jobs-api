import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import OnboardingProfileSetup from '../../pages/OnboardingProfileSetup';
import { onboardingService } from '../../services/onboardingService';

// Mock the service
jest.mock('../../services/onboardingService');

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', async () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useLocation: () => ({ state: { userId: 'test-user-id' } })
  };
});

// Mock file reader for CV upload
global.FileReader = jest.fn(() => ({
  readAsDataURL: jest.fn(),
  addEventListener: jest.fn(),
  removeEventListener: jest.fn(),
  result: 'data:application/pdf;base64,mock-pdf-data'
}));

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('OnboardingProfileSetup', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('should render profile setup options', () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    expect(screen.getByText(/Profilinizi Oluşturun/i)).toBeInTheDocument();
    expect(screen.getByText(/LinkedIn ile Bağlan/i)).toBeInTheDocument();
    expect(screen.getByText(/CV Yükle/i)).toBeInTheDocument();
    expect(screen.getByText(/Manuel Giriş/i)).toBeInTheDocument();
  });

  it('should show LinkedIn auth URL when LinkedIn option is selected', async () => {
    const mockAuthUrl = {
      auth_url: 'https://linkedin.com/oauth/authorize?client_id=123',
      state: 'test-state'
    };

    (onboardingService.getLinkedInAuthUrl).mockResolvedValue(mockAuthUrl);

    renderWithRouter(<OnboardingProfileSetup />);
    
    const linkedinButton = screen.getByRole('button', { name: /LinkedIn ile Bağlan/i });
    fireEvent.click(linkedinButton);

    await waitFor(() => {
      expect(onboardingService.getLinkedInAuthUrl).toHaveBeenCalled();
    });

    // Should open LinkedIn auth URL
    expect(window.open).toHaveBeenCalledWith(mockAuthUrl.auth_url, '_blank');
  });

  it('should handle CV upload successfully', async () => {
    const mockUploadResponse = {
      message: 'CV başarıyla yüklendi ve analiz edildi',
      file_url: '/uploads/cv/test.pdf',
      parsed_data: {
        name: 'John Doe',
        email: 'john@example.com',
        skills: ['Python', 'React'],
        experience_years: 5
      }
    };

    (onboardingService.uploadCVWithParsing).mockResolvedValue(mockUploadResponse);

    renderWithRouter(<OnboardingProfileSetup />);
    
    const cvUploadButton = screen.getByRole('button', { name: /CV Yükle/i });
    fireEvent.click(cvUploadButton);

    const fileInput = screen.getByLabelText(/CV dosyanızı seçin/i);
    const file = new File(['cv content'], 'test.pdf', { type: 'application/pdf' });
    
    await user.upload(fileInput, file);

    await waitFor(() => {
      expect(onboardingService.uploadCVWithParsing).toHaveBeenCalledWith(
        'test-user-id',
        file,
        true
      );
    });

    expect(screen.getByText(/CV başarıyla yüklendi/i)).toBeInTheDocument();
    expect(screen.getByText(/Otomatik doldurulan veriler:/i)).toBeInTheDocument();
    expect(screen.getByText(/John Doe/i)).toBeInTheDocument();
    expect(screen.getByText(/Python, React/i)).toBeInTheDocument();
  });

  it('should handle CV upload error', async () => {
    (onboardingService.uploadCVWithParsing).mockRejectedValue(
      new Error('Dosya boyutu çok büyük')
    );

    renderWithRouter(<OnboardingProfileSetup />);
    
    const cvUploadButton = screen.getByRole('button', { name: /CV Yükle/i });
    fireEvent.click(cvUploadButton);

    const fileInput = screen.getByLabelText(/CV dosyanızı seçin/i);
    const file = new File(['large content'], 'large.pdf', { type: 'application/pdf' });
    
    await user.upload(fileInput, file);

    await waitFor(() => {
      expect(screen.getByText(/Dosya boyutu çok büyük/i)).toBeInTheDocument();
    });
  });

  it('should validate CV file type', async () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    const cvUploadButton = screen.getByRole('button', { name: /CV Yükle/i });
    fireEvent.click(cvUploadButton);

    const fileInput = screen.getByLabelText(/CV dosyanızı seçin/i);
    const invalidFile = new File(['text content'], 'test.txt', { type: 'text/plain' });
    
    await user.upload(fileInput, invalidFile);

    expect(screen.getByText(/Sadece PDF, DOC, DOCX dosyaları kabul edilir/i)).toBeInTheDocument();
  });

  it('should show manual profile form when manual option is selected', async () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    const manualButton = screen.getByRole('button', { name: /Manuel Giriş/i });
    fireEvent.click(manualButton);

    expect(screen.getByLabelText(/Ad Soyad/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Meslek/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Şehir/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Yetenekler/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Deneyim \(Yıl\)/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Profili Tamamla/i })).toBeInTheDocument();
  });

  it('should complete manual profile successfully', async () => {
    const mockCompleteResponse = {
      message: 'Profil başarıyla tamamlandı',
      onboarding_step: 4,
      next_step: 'dashboard',
      access_token: 'jwt-token'
    };

    (onboardingService.completeProfile).mockResolvedValue(mockCompleteResponse);

    renderWithRouter(<OnboardingProfileSetup />);
    
    // Select manual option
    const manualButton = screen.getByRole('button', { name: /Manuel Giriş/i });
    fireEvent.click(manualButton);

    // Fill the form
    await user.type(screen.getByLabelText(/Ad Soyad/i), 'John Doe');
    await user.type(screen.getByLabelText(/Meslek/i), 'Software Engineer');
    await user.type(screen.getByLabelText(/Şehir/i), 'Istanbul');
    await user.type(screen.getByLabelText(/Yetenekler/i), 'Python, React, Node.js');
    await user.selectOptions(screen.getByLabelText(/Deneyim \(Yıl\)/i), '5');

    const submitButton = screen.getByRole('button', { name: /Profili Tamamla/i });
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(onboardingService.completeProfile).toHaveBeenCalledWith(
        'test-user-id',
        {
          name: 'John Doe',
          title: 'Software Engineer',
          location: 'Istanbul',
          skills: ['Python', 'React', 'Node.js'],
          experience_years: 5
        }
      );
    });

    expect(screen.getByText(/Profil başarıyla tamamlandı/i)).toBeInTheDocument();
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/dashboard');
    });
  });

  it('should validate required fields in manual form', async () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    const manualButton = screen.getByRole('button', { name: /Manuel Giriş/i });
    fireEvent.click(manualButton);

    const submitButton = screen.getByRole('button', { name: /Profili Tamamla/i });
    fireEvent.click(submitButton);

    expect(screen.getByText(/Ad Soyad gereklidir/i)).toBeInTheDocument();
  });

  it('should show progress indicator', () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    expect(screen.getByText(/Adım 3\/4/i)).toBeInTheDocument();
    expect(screen.getByTestId('progress-bar')).toBeInTheDocument();
    expect(screen.getByTestId('progress-bar')).toHaveAttribute('value', '75');
  });

  it('should handle LinkedIn callback successfully', async () => {
    const mockCallbackResponse = {
      message: 'LinkedIn başarıyla bağlandı',
      onboarding_step: 3,
      next_step: 'complete_profile',
      linkedin_profile: {
        id: 'linkedin-123',
        firstName: { en_US: 'John' },
        lastName: { en_US: 'Doe' }
      }
    };

    (onboardingService.handleLinkedInCallback).mockResolvedValue(mockCallbackResponse);

    // Simulate LinkedIn callback URL
    (require('react-router-dom').useLocation).mockReturnValue({
      state: { userId: 'test-user-id' },
      search: '?code=auth-code&state=test-state'
    });

    renderWithRouter(<OnboardingProfileSetup />);

    await waitFor(() => {
      expect(onboardingService.handleLinkedInCallback).toHaveBeenCalledWith(
        'auth-code',
        'test-state',
        'test-user-id'
      );
    });

    expect(screen.getByText(/LinkedIn başarıyla bağlandı/i)).toBeInTheDocument();
    expect(screen.getByText(/Profil bilgileriniz otomatik dolduruldu/i)).toBeInTheDocument();
  });

  it('should handle LinkedIn callback error', async () => {
    (onboardingService.handleLinkedInCallback).mockRejectedValue(
      new Error('LinkedIn bağlantısında hata oluştu')
    );

    (require('react-router-dom').useLocation).mockReturnValue({
      state: { userId: 'test-user-id' },
      search: '?code=invalid-code&state=test-state'
    });

    renderWithRouter(<OnboardingProfileSetup />);

    await waitFor(() => {
      expect(screen.getByText(/LinkedIn bağlantısında hata oluştu/i)).toBeInTheDocument();
    });
  });

  it('should allow switching between profile setup methods', async () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    // Start with LinkedIn
    const linkedinButton = screen.getByRole('button', { name: /LinkedIn ile Bağlan/i });
    fireEvent.click(linkedinButton);

    // Switch to CV upload
    const cvButton = screen.getByRole('button', { name: /CV Yükle/i });
    fireEvent.click(cvButton);
    expect(screen.getByLabelText(/CV dosyanızı seçin/i)).toBeInTheDocument();

    // Switch to manual
    const manualButton = screen.getByRole('button', { name: /Manuel Giriş/i });
    fireEvent.click(manualButton);
    expect(screen.getByLabelText(/Ad Soyad/i)).toBeInTheDocument();
  });

  it('should show skills input with autocomplete', async () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    const manualButton = screen.getByRole('button', { name: /Manuel Giriş/i });
    fireEvent.click(manualButton);

    const skillsInput = screen.getByLabelText(/Yetenekler/i);
    await user.type(skillsInput, 'Pyth');

    // Should show autocomplete suggestions
    expect(screen.getByText(/Python/i)).toBeInTheDocument();
    expect(screen.getByText(/PyTorch/i)).toBeInTheDocument();
  });

  it('should handle back navigation', async () => {
    renderWithRouter(<OnboardingProfileSetup />);
    
    const backButton = screen.getByRole('button', { name: /Geri/i });
    fireEvent.click(backButton);

    expect(mockNavigate).toHaveBeenCalledWith(-1);
  });

  it('should show loading state during profile completion', async () => {
    (onboardingService.completeProfile).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithRouter(<OnboardingProfileSetup />);
    
    const manualButton = screen.getByRole('button', { name: /Manuel Giriş/i });
    fireEvent.click(manualButton);

    await user.type(screen.getByLabelText(/Ad Soyad/i), 'John Doe');
    
    const submitButton = screen.getByRole('button', { name: /Profili Tamamla/i });
    fireEvent.click(submitButton);

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
  });
}); 