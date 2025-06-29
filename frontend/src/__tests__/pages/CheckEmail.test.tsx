import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CheckEmail from '../../pages/CheckEmail';
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
    useLocation: () => ({ state: { email: 'test@example.com' } })
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('CheckEmail', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('should render email check message correctly', () => {
    renderWithRouter(<CheckEmail />);
    
    expect(screen.getByText(/Email Gönderildi/i)).toBeInTheDocument();
    expect(screen.getByText(/test@example.com/i)).toBeInTheDocument();
    expect(screen.getByText(/adresine doğrulama emaili gönderdik/i)).toBeInTheDocument();
    expect(screen.getByText(/Email kutunuzu kontrol edin/i)).toBeInTheDocument();
  });

  it('should show email instructions and tips', () => {
    renderWithRouter(<CheckEmail />);
    
    expect(screen.getByText(/Email gelmedi mi\?/i)).toBeInTheDocument();
    expect(screen.getByText(/Spam\/Junk klasörünüzü kontrol edin/i)).toBeInTheDocument();
    expect(screen.getByText(/Email'in gelmesi 2-5 dakika sürebilir/i)).toBeInTheDocument();
    expect(screen.getByText(/Email adresinizi yanlış mı yazdınız\?/i)).toBeInTheDocument();
  });

  it('should handle resend email successfully', async () => {
    const mockResponse = {
      message: 'Email tekrar gönderildi'
    };

    (onboardingService.registerWithEmail).mockResolvedValue(mockResponse);

    renderWithRouter(<CheckEmail />);
    
    const resendButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
    fireEvent.click(resendButton);

    await waitFor(() => {
      expect(onboardingService.registerWithEmail).toHaveBeenCalledWith('test@example.com');
    });

    expect(screen.getByText(/Email tekrar gönderildi/i)).toBeInTheDocument();
    expect(screen.getByTestId('success-message')).toBeInTheDocument();
  });

  it('should handle resend email error', async () => {
    (onboardingService.registerWithEmail).mockRejectedValue(
      new Error('Too many requests')
    );

    renderWithRouter(<CheckEmail />);
    
    const resendButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
    fireEvent.click(resendButton);

    await waitFor(() => {
      expect(screen.getByText(/Too many requests/i)).toBeInTheDocument();
    });

    expect(screen.getByTestId('error-message')).toBeInTheDocument();
  });

  it('should show countdown for resend button', async () => {
    renderWithRouter(<CheckEmail />);
    
    const resendButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
    
    // Initially enabled
    expect(resendButton).toBeEnabled();

    // After click, should show countdown
    (onboardingService.registerWithEmail).mockResolvedValue({
      message: 'Email tekrar gönderildi'
    });

    fireEvent.click(resendButton);

    await waitFor(() => {
      expect(screen.getByText(/60 saniye sonra tekrar gönderebilirsiniz/i)).toBeInTheDocument();
    });

    // Button should be disabled with countdown
    const countdownButton = screen.getByRole('button', { name: /Tekrar Gönder \(60\)/i });
    expect(countdownButton).toBeDisabled();
  });

  it('should enable resend button after countdown', async () => {
    jest.useFakeTimers();
    
    renderWithRouter(<CheckEmail />);
    
    (onboardingService.registerWithEmail).mockResolvedValue({
      message: 'Email tekrar gönderildi'
    });

    const resendButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
    fireEvent.click(resendButton);

    await waitFor(() => {
      expect(screen.getByText(/60 saniye sonra/i)).toBeInTheDocument();
    });

    // Fast forward 60 seconds
    jest.advanceTimersByTime(60000);

    await waitFor(() => {
      const enabledButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
      expect(enabledButton).toBeEnabled();
    });

    jest.useRealTimers();
  });

  it('should navigate to different email when change email is clicked', () => {
    renderWithRouter(<CheckEmail />);
    
    const changeEmailButton = screen.getByRole('button', { name: /Farklı Email Kullan/i });
    fireEvent.click(changeEmailButton);

    expect(mockNavigate).toHaveBeenCalledWith('/register');
  });

  it('should handle missing email from navigation state', () => {
    (require('react-router-dom').useLocation).mockReturnValue({
      state: null
    });

    renderWithRouter(<CheckEmail />);

    expect(screen.getByText(/Email doğrulama sayfası/i)).toBeInTheDocument();
    expect(screen.getByText(/Email adresinize doğrulama bağlantısı gönderildi/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Giriş sayfasına dön/i })).toBeInTheDocument();
  });

  it('should show loading state during resend', async () => {
    (onboardingService.registerWithEmail).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithRouter(<CheckEmail />);
    
    const resendButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
    fireEvent.click(resendButton);

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(screen.getByText(/Gönderiliyor.../i)).toBeInTheDocument();
    expect(resendButton).toBeDisabled();
  });

  it('should show email client suggestions', () => {
    renderWithRouter(<CheckEmail />);
    
    expect(screen.getByText(/Email uygulamanızı açın/i)).toBeInTheDocument();
    
    const gmailLink = screen.getByRole('link', { name: /Gmail'i Aç/i });
    expect(gmailLink).toHaveAttribute('href', 'https://mail.google.com');
    expect(gmailLink).toHaveAttribute('target', '_blank');

    const outlookLink = screen.getByRole('link', { name: /Outlook'u Aç/i });
    expect(outlookLink).toHaveAttribute('href', 'https://outlook.live.com');
    expect(outlookLink).toHaveAttribute('target', '_blank');
  });

  it('should show help and support options', () => {
    renderWithRouter(<CheckEmail />);
    
    expect(screen.getByText(/Hala problem yaşıyorsunuz\?/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Destek ekibimizle iletişime geçin/i })).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /SSS sayfasını inceleyin/i })).toBeInTheDocument();
  });

  it('should display correct email domain suggestions', () => {
    (require('react-router-dom').useLocation).mockReturnValue({
      state: { email: 'user@gmial.com' }
    });

    renderWithRouter(<CheckEmail />);
    
    expect(screen.getByText(/user@gmial.com/i)).toBeInTheDocument();
    expect(screen.getByText(/gmail.com demek istediniz mi\?/i)).toBeInTheDocument();
    
    const correctionButton = screen.getByRole('button', { name: /gmail.com'a düzelt/i });
    fireEvent.click(correctionButton);

    expect(mockNavigate).toHaveBeenCalledWith('/register', { 
      state: { email: 'user@gmail.com' } 
    });
  });

  it('should show different messages for different email providers', () => {
    const emailProviders = [
      { email: 'user@gmail.com', provider: 'Gmail' },
      { email: 'user@outlook.com', provider: 'Outlook' },
      { email: 'user@yahoo.com', provider: 'Yahoo' },
      { email: 'user@company.com', provider: 'work email' }
    ];

    emailProviders.forEach(({ email, provider }) => {
      (require('react-router-dom').useLocation).mockReturnValue({
        state: { email }
      });

      const { rerender } = renderWithRouter(<CheckEmail />);
      
      expect(screen.getByText(new RegExp(provider, 'i'))).toBeInTheDocument();
      
      rerender(<div />); // Clean up for next iteration
    });
  });

  it('should handle multiple resend attempts with rate limiting', async () => {
    renderWithRouter(<CheckEmail />);
    
    // First resend - success
    (onboardingService.registerWithEmail).mockResolvedValueOnce({
      message: 'Email tekrar gönderildi'
    });

    const resendButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
    fireEvent.click(resendButton);

    await waitFor(() => {
      expect(screen.getByText(/Email tekrar gönderildi/i)).toBeInTheDocument();
    });

    // Second resend attempt - rate limited
    (onboardingService.registerWithEmail).mockRejectedValueOnce(
      new Error('Rate limit exceeded. Please wait before retrying.')
    );

    // Try to click again (should be disabled during countdown)
    const disabledButton = screen.getByRole('button', { name: /Tekrar Gönder \(\d+\)/i });
    expect(disabledButton).toBeDisabled();
  });

  it('should show email verification progress steps', () => {
    renderWithRouter(<CheckEmail />);
    
    expect(screen.getByText(/Adım 1/i)).toBeInTheDocument();
    expect(screen.getByText(/Email kutunuzu kontrol edin/i)).toBeInTheDocument();
    
    expect(screen.getByText(/Adım 2/i)).toBeInTheDocument();
    expect(screen.getByText(/Doğrulama bağlantısına tıklayın/i)).toBeInTheDocument();
    
    expect(screen.getByText(/Adım 3/i)).toBeInTheDocument();
    expect(screen.getByText(/Şifre belirleme sayfasına yönlendirileceksiniz/i)).toBeInTheDocument();
  });

  it('should handle back navigation to login page', () => {
    renderWithRouter(<CheckEmail />);
    
    const backToLoginLink = screen.getByRole('link', { name: /Giriş sayfasına dön/i });
    expect(backToLoginLink).toHaveAttribute('href', '/');
  });

  it('should clear success/error messages after some time', async () => {
    jest.useFakeTimers();
    
    renderWithRouter(<CheckEmail />);
    
    (onboardingService.registerWithEmail).mockResolvedValue({
      message: 'Email tekrar gönderildi'
    });

    const resendButton = screen.getByRole('button', { name: /Email'i Tekrar Gönder/i });
    fireEvent.click(resendButton);

    await waitFor(() => {
      expect(screen.getByText(/Email tekrar gönderildi/i)).toBeInTheDocument();
    });

    // Success message should disappear after 5 seconds
    jest.advanceTimersByTime(5000);

    await waitFor(() => {
      expect(screen.queryByText(/Email tekrar gönderildi/i)).not.toBeInTheDocument();
    });

    jest.useRealTimers();
  });
}); 