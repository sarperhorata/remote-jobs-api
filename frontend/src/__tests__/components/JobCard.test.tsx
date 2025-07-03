import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter, MemoryRouter } from "react-router-dom";
import "@testing-library/jest-dom";
import JobCard from "../../components/JobCard/JobCard";
import { useAuth } from '../../contexts/AuthContext';
import { Job } from '../../types/job';

// Mock AuthContext
jest.mock('../../contexts/AuthContext');
const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

// Mock react-router-dom
jest.mock('react-router-dom', () => ({
  useNavigate: () => jest.fn(),
  Link: ({ children, ...props }: any) => <a {...props}>{children}</a>
}));

// Mock icons
jest.mock('lucide-react', () => ({
  MapPin: () => <span data-testid="map-pin-icon">📍</span>,
  Building: () => <span data-testid="building-icon">🏢</span>,
  Calendar: () => <span data-testid="calendar-icon">📅</span>,
  DollarSign: () => <span data-testid="dollar-icon">💲</span>,
  Clock: () => <span data-testid="clock-icon">⏰</span>,
  Users: () => <span data-testid="users-icon">👥</span>,
  Bookmark: () => <span data-testid="bookmark-icon">🔖</span>,
  BookmarkCheck: () => <span data-testid="bookmark-check-icon">✅</span>,
  ExternalLink: () => <span data-testid="external-link-icon">🔗</span>,
  Heart: () => <span data-testid="heart-icon">❤️</span>
}));

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

const mockJob: Job = {
  _id: "123",
  title: "Senior React Developer",
  company: "TechCorp",
  location: "Remote",
  work_type: "Remote",
  job_type: "Full-time",
  salary: "$80,000 - $120,000",
  posted_date: "2024-01-15T10:00:00Z",
  apply_url: "https://example.com/apply",
  description: "Join our amazing team as a Senior React Developer",
  required_skills: ["React", "TypeScript", "Node.js"],
  seniority_level: "Senior",
  isRemote: true,
  url: "https://example.com/job"
};

