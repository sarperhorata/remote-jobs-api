import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../../contexts/AuthContext';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import App from '../../../App';
import { paymentService, userService } from '../../../services/AllServices';

// Mock services
jest.mock('../../../services/AllServices', () => ({
  paymentService: {
    createPaymentIntent: jest.fn(),
    confirmPayment: jest.fn(),
    getPaymentHistory: jest.fn(),
    cancelSubscription: jest.fn(),
  },
  userService: {
    upgradeToPremium: jest.fn(),
    getSubscriptionStatus: jest.fn(),
    updateBillingInfo: jest.fn(),
  },
  authService: {
    getCurrentUser: jest.fn(),
  },
}));

const mockPaymentService = paymentService as jest.Mocked<typeof paymentService>;
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

describe('Payment and Premium Features Critical Path', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorage.clear();
    sessionStorage.clear();
    
    // Mock authenticated user
    localStorage.setItem('authToken', 'mock-token');
    localStorage.setItem('user', JSON.stringify({
      id: '1',
      name: 'Test User',
      email: 'test@example.com',
      isPremium: false
    }));
  });

  describe('Premium Subscription Flow', () => {
    it('should complete full premium subscription process', async () => {
      // Mock payment intent creation
      mockPaymentService.createPaymentIntent.mockResolvedValue({
        clientSecret: 'pi_test_secret',
        paymentIntentId: 'pi_test_123'
      });

      // Mock payment confirmation
      mockPaymentService.confirmPayment.mockResolvedValue({
        success: true,
        paymentId: 'pay_test_123'
      });

      // Mock user upgrade
      mockUserService.upgradeToPremium.mockResolvedValue({
        success: true,
        subscriptionId: 'sub_test_123'
      });

      renderApp();

      // 1. Navigate to pricing page
      const pricingLink = screen.getByText(/Pricing/i) || screen.getByText(/Fiyatlandırma/i);
      fireEvent.click(pricingLink);

      // 2. Select premium plan
      await waitFor(() => {
        const premiumPlan = screen.getByText(/Premium/i);
        expect(premiumPlan).toBeInTheDocument();
      });

      const selectPremiumButton = screen.getByText(/Premium Seç/i) || screen.getByText(/Select Premium/i);
      fireEvent.click(selectPremiumButton);

      // 3. Fill billing information
      const cardNumberInput = screen.getByLabelText(/Card Number/i) || screen.getByLabelText(/Kart Numarası/i);
      const expiryInput = screen.getByLabelText(/Expiry/i) || screen.getByLabelText(/Son Kullanma/i);
      const cvvInput = screen.getByLabelText(/CVV/i);

      fireEvent.change(cardNumberInput, { target: { value: '4242424242424242' } });
      fireEvent.change(expiryInput, { target: { value: '12/25' } });
      fireEvent.change(cvvInput, { target: { value: '123' } });

      // 4. Submit payment
      const payButton = screen.getByText(/Öde/i) || screen.getByText(/Pay/i);
      fireEvent.click(payButton);

      // 5. Verify payment processing
      await waitFor(() => {
        expect(mockPaymentService.createPaymentIntent).toHaveBeenCalled();
      });

      // 6. Verify payment confirmation
      await waitFor(() => {
        expect(mockPaymentService.confirmPayment).toHaveBeenCalled();
      });

      // 7. Verify user upgrade
      await waitFor(() => {
        expect(mockUserService.upgradeToPremium).toHaveBeenCalled();
      });

      // 8. Verify success message
      await waitFor(() => {
        expect(screen.getByText(/Premium üyeliğiniz aktif/i) || screen.getByText(/Premium subscription activated/i)).toBeInTheDocument();
      });
    });

    it('should handle payment failure gracefully', async () => {
      // Mock payment failure
      mockPaymentService.createPaymentIntent.mockRejectedValue(new Error('Payment failed'));

      renderApp();

      // Navigate to pricing
      const pricingLink = screen.getByText(/Pricing/i) || screen.getByText(/Fiyatlandırma/i);
      fireEvent.click(pricingLink);

      // Try to subscribe
      const selectPremiumButton = screen.getByText(/Premium Seç/i) || screen.getByText(/Select Premium/i);
      fireEvent.click(selectPremiumButton);

      // Fill payment info
      const cardNumberInput = screen.getByLabelText(/Card Number/i) || screen.getByLabelText(/Kart Numarası/i);
      fireEvent.change(cardNumberInput, { target: { value: '4000000000000002' } }); // Declined card

      const payButton = screen.getByText(/Öde/i) || screen.getByText(/Pay/i);
      fireEvent.click(payButton);

      // Verify error handling
      await waitFor(() => {
        expect(screen.getByText(/Ödeme başarısız/i) || screen.getByText(/Payment failed/i)).toBeInTheDocument();
      });
    });
  });

  describe('Premium Features Access', () => {
    beforeEach(() => {
      // Mock premium user
      localStorage.setItem('user', JSON.stringify({
        id: '1',
        name: 'Test User',
        email: 'test@example.com',
        isPremium: true
      }));
    });

    it('should access premium features after subscription', async () => {
      renderApp();

      // 1. Navigate to premium features
      const premiumFeaturesLink = screen.getByText(/Premium Özellikler/i) || screen.getByText(/Premium Features/i);
      fireEvent.click(premiumFeaturesLink);

      // 2. Verify premium features are accessible
      await waitFor(() => {
        expect(screen.getByText(/Gelişmiş Arama/i) || screen.getByText(/Advanced Search/i)).toBeInTheDocument();
        expect(screen.getByText(/Öncelikli Başvuru/i) || screen.getByText(/Priority Application/i)).toBeInTheDocument();
      });

      // 3. Test advanced search feature
      const advancedSearchButton = screen.getByText(/Gelişmiş Arama/i) || screen.getByText(/Advanced Search/i);
      fireEvent.click(advancedSearchButton);

      // 4. Verify advanced filters are available
      await waitFor(() => {
        expect(screen.getByText(/Maaş Aralığı/i) || screen.getByText(/Salary Range/i)).toBeInTheDocument();
        expect(screen.getByText(/Şirket Büyüklüğü/i) || screen.getByText(/Company Size/i)).toBeInTheDocument();
      });
    });

    it('should show premium badge and benefits', async () => {
      renderApp();

      // 1. Navigate to profile
      const profileLink = screen.getByText(/Profil/i) || screen.getByText(/Profile/i);
      fireEvent.click(profileLink);

      // 2. Verify premium badge
      await waitFor(() => {
        expect(screen.getByText(/Premium Üye/i) || screen.getByText(/Premium Member/i)).toBeInTheDocument();
      });

      // 3. Verify premium benefits
      expect(screen.getByText(/Sınırsız Başvuru/i) || screen.getByText(/Unlimited Applications/i)).toBeInTheDocument();
      expect(screen.getByText(/Öncelikli Destek/i) || screen.getByText(/Priority Support/i)).toBeInTheDocument();
    });
  });

  describe('Subscription Management', () => {
    it('should manage subscription settings', async () => {
      // Mock subscription status
      mockUserService.getSubscriptionStatus.mockResolvedValue({
        isActive: true,
        plan: 'premium',
        nextBillingDate: '2024-02-01',
        amount: 29.99
      });

      renderApp();

      // 1. Navigate to subscription settings
      const settingsLink = screen.getByText(/Ayarlar/i) || screen.getByText(/Settings/i);
      fireEvent.click(settingsLink);

      const subscriptionTab = screen.getByText(/Abonelik/i) || screen.getByText(/Subscription/i);
      fireEvent.click(subscriptionTab);

      // 2. Verify subscription details
      await waitFor(() => {
        expect(screen.getByText(/Premium Plan/i)).toBeInTheDocument();
        expect(screen.getByText(/29.99/i)).toBeInTheDocument();
      });

      // 3. Test billing info update
      const updateBillingButton = screen.getByText(/Fatura Bilgilerini Güncelle/i) || screen.getByText(/Update Billing/i);
      fireEvent.click(updateBillingButton);

      // 4. Fill new billing info
      const newCardInput = screen.getByLabelText(/New Card Number/i) || screen.getByLabelText(/Yeni Kart Numarası/i);
      fireEvent.change(newCardInput, { target: { value: '5555555555554444' } });

      const saveButton = screen.getByText(/Kaydet/i) || screen.getByText(/Save/i);
      fireEvent.click(saveButton);

      // 5. Verify billing update
      await waitFor(() => {
        expect(mockUserService.updateBillingInfo).toHaveBeenCalled();
      });
    });

    it('should cancel subscription', async () => {
      // Mock subscription cancellation
      mockPaymentService.cancelSubscription.mockResolvedValue({
        success: true,
        cancelledAt: new Date().toISOString()
      });

      renderApp();

      // 1. Navigate to subscription settings
      const settingsLink = screen.getByText(/Ayarlar/i) || screen.getByText(/Settings/i);
      fireEvent.click(settingsLink);

      const subscriptionTab = screen.getByText(/Abonelik/i) || screen.getByText(/Subscription/i);
      fireEvent.click(subscriptionTab);

      // 2. Cancel subscription
      const cancelButton = screen.getByText(/Aboneliği İptal Et/i) || screen.getByText(/Cancel Subscription/i);
      fireEvent.click(cancelButton);

      // 3. Confirm cancellation
      const confirmButton = screen.getByText(/Evet, İptal Et/i) || screen.getByText(/Yes, Cancel/i);
      fireEvent.click(confirmButton);

      // 4. Verify cancellation
      await waitFor(() => {
        expect(mockPaymentService.cancelSubscription).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText(/Abonelik iptal edildi/i) || screen.getByText(/Subscription cancelled/i)).toBeInTheDocument();
      });
    });
  });

  describe('Payment History and Receipts', () => {
    it('should display payment history', async () => {
      // Mock payment history
      mockPaymentService.getPaymentHistory.mockResolvedValue([
        {
          id: 'pay_1',
          amount: 29.99,
          status: 'succeeded',
          date: '2024-01-01',
          description: 'Premium Subscription'
        },
        {
          id: 'pay_2',
          amount: 29.99,
          status: 'succeeded',
          date: '2023-12-01',
          description: 'Premium Subscription'
        }
      ]);

      renderApp();

      // 1. Navigate to payment history
      const settingsLink = screen.getByText(/Ayarlar/i) || screen.getByText(/Settings/i);
      fireEvent.click(settingsLink);

      const billingTab = screen.getByText(/Fatura Geçmişi/i) || screen.getByText(/Billing History/i);
      fireEvent.click(billingTab);

      // 2. Verify payment history
      await waitFor(() => {
        expect(mockPaymentService.getPaymentHistory).toHaveBeenCalled();
      });

      await waitFor(() => {
        expect(screen.getByText(/29.99/i)).toBeInTheDocument();
        expect(screen.getByText(/Premium Subscription/i)).toBeInTheDocument();
      });

      // 3. Download receipt
      const downloadButton = screen.getByText(/Makbuz İndir/i) || screen.getByText(/Download Receipt/i);
      fireEvent.click(downloadButton);

      // 4. Verify download functionality
      await waitFor(() => {
        expect(screen.getByText(/Makbuz indirildi/i) || screen.getByText(/Receipt downloaded/i)).toBeInTheDocument();
      });
    });
  });
});