import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useQuery } from 'react-query';
import axios from 'axios';

interface Job {
  id: string;
  company: string;
  job_title: string;
  link: string;
}

const Jobs: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  
  const fetchJobs = async () => {
    const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';
    const response = await axios.get(`${API_URL}/jobs`);
    return response.data;
  };
  
  const { data: jobs, isLoading, error } = useQuery<Job[]>('jobs', fetchJobs);
  
  const filteredJobs = jobs?.filter(job => 
    job.job_title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    job.company.toLowerCase().includes(searchTerm.toLowerCase())
  );
  
  if (isLoading) return <div>Loading jobs...</div>;
  
  if (error) return <div>Error loading jobs. Please try again later.</div>;
  
  return (
    <div className="jobs-page">
      <h1>Remote Jobs</h1>
      
      <div className="search-bar">
        <input
          type="text"
          placeholder="Search by title or company..."
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>
      
      <div className="job-list">
        {filteredJobs && filteredJobs.length > 0 ? (
          filteredJobs.map((job) => (
            <div key={job.id} className="job-card">
              <h2 className="job-title">{job.job_title}</h2>
              <p className="job-company">{job.company}</p>
              <div className="job-actions">
                <Link to={`/jobs/${job.id}`}>View Details</Link>
                <a href={job.link} target="_blank" rel="noopener noreferrer">Apply</a>
              </div>
            </div>
          ))
        ) : (
          <p>No jobs found matching your search criteria.</p>
        )}
      </div>
    </div>
  );
};

export default Jobs; 