import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import ForgotPassword from '../../pages/ForgotPassword';
import { onboardingService } from '../../services/onboardingService';

// Mock the service
jest.mock('../../services/onboardingService');

// Mock react-router-dom
const mockNavigate = jest.fn();
jest.mock('react-router-dom', async () => {
  const actual = await jest.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => mockNavigate
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ForgotPassword', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('should render forgot password form correctly', () => {
    renderWithRouter(<ForgotPassword />);
    
    expect(screen.getByText(/Şifremi Unuttum/i)).toBeInTheDocument();
    expect(screen.getByText(/Email adresinizi girin, şifre sıfırlama bağlantısı göndereceğiz/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Email Adresi/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i })).toBeInTheDocument();
  });

  it('should validate email format', async () => {
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'invalid-email');
    fireEvent.click(submitButton);

    expect(screen.getByText(/Geçerli bir email adresi girin/i)).toBeInTheDocument();
  });

  it('should send reset email successfully', async () => {
    const mockResponse = {
      message: 'Şifre sıfırlama bağlantısı email adresinize gönderildi'
    };

    (onboardingService.forgotPassword).mockResolvedValue(mockResponse);

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'test@example.com');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(onboardingService.forgotPassword).toHaveBeenCalledWith('test@example.com');
    });

    expect(screen.getByText(/Email Gönderildi/i)).toBeInTheDocument();
    expect(screen.getByText(/Şifre sıfırlama bağlantısı email adresinize gönderildi/i)).toBeInTheDocument();
    expect(screen.getByText(/Email gelmedi mi\?/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tekrar Gönder/i })).toBeInTheDocument();
  });

  it('should handle email not found error', async () => {
    (onboardingService.forgotPassword).mockRejectedValue(
      new Error('Bu email adresi ile kayıtlı kullanıcı bulunamadı')
    );

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'notfound@example.com');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Bu email adresi ile kayıtlı kullanıcı bulunamadı/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Email adresi sistemde kayıtlı değil/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Yeni hesap oluştur/i })).toBeInTheDocument();
  });

  it('should handle server error', async () => {
    (onboardingService.forgotPassword).mockRejectedValue(
      new Error('Server error')
    );

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'test@example.com');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Bir hata oluştu/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Server error/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tekrar Dene/i })).toBeInTheDocument();
  });

  it('should resend email successfully', async () => {
    const mockResponse = {
      message: 'Şifre sıfırlama bağlantısı email adresinize gönderildi'
    };

    (onboardingService.forgotPassword).mockResolvedValue(mockResponse);

    renderWithRouter(<ForgotPassword />);
    
    // First submission
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'test@example.com');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Email Gönderildi/i)).toBeInTheDocument();
    });

    // Resend email
    const resendButton = screen.getByRole('button', { name: /Tekrar Gönder/i });
    fireEvent.click(resendButton);

    await waitFor(() => {
      expect(onboardingService.forgotPassword).toHaveBeenCalledTimes(2);
    });

    expect(screen.getByText(/Email tekrar gönderildi/i)).toBeInTheDocument();
  });

  it('should show loading state during submission', async () => {
    (onboardingService.forgotPassword).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'test@example.com');
    fireEvent.click(submitButton);

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/Gönderiliyor.../i)).toBeInTheDocument();
  });

  it('should disable submit button for invalid email', async () => {
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    // Initially disabled
    expect(submitButton).toBeDisabled();

    // Invalid email - still disabled
    await user.type(emailInput, 'invalid');
    expect(submitButton).toBeDisabled();

    // Valid email - enabled
    await user.clear(emailInput);
    await user.type(emailInput, 'valid@example.com');
    expect(submitButton).toBeEnabled();
  });

  it('should navigate back to login', () => {
    renderWithRouter(<ForgotPassword />);
    
    const backToLoginLink = screen.getByRole('link', { name: /Giriş sayfasına dön/i });
    expect(backToLoginLink).toHaveAttribute('href', '/');
  });

  it('should show email suggestions for typos', async () => {
    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);

    // Type email with typo
    await user.type(emailInput, 'test@gmial.com');

    expect(screen.getByText(/gmail.com demek istediniz mi\?/i)).toBeInTheDocument();
    
    // Click suggestion
    const suggestionButton = screen.getByRole('button', { name: /gmail.com/i });
    fireEvent.click(suggestionButton);

    expect(emailInput).toHaveValue('test@gmail.com');
  });

  it('should show countdown for resend button', async () => {
    const mockResponse = {
      message: 'Şifre sıfırlama bağlantısı email adresinize gönderildi'
    };

    (onboardingService.forgotPassword).mockResolvedValue(mockResponse);

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'test@example.com');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Email Gönderildi/i)).toBeInTheDocument();
    });

    // Should show countdown
    expect(screen.getByText(/60 saniye sonra tekrar gönderebilirsiniz/i)).toBeInTheDocument();
    
    const resendButton = screen.getByRole('button', { name: /Tekrar Gönder \(60\)/i });
    expect(resendButton).toBeDisabled();
  });

  it('should handle rate limiting error', async () => {
    (onboardingService.forgotPassword).mockRejectedValue(
      new Error('Too many requests. Please try again later.')
    );

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'test@example.com');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Çok fazla deneme/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Bir süre bekleyip tekrar deneyiniz/i)).toBeInTheDocument();
  });

  it('should show help information', () => {
    renderWithRouter(<ForgotPassword />);
    
    expect(screen.getByText(/Email gelmedi mi\?/i)).toBeInTheDocument();
    expect(screen.getByText(/Spam klasörünüzü kontrol edin/i)).toBeInTheDocument();
    expect(screen.getByText(/5-10 dakika bekleyin/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Destek ile iletişime geçin/i })).toBeInTheDocument();
  });

  it('should clear error when email changes', async () => {
    (onboardingService.forgotPassword).mockRejectedValue(
      new Error('Email not found')
    );

    renderWithRouter(<ForgotPassword />);
    
    const emailInput = screen.getByLabelText(/Email Adresi/i);
    const submitButton = screen.getByRole('button', { name: /Sıfırlama Bağlantısı Gönder/i });

    await user.type(emailInput, 'test@example.com');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Email not found/i)).toBeInTheDocument();
    });

    // Change email - error should clear
    await user.clear(emailInput);
    await user.type(emailInput, 'other@example.com');

    expect(screen.queryByText(/Email not found/i)).not.toBeInTheDocument();
  });
}); 