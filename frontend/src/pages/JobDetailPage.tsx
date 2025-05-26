import React from 'react';
import { useParams } from 'react-router-dom';

const JobDetailPage: React.FC = () => {
  const { id } = useParams<{ id: string }>();

  return (
    <div>
      <h1>Job Detail Page</h1>
      <p>Details for job ID: {id}</p>
      {/* TODO: Implement job details display, related jobs, apply button etc. */}
    </div>
  );
};

export default JobDetailPage; 