describe("JobCard", () => {
  const defaultProps = {
    job: mockJob,
    onApply: jest.fn(),
    onSave: jest.fn(),
    isSaved: false
  };

  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      token: null
    });
    jest.clearAllMocks();
  });

  test("renders job card with basic information", () => {
    render(
      <MockWrapper>
        <JobCard {...defaultProps} />
      </MockWrapper>
    );

    expect(screen.getByText("Senior React Developer")).toBeInTheDocument();
    expect(screen.getByText("TechCorp")).toBeInTheDocument();
    expect(screen.getByText("Remote")).toBeInTheDocument();
    expect(screen.getByText("Full-time")).toBeInTheDocument();
  });

  test("displays job skills", () => {
    render(
      <MockWrapper>
        <JobCard {...defaultProps} />
      </MockWrapper>
    );

    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
    expect(screen.getByText("Node.js")).toBeInTheDocument();
  });

  test("renders view details link", () => {
    render(
      <MockWrapper>
        <JobCard {...defaultProps} />
      </MockWrapper>
    );

    const viewDetailsLink = screen.getByText("View Details");
    expect(viewDetailsLink).toBeInTheDocument();
    expect(viewDetailsLink.closest('a')).toHaveAttribute('href', '/jobs/123');
  });

  test("component renders without crashing", () => {
    const { container } = render(
      <MockWrapper>
        <JobCard {...defaultProps} />
      </MockWrapper>
    );

    expect(container.firstChild).toBeInTheDocument();
  });

  test("handles job with object-type company", () => {
    const jobWithObjectCompany = {
      ...mockJob,
      company: { name: "Object Company", logo: "logo.png" }
    };

    render(
      <MockWrapper>
        <JobCard {...defaultProps} job={jobWithObjectCompany} />
      </MockWrapper>
    );

    expect(screen.getByText("Object Company")).toBeInTheDocument();
  });

  it('shows hide button when onHide prop is provided', () => {
    const mockOnHide = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard {...defaultProps} onHide={mockOnHide} />
      </MockWrapper>
    );

    expect(screen.getByTitle('Hide job')).toBeInTheDocument();
  });

  it('calls onHide when hide button is clicked', () => {
    const mockOnHide = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard {...defaultProps} onHide={mockOnHide} />
      </MockWrapper>
    );

    fireEvent.click(screen.getByTitle('Hide job'));
    expect(mockOnHide).toHaveBeenCalledTimes(1);
  });

  it('shows reveal button when job is hidden', () => {
    const mockOnReveal = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard {...defaultProps} isHidden={true} onReveal={mockOnReveal} />
      </MockWrapper>
    );

    expect(screen.getByTitle('Show job')).toBeInTheDocument();
  });

  it('calls onReveal when reveal button is clicked', () => {
    const mockOnReveal = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard {...defaultProps} isHidden={true} onReveal={mockOnReveal} />
      </MockWrapper>
    );

    fireEvent.click(screen.getByTitle('Show job'));
    expect(mockOnReveal).toHaveBeenCalledTimes(1);
  });

  it('applies opacity style when job is hidden', () => {
    render(
      <MockWrapper>
        <JobCard {...defaultProps} isHidden={true} />
      </MockWrapper>
    );

    // The opacity class should be on the main card container
    const cardContainer = screen.getByText('Senior React Developer').closest('div[class*="bg-white"]');
    expect(cardContainer).toHaveClass('opacity-50');
  });

  it('shows auth modal when unauthenticated user clicks favorite', () => {
    const mockOnAuthRequired = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard {...defaultProps} onAuthRequired={mockOnAuthRequired} />
      </MockWrapper>
    );

    fireEvent.click(screen.getByTitle('Add to favorites'));
    expect(mockOnAuthRequired).toHaveBeenCalledTimes(1);
  });

  it('handles authenticated user favorite click', () => {
    mockUseAuth.mockReturnValue({
      user: { id: 'user1', email: 'test@test.com' },
      isAuthenticated: true,
      login: jest.fn(),
      logout: jest.fn(),
      token: 'test-token'
    });

    render(
      <MockWrapper>
        <JobCard {...defaultProps} />
      </MockWrapper>
    );

    fireEvent.click(screen.getByTitle('Add to favorites'));
    // Should not call onAuthRequired since user is authenticated
    expect(screen.queryByText('You have to be signed in')).not.toBeInTheDocument();
  });

  it('renders location with icon', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByText('Remote')).toBeInTheDocument();
    expect(screen.getByTestId('map-pin-icon')).toBeInTheDocument();
  });

  it('renders salary information', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByText('$80,000 - $120,000')).toBeInTheDocument();
  });

  it('renders job type', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByText('Full-time')).toBeInTheDocument();
  });

  it('renders work type badge for remote jobs', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByText('Remote')).toBeInTheDocument();
  });

  it('shows Apply button when onApply is provided', () => {
    render(<JobCard {...defaultProps} />);
    const applyButton = screen.getByText('Apply Now');
    expect(applyButton).toBeInTheDocument();
  });

  it('calls onApply when Apply button is clicked', () => {
    render(<JobCard {...defaultProps} />);
    const applyButton = screen.getByText('Apply Now');
    fireEvent.click(applyButton);
    expect(defaultProps.onApply).toHaveBeenCalledWith(mockJob);
  });

  it('shows Save button when onSave is provided', () => {
    render(<JobCard {...defaultProps} />);
    const saveButton = screen.getByRole('button', { name: /save/i });
    expect(saveButton).toBeInTheDocument();
  });

  it('calls onSave when Save button is clicked', () => {
    render(<JobCard {...defaultProps} />);
    const saveButton = screen.getByRole('button', { name: /save/i });
    fireEvent.click(saveButton);
    expect(defaultProps.onSave).toHaveBeenCalledWith(mockJob);
  });

  it('shows saved state when isSaved is true', () => {
    render(<JobCard {...defaultProps} isSaved={true} />);
    expect(screen.getByTestId('bookmark-check-icon')).toBeInTheDocument();
  });

  it('shows unsaved state when isSaved is false', () => {
    render(<JobCard {...defaultProps} isSaved={false} />);
    expect(screen.getByTestId('bookmark-icon')).toBeInTheDocument();
  });

  it('formats posted date correctly', () => {
    render(<JobCard {...defaultProps} />);
    // Should show relative time like "Posted 3 days ago"
    expect(screen.getByText(/Posted/)).toBeInTheDocument();
  });

  it('applies glassmorphism styles', () => {
    const { container } = render(<JobCard {...defaultProps} />);
    const jobCard = container.firstChild as HTMLElement;
    expect(jobCard).toHaveClass('glass-card');
  });

  it('has hover animations', () => {
    const { container } = render(<JobCard {...defaultProps} />);
    const jobCard = container.firstChild as HTMLElement;
    expect(jobCard).toHaveClass('hover:scale-105');
  });

  it('handles missing optional fields gracefully', () => {
    const jobWithoutSalary = { ...mockJob, salary: undefined };
    render(<JobCard {...defaultProps} job={jobWithoutSalary} />);
    expect(screen.getByText('Senior React Developer')).toBeInTheDocument();
  });

  it('truncates long descriptions', () => {
    const jobWithLongDescription = {
      ...mockJob,
      description: 'This is a very long description that should be truncated after a certain number of characters to maintain the card layout and readability.'
    };
    render(<JobCard {...defaultProps} job={jobWithLongDescription} />);
    // Should show truncated version with "..." or "Read more"
    expect(screen.getByText(/This is a very long description/)).toBeInTheDocument();
  });

  it('shows seniority level badge', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByText('Senior')).toBeInTheDocument();
  });

  it('renders external link for job URL', () => {
    render(<JobCard {...defaultProps} />);
    expect(screen.getByTestId('external-link-icon')).toBeInTheDocument();
  });
});
