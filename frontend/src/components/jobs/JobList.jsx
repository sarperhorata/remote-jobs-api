import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { 
  Box, Container, Typography, Grid, Card, CardContent, 
  CardActions, Chip, Button, TextField, InputAdornment,
  CircularProgress, Pagination, Select, MenuItem, FormControl,
  InputLabel, Divider, Paper, IconButton, Tooltip, Alert,
  useMediaQuery,
  useTheme
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  WorkOutline as WorkIcon,
  Search as SearchIcon,
  Bookmark as BookmarkIcon,
  BookmarkBorder as BookmarkBorderIcon,
  FilterAlt as FilterIcon,
  Check as CheckIcon,
  FilterListOff as FilterListOffIcon,
  Close as CloseIcon
} from '@mui/icons-material';
import { format, formatDistanceToNow } from 'date-fns';
import axios from 'axios';
import JobCard, { JobCardSkeleton } from './JobCard';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

const JobList = () => {
  const navigate = useNavigate();
  const location = useLocation();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const queryParams = new URLSearchParams(location.search);
  
  // State
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [totalJobs, setTotalJobs] = useState(0);
  const [savedJobs, setSavedJobs] = useState([]);
  const [page, setPage] = useState(parseInt(queryParams.get('page') || '1', 10));
  const [searchTerm, setSearchTerm] = useState(queryParams.get('search') || '');
  const [filters, setFilters] = useState({
    jobType: queryParams.get('jobType') || '',
    location: queryParams.get('location') || '',
    remote: queryParams.get('remote') === 'true',
    sortBy: queryParams.get('sortBy') || 'date',
    search: queryParams.get('search') || '',
    salary_min: queryParams.get('salary_min') || '',
    salary_max: queryParams.get('salary_max') || '',
    sort_by: queryParams.get('sort_by') || 'date_posted',
    sort_order: queryParams.get('sort_order') || 'desc',
    page: parseInt(queryParams.get('page') || '1'),
    limit: 10
  });
  const [filtersVisible, setFiltersVisible] = useState(false);
  const [availableFilters, setAvailableFilters] = useState({
    jobTypes: [],
    locations: []
  });
  const [showFilters, setShowFilters] = useState(false);
  
  const PAGE_SIZE = 10;

  useEffect(() => {
    fetchJobs();
    fetchSavedJobs();
    fetchFilterOptions();
  }, [page, filters.sortBy]);

  useEffect(() => {
    // Update URL with current search and filters
    const params = new URLSearchParams();
    if (page > 1) params.set('page', page.toString());
    if (searchTerm) params.set('search', searchTerm);
    if (filters.jobType) params.set('jobType', filters.jobType);
    if (filters.location) params.set('location', filters.location);
    if (filters.remote) params.set('remote', 'true');
    if (filters.sortBy !== 'date') params.set('sortBy', filters.sortBy);
    
    const newUrl = `${location.pathname}?${params.toString()}`;
    window.history.replaceState({}, '', newUrl);
  }, [page, searchTerm, filters, location.pathname]);

  const fetchJobs = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      params.set('page', page.toString());
      params.set('limit', PAGE_SIZE.toString());
      params.set('sort', filters.sortBy);
      
      if (searchTerm) params.set('search', searchTerm);
      if (filters.jobType) params.set('job_type', filters.jobType);
      if (filters.location) params.set('location', filters.location);
      if (filters.remote) params.set('remote', 'true');
      
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/search?${params.toString()}`
      );
      
      setJobs(response.data.jobs);
      setTotalJobs(response.data.total);
    } catch (error) {
      console.error('Error fetching jobs:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchSavedJobs = async () => {
    try {
      // Check if user is logged in first
      const token = localStorage.getItem('token');
      if (!token) return;
      
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/saved`,
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setSavedJobs(response.data.map(job => job._id));
    } catch (error) {
      console.error('Error fetching saved jobs:', error);
    }
  };

  const fetchFilterOptions = async () => {
    try {
      const response = await axios.get(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/filters`
      );
      
      setAvailableFilters({
        jobTypes: response.data.job_types || [],
        locations: response.data.locations || []
      });
    } catch (error) {
      console.error('Error fetching filter options:', error);
    }
  };

  const handleSearch = (event) => {
    event.preventDefault();
    setPage(1);
    fetchJobs();
  };

  const handleFilterChange = (name, value) => {
    setFilters(prev => ({
      ...prev,
      [name]: value
    }));
    setPage(1);
  };

  const handleClearFilters = () => {
    setFilters({
      jobType: '',
      location: '',
      remote: false,
      sortBy: 'date',
      search: '',
      salary_min: '',
      salary_max: '',
      sort_by: 'date_posted',
      sort_order: 'desc',
      page: 1,
      limit: 10
    });
    setSearchTerm('');
    setPage(1);
  };

  const handlePageChange = (event, value) => {
    setPage(value);
    window.scrollTo(0, 0);
  };

  const toggleSaveJob = async (jobId) => {
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login?redirect=' + encodeURIComponent(location.pathname + location.search));
        return;
      }
      
      if (savedJobs.includes(jobId)) {
        await axios.delete(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${jobId}/save`,
          { headers: { Authorization: `Bearer ${token}` }}
        );
        setSavedJobs(savedJobs.filter(id => id !== jobId));
      } else {
        await axios.post(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${jobId}/save`,
          {},
          { headers: { Authorization: `Bearer ${token}` }}
        );
        setSavedJobs([...savedJobs, jobId]);
      }
    } catch (error) {
      console.error('Error toggling saved job:', error);
    }
  };

  const formatPostedDate = (dateStr) => {
    try {
      const date = new Date(dateStr);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (e) {
      return 'Unknown date';
    }
  };

  const getTotalPages = () => {
    return Math.ceil(totalJobs / PAGE_SIZE);
  };

  return (
    <Container maxWidth="lg" sx={{ my: 4 }}>
      <Grid container spacing={3}>
        {/* Filters section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', flexWrap: 'wrap', gap: 2 }}>
              <Typography variant="h6" component="h1" sx={{ flexGrow: 1 }}>
                Job Listings
                {totalJobs > 0 && !loading && (
                  <Typography component="span" variant="body2" color="text.secondary" sx={{ ml: 1 }}>
                    ({totalJobs} results)
                  </Typography>
                )}
              </Typography>
              
              <Button 
                startIcon={<FilterIcon />}
                onClick={() => setShowFilters(!showFilters)}
                variant={showFilters ? "contained" : "outlined"}
                size="small"
              >
                Filters
              </Button>
              
              <FormControl size="small" sx={{ minWidth: 200 }}>
                <InputLabel id="sort-select-label">Sort by</InputLabel>
                <Select
                  labelId="sort-select-label"
                  id="sort-select"
                  value={`${filters.sort_by}:${filters.sort_order}`}
                  label="Sort by"
                  onChange={(e) => handleFilterChange('sort_by', e.target.value.split(':')[0])}
                >
                  {sortOptions.map(option => (
                    <MenuItem key={option.value} value={option.value}>
                      {option.label}
                    </MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Box>
            
            {showFilters && (
              <Box sx={{ mt: 2 }}>
                <Divider sx={{ my: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12} md={4}>
                    <TextField
                      fullWidth
                      label="Search jobs"
                      name="search"
                      value={filters.search}
                      onChange={(e) => handleFilterChange('search', e.target.value)}
                      placeholder="Job title, skills, or keywords"
                      InputProps={{
                        startAdornment: (
                          <InputAdornment position="start">
                            <SearchIcon />
                          </InputAdornment>
                        ),
                        endAdornment: filters.search && (
                          <InputAdornment position="end">
                            <IconButton
                              size="small"
                              onClick={() => handleFilterChange('search', '')}
                            >
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                      size="small"
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={3}>
                    <TextField
                      fullWidth
                      label="Location"
                      name="location"
                      value={filters.location}
                      onChange={(e) => handleFilterChange('location', e.target.value)}
                      placeholder="City, country, or remote"
                      size="small"
                      InputProps={{
                        endAdornment: filters.location && (
                          <InputAdornment position="end">
                            <IconButton
                              size="small"
                              onClick={() => handleFilterChange('location', '')}
                            >
                              <CloseIcon fontSize="small" />
                            </IconButton>
                          </InputAdornment>
                        )
                      }}
                    />
                  </Grid>
                  
                  <Grid item xs={12} md={2}>
                    <FormControl fullWidth size="small">
                      <InputLabel id="job-type-label">Job Type</InputLabel>
                      <Select
                        labelId="job-type-label"
                        name="jobType"
                        value={filters.jobType}
                        onChange={(e) => handleFilterChange('jobType', e.target.value)}
                        label="Job Type"
                      >
                        <MenuItem value="">All types</MenuItem>
                        {availableFilters.jobTypes.map(type => (
                          <MenuItem key={type} value={type}>
                            {type}
                          </MenuItem>
                        ))}
                      </Select>
                    </FormControl>
                  </Grid>
                  
                  <Grid item xs={6} md={1.5}>
                    <TextField
                      fullWidth
                      label="Min Salary"
                      name="salary_min"
                      type="number"
                      value={filters.salary_min}
                      onChange={(e) => handleFilterChange('salary_min', e.target.value)}
                      size="small"
                    />
                  </Grid>
                  
                  <Grid item xs={6} md={1.5}>
                    <TextField
                      fullWidth
                      label="Max Salary"
                      name="salary_max"
                      type="number"
                      value={filters.salary_max}
                      onChange={(e) => handleFilterChange('salary_max', e.target.value)}
                      size="small"
                    />
                  </Grid>
                </Grid>
                
                <Box sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
                  <Button 
                    size="small"
                    onClick={handleClearFilters}
                    sx={{ mr: 1 }}
                  >
                    Clear all
                  </Button>
                  
                  <Button 
                    variant="contained" 
                    color="primary"
                    size="small"
                    onClick={() => setShowFilters(false)}
                  >
                    Apply filters
                  </Button>
                </Box>
              </Box>
            )}
            
            {/* Active filters display */}
            {(filters.search || filters.location || filters.jobType || 
              filters.salary_min || filters.salary_max) && (
              <Box sx={{ mt: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {filters.search && (
                  <Chip 
                    label={`Search: ${filters.search}`}
                    onDelete={() => handleFilterChange('search', '')}
                    size="small"
                  />
                )}
                
                {filters.location && (
                  <Chip 
                    label={`Location: ${filters.location}`}
                    onDelete={() => handleFilterChange('location', '')}
                    size="small"
                  />
                )}
                
                {filters.jobType && (
                  <Chip 
                    label={`Type: ${filters.jobType}`}
                    onDelete={() => handleFilterChange('jobType', '')}
                    size="small"
                  />
                )}
                
                {filters.salary_min && (
                  <Chip 
                    label={`Min salary: $${filters.salary_min}`}
                    onDelete={() => handleFilterChange('salary_min', '')}
                    size="small"
                  />
                )}
                
                {filters.salary_max && (
                  <Chip 
                    label={`Max salary: $${filters.salary_max}`}
                    onDelete={() => handleFilterChange('salary_max', '')}
                    size="small"
                  />
                )}
              </Box>
            )}
          </Paper>
        </Grid>
        
        {/* Jobs listing */}
        <Grid item xs={12}>
          {loading ? (
            // Loading skeletons
            Array.from(new Array(5)).map((_, index) => (
              <JobCardSkeleton key={index} />
            ))
          ) : jobs.length === 0 ? (
            // No results
            <Paper sx={{ p: 4, textAlign: 'center' }}>
              <Typography variant="h6" color="text.secondary" gutterBottom>
                No job listings found
              </Typography>
              <Typography variant="body2" color="text.secondary">
                Try adjusting your search filters or check back later for new opportunities.
              </Typography>
              {Object.values(filters).some(val => val !== '' && val !== null && val !== 1 && val !== 10) && (
                <Button 
                  variant="outlined" 
                  onClick={handleClearFilters}
                  sx={{ mt: 2 }}
                >
                  Clear all filters
                </Button>
              )}
            </Paper>
          ) : (
            // Job listings
            <>
              {jobs.map(job => (
                <JobCard 
                  key={job._id} 
                  job={job} 
                  isSaved={savedJobs.includes(job._id)}
                  onToggleSave={toggleSaveJob}
                />
              ))}
              
              {/* Pagination */}
              {getTotalPages() > 1 && (
                <Box sx={{ display: 'flex', justifyContent: 'center', mt: 4 }}>
                  <Pagination 
                    count={getTotalPages()} 
                    page={page}
                    onChange={handlePageChange}
                    color="primary"
                    siblingCount={isMobile ? 0 : 1}
                  />
                </Box>
              )}
            </>
          )}
        </Grid>
      </Grid>
    </Container>
  );
};

export default JobList; 