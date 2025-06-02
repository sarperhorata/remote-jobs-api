import { render, screen } from '@testing-library/react';
import { CompanyCard } from '../../components/CompanyCard';
import { Company } from '../../types/Company';
import '@testing-library/jest-dom';

const mockCompany: Company = {
  id: '1',
  name: 'TechCorp Inc.',
  logo: 'https://example.com/logo.png',
  website: 'https://techcorp.com',
  description: 'Leading technology company specializing in remote work solutions.',
  industry: 'Technology',
  size: '100-500',
  location: 'San Francisco, CA',
  founded: 2015,
  techStack: ['React', 'TypeScript', 'Node.js', 'Python', 'Docker', 'AWS'],
  remotePolicy: 'Remote-first'
};

const mockCompanyMinimal: Company = {
  id: '2',
  name: 'StartupCo',
  industry: 'Software',
  size: '10-50',
  location: 'Remote'
};

describe('CompanyCard', () => {
  it('renders company information correctly', () => {
    render(<CompanyCard company={mockCompany} />);
    
    expect(screen.getByText('TechCorp Inc.')).toBeInTheDocument();
    expect(screen.getByText('Technology')).toBeInTheDocument();
    expect(screen.getByText('Leading technology company specializing in remote work solutions.')).toBeInTheDocument();
    expect(screen.getByText('100-500 employees')).toBeInTheDocument();
    expect(screen.getByText('San Francisco, CA')).toBeInTheDocument();
  });

  it('displays company logo when provided', () => {
    render(<CompanyCard company={mockCompany} />);
    
    const logo = screen.getByAltText('TechCorp Inc. logo');
    expect(logo).toBeInTheDocument();
    expect(logo).toHaveAttribute('src', 'https://example.com/logo.png');
  });

  it('shows company initial when logo is not provided', () => {
    render(<CompanyCard company={mockCompanyMinimal} />);
    
    expect(screen.getByText('S')).toBeInTheDocument(); // First letter of StartupCo
    expect(screen.queryByRole('img')).not.toBeInTheDocument();
  });

  it('renders website link when provided', () => {
    render(<CompanyCard company={mockCompany} />);
    
    const websiteLink = screen.getByText('Website');
    expect(websiteLink).toBeInTheDocument();
    expect(websiteLink.closest('a')).toHaveAttribute('href', 'https://techcorp.com');
    expect(websiteLink.closest('a')).toHaveAttribute('target', '_blank');
  });

  it('does not render website link when not provided', () => {
    render(<CompanyCard company={mockCompanyMinimal} />);
    
    expect(screen.queryByText('Website')).not.toBeInTheDocument();
  });

  it('displays tech stack when provided', () => {
    render(<CompanyCard company={mockCompany} />);
    
    expect(screen.getByText('React')).toBeInTheDocument();
    expect(screen.getByText('TypeScript')).toBeInTheDocument();
    expect(screen.getByText('Node.js')).toBeInTheDocument();
    expect(screen.getByText('Python')).toBeInTheDocument();
    expect(screen.getByText('Docker')).toBeInTheDocument();
  });

  it('shows "+X more" when tech stack has more than 5 items', () => {
    render(<CompanyCard company={mockCompany} />);
    
    expect(screen.getByText('+1 more')).toBeInTheDocument();
  });

  it('does not render tech stack section when not provided', () => {
    render(<CompanyCard company={mockCompanyMinimal} />);
    
    expect(screen.queryByText('React')).not.toBeInTheDocument();
  });

  it('handles missing description gracefully', () => {
    render(<CompanyCard company={mockCompanyMinimal} />);
    
    expect(screen.getByText('StartupCo')).toBeInTheDocument();
    expect(screen.getByText('Software')).toBeInTheDocument();
  });

  it('applies hover effect classes', () => {
    const { container } = render(<CompanyCard company={mockCompany} />);
    
    const card = container.firstChild as HTMLElement;
    expect(card).toHaveClass('hover:shadow-lg', 'transition-shadow');
  });

  it('renders without crashing', () => {
    expect(() => render(<CompanyCard company={mockCompany} />)).not.toThrow();
  });
}); 