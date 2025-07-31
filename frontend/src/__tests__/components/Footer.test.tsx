import React from 'react';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Footer from '../../components/Footer';

// Mock lucide-react icons
jest.mock('lucide-react', () => ({
  Heart: () => <div data-testid="heart-icon">Heart</div>,
  Twitter: () => <div data-testid="twitter-icon">Twitter</div>,
  Linkedin: () => <div data-testid="linkedin-icon">LinkedIn</div>,
  Github: () => <div data-testid="github-icon">GitHub</div>,
  Mail: () => <div data-testid="mail-icon">Mail</div>,
}));

const renderFooter = () => {
  return render(
    <BrowserRouter>
      <Footer />
    </BrowserRouter>
  );
};

describe('Footer Component', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  it('should render footer with company information', () => {
    renderFooter();
    
    expect(screen.getByText('Buzz2Remote')).toBeInTheDocument();
    expect(screen.getByText('Find Remote Jobs 🚀')).toBeInTheDocument();
    expect(screen.getByText(/Connect with top companies/)).toBeInTheDocument();
  });

  it('should render social media links', () => {
    renderFooter();
    
    expect(screen.getByTestId('twitter-icon')).toBeInTheDocument();
    expect(screen.getByTestId('linkedin-icon')).toBeInTheDocument();
    expect(screen.getByTestId('github-icon')).toBeInTheDocument();
    expect(screen.getByTestId('mail-icon')).toBeInTheDocument();
  });

  it('should render "For Job Seekers" section with correct links', () => {
    renderFooter();
    
    expect(screen.getByText('For Job Seekers')).toBeInTheDocument();
    expect(screen.getByText('Browse Jobs')).toBeInTheDocument();
    expect(screen.getByText('Create Profile')).toBeInTheDocument();
    expect(screen.getByText('Career Tips')).toBeInTheDocument();
    expect(screen.getByText('Remote Tips')).toBeInTheDocument();
    expect(screen.getByText('Visa Sponsorship')).toBeInTheDocument();
    expect(screen.getByText('Relocation Guide')).toBeInTheDocument();
  });

  it('should render "Company" section with correct links', () => {
    renderFooter();
    
    expect(screen.getByText('Company')).toBeInTheDocument();
    expect(screen.getByText('About Us')).toBeInTheDocument();
    expect(screen.getByText('Contact')).toBeInTheDocument();
    expect(screen.getByText('Privacy Policy')).toBeInTheDocument();
    expect(screen.getByText('Terms of Service')).toBeInTheDocument();
    expect(screen.getByText('Cookie Policy')).toBeInTheDocument();
  });

  it('should render bottom section with copyright and love message', () => {
    renderFooter();
    
    const currentYear = new Date().getFullYear();
    expect(screen.getByText(`© ${currentYear} Buzz2Remote. All rights reserved.`)).toBeInTheDocument();
    expect(screen.getByText('Made with love for remote workers everywhere')).toBeInTheDocument();
    expect(screen.getByTestId('heart-icon')).toBeInTheDocument();
  });

  it('should have correct navigation links', () => {
    renderFooter();
    
    const browseJobsLink = screen.getByText('Browse Jobs').closest('a');
    const createProfileLink = screen.getByText('Create Profile').closest('a');
    const aboutUsLink = screen.getByText('About Us').closest('a');
    
    expect(browseJobsLink).toHaveAttribute('href', '/jobs');
    expect(createProfileLink).toHaveAttribute('href', '/profile');
    expect(aboutUsLink).toHaveAttribute('href', '/about');
  });

  it('should have correct external social media links', () => {
    renderFooter();
    
    const twitterLink = screen.getByTestId('twitter-icon').closest('a');
    const linkedinLink = screen.getByTestId('linkedin-icon').closest('a');
    const githubLink = screen.getByTestId('github-icon').closest('a');
    const mailLink = screen.getByTestId('mail-icon').closest('a');
    
    expect(twitterLink).toHaveAttribute('href', 'https://twitter.com/buzz2remote');
    expect(twitterLink).toHaveAttribute('target', '_blank');
    expect(twitterLink).toHaveAttribute('rel', 'noopener noreferrer');
    
    expect(linkedinLink).toHaveAttribute('href', 'https://linkedin.com/company/buzz2remote');
    expect(linkedinLink).toHaveAttribute('target', '_blank');
    expect(linkedinLink).toHaveAttribute('rel', 'noopener noreferrer');
    
    expect(githubLink).toHaveAttribute('href', 'https://github.com/buzz2remote');
    expect(githubLink).toHaveAttribute('target', '_blank');
    expect(githubLink).toHaveAttribute('rel', 'noopener noreferrer');
    
    expect(mailLink).toHaveAttribute('href', 'mailto:contact@buzz2remote.com');
  });

  it('should have proper CSS classes for styling', () => {
    renderFooter();
    
    const footer = screen.getByRole('contentinfo');
    expect(footer).toHaveClass('bg-gradient-to-r', 'from-gray-900', 'via-purple-900', 'to-gray-900', 'text-white');
  });

  it('should render company logo and branding', () => {
    renderFooter();
    
    expect(screen.getByText('🐝')).toBeInTheDocument();
    expect(screen.getByText('Buzz2Remote')).toHaveClass('text-xl', 'font-bold', 'bg-gradient-to-r', 'from-yellow-400', 'to-orange-500', 'bg-clip-text', 'text-transparent');
  });

  it('should have responsive grid layout', () => {
    renderFooter();
    
    const container = screen.getByRole('contentinfo').querySelector('.container');
    expect(container).toHaveClass('grid', 'grid-cols-1', 'md:grid-cols-4', 'gap-8');
  });

  it('should have proper hover effects on links', () => {
    renderFooter();
    
    const links = screen.getAllByRole('link');
    links.forEach(link => {
      expect(link).toHaveClass('hover:text-white', 'transition-colors');
    });
  });

  it('should have proper border styling in bottom section', () => {
    renderFooter();
    
    const bottomSection = screen.getByText('Made with love for remote workers everywhere').closest('div');
    expect(bottomSection?.parentElement).toHaveClass('border-t', 'border-gray-700');
  });

  it('should display current year in copyright', () => {
    renderFooter();
    
    const currentYear = new Date().getFullYear();
    expect(screen.getByText(new RegExp(`${currentYear} Buzz2Remote`))).toBeInTheDocument();
  });

  it('should have proper semantic HTML structure', () => {
    renderFooter();
    
    expect(screen.getByRole('contentinfo')).toBeInTheDocument();
    expect(screen.getAllByRole('link').length).toBeGreaterThan(0);
    expect(screen.getAllByRole('list')).toHaveLength(2); // Two ul elements
  });
});