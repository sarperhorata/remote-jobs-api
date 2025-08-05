import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '../../../contexts/ThemeContext';
import TabNavigation from '../../../components/company/TabNavigation';
import { Briefcase, Heart, Star, Users } from 'lucide-react';

const renderWithProviders = (component: React.ReactElement) => {
  return render(
    <BrowserRouter>
      <ThemeProvider>
        {component}
      </ThemeProvider>
    </BrowserRouter>
  );
};

describe('TabNavigation', () => {
  const mockTabs = [
    {
      id: 'jobs',
      label: 'Open Positions',
      icon: <Briefcase className="w-4 h-4" />,
      count: 5
    },
    {
      id: 'culture',
      label: 'Company Culture',
      icon: <Heart className="w-4 h-4" />,
      count: undefined
    },
    {
      id: 'reviews',
      label: 'Employee Reviews',
      icon: <Star className="w-4 h-4" />,
      count: 12
    },
    {
      id: 'about',
      label: 'About',
      icon: <Users className="w-4 h-4" />,
      count: undefined
    }
  ];

  const mockOnTabChange = jest.fn();

  beforeEach(() => {
    mockOnTabChange.mockClear();
  });

  it('renders all tabs correctly', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    expect(screen.getByText('Open Positions')).toBeInTheDocument();
    expect(screen.getByText('Company Culture')).toBeInTheDocument();
    expect(screen.getByText('Employee Reviews')).toBeInTheDocument();
    expect(screen.getByText('About')).toBeInTheDocument();
  });

  it('displays tab counts when provided', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    expect(screen.getByText('5')).toBeInTheDocument();
    expect(screen.getByText('12')).toBeInTheDocument();
  });

  it('does not display count when undefined', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    // Culture and About tabs should not have count badges
    const cultureTab = screen.getByText('Company Culture').closest('button');
    const aboutTab = screen.getByText('About').closest('button');
    
    expect(cultureTab).not.toHaveTextContent('undefined');
    expect(aboutTab).not.toHaveTextContent('undefined');
  });

  it('calls onTabChange when tab is clicked', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    const cultureTab = screen.getByText('Company Culture');
    fireEvent.click(cultureTab);

    expect(mockOnTabChange).toHaveBeenCalledWith('culture');
  });

  it('applies active styles to active tab', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="reviews"
        onTabChange={mockOnTabChange}
      />
    );

    const reviewsTab = screen.getByText('Employee Reviews').closest('button');
    const jobsTab = screen.getByText('Open Positions').closest('button');

    expect(reviewsTab).toHaveClass('border-blue-500', 'text-blue-600');
    expect(jobsTab).not.toHaveClass('border-blue-500', 'text-blue-600');
  });

  it('applies hover styles to inactive tabs', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    const cultureTab = screen.getByText('Company Culture').closest('button');
    expect(cultureTab).toHaveClass('hover:text-gray-700', 'hover:border-gray-300');
  });

  it('renders with custom className', () => {
    const { container } = renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
        className="custom-class"
      />
    );

    const navElement = container.querySelector('.custom-class');
    expect(navElement).toBeInTheDocument();
  });

  it('renders without icons', () => {
    const tabsWithoutIcons = mockTabs.map(tab => ({ ...tab, icon: undefined }));
    
    renderWithProviders(
      <TabNavigation
        tabs={tabsWithoutIcons}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    expect(screen.getByText('Open Positions')).toBeInTheDocument();
    expect(screen.getByText('Company Culture')).toBeInTheDocument();
  });

  it('handles empty tabs array', () => {
    renderWithProviders(
      <TabNavigation
        tabs={[]}
        activeTab=""
        onTabChange={mockOnTabChange}
      />
    );

    expect(screen.queryByRole('button')).not.toBeInTheDocument();
  });

  it('is accessible with proper ARIA labels', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    const nav = screen.getByLabelText('Tabs');
    expect(nav).toBeInTheDocument();
  });

  it('maintains focus management', () => {
    renderWithProviders(
      <TabNavigation
        tabs={mockTabs}
        activeTab="jobs"
        onTabChange={mockOnTabChange}
      />
    );

    const jobsTab = screen.getByText('Open Positions').closest('button');
    const cultureTab = screen.getByText('Company Culture').closest('button');

    // Buttons should be focusable by default
    expect(jobsTab).toBeInTheDocument();
    expect(cultureTab).toBeInTheDocument();
    expect(jobsTab).toBeEnabled();
    expect(cultureTab).toBeEnabled();
  });
}); 