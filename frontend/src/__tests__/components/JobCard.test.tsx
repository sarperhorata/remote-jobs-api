import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter, MemoryRouter } from "react-router-dom";
import "@testing-library/jest-dom";
import JobCard from "../../components/JobCard/JobCard";
import { useAuth } from '../../contexts/AuthContext';

// Mock AuthContext
jest.mock('../../contexts/AuthContext');
const mockUseAuth = useAuth as jest.MockedFunction<typeof useAuth>;

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

const mockJob = {
  _id: "1",
  id: "1", 
  title: "Frontend Developer",
  company: "Tech Company",
  companyName: "Tech Company",
  location: "Remote",
  salary_range: "$60,000 - $80,000",
  job_type: "Full-time",
  description: "Frontend developer role",
  skills: ["React", "TypeScript", "JavaScript"],
  posted_date: "2024-01-01",
  postedAt: "2024-01-01",
  status: "active",
};

describe("JobCard", () => {
  beforeEach(() => {
    mockUseAuth.mockReturnValue({
      user: null,
      isAuthenticated: false,
      login: jest.fn(),
      logout: jest.fn(),
      token: null
    });
  });

  test("renders job card with basic information", () => {
    render(
      <MockWrapper>
        <JobCard job={mockJob} />
      </MockWrapper>
    );

    expect(screen.getByText("Frontend Developer")).toBeInTheDocument();
    expect(screen.getByText("Tech Company")).toBeInTheDocument();
    expect(screen.getByText("Remote")).toBeInTheDocument();
    expect(screen.getByText("Full-time")).toBeInTheDocument();
  });

  test("displays job skills", () => {
    render(
      <MockWrapper>
        <JobCard job={mockJob} />
      </MockWrapper>
    );

    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
    expect(screen.getByText("JavaScript")).toBeInTheDocument();
  });

  test("renders view details link", () => {
    render(
      <MockWrapper>
        <JobCard job={mockJob} />
      </MockWrapper>
    );

    const viewDetailsLink = screen.getByText("View Details");
    expect(viewDetailsLink).toBeInTheDocument();
    expect(viewDetailsLink.closest('a')).toHaveAttribute('href', '/jobs/1');
  });

  test("component renders without crashing", () => {
    const { container } = render(
      <MockWrapper>
        <JobCard job={mockJob} />
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
        <JobCard job={jobWithObjectCompany} />
      </MockWrapper>
    );

    expect(screen.getByText("Object Company")).toBeInTheDocument();
  });

  it('shows hide button when onHide prop is provided', () => {
    const mockOnHide = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard job={mockJob} onHide={mockOnHide} />
      </MockWrapper>
    );

    expect(screen.getByTitle('Hide job')).toBeInTheDocument();
  });

  it('calls onHide when hide button is clicked', () => {
    const mockOnHide = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard job={mockJob} onHide={mockOnHide} />
      </MockWrapper>
    );

    fireEvent.click(screen.getByTitle('Hide job'));
    expect(mockOnHide).toHaveBeenCalledTimes(1);
  });

  it('shows reveal button when job is hidden', () => {
    const mockOnReveal = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard job={mockJob} isHidden={true} onReveal={mockOnReveal} />
      </MockWrapper>
    );

    expect(screen.getByTitle('Show job')).toBeInTheDocument();
  });

  it('calls onReveal when reveal button is clicked', () => {
    const mockOnReveal = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard job={mockJob} isHidden={true} onReveal={mockOnReveal} />
      </MockWrapper>
    );

    fireEvent.click(screen.getByTitle('Show job'));
    expect(mockOnReveal).toHaveBeenCalledTimes(1);
  });

  it('applies opacity style when job is hidden', () => {
    render(
      <MockWrapper>
        <JobCard job={mockJob} isHidden={true} />
      </MockWrapper>
    );

    // The opacity class should be on the main card container
    const cardContainer = screen.getByText('Frontend Developer').closest('div[class*="bg-white"]');
    expect(cardContainer).toHaveClass('opacity-50');
  });

  it('shows auth modal when unauthenticated user clicks favorite', () => {
    const mockOnAuthRequired = jest.fn();
    
    render(
      <MockWrapper>
        <JobCard job={mockJob} onAuthRequired={mockOnAuthRequired} />
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
        <JobCard job={mockJob} />
      </MockWrapper>
    );

    fireEvent.click(screen.getByTitle('Add to favorites'));
    // Should not call onAuthRequired since user is authenticated
    expect(screen.queryByText('You have to be signed in')).not.toBeInTheDocument();
  });
});
