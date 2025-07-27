import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CookieDisclaimer from '../../components/CookieDisclaimer';

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
Object.defineProperty(window, 'localStorage', {
  value: localStorageMock,
});

// Mock icons
jest.mock('../../components/icons/EmojiIcons', () => ({
  X: ({ className }: { className?: string }) => <div data-testid="x-icon" className={className}>X</div>,
  Cookie: ({ className }: { className?: string }) => <div data-testid="cookie-icon" className={className}>Cookie</div>,
  Settings: ({ className }: { className?: string }) => <div data-testid="settings-icon" className={className}>Settings</div>,
}));

const renderCookieDisclaimer = () => {
  return render(
    <BrowserRouter>
      <CookieDisclaimer />
    </BrowserRouter>
  );
};

describe('CookieDisclaimer Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    localStorageMock.getItem.mockReturnValue(null); // No previous consent
  });

  test('renders cookie banner when no consent is given', () => {
    renderCookieDisclaimer();
    
    expect(screen.getByText('We use cookies to enhance your experience')).toBeInTheDocument();
    expect(screen.getByText(/We use cookies to analyze site traffic/)).toBeInTheDocument();
    expect(screen.getByText('Accept All')).toBeInTheDocument();
    expect(screen.getByText('Essential Only')).toBeInTheDocument();
  });

  test('does not render when consent is already given', () => {
    localStorageMock.getItem.mockReturnValue(JSON.stringify({
      essential: true,
      performance: true,
      functionality: true,
      marketing: true
    }));
    
    renderCookieDisclaimer();
    
    expect(screen.queryByText('We use cookies to enhance your experience')).not.toBeInTheDocument();
  });

  test('accepts all cookies when Accept All is clicked', () => {
    renderCookieDisclaimer();
    
    const acceptAllButton = screen.getByText('Accept All');
    fireEvent.click(acceptAllButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('cookieConsent', JSON.stringify({
      essential: true,
      performance: true,
      functionality: true,
      marketing: true
    }));
    
    // Banner should disappear
    expect(screen.queryByText('We use cookies to enhance your experience')).not.toBeInTheDocument();
  });

  test('accepts only essential cookies when Essential Only is clicked', () => {
    renderCookieDisclaimer();
    
    const essentialOnlyButton = screen.getByText('Essential Only');
    fireEvent.click(essentialOnlyButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('cookieConsent', JSON.stringify({
      essential: true,
      performance: false,
      functionality: false,
      marketing: false
    }));
    
    // Banner should disappear
    expect(screen.queryByText('We use cookies to enhance your experience')).not.toBeInTheDocument();
  });

  test('shows settings when Customize is clicked', () => {
    renderCookieDisclaimer();
    
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    expect(screen.getByText('Cookie Preferences')).toBeInTheDocument();
    expect(screen.getByText('Essential Cookies')).toBeInTheDocument();
    expect(screen.getByText('Performance Cookies')).toBeInTheDocument();
    expect(screen.getByText('Functionality Cookies')).toBeInTheDocument();
    expect(screen.getByText('Marketing Cookies')).toBeInTheDocument();
  });

  test('allows toggling cookie preferences', () => {
    renderCookieDisclaimer();
    
    // Open settings
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    // Get all checkboxes
    const checkboxes = screen.getAllByRole('checkbox');
    const performanceCheckbox = checkboxes[1]; // Second checkbox (first is essential)
    const functionalityCheckbox = checkboxes[2]; // Third checkbox
    
    // Toggle performance cookies
    fireEvent.click(performanceCheckbox);
    expect(performanceCheckbox).toBeChecked();
    
    // Toggle functionality cookies
    fireEvent.click(functionalityCheckbox);
    expect(functionalityCheckbox).toBeChecked();
  });

  test('essential cookies cannot be disabled', () => {
    renderCookieDisclaimer();
    
    // Open settings
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    const checkboxes = screen.getAllByRole('checkbox');
    const essentialCheckbox = checkboxes[0]; // First checkbox
    expect(essentialCheckbox).toBeDisabled();
    expect(essentialCheckbox).toBeChecked();
    
    // Try to click it
    fireEvent.click(essentialCheckbox);
    
    // Should still be checked and disabled
    expect(essentialCheckbox).toBeChecked();
    expect(essentialCheckbox).toBeDisabled();
  });

  test('saves preferences when Save Preferences is clicked', () => {
    renderCookieDisclaimer();
    
    // Open settings
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    // Toggle some preferences
    const checkboxes = screen.getAllByRole('checkbox');
    const performanceCheckbox = checkboxes[1]; // Second checkbox
    fireEvent.click(performanceCheckbox);
    
    const saveButton = screen.getByText('Save Preferences');
    fireEvent.click(saveButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('cookieConsent', JSON.stringify({
      essential: true,
      performance: true,
      functionality: false,
      marketing: false
    }));
    
    // Settings should close and banner should disappear
    expect(screen.queryByText('Cookie Preferences')).not.toBeInTheDocument();
    expect(screen.queryByText('We use cookies to enhance your experience')).not.toBeInTheDocument();
  });

  test('cancels settings when Cancel is clicked', () => {
    renderCookieDisclaimer();
    
    // Open settings
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    const cancelButton = screen.getByText('Cancel');
    fireEvent.click(cancelButton);
    
    // Settings should close but banner should remain
    expect(screen.queryByText('Cookie Preferences')).not.toBeInTheDocument();
    expect(screen.getByText('We use cookies to enhance your experience')).toBeInTheDocument();
  });

  test('closes settings when X button is clicked', () => {
    renderCookieDisclaimer();
    
    // Open settings
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    const closeButton = screen.getByTestId('x-icon').parentElement;
    fireEvent.click(closeButton!);
    
    // Settings should close but banner should remain
    expect(screen.queryByText('Cookie Preferences')).not.toBeInTheDocument();
    expect(screen.getByText('We use cookies to enhance your experience')).toBeInTheDocument();
  });

  test('renders Learn more link', () => {
    renderCookieDisclaimer();
    
    const learnMoreLink = screen.getByText('Learn more');
    expect(learnMoreLink).toBeInTheDocument();
    expect(learnMoreLink).toHaveAttribute('href', '/cookie-policy');
  });

  test('renders icons correctly', () => {
    renderCookieDisclaimer();
    
    expect(screen.getByTestId('cookie-icon')).toBeInTheDocument();
    expect(screen.getByTestId('settings-icon')).toBeInTheDocument();
  });

  test('has correct styling classes', () => {
    renderCookieDisclaimer();
    
    const banner = screen.getByText('We use cookies to enhance your experience').closest('.fixed.bottom-0');
    expect(banner).toHaveClass('bg-white', 'border-t', 'border-gray-200', 'shadow-lg');
    
    const acceptAllButton = screen.getByText('Accept All');
    expect(acceptAllButton).toHaveClass('bg-blue-600', 'text-white');
    
    const essentialOnlyButton = screen.getByText('Essential Only');
    expect(essentialOnlyButton).toHaveClass('bg-gray-100', 'text-gray-700');
  });

  test('handles multiple preference changes', () => {
    renderCookieDisclaimer();
    
    // Open settings
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    // Toggle multiple preferences
    const checkboxes = screen.getAllByRole('checkbox');
    const performanceCheckbox = checkboxes[1]; // Second checkbox
    const functionalityCheckbox = checkboxes[2]; // Third checkbox
    const marketingCheckbox = checkboxes[3]; // Fourth checkbox
    
    fireEvent.click(performanceCheckbox);
    fireEvent.click(functionalityCheckbox);
    fireEvent.click(marketingCheckbox);
    
    expect(performanceCheckbox).toBeChecked();
    expect(functionalityCheckbox).toBeChecked();
    expect(marketingCheckbox).toBeChecked();
    
    // Save preferences
    const saveButton = screen.getByText('Save Preferences');
    fireEvent.click(saveButton);
    
    expect(localStorageMock.setItem).toHaveBeenCalledWith('cookieConsent', JSON.stringify({
      essential: true,
      performance: true,
      functionality: true,
      marketing: true
    }));
  });

  test('maintains state when toggling preferences back and forth', () => {
    renderCookieDisclaimer();
    
    // Open settings
    const customizeButton = screen.getByText('Customize');
    fireEvent.click(customizeButton);
    
    const checkboxes = screen.getAllByRole('checkbox');
    const performanceCheckbox = checkboxes[1]; // Second checkbox
    
    // Toggle on
    fireEvent.click(performanceCheckbox);
    expect(performanceCheckbox).toBeChecked();
    
    // Toggle off
    fireEvent.click(performanceCheckbox);
    expect(performanceCheckbox).not.toBeChecked();
    
    // Toggle on again
    fireEvent.click(performanceCheckbox);
    expect(performanceCheckbox).toBeChecked();
  });
});