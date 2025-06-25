import React from "react";
import { render, screen, fireEvent, waitFor } from "@testing-library/react";
import { BrowserRouter } from "react-router-dom";
import "@testing-library/jest-dom";
import JobCard from "../../components/JobCard";

const MockWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <BrowserRouter>{children}</BrowserRouter>
);

const mockJob = {
  _id: "1",
  id: "1", 
  title: "Frontend Developer",
  company: { id: "1", name: "Tech Company", logo: "" },
  location: "Remote",
  salary: { min: 60000, max: 80000, currency: "USD" },
  job_type: "Full-time",
  description: "Frontend developer role",
  requirements: ["React", "TypeScript"],
  skills: ["React", "TypeScript"],
  posted_date: "2024-01-01",
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
  });

  test("displays job requirements", () => {
    render(
      <MockWrapper>
        <JobCard job={mockJob} />
      </MockWrapper>
    );

    expect(screen.getByText("React")).toBeInTheDocument();
    expect(screen.getByText("TypeScript")).toBeInTheDocument();
  });

  test("component renders without crashing", () => {
    const { container } = render(
      <MockWrapper>
        <JobCard job={mockJob} />
      </MockWrapper>
    );

    expect(container.firstChild).toBeInTheDocument();
  });
});
