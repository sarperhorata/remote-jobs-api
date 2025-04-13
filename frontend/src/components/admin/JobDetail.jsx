import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Box, Container, Typography, Paper, Grid, Chip, Button, 
  Divider, CircularProgress, Tabs, Tab, Card, CardContent, 
  List, ListItem, ListItemText, Tooltip, IconButton
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Edit as EditIcon,
  Delete as DeleteIcon,
  Visibility as VisibilityIcon,
  History as HistoryIcon,
  OpenInNew as OpenInNewIcon,
  RadioButtonChecked as RadioButtonCheckedIcon
} from '@mui/icons-material';
import { format } from 'date-fns';
import ReactDiffViewer from 'react-diff-viewer';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const [job, setJob] = useState(null);
  const [changeHistory, setChangeHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [tabValue, setTabValue] = useState(0);
  const [selectedChange, setSelectedChange] = useState(null);

  useEffect(() => {
    const fetchJobDetails = async () => {
      setLoading(true);
      try {
        const jobResponse = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${id}`);
        setJob(jobResponse.data);
        
        // Fetch change history
        const historyResponse = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${id}/history`);
        setChangeHistory(historyResponse.data);
        
        if (historyResponse.data.length > 0) {
          setSelectedChange(historyResponse.data[0]);
        }
      } catch (error) {
        console.error('Error fetching job details:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchJobDetails();
  }, [id]);

  const handleChangeTab = (event, newValue) => {
    setTabValue(newValue);
  };

  const handleChangeSelect = (change) => {
    setSelectedChange(change);
  };

  const handleDeleteJob = async () => {
    if (window.confirm(`Are you sure you want to delete "${job.title}"?`)) {
      try {
        await axios.delete(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${id}`);
        navigate('/admin/jobs');
      } catch (error) {
        console.error('Error deleting job:', error);
      }
    }
  };

  const formatDate = (dateString) => {
    try {
      return format(new Date(dateString), 'MMM d, yyyy h:mm a');
    } catch (e) {
      return 'Invalid date';
    }
  };

  // Function to render diff blocks based on the selected change
  const renderDiffView = () => {
    if (!selectedChange) return null;
    
    const oldData = selectedChange.old_data || {};
    const newData = selectedChange.new_data || {};
    
    // Determine which fields changed
    const changedFields = new Set();
    
    // Add fields from old data
    Object.keys(oldData).forEach(key => {
      if (JSON.stringify(oldData[key]) !== JSON.stringify(newData[key])) {
        changedFields.add(key);
      }
    });
    
    // Add new fields from new data
    Object.keys(newData).forEach(key => {
      if (!oldData.hasOwnProperty(key) || JSON.stringify(oldData[key]) !== JSON.stringify(newData[key])) {
        changedFields.add(key);
      }
    });
    
    return Array.from(changedFields).map(field => (
      <Box key={field} sx={{ mb: 3 }}>
        <Typography variant="subtitle1" sx={{ fontWeight: 'bold', mb: 1 }}>
          {field.charAt(0).toUpperCase() + field.slice(1).replace(/_/g, ' ')}
        </Typography>
        <ReactDiffViewer
          oldValue={typeof oldData[field] === 'object' ? JSON.stringify(oldData[field], null, 2) : String(oldData[field] || '')}
          newValue={typeof newData[field] === 'object' ? JSON.stringify(newData[field], null, 2) : String(newData[field] || '')}
          splitView={true}
          useDarkTheme={false}
          showDiffOnly={false}
        />
      </Box>
    ));
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  if (!job) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ py: 4 }}>
          <Typography variant="h5" color="error">Job not found</Typography>
          <Button 
            component={Link} 
            to="/admin/jobs"
            startIcon={<ArrowBackIcon />}
            sx={{ mt: 2 }}
          >
            Back to Job List
          </Button>
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 3 }}>
          <Box>
            <Button 
              component={Link} 
              to="/admin/jobs"
              startIcon={<ArrowBackIcon />}
              sx={{ mb: 2 }}
            >
              Back to Job List
            </Button>
            <Typography variant="h4" sx={{ mb: 1 }}>
              {job.title}
            </Typography>
            <Typography variant="h6" color="text.secondary">
              {job.company}
            </Typography>
          </Box>
          <Box>
            <Button 
              variant="contained" 
              color="primary" 
              startIcon={<EditIcon />}
              component={Link}
              to={`/admin/jobs/${id}/edit`}
              sx={{ mr: 1 }}
            >
              Edit
            </Button>
            <Button 
              variant="outlined" 
              color="primary"
              startIcon={<VisibilityIcon />}
              component={Link}
              to={`/jobs/${id}`}
              sx={{ mr: 1 }}
            >
              View Public
            </Button>
            <Button 
              variant="outlined" 
              color="error"
              startIcon={<DeleteIcon />}
              onClick={handleDeleteJob}
            >
              Delete
            </Button>
          </Box>
        </Box>

        <Tabs value={tabValue} onChange={handleChangeTab} sx={{ borderBottom: 1, borderColor: 'divider', mb: 3 }}>
          <Tab label="Job Details" />
          <Tab 
            label={
              <Box sx={{ display: 'flex', alignItems: 'center' }}>
                <HistoryIcon sx={{ mr: 0.5 }} />
                Changes History
                {changeHistory.length > 0 && (
                  <Chip 
                    label={changeHistory.length} 
                    size="small" 
                    sx={{ ml: 1 }}
                    color="primary"
                  />
                )}
              </Box>
            } 
          />
        </Tabs>

        {tabValue === 0 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>Job Description</Typography>
                <Divider sx={{ mb: 2 }} />
                {job.description ? (
                  <ReactMarkdown>{job.description}</ReactMarkdown>
                ) : (
                  <Typography color="text.secondary" variant="body2">No description provided</Typography>
                )}
              </Paper>

              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>Details</Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Grid container spacing={2}>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Salary</Typography>
                    <Typography variant="body1" gutterBottom>
                      {job.salary || 'Not specified'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Location</Typography>
                    <Typography variant="body1" gutterBottom>
                      {job.location || 'Not specified'}
                      {job.is_remote && (
                        <Chip 
                          label="Remote" 
                          size="small" 
                          color="primary" 
                          variant="outlined"
                          sx={{ ml: 1 }}
                        />
                      )}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Date Posted</Typography>
                    <Typography variant="body1" gutterBottom>
                      {job.date_posted ? formatDate(job.date_posted) : 'Unknown'}
                    </Typography>
                  </Grid>
                  <Grid item xs={12} sm={6}>
                    <Typography variant="subtitle2">Job Type</Typography>
                    <Typography variant="body1" gutterBottom>
                      {job.job_type || 'Not specified'}
                    </Typography>
                  </Grid>
                  {job.tags && job.tags.length > 0 && (
                    <Grid item xs={12}>
                      <Typography variant="subtitle2">Tags</Typography>
                      <Box sx={{ mt: 1 }}>
                        {job.tags.map((tag, index) => (
                          <Chip 
                            key={index} 
                            label={tag} 
                            size="small" 
                            sx={{ mr: 1, mb: 1 }}
                          />
                        ))}
                      </Box>
                    </Grid>
                  )}
                  {job.apply_url && (
                    <Grid item xs={12}>
                      <Button
                        variant="contained"
                        color="primary"
                        endIcon={<OpenInNewIcon />}
                        href={job.apply_url}
                        target="_blank"
                        rel="noopener noreferrer"
                      >
                        Apply Link
                      </Button>
                    </Grid>
                  )}
                </Grid>
              </Paper>
            </Grid>

            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 3, mb: 3 }}>
                <Typography variant="h6" gutterBottom>Status Information</Typography>
                <Divider sx={{ mb: 2 }} />
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Status:</Typography>
                  <Chip 
                    label={job.is_active ? "Active" : "Inactive"} 
                    size="small" 
                    color={job.is_active ? "success" : "default"}
                  />
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Source:</Typography>
                  <Chip 
                    label={job.source || 'manual'} 
                    size="small" 
                    color="secondary" 
                    variant="outlined"
                  />
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Created:</Typography>
                  <Typography variant="body2">
                    {formatDate(job.created_at)}
                  </Typography>
                </Box>
                
                <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                  <Typography variant="body2">Last Updated:</Typography>
                  <Typography variant="body2">
                    {formatDate(job.updated_at)}
                  </Typography>
                </Box>
                
                {job.is_archived && (
                  <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                    <Typography variant="body2">Archived:</Typography>
                    <Chip 
                      label="Archived" 
                      size="small" 
                      color="error"
                    />
                  </Box>
                )}
              </Paper>

              <Paper sx={{ p: 3 }}>
                <Typography variant="h6" gutterBottom>Related Links</Typography>
                <Divider sx={{ mb: 2 }} />
                
                <List disablePadding>
                  {job.url && (
                    <ListItem disablePadding sx={{ mb: 1 }}>
                      <ListItemText 
                        primary="Original Job Post" 
                        secondary={
                          <Button
                            variant="text"
                            size="small"
                            endIcon={<OpenInNewIcon />}
                            href={job.url}
                            target="_blank"
                            rel="noopener noreferrer"
                          >
                            View original post
                          </Button>
                        }
                      />
                    </ListItem>
                  )}
                  
                  <ListItem disablePadding sx={{ mb: 1 }}>
                    <ListItemText 
                      primary="Company Jobs" 
                      secondary={
                        <Button
                          variant="text"
                          size="small"
                          component={Link}
                          to={`/admin/jobs?company=${encodeURIComponent(job.company)}`}
                        >
                          View all jobs from {job.company}
                        </Button>
                      }
                    />
                  </ListItem>
                </List>
              </Paper>
            </Grid>
          </Grid>
        )}

        {tabValue === 1 && (
          <Grid container spacing={3}>
            <Grid item xs={12} md={4}>
              <Paper sx={{ p: 2 }}>
                <Typography variant="h6" gutterBottom>Change History</Typography>
                <Divider sx={{ mb: 2 }} />
                
                {changeHistory.length === 0 ? (
                  <Typography color="text.secondary" variant="body2">No change history available</Typography>
                ) : (
                  <List sx={{ maxHeight: 500, overflow: 'auto' }}>
                    {changeHistory.map((change, index) => (
                      <ListItem 
                        key={index} 
                        button 
                        selected={selectedChange?._id === change._id}
                        onClick={() => handleChangeSelect(change)}
                        sx={{ 
                          mb: 1, 
                          border: '1px solid',
                          borderColor: 'divider',
                          borderRadius: 1,
                          '&.Mui-selected': {
                            backgroundColor: 'action.selected',
                            borderColor: 'primary.main'
                          }
                        }}
                      >
                        <ListItemText
                          primary={
                            <Box sx={{ display: 'flex', alignItems: 'center' }}>
                              {change.change_type === 'new' && (
                                <Tooltip title="New Job">
                                  <RadioButtonCheckedIcon fontSize="small" color="success" sx={{ mr: 1 }} />
                                </Tooltip>
                              )}
                              {change.change_type === 'updated' && (
                                <Tooltip title="Updated">
                                  <EditIcon fontSize="small" color="primary" sx={{ mr: 1 }} />
                                </Tooltip>
                              )}
                              {change.change_type === 'removed' && (
                                <Tooltip title="Removed">
                                  <DeleteIcon fontSize="small" color="error" sx={{ mr: 1 }} />
                                </Tooltip>
                              )}
                              {change.change_type.charAt(0).toUpperCase() + change.change_type.slice(1)}
                            </Box>
                          }
                          secondary={
                            <Typography variant="caption" color="text.secondary">
                              {formatDate(change.created_at)}
                            </Typography>
                          }
                        />
                      </ListItem>
                    ))}
                  </List>
                )}
              </Paper>
            </Grid>
            
            <Grid item xs={12} md={8}>
              <Paper sx={{ p: 3 }}>
                {selectedChange ? (
                  <>
                    <Box sx={{ mb: 3 }}>
                      <Typography variant="h6" gutterBottom>
                        Change Details - {selectedChange.change_type.charAt(0).toUpperCase() + selectedChange.change_type.slice(1)}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {formatDate(selectedChange.created_at)}
                      </Typography>
                      <Divider sx={{ my: 2 }} />
                    </Box>
                    
                    {renderDiffView()}
                  </>
                ) : (
                  <Typography color="text.secondary" variant="body1">
                    Select a change from the history to view details
                  </Typography>
                )}
              </Paper>
            </Grid>
          </Grid>
        )}
      </Box>
    </Container>
  );
};

export default JobDetail; 