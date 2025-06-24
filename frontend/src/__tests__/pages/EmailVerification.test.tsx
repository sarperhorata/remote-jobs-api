import { render, screen, waitFor } from '@testing-library/react';
import EmailVerification from '../../pages/EmailVerification';
import { onboardingService } from '../../services/onboardingService';

// Mock the service
jest.mock('../../services/onboardingService');

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', async () => {
  const actual = await jest.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate,
    useSearchParams: jest.fn(() => [new URLSearchParams('token=test-token')])
  };
});

// Mock localStorage
const mockLocalStorage = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: mockLocalStorage
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('EmailVerification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('should render loading state initially', () => {
    renderWithRouter(<EmailVerification />);
    
    expect(screen.getByText(/Email Doğrulanıyor/i)).toBeInTheDocument();
    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
  });

  it('should verify email successfully and navigate to next step', async () => {
    const mockResponse = {
      message: 'Email başarıyla doğrulandı',
      onboarding_step: 1,
      next_step: 'set_password'
    };

    (onboardingService.verifyEmail).mockResolvedValue(mockResponse);

    renderWithRouter(<EmailVerification />);

    await waitFor(() => {
      expect(onboardingService.verifyEmail).toHaveBeenCalledWith('test-token');
    });

    expect(screen.getByText(/Email başarıyla doğrulandı/i)).toBeInTheDocument();
    expect(screen.getByText(/Şifre belirleme sayfasına yönlendiriliyorsunuz/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/set-password?token=test-token');
    }, { timeout: 3000 });
  });

  it('should handle invalid token error', async () => {
    (onboardingService.verifyEmail).mockRejectedValue(
      new Error('Geçersiz veya süresi dolmuş token')
    );

    renderWithRouter(<EmailVerification />);

    await waitFor(() => {
      expect(screen.getByText(/Email Doğrulama Hatası/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Geçersiz veya süresi dolmuş token/i)).toBeInTheDocument();
    expect(screen.getByText(/Yeni doğrulama emaili almak için/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /buraya tıklayın/i })).toBeInTheDocument();
  });

  it('should handle network error', async () => {
    (onboardingService.verifyEmail).mockRejectedValue(
      new Error('Network error')
    );

    renderWithRouter(<EmailVerification />);

    await waitFor(() => {
      expect(screen.getByText(/Bağlantı Hatası/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/İnternet bağlantınızı kontrol edin/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tekrar Dene/i })).toBeInTheDocument();
  });

  it('should handle missing token', async () => {
    (require('react-router-dom').useSearchParams).mockReturnValue([
      new URLSearchParams('')
    ]);

    renderWithRouter(<EmailVerification />);

    expect(screen.getByText(/Geçersiz Bağlantı/i)).toBeInTheDocument();
    expect(screen.getByText(/Email doğrulama bağlantısı geçersiz/i)).toBeInTheDocument();
  });

  it('should retry verification on button click', async () => {
    (onboardingService.verifyEmail)
      .mockRejectedValueOnce(new Error('Network error'))
      .mockResolvedValue({
        message: 'Email başarıyla doğrulandı',
        onboarding_step: 1,
        next_step: 'set_password'
      });

    renderWithRouter(<EmailVerification />);

    await waitFor(() => {
      expect(screen.getByRole('button', { name: /Tekrar Dene/i })).toBeInTheDocument();
    });

    const retryButton = screen.getByRole('button', { name: /Tekrar Dene/i });
    retryButton.click();

    await waitFor(() => {
      expect(onboardingService.verifyEmail).toHaveBeenCalledTimes(2);
    });

    await waitFor(() => {
      expect(screen.getByText(/Email başarıyla doğrulandı/i)).toBeInTheDocument();
    });
  });

  it('should show correct countdown timer', async () => {
    const mockResponse = {
      message: 'Email başarıyla doğrulandı',
      onboarding_step: 1,
      next_step: 'set_password'
    };

    (onboardingService.verifyEmail).mockResolvedValue(mockResponse);

    renderWithRouter(<EmailVerification />);

    await waitFor(() => {
      expect(screen.getByText(/Email başarıyla doğrulandı/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/3 saniye içinde/i)).toBeInTheDocument();
  });

  it('should handle already verified email', async () => {
    (onboardingService.verifyEmail).mockRejectedValue(
      new Error('Email zaten doğrulanmış')
    );

    renderWithRouter(<EmailVerification />);

    await waitFor(() => {
      expect(screen.getByText(/Email Zaten Doğrulanmış/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Bu email adresi zaten doğrulanmış/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Giriş yap/i })).toBeInTheDocument();
  });
}); 