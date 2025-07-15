import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";
import JobCard from "../../components/JobCard/JobCard";
import { Job } from '../../types/job';

// Mock window.open
const mockWindowOpen = jest.fn();
window.open = mockWindowOpen;

// Mock child components/hooks to isolate JobCard
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: false }),
}));

jest.mock('lucide-react', () => ({
  MapPin: () => <span data-testid="map-pin-icon">📍</span>,
  Clock: () => <span data-testid="clock-icon">⏰</span>,
  ExternalLink: () => <span data-testid="external-link-icon">🔗</span>,
  Bookmark: () => <span data-testid="bookmark-icon">🔖</span>,
  BookmarkCheck: () => <span data-testid="bookmark-check-icon">✅</span>,
}));

// Test Wrapper
const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

// Mock Data
const mockJob: Job = {
  _id: "123",
  title: "Senior React Developer",
  company: "TechCorp",
  location: "Remote",
  work_type: "Remote",
  job_type: "Full-time",
  salary: {
    min: 80000,
    max: 120000,
    currency: "USD"
  },
  posted_date: "2024-01-15T10:00:00Z",
  description: "Join our amazing team as a Senior React Developer",
  skills: ["React", "TypeScript", "Node.js"],
  apply_url: "https://example.com/apply",
};

describe("JobCard Component", () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  test("renders all basic job information correctly", () => {
    render(<MockWrapper><JobCard job={mockJob} /></MockWrapper>);
    
    expect(screen.getByText("Senior React Developer")).toBeInTheDocument();
    expect(screen.getByText("TechCorp")).toBeInTheDocument();
    expect(screen.getByText("$80,000 - $120,000")).toBeInTheDocument();
    expect(screen.getByText("Full-time")).toBeInTheDocument();
    // 'Remote' can appear multiple times, so we check for its presence
    expect(screen.getAllByText("Remote").length).toBeGreaterThan(0);
  });

  test("displays job skills tags", () => {
    render(<MockWrapper><JobCard job={mockJob} /></MockWrapper>);
    
    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
    expect(screen.getByText("Node.js")).toBeInTheDocument();
  });

  test("renders formatted posted date", () => {
    render(<MockWrapper><JobCard job={mockJob} /></MockWrapper>);
    
    expect(screen.getByTestId("clock-icon")).toBeInTheDocument();
    expect(screen.getByText(/months ago/i)).toBeInTheDocument(); 
  });

  test("clicking the card opens the apply_url in a new tab", () => {
    render(<MockWrapper><JobCard job={mockJob} /></MockWrapper>);
    
    const card = screen.getByText("Senior React Developer").closest('div.group');
    expect(card).toBeInTheDocument();

    if (card) {
      fireEvent.click(card);
    }
    
    expect(mockWindowOpen).toHaveBeenCalledTimes(1);
    expect(mockWindowOpen).toHaveBeenCalledWith(mockJob.apply_url, '_blank', 'noopener,noreferrer');
  });

  test("falls back to a google search URL if no apply_url is provided", () => {
    const jobWithoutUrl = { ...mockJob, apply_url: undefined };
    render(<MockWrapper><JobCard job={jobWithoutUrl} /></MockWrapper>);
    
    const card = screen.getByText("Senior React Developer").closest('div.group');
    if (card) {
      fireEvent.click(card);
    }
    
    const expectedSearchUrl = 'https://www.google.com/search?q="Senior%20React%20Developer"+at+"TechCorp"';
    expect(mockWindowOpen).toHaveBeenCalledTimes(1);
    expect(mockWindowOpen).toHaveBeenCalledWith(expectedSearchUrl, '_blank', 'noopener,noreferrer');
  });

  test("renders company name from object correctly", () => {
    const jobWithObjectCompany = {
      ...mockJob,
      company: { id: "company-1", name: "Object Corp", logo: "logo.png" }
    };
    render(<MockWrapper><JobCard job={jobWithObjectCompany} /></MockWrapper>);
    expect(screen.getByText("Object Corp")).toBeInTheDocument();
  });
});
