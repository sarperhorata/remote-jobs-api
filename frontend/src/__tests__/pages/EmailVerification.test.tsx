import React from 'react';
import { render, screen, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import EmailVerification from '../../pages/EmailVerification';
import { onboardingService } from '../../services/onboardingService';

// Mock the service
jest.mock('../../services/onboardingService');

// Mock react-router-dom
jest.mock('react-router-dom', () => {
  const actual = jest.requireActual('react-router-dom');
  return {
    ...actual,
    useSearchParams: () => [
      new URLSearchParams('?token=test-token'),
      jest.fn()
    ],
    useNavigate: () => jest.fn(),
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

const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>
    {children}
  </BrowserRouter>
);

describe('EmailVerification', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('renders verification page', () => {
    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    expect(screen.getByText('Verifying Your Email')).toBeInTheDocument();
  });

  it('shows loading state initially', () => {
    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    expect(screen.getByText('Please wait while we verify your email...')).toBeInTheDocument();
  });

  it('handles successful verification', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: true,
      json: () => Promise.resolve({ message: 'Email verified successfully' })
    });
    global.fetch = mockFetch;

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(mockFetch).toHaveBeenCalledWith('/api/auth/verify-email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: 'test-token' })
      });
    });
  });

  it('handles verification error', async () => {
    const mockFetch = jest.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ message: 'Invalid token' })
    });
    global.fetch = mockFetch;

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('Verification Failed')).toBeInTheDocument();
    });
  });

  it('should verify email successfully and navigate to next step', async () => {
    const mockResponse = {
      message: 'Email başarıyla doğrulandı',
      onboarding_step: 1,
      next_step: 'set_password'
    };

    (onboardingService.verifyEmail).mockResolvedValue(mockResponse);

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(onboardingService.verifyEmail).toHaveBeenCalledWith('test-token');
    });

    expect(screen.getByText(/Email başarıyla doğrulandı/i)).toBeInTheDocument();
    expect(screen.getByText(/Şifre belirleme sayfasına yönlendiriliyorsunuz/i)).toBeInTheDocument();

    await waitFor(() => {
      expect(jest.requireActual('react-router-dom').useNavigate).toHaveBeenCalledWith('/set-password?token=test-token');
    }, { timeout: 3000 });
  });

  it('should handle invalid token error', async () => {
    (onboardingService.verifyEmail).mockRejectedValue(
      new Error('Geçersiz veya süresi dolmuş token')
    );

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

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

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Bağlantı Hatası/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/İnternet bağlantınızı kontrol edin/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tekrar Dene/i })).toBeInTheDocument();
  });

  it('should handle missing token', async () => {
    (jest.requireActual('react-router-dom').useSearchParams).mockReturnValue([
      new URLSearchParams('')
    ]);

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

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

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

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

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Email başarıyla doğrulandı/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/3 saniye içinde/i)).toBeInTheDocument();
  });

  it('should handle already verified email', async () => {
    (onboardingService.verifyEmail).mockRejectedValue(
      new Error('Email zaten doğrulanmış')
    );

    render(
      <TestWrapper>
        <EmailVerification />
      </TestWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText(/Email Zaten Doğrulanmış/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Bu email adresi zaten doğrulanmış/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Giriş yap/i })).toBeInTheDocument();
  });
}); 