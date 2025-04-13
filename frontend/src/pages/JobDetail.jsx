import React from 'react';
import { useParams } from 'react-router-dom';
import { Container, Box } from '@mui/material';
import JobDetail from '../components/jobs/JobDetail';
import Navbar from '../components/layout/Navbar';
import Footer from '../components/layout/Footer';

const JobDetailPage = () => {
  const { jobId } = useParams();

  return (
    <>
      <Navbar />
      <Box component="main" sx={{ py: 4 }}>
        <Container>
          <JobDetail jobId={jobId} />
        </Container>
      </Box>
      <Footer />
    </>
  );
};

export default JobDetailPage; 