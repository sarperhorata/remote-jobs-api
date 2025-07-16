import React from "react";
import { render, screen, fireEvent } from "@testing-library/react";
import "@testing-library/jest-dom";
import { BrowserRouter } from "react-router-dom";
import JobCard from "../../components/JobCard";
import { Job } from '../../types/job';

// Mock window.open
const mockWindowOpen = jest.fn();
window.open = mockWindowOpen;

// Mock child components/hooks to isolate JobCard
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({ isAuthenticated: false }),
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
    expect(screen.getByText("Remote")).toBeInTheDocument();
  });

  test("renders company name from object correctly", () => {
    const jobWithObjectCompany = {
      ...mockJob,
      company: { id: "company-1", name: "Object Corp", logo: "logo.png" }
    };
    render(<MockWrapper><JobCard job={jobWithObjectCompany} /></MockWrapper>);
    expect(screen.getByText("Object Corp")).toBeInTheDocument();
  });

  test("renders description correctly", () => {
    render(<MockWrapper><JobCard job={mockJob} /></MockWrapper>);
    expect(screen.getByText("Join our amazing team as a Senior React Developer")).toBeInTheDocument();
  });

  test("renders View Details button", () => {
    render(<MockWrapper><JobCard job={mockJob} /></MockWrapper>);
    expect(screen.getByText("View Details")).toBeInTheDocument();
  });

  test("renders posted date correctly", () => {
    render(<MockWrapper><JobCard job={mockJob} /></MockWrapper>);
    expect(screen.getByText(/Posted/)).toBeInTheDocument();
  });
});
