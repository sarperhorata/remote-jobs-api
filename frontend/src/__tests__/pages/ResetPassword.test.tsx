import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import ResetPassword from '../../pages/ResetPassword';
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
    useSearchParams: jest.fn(() => [new URLSearchParams('token=reset-token')])
  };
});

const renderWithRouter = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ResetPassword', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
    mockNavigate.mockClear();
  });

  it('should render reset password form correctly', () => {
    renderWithRouter(<ResetPassword />);
    
    expect(screen.getByText(/Yeni Şifre Belirle/i)).toBeInTheDocument();
    expect(screen.getByText(/Hesabınız için yeni bir şifre oluşturun/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Yeni Şifre/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/Şifre Tekrar/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Şifreyi Sıfırla/i })).toBeInTheDocument();
  });

  it('should show password strength indicator', async () => {
    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    
    await user.type(passwordInput, 'weak');
    expect(screen.getByText(/Zayıf/i)).toBeInTheDocument();
    expect(screen.getByTestId('strength-indicator')).toHaveClass('strength-weak');

    await user.clear(passwordInput);
    await user.type(passwordInput, 'MediumPass123');
    expect(screen.getByText(/Orta/i)).toBeInTheDocument();
    expect(screen.getByTestId('strength-indicator')).toHaveClass('strength-medium');

    await user.clear(passwordInput);
    await user.type(passwordInput, 'StrongPass123!@#');
    expect(screen.getByText(/Güçlü/i)).toBeInTheDocument();
    expect(screen.getByTestId('strength-indicator')).toHaveClass('strength-strong');
  });

  it('should validate password requirements', async () => {
    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    // Test minimum length
    await user.type(passwordInput, '123');
    fireEvent.click(submitButton);
    expect(screen.getByText(/en az 8 karakter/i)).toBeInTheDocument();

    // Test uppercase requirement
    await user.clear(passwordInput);
    await user.type(passwordInput, 'lowercase123');
    fireEvent.click(submitButton);
    expect(screen.getByText(/büyük harf/i)).toBeInTheDocument();

    // Test number requirement  
    await user.clear(passwordInput);
    await user.type(passwordInput, 'NoNumbers');
    fireEvent.click(submitButton);
    expect(screen.getByText(/rakam/i)).toBeInTheDocument();
  });

  it('should validate password confirmation match', async () => {
    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    await user.type(passwordInput, 'ValidPass123!');
    await user.type(confirmInput, 'DifferentPass123!');
    
    fireEvent.click(submitButton);
    
    expect(screen.getByText(/eşleşmiyor/i)).toBeInTheDocument();
  });

  it('should reset password successfully and navigate to login', async () => {
    const mockResponse = {
      message: 'Şifre başarıyla sıfırlandı'
    };

    (onboardingService.resetPassword).mockResolvedValue(mockResponse);

    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    await user.type(passwordInput, 'NewSecurePass123!');
    await user.type(confirmInput, 'NewSecurePass123!');
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(onboardingService.resetPassword).toHaveBeenCalledWith(
        'reset-token',
        'NewSecurePass123!',
        'NewSecurePass123!'
      );
    });

    expect(screen.getByText(/Şifre başarıyla sıfırlandı/i)).toBeInTheDocument();
    expect(screen.getByText(/Giriş sayfasına yönlendiriliyorsunuz/i)).toBeInTheDocument();
    
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith('/');
    }, { timeout: 3000 });
  });

  it('should handle invalid token error', async () => {
    (onboardingService.resetPassword).mockRejectedValue(
      new Error('Geçersiz veya süresi dolmuş token')
    );

    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    await user.type(passwordInput, 'NewSecurePass123!');
    await user.type(confirmInput, 'NewSecurePass123!');
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Geçersiz Token/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Şifre sıfırlama bağlantısının süresi dolmuş/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Yeni sıfırlama bağlantısı al/i })).toBeInTheDocument();
  });

  it('should handle server error', async () => {
    (onboardingService.resetPassword).mockRejectedValue(
      new Error('Server error')
    );

    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    await user.type(passwordInput, 'NewSecurePass123!');
    await user.type(confirmInput, 'NewSecurePass123!');
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Bir hata oluştu/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Server error/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /Tekrar Dene/i })).toBeInTheDocument();
  });

  it('should toggle password visibility', async () => {
    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const passwordToggle = screen.getByTestId('password-toggle');
    const confirmToggle = screen.getByTestId('confirm-toggle');

    // Initially password type
    expect(passwordInput).toHaveAttribute('type', 'password');
    expect(confirmInput).toHaveAttribute('type', 'password');

    // Toggle password visibility
    fireEvent.click(passwordToggle);
    expect(passwordInput).toHaveAttribute('type', 'text');

    fireEvent.click(confirmToggle);
    expect(confirmInput).toHaveAttribute('type', 'text');

    // Toggle back to hidden
    fireEvent.click(passwordToggle);
    expect(passwordInput).toHaveAttribute('type', 'password');
  });

  it('should disable submit button when form is invalid', async () => {
    renderWithRouter(<ResetPassword />);
    
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });
    
    // Initially disabled
    expect(submitButton).toBeDisabled();

    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    await user.type(passwordInput, 'weak');
    
    // Still disabled for weak password
    expect(submitButton).toBeDisabled();

    await user.clear(passwordInput);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    await user.type(passwordInput, 'StrongPass123!');
    await user.type(confirmInput, 'StrongPass123!');
    
    // Enabled when both passwords are valid and match
    expect(submitButton).toBeEnabled();
  });

  it('should show loading state during submission', async () => {
    (onboardingService.resetPassword).mockImplementation(
      () => new Promise(resolve => setTimeout(resolve, 100))
    );

    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    await user.type(passwordInput, 'NewSecurePass123!');
    await user.type(confirmInput, 'NewSecurePass123!');
    
    fireEvent.click(submitButton);

    expect(screen.getByTestId('loading-spinner')).toBeInTheDocument();
    expect(submitButton).toBeDisabled();
    expect(screen.getByText(/Sıfırlanıyor.../i)).toBeInTheDocument();
  });

  it('should handle missing token in URL', () => {
    (require('react-router-dom').useSearchParams).mockReturnValue([
      new URLSearchParams('')
    ]);

    renderWithRouter(<ResetPassword />);

    expect(screen.getByText(/Geçersiz Bağlantı/i)).toBeInTheDocument();
    expect(screen.getByText(/Şifre sıfırlama bağlantısı geçersiz/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Yeni bağlantı talep et/i })).toBeInTheDocument();
  });

  it('should show password requirements checklist', async () => {
    renderWithRouter(<ResetPassword />);
    
    expect(screen.getByText(/En az 8 karakter/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir büyük harf/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir küçük harf/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir rakam/i)).toBeInTheDocument();
    expect(screen.getByText(/En az bir özel karakter/i)).toBeInTheDocument();

    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    await user.type(passwordInput, 'StrongPass123!');

    // Requirements should be marked as met
    expect(screen.getByTestId('requirement-length')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-uppercase')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-lowercase')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-number')).toHaveClass('requirement-met');
    expect(screen.getByTestId('requirement-special')).toHaveClass('requirement-met');
  });

  it('should show success countdown timer', async () => {
    const mockResponse = {
      message: 'Şifre başarıyla sıfırlandı'
    };

    (onboardingService.resetPassword).mockResolvedValue(mockResponse);

    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    await user.type(passwordInput, 'NewSecurePass123!');
    await user.type(confirmInput, 'NewSecurePass123!');
    
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Şifre başarıyla sıfırlandı/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/5 saniye içinde/i)).toBeInTheDocument();
    expect(screen.getByRole('link', { name: /Hemen giriş yap/i })).toBeInTheDocument();
  });

  it('should navigate back to forgot password page', () => {
    renderWithRouter(<ResetPassword />);
    
    const backLink = screen.getByRole('link', { name: /Geri dön/i });
    expect(backLink).toHaveAttribute('href', '/forgot-password');
  });

  it('should handle password strength validation on blur', async () => {
    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);

    await user.type(passwordInput, 'weak');
    fireEvent.blur(passwordInput);

    expect(screen.getByText(/Şifre çok zayıf/i)).toBeInTheDocument();
    expect(screen.getByText(/Daha güçlü bir şifre seçin/i)).toBeInTheDocument();
  });

  it('should clear form errors when user starts typing', async () => {
    (onboardingService.resetPassword).mockRejectedValue(
      new Error('Invalid password')
    );

    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);
    const submitButton = screen.getByRole('button', { name: /Şifreyi Sıfırla/i });

    await user.type(passwordInput, 'BadPass123!');
    await user.type(confirmInput, 'BadPass123!');
    fireEvent.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/Invalid password/i)).toBeInTheDocument();
    });

    // Start typing again - error should clear
    await user.clear(passwordInput);
    await user.type(passwordInput, 'NewPass');

    expect(screen.queryByText(/Invalid password/i)).not.toBeInTheDocument();
  });

  it('should handle different password mismatch errors', async () => {
    renderWithRouter(<ResetPassword />);
    
    const passwordInput = screen.getByLabelText(/^Yeni Şifre$/i);
    const confirmInput = screen.getByLabelText(/Şifre Tekrar/i);

    await user.type(passwordInput, 'Password123!');
    await user.type(confirmInput, 'Different123!');
    
    fireEvent.blur(confirmInput);

    expect(screen.getByText(/Şifreler eşleşmiyor/i)).toBeInTheDocument();
    expect(screen.getByTestId('confirm-input')).toHaveClass('error');
  });
}); 