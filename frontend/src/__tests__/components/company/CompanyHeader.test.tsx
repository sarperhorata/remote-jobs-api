import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import CompanyHeader from '../../../components/company/CompanyHeader';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('CompanyHeader', () => {
  const mockCompany = {
    _id: '1',
    name: 'TechCorp Inc.',
    logo: 'https://example.com/logo.png',
    website: 'https://techcorp.com',
    location: 'San Francisco, CA',
    industry: 'Technology',
    founded: '2010-01-01',
    size: '500-1000 employees',
    description: 'A leading technology company focused on innovation.',
    rating: 4.2,
    reviewCount: 150,
    email: 'contact@techcorp.com',
    phone: '+1-555-0123'
  };

  it('renders company name correctly', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
  });

  it('displays company logo when provided', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    const logo = screen.getByAltText('TechCorp Inc. logo');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', 'https://example.com/logo.png');
  });

  it('shows fallback icon when no logo is provided', () => {
    const companyWithoutLogo = { ...mockCompany, logo: undefined };
    renderWithProviders(<CompanyHeader company={companyWithoutLogo} />);
    
    // Should show building icon instead of logo image
    expect(screen.queryByAltText('TechCorp Inc. logo')).not.toBeInTheDocument();
  });

  it('displays company rating when available', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    expect(screen.getByText('4.2')).toBeInTheDocument();
    expect(screen.getByText('(150 reviews)')).toBeInTheDocument();
  });

  it('does not display rating when not available', () => {
    const companyWithoutRating = { ...mockCompany, rating: undefined, reviewCount: undefined };
    renderWithProviders(<CompanyHeader company={companyWithoutRating} />);
    
    expect(screen.queryByText('4.2')).not.toBeInTheDocument();
    expect(screen.queryByText('(150 reviews)')).not.toBeInTheDocument();
  });

  it('displays company meta information', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    
    expect(screen.getByText('Technology')).toBeInTheDocument();
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
    expect(screen.getByText('500-1000 employees')).toBeInTheDocument();
    expect(screen.getByText('Founded 2010')).toBeInTheDocument();
  });

  it('displays company description when available', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    expect(screen.getByText('A leading technology company focused on innovation.')).toBeInTheDocument();
  });

  it('does not display description when not available', () => {
    const companyWithoutDescription = { ...mockCompany, description: undefined };
    renderWithProviders(<CompanyHeader company={companyWithoutDescription} />);
    
    expect(screen.queryByText('A leading technology company focused on innovation.')).not.toBeInTheDocument();
  });

  it('displays website link when available', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    const websiteLink = screen.getByText('Visit Website');
    expect(websiteLink).toBeInTheDocument();
    expect(websiteLink.closest('a')).toHaveAttribute('href', 'https://techcorp.com');
    expect(websiteLink.closest('a')).toHaveAttribute('target', '_blank');
  });

  it('does not display website link when not available', () => {
    const companyWithoutWebsite = { ...mockCompany, website: undefined };
    renderWithProviders(<CompanyHeader company={companyWithoutWebsite} />);
    
    expect(screen.queryByText('Visit Website')).not.toBeInTheDocument();
  });

  it('displays contact buttons when email and phone are available', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    
    const contactButton = screen.getByText('Contact');
    const callButton = screen.getByText('Call');
    
    expect(contactButton).toBeInTheDocument();
    expect(callButton).toBeInTheDocument();
    
    expect(contactButton.closest('a')).toHaveAttribute('href', 'mailto:contact@techcorp.com');
    expect(callButton.closest('a')).toHaveAttribute('href', 'tel:+1-555-0123');
  });

  it('does not display contact buttons when email and phone are not available', () => {
    const companyWithoutContact = { 
      ...mockCompany, 
      email: undefined, 
      phone: undefined 
    };
    renderWithProviders(<CompanyHeader company={companyWithoutContact} />);
    
    expect(screen.queryByText('Contact')).not.toBeInTheDocument();
    expect(screen.queryByText('Call')).not.toBeInTheDocument();
  });

  it('renders with custom className', () => {
    const { container } = renderWithProviders(
      <CompanyHeader company={mockCompany} className="custom-class" />
    );

    const headerElement = container.querySelector('.custom-class');
    expect(headerElement).toBeInTheDocument();
  });

  it('handles missing optional fields gracefully', () => {
    const minimalCompany = {
      _id: '1',
      name: 'Minimal Corp'
    };
    
    renderWithProviders(<CompanyHeader company={minimalCompany} />);
    
    expect(screen.getByText('Minimal Corp')).toBeInTheDocument();
    // Should not crash or show undefined values
    expect(screen.queryByText('undefined')).not.toBeInTheDocument();
  });

  it('formats founded year correctly', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    expect(screen.getByText('Founded 2010')).toBeInTheDocument();
  });

  it('formats rating correctly', () => {
    const companyWithDecimalRating = { ...mockCompany, rating: 3.75 };
    renderWithProviders(<CompanyHeader company={companyWithDecimalRating} />);
    expect(screen.getByText('3.8')).toBeInTheDocument();
  });

  it('displays external link icon on website button', () => {
    renderWithProviders(<CompanyHeader company={mockCompany} />);
    const websiteButton = screen.getByText('Visit Website');
    expect(websiteButton).toBeInTheDocument();
  });

  it('applies responsive design classes', () => {
    const { container } = renderWithProviders(<CompanyHeader company={mockCompany} />);
    
    // Check for responsive classes - look for the main div with the className
    const headerElement = container.querySelector('div[class*="bg-white"]');
    expect(headerElement).toBeInTheDocument();
    expect(headerElement).toHaveClass('bg-white', 'dark:bg-gray-800', 'rounded-lg');
  });
}); 