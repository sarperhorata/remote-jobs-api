import React from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';

interface Job {
  id: string;
  company: string;
  job_title: string;
  link: string;
  description?: string;
  location?: string;
  salary_range?: string;
  requirements?: string[];
}

const JobDetail: React.FC = () => {
  const { id } = useParams<{ id: string }>();
  
  const fetchJobDetails = async () => {
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    const response = await axios.get(`${API_URL}/jobs/${id}`);
    return response.data;
  };
  
  const { data: job, isLoading, error } = useQuery<Job>(
    ['job', id], 
    fetchJobDetails
  );
  
  if (isLoading) return <div>Loading job details...</div>;
  
  if (error) return <div>Error loading job details. Please try again later.</div>;
  
  if (!job) return <div>Job not found.</div>;
  
  return (
    <div className="job-detail-page">
      <Link to="/jobs" className="back-button">← Back to Jobs</Link>
      
      <div className="job-header">
        <h1>{job.job_title}</h1>
        <p className="company-name">{job.company}</p>
        {job.location && <p className="job-location">{job.location}</p>}
        {job.salary_range && <p className="job-salary">{job.salary_range}</p>}
      </div>
      
      <div className="job-content">
        {job.description && (
          <section className="job-description">
            <h2>Description</h2>
            <p>{job.description}</p>
          </section>
        )}
        
        {job.requirements && job.requirements.length > 0 && (
          <section className="job-requirements">
            <h2>Requirements</h2>
            <ul>
              {job.requirements.map((req, index) => (
                <li key={index}>{req}</li>
              ))}
            </ul>
          </section>
        )}
      </div>
      
      <div className="job-actions">
        <a 
          href={job.link} 
          target="_blank" 
          rel="noopener noreferrer" 
          className="apply-button"
        >
          Apply for this Position
        </a>
      </div>
    </div>
  );
};

export default JobDetail; 