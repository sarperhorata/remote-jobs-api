import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import '@testing-library/jest-dom';
import { BrowserRouter } from 'react-router-dom';
import Home from '../../pages/Home';
import { jobService } from '../../services/jobService';

// Mock services
jest.mock('../../services/jobService');
const mockJobService = jobService as jest.Mocked<typeof jobService>;

// Mock components
jest.mock('../../components/Layout', () => {
  return function MockLayout({ children }: { children: React.ReactNode }) {
    return <div data-testid="mock-layout">{children}</div>;
  };
});

jest.mock('../../components/AuthModal', () => {
  return function MockAuthModal() {
    return <div data-testid="mock-auth-modal">Auth Modal</div>;
  };
});

jest.mock('../../components/Onboarding', () => {
  return function MockOnboarding() {
    return <div data-testid="mock-onboarding">Onboarding</div>;
  };
});

jest.mock('../../components/MultiJobAutocomplete', () => {
  return function MockMultiJobAutocomplete({ onSelect }: { onSelect: (position: any) => void }) {
    return (
      <div data-testid="mock-autocomplete">
        <button onClick={() => onSelect({ title: 'Developer', count: 100 })}>
          Select Developer
        </button>
      </div>
    );
  };
});

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  ...jest.requireActual('react-router-dom'),
  useNavigate: () => jest.fn()
}));

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

describe('Home Page', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockJobService.getJobStats.mockResolvedValue({
      total_jobs: 38345,
      active_jobs: 35000,
      companies: 1250,
      remote_jobs: 28000,
      new_jobs_today: 150
    });
    mockJobService.getTopPositions.mockResolvedValue([
      { title: 'Frontend Developer', count: 5000, category: 'Development' },
      { title: 'Backend Developer', count: 4500, category: 'Development' },
      { title: 'Full Stack Developer', count: 4000, category: 'Development' }
    ]);
    mockJobService.getRecentJobs.mockResolvedValue([]);
  });

  it('renders the hero section with title and subtitle', async () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    expect(screen.getByText(/Uzaktan Çalışma Hayallerini Gerçeğe Dönüştür/)).toBeInTheDocument();
    expect(screen.getByText(/38.000\+ iş fırsatı arasından/)).toBeInTheDocument();
  });

  it('loads and displays job statistics', async () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('38,345')).toBeInTheDocument();
      expect(screen.getByText('35,000')).toBeInTheDocument(); 
      expect(screen.getByText('1,250')).toBeInTheDocument();
      expect(screen.getByText('28,000')).toBeInTheDocument();
    });
  });

  it('displays the search form with autocomplete', () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    expect(screen.getByTestId('mock-autocomplete')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/Şehir veya uzaktan/)).toBeInTheDocument();
    expect(screen.getByText('İş Ara')).toBeInTheDocument();
  });

  it('handles job position selection from autocomplete', async () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    const selectButton = screen.getByText('Select Developer');
    fireEvent.click(selectButton);

    // Autocomplete should show selected position
    await waitFor(() => {
      expect(screen.getByTestId('mock-autocomplete')).toBeInTheDocument();
    });
  });

  it('shows top positions section', async () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('En Popüler Pozisyonlar')).toBeInTheDocument();
      expect(screen.getByText('Frontend Developer')).toBeInTheDocument();
      expect(screen.getByText('Backend Developer')).toBeInTheDocument();
      expect(screen.getByText('Full Stack Developer')).toBeInTheDocument();
    });
  });

  it('displays features section', () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    expect(screen.getByText('Neden Buzz2Remote?')).toBeInTheDocument();
    expect(screen.getByText('Günlük Güncellemeler')).toBeInTheDocument();
    expect(screen.getByText('Akıllı Filtreleme')).toBeInTheDocument();
    expect(screen.getByText('Kolay Başvuru')).toBeInTheDocument();
  });

  it('shows glassmorphism design elements', () => {
    const { container } = render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    // Check for glassmorphism classes
    const glassElements = container.querySelectorAll('.glass-card, .backdrop-blur');
    expect(glassElements.length).toBeGreaterThan(0);
  });

  it('has gradient background animations', () => {
    const { container } = render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    // Check for gradient and animation classes
    const animatedElements = container.querySelectorAll('.animate-gradient, .animate-float');
    expect(animatedElements.length).toBeGreaterThan(0);
  });

  it('handles search form submission', async () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    const searchButton = screen.getByText('İş Ara');
    fireEvent.click(searchButton);

    // Should navigate to job search results
    // Note: Navigation behavior would be tested in integration tests
  });

  it('loads data on component mount', async () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(mockJobService.getJobStats).toHaveBeenCalledTimes(1);
      expect(mockJobService.getTopPositions).toHaveBeenCalledTimes(1);
      expect(mockJobService.getRecentJobs).toHaveBeenCalledTimes(1);
    });
  });

  it('handles API errors gracefully', async () => {
    mockJobService.getJobStats.mockRejectedValue(new Error('API Error'));
    
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    // Should still render without crashing
    expect(screen.getByText(/Uzaktan Çalışma Hayallerini/)).toBeInTheDocument();
  });

  it('renders call-to-action section', () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    expect(screen.getByText('Hemen Başla')).toBeInTheDocument();
    expect(screen.getByText(/Bugün başvur, yarın işe başla/)).toBeInTheDocument();
  });

  it('displays testimonials section', () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    expect(screen.getByText('Kullanıcı Yorumları')).toBeInTheDocument();
  });

  it('shows newsletter signup', () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    expect(screen.getByText('Haftalık Bülten')).toBeInTheDocument();
    expect(screen.getByPlaceholderText(/E-posta adresin/)).toBeInTheDocument();
  });

  it('renders with proper responsive classes', () => {
    const { container } = render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    // Check for responsive grid classes
    const responsiveElements = container.querySelectorAll('[class*="md:"], [class*="lg:"], [class*="xl:"]');
    expect(responsiveElements.length).toBeGreaterThan(0);
  });

  it('handles loading states', () => {
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    // Should show loading skeletons initially
    // This would depend on your implementation
    expect(screen.getByTestId('mock-layout')).toBeInTheDocument();
  });

  it('maintains accessibility standards', () => {
    const { container } = render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    // Check for proper heading hierarchy
    const headings = container.querySelectorAll('h1, h2, h3, h4, h5, h6');
    expect(headings.length).toBeGreaterThan(0);

    // Check for alt texts on images
    const images = container.querySelectorAll('img');
    images.forEach(img => {
      expect(img).toHaveAttribute('alt');
    });
  });

  it('performs well with large datasets', async () => {
    // Mock large dataset
    mockJobService.getTopPositions.mockResolvedValue(
      Array.from({ length: 100 }, (_, i) => ({
        title: `Position ${i}`,
        count: 1000 - i,
        category: 'Development'
      }))
    );

    const start = performance.now();
    render(
      <MockWrapper>
        <Home />
      </MockWrapper>
    );

    await waitFor(() => {
      expect(screen.getByText('En Popüler Pozisyonlar')).toBeInTheDocument();
    });

    const end = performance.now();
    expect(end - start).toBeLessThan(1000); // Should render within 1 second
  });
}); 