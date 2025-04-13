import React, { useState, useEffect } from 'react';
import { 
  Box, Container, Typography, Table, TableBody, TableCell, 
  TableContainer, TableHead, TableRow, Paper, Button, IconButton,
  Chip, Checkbox, Tooltip, TextField, InputAdornment
} from '@mui/material';
import { 
  Refresh as RefreshIcon, 
  Edit as EditIcon, 
  Delete as DeleteIcon,
  Search as SearchIcon,
  Add as AddIcon,
  FilterList as FilterIcon 
} from '@mui/icons-material';
import { format } from 'date-fns';
import { Link } from 'react-router-dom';
import axios from 'axios';

const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedJobs, setSelectedJobs] = useState([]);
  const [searchTerm, setSearchTerm] = useState('');
  const [filters, setFilters] = useState({
    remote: false,
    newOnly: false
  });

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs`);
      setJobs(response.data);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchJobs();
  }, []);

  const handleSelectAll = (event) => {
    if (event.target.checked) {
      setSelectedJobs(jobs.map(job => job._id));
    } else {
      setSelectedJobs([]);
    }
  };

  const handleSelectJob = (event, jobId) => {
    if (event.target.checked) {
      setSelectedJobs([...selectedJobs, jobId]);
    } else {
      setSelectedJobs(selectedJobs.filter(id => id !== jobId));
    }
  };

  const handleDeleteSelected = async () => {
    if (window.confirm(`Delete ${selectedJobs.length} selected jobs?`)) {
      try {
        await Promise.all(selectedJobs.map(jobId => 
          axios.delete(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${jobId}`)
        ));
        fetchJobs();
        setSelectedJobs([]);
      } catch (error) {
        console.error('Error deleting jobs:', error);
      }
    }
  };

  const handleSearchChange = (event) => {
    setSearchTerm(event.target.value);
  };

  const toggleFilter = (filterName) => {
    setFilters({
      ...filters,
      [filterName]: !filters[filterName]
    });
  };

  const filteredJobs = jobs.filter(job => {
    // Search filter
    const matchesSearch = 
      job.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
      job.company.toLowerCase().includes(searchTerm.toLowerCase()) ||
      (job.location && job.location.toLowerCase().includes(searchTerm.toLowerCase()));
    
    // Remote filter
    const matchesRemote = !filters.remote || job.is_remote;
    
    // New only filter (jobs less than 7 days old)
    const matchesNew = !filters.newOnly || 
      (new Date(job.created_at) > new Date(Date.now() - 7 * 24 * 60 * 60 * 1000));
    
    return matchesSearch && matchesRemote && matchesNew;
  });

  return (
    <Container maxWidth="xl">
      <Box sx={{ my: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 3 }}>
          <Typography variant="h4" component="h1" gutterBottom>
            Job Listings
          </Typography>
          <Box>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<AddIcon />}
              component={Link}
              to="/admin/jobs/new"
              sx={{ mr: 1 }}
            >
              Add Job
            </Button>
            <Button 
              variant="outlined" 
              color="primary"
              startIcon={<RefreshIcon />}
              onClick={fetchJobs}
            >
              Refresh
            </Button>
          </Box>
        </Box>

        <Box sx={{ display: 'flex', mb: 2 }}>
          <TextField
            label="Search Jobs"
            variant="outlined"
            size="small"
            value={searchTerm}
            onChange={handleSearchChange}
            sx={{ flexGrow: 1, mr: 2 }}
            InputProps={{
              startAdornment: (
                <InputAdornment position="start">
                  <SearchIcon />
                </InputAdornment>
              ),
            }}
          />
          <Tooltip title="Remote jobs only">
            <Chip 
              icon={<FilterIcon />} 
              label="Remote" 
              clickable
              color={filters.remote ? "primary" : "default"}
              onClick={() => toggleFilter('remote')}
              sx={{ mr: 1 }}
            />
          </Tooltip>
          <Tooltip title="Only show jobs posted in the last 7 days">
            <Chip 
              icon={<FilterIcon />} 
              label="New Only" 
              clickable
              color={filters.newOnly ? "primary" : "default"}
              onClick={() => toggleFilter('newOnly')}
            />
          </Tooltip>
        </Box>

        {selectedJobs.length > 0 && (
          <Box sx={{ mb: 2 }}>
            <Button 
              variant="contained" 
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteSelected}
            >
              Delete Selected ({selectedJobs.length})
            </Button>
          </Box>
        )}

        <TableContainer component={Paper}>
          <Table sx={{ minWidth: 650 }}>
            <TableHead>
              <TableRow>
                <TableCell padding="checkbox">
                  <Checkbox
                    indeterminate={selectedJobs.length > 0 && selectedJobs.length < jobs.length}
                    checked={jobs.length > 0 && selectedJobs.length === jobs.length}
                    onChange={handleSelectAll}
                  />
                </TableCell>
                <TableCell><strong>Title</strong></TableCell>
                <TableCell><strong>Company</strong></TableCell>
                <TableCell><strong>Location</strong></TableCell>
                <TableCell><strong>Posted</strong></TableCell>
                <TableCell><strong>Source</strong></TableCell>
                <TableCell><strong>Status</strong></TableCell>
                <TableCell><strong>Actions</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {loading ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">Loading...</TableCell>
                </TableRow>
              ) : filteredJobs.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} align="center">No jobs found</TableCell>
                </TableRow>
              ) : (
                filteredJobs.map((job) => (
                  <TableRow key={job._id} hover>
                    <TableCell padding="checkbox">
                      <Checkbox
                        checked={selectedJobs.includes(job._id)}
                        onChange={(event) => handleSelectJob(event, job._id)}
                      />
                    </TableCell>
                    <TableCell component="th" scope="row">
                      <Link to={`/admin/jobs/${job._id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
                        {job.title}
                      </Link>
                    </TableCell>
                    <TableCell>{job.company}</TableCell>
                    <TableCell>
                      {job.location || 'N/A'}
                      {job.is_remote && (
                        <Chip 
                          label="Remote" 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </TableCell>
                    <TableCell>
                      {job.date_posted ? 
                        format(new Date(job.date_posted), 'MMM d, yyyy') : 
                        format(new Date(job.created_at), 'MMM d, yyyy')}
                    </TableCell>
                    <TableCell>
                      <Chip 
                        label={job.source || 'manual'} 
                        size="small" 
                        color="secondary" 
                        variant="outlined"
                      />
                    </TableCell>
                    <TableCell>
                      {job.is_active ? (
                        <Chip label="Active" size="small" color="success" />
                      ) : (
                        <Chip label="Inactive" size="small" color="default" />
                      )}
                      {job.is_archived && (
                        <Chip label="Archived" size="small" color="error" sx={{ ml: 1 }} />
                      )}
                    </TableCell>
                    <TableCell>
                      <Tooltip title="Edit">
                        <IconButton 
                          component={Link} 
                          to={`/admin/jobs/${job._id}/edit`}
                          size="small"
                        >
                          <EditIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Delete">
                        <IconButton 
                          size="small"
                          color="error"
                          onClick={() => {
                            if (window.confirm(`Delete job: ${job.title}?`)) {
                              axios.delete(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${job._id}`)
                                .then(() => fetchJobs())
                                .catch(err => console.error('Error deleting job:', err));
                            }
                          }}
                        >
                          <DeleteIcon fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        </TableContainer>
      </Box>
    </Container>
  );
};

export default JobList; 