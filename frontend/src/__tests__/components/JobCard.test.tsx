import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import "@testing-library/jest-dom";
import JobCard from "../../components/JobCard/JobCard";

// Mock AuthContext
jest.mock('../../contexts/AuthContext', () => ({
  useAuth: () => ({
    user: null
  })
}));

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
});
