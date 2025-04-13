import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Box, Container, Typography, Grid, Paper, Chip, Button, 
  Divider, CircularProgress, List, ListItem, ListItemIcon, 
  ListItemText, Card, CardContent, Dialog, DialogTitle,
  DialogContent, DialogActions, IconButton, Tooltip, Modal,
  TextField, Alert, Backdrop, Fade, Tabs, Tab, Avatar, Skeleton,
  useTheme, useMediaQuery, Snackbar
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Work as WorkIcon,
  Business as BusinessIcon,
  AttachMoney as AttachMoneyIcon,
  Schedule as ScheduleIcon,
  Check as CheckIcon,
  Close as CloseIcon,
  BookmarkBorder as BookmarkBorderIcon,
  Bookmark as BookmarkIcon,
  Share as ShareIcon,
  ArrowBack as ArrowBackIcon,
  OpenInNew as OpenInNewIcon,
  BusinessCenter,
  WorkOutline,
  CheckCircleOutline,
  Assignment,
  BusinessOutlined
} from '@mui/icons-material';
import { format } from 'date-fns';
import ReactMarkdown from 'react-markdown';
import axios from 'axios';
import parse from 'html-react-parser';
import DOMPurify from 'dompurify';
import jobService from '../../services/AllServices';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

// Helper function to generate a color based on string
const stringToColor = (string) => {
  let hash = 0;
  for (let i = 0; i < string.length; i++) {
    hash = string.charCodeAt(i) + ((hash << 5) - hash);
  }
  let color = '#';
  for (let i = 0; i < 3; i++) {
    const value = (hash >> (i * 8)) & 0xff;
    color += `00${value.toString(16)}`.slice(-2);
  }
  return color;
};

// Helper function to get company initials
const getCompanyInitials = (name) => {
  if (!name) return '?';
  const words = name.split(' ');
  return words.length > 1
    ? `${words[0][0]}${words[1][0]}`
    : name.substring(0, 2).toUpperCase();
};

// Component for similar jobs
const SimilarJobCard = ({ job, onClick }) => {
  return (
    <Card variant="outlined" sx={{ mb: 2, cursor: 'pointer' }} onClick={onClick}>
      <CardContent sx={{ py: 1.5 }}>
        <Typography variant="subtitle1" noWrap>
          {job.title}
        </Typography>
        <Typography variant="body2" color="text.secondary" noWrap>
          {job.company}
        </Typography>
        <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
          {job.is_remote && (
            <Chip 
              label="Remote" 
              size="small" 
              color="primary" 
              variant="outlined"
              sx={{ height: 20, fontSize: '0.7rem' }}
            />
          )}
          {job.location && (
            <Chip 
              label={job.location} 
              size="small" 
              variant="outlined"
              sx={{ height: 20, fontSize: '0.7rem' }}
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

// Premium apply modal component
const ApplyModal = ({ open, handleClose, job, isPremium }) => {
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState(0);
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    resumeUrl: '',
    coverLetter: ''
  });

  const iframeRef = useRef(null);

  useEffect(() => {
    if (open && isPremium && job?.apply_url) {
      setLoading(true);
    }
  }, [open, job, isPremium]);

  const handleTabChange = (event, newValue) => {
    setActiveTab(newValue);
  };

  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleApply = async () => {
    // If premium user, we'll use the iframe method
    if (isPremium) {
      // Handle premium apply with autofill
      handleClose();
      return;
    }
    
    // Otherwise, handle regular apply
    setLoading(true);
    try {
      await axios.post(
        `${API_URL}/jobs/${job._id}/apply`,
        formData,
        { 
          headers: { 
            Authorization: `Bearer ${localStorage.getItem('token')}` 
          }
        }
      );
      
      // Open the apply URL in a new tab
      if (job.apply_url) {
        window.open(job.apply_url, '_blank');
      }
      
      handleClose();
    } catch (error) {
      console.error('Error applying to job:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleIframeLoad = () => {
    setLoading(false);
    
    // Auto-fill form fields if premium user
    if (isPremium && iframeRef.current) {
      const iframe = iframeRef.current;
      try {
        // This is just a simplified example, in reality this would need more sophisticated 
        // logic to identify form fields across different job application sites
        setTimeout(() => {
          const iframeDoc = iframe.contentWindow.document;
          
          // Find and fill common form fields
          const nameFields = iframeDoc.querySelectorAll('input[name*="name"], input[id*="name"]');
          const emailFields = iframeDoc.querySelectorAll('input[type="email"], input[name*="email"], input[id*="email"]');
          const phoneFields = iframeDoc.querySelectorAll('input[type="tel"], input[name*="phone"], input[id*="phone"]');
          
          // Fill name fields
          nameFields.forEach(field => {
            field.value = 'John Doe'; // Would use actual user data
          });
          
          // Fill email fields
          emailFields.forEach(field => {
            field.value = 'john.doe@example.com'; // Would use actual user data
          });
          
          // Fill phone fields
          phoneFields.forEach(field => {
            field.value = '+1 (555) 123-4567'; // Would use actual user data
          });
          
        }, 2000); // Give time for any JS on the page to initialize
      } catch (error) {
        console.error('Error auto-filling form:', error);
      }
    }
  };

  return (
    <Dialog
      open={open}
      onClose={handleClose}
      fullWidth
      maxWidth="md"
      aria-labelledby="apply-dialog-title"
    >
      <DialogTitle id="apply-dialog-title">
        Apply to: {job?.title} at {job?.company}
        <IconButton
          aria-label="close"
          onClick={handleClose}
          sx={{
            position: 'absolute',
            right: 8,
            top: 8,
            color: (theme) => theme.palette.grey[500],
          }}
        >
          <CloseIcon />
        </IconButton>
      </DialogTitle>
      
      <DialogContent dividers>
        {isPremium ? (
          <>
            {loading && (
              <Box sx={{ display: 'flex', justifyContent: 'center', my: 3 }}>
                <CircularProgress />
              </Box>
            )}
            
            <Alert severity="info" sx={{ mb: 2 }}>
              <Typography variant="body2">
                Premium feature: Auto-fill is active. Your profile information will be automatically filled in the application form where possible.
              </Typography>
            </Alert>
            
            <Box sx={{ height: '60vh', width: '100%', overflow: 'hidden' }}>
              {job?.apply_url && (
                <iframe
                  ref={iframeRef}
                  src={job.apply_url}
                  width="100%"
                  height="100%"
                  title="Job Application Form"
                  onLoad={handleIframeLoad}
                  style={{ border: 'none' }}
                />
              )}
            </Box>
          </>
        ) : (
          <>
            <Tabs value={activeTab} onChange={handleTabChange} sx={{ mb: 2 }}>
              <Tab label="Application Form" />
              <Tab label="External Apply" />
            </Tabs>
            
            {activeTab === 0 && (
              <Grid container spacing={2}>
                <Grid item xs={12}>
                  <Alert severity="info" sx={{ mb: 2 }}>
                    <Typography variant="body2">
                      This job application will be sent to the employer. 
                      <Link 
                        to="/pricing" 
                        style={{ marginLeft: 8 }}
                      >
                        Upgrade to Premium
                      </Link> for auto-fill and direct application features.
                    </Typography>
                  </Alert>
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    label="Full Name"
                    name="name"
                    value={formData.name}
                    onChange={handleInputChange}
                    fullWidth
                    required
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    label="Email"
                    name="email"
                    type="email"
                    value={formData.email}
                    onChange={handleInputChange}
                    fullWidth
                    required
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    label="Phone"
                    name="phone"
                    value={formData.phone}
                    onChange={handleInputChange}
                    fullWidth
                  />
                </Grid>
                
                <Grid item xs={12} md={6}>
                  <TextField
                    label="Resume URL"
                    name="resumeUrl"
                    value={formData.resumeUrl}
                    onChange={handleInputChange}
                    fullWidth
                    placeholder="https://example.com/your-resume.pdf"
                  />
                </Grid>
                
                <Grid item xs={12}>
                  <TextField
                    label="Cover Letter"
                    name="coverLetter"
                    value={formData.coverLetter}
                    onChange={handleInputChange}
                    fullWidth
                    multiline
                    rows={5}
                  />
                </Grid>
              </Grid>
            )}
            
            {activeTab === 1 && (
              <Box sx={{ p: 2, textAlign: 'center' }}>
                <Typography variant="body1" gutterBottom>
                  You'll be redirected to the company's website to complete your application.
                </Typography>
                
                <Button 
                  variant="contained" 
                  color="primary"
                  href={job?.apply_url} 
                  target="_blank"
                  rel="noopener noreferrer"
                  endIcon={<OpenInNewIcon />}
                  sx={{ mt: 2 }}
                >
                  Go to Job Application
                </Button>
              </Box>
            )}
          </>
        )}
      </DialogContent>
      
      <DialogActions>
        <Button onClick={handleClose} color="primary">
          Cancel
        </Button>
        {activeTab === 0 && !isPremium && (
          <Button 
            onClick={handleApply} 
            color="primary" 
            variant="contained"
            disabled={!formData.name || !formData.email || loading}
          >
            {loading ? 'Submitting...' : 'Submit Application'}
          </Button>
        )}
      </DialogActions>
    </Dialog>
  );
};

// Skeleton loader component for loading state
const JobDetailSkeleton = () => (
  <Box sx={{ mt: 4 }}>
    <Skeleton variant="rectangular" width="100%" height={60} sx={{ mb: 2 }} />
    <Grid container spacing={3}>
      <Grid item xs={12} md={8}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Skeleton variant="circular" width={60} height={60} sx={{ mb: 2 }} />
          <Skeleton variant="text" width="70%" height={40} sx={{ mb: 1 }} />
          <Skeleton variant="text" width="50%" height={30} sx={{ mb: 2 }} />
          <Grid container spacing={2} sx={{ mb: 3 }}>
            <Grid item xs={6}>
              <Skeleton variant="text" width="90%" />
            </Grid>
            <Grid item xs={6}>
              <Skeleton variant="text" width="90%" />
            </Grid>
            <Grid item xs={6}>
              <Skeleton variant="text" width="90%" />
            </Grid>
            <Grid item xs={6}>
              <Skeleton variant="text" width="90%" />
            </Grid>
          </Grid>
          <Skeleton variant="rectangular" width="100%" height={200} sx={{ mb: 3 }} />
          <Skeleton variant="text" width="40%" height={30} sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" width="100%" height={100} sx={{ mb: 3 }} />
          <Skeleton variant="text" width="40%" height={30} sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" width="100%" height={100} />
        </Paper>
      </Grid>
      <Grid item xs={12} md={4}>
        <Paper sx={{ p: 3, mb: 3 }}>
          <Skeleton variant="text" width="60%" height={30} sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" width="100%" height={100} />
        </Paper>
        <Paper sx={{ p: 3 }}>
          <Skeleton variant="text" width="80%" height={30} sx={{ mb: 2 }} />
          <Skeleton variant="rectangular" width="100%" height={200} />
        </Paper>
      </Grid>
    </Grid>
  </Box>
);

const JobDetail = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const theme = useTheme();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));
  
  const [job, setJob] = useState(null);
  const [similarJobs, setSimilarJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isSaved, setIsSaved] = useState(false);
  const [applyModalOpen, setApplyModalOpen] = useState(false);
  const [userProfile, setUserProfile] = useState(null);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const [isPremium, setIsPremium] = useState(false);
  const [error, setError] = useState(null);
  const [saveLoading, setSaveLoading] = useState(false);
  const [snackbar, setSnackbar] = useState({
    open: false,
    message: '',
    severity: 'info'
  });

  useEffect(() => {
    fetchJobDetails();
    checkLoginStatus();
  }, [id]);

  const fetchJobDetails = async () => {
    setLoading(true);
    setError(null);
    
    try {
      const jobData = await jobService.fetchJobById(id);
      setJob(jobData);
      
      // Check if job is saved
      const savedJobs = JSON.parse(localStorage.getItem('savedJobs') || '[]');
      setIsSaved(savedJobs.some(savedJob => savedJob.id === id));
      
      // Fetch similar jobs
      const similarJobsData = await jobService.fetchSimilarJobs(id);
      setSimilarJobs(similarJobsData);
    } catch (err) {
      console.error('Error fetching job details:', err);
      if (err.response && err.response.status === 404) {
        setError('Job not found');
      } else {
        setError('Failed to load job details. Please try again later.');
      }
    } finally {
      setLoading(false);
    }
  };

  const checkLoginStatus = async () => {
    const token = localStorage.getItem('token');
    if (token) {
      try {
        const response = await axios.get(
          `${API_URL}/users/profile`,
          { headers: { Authorization: `Bearer ${token}` }}
        );
        
        setUserProfile(response.data);
        setIsLoggedIn(true);
        setIsPremium(response.data.is_premium);
      } catch (error) {
        console.error('Error fetching user profile:', error);
        localStorage.removeItem('token');
        setIsLoggedIn(false);
        setIsPremium(false);
      }
    }
  };

  const toggleSaveJob = async () => {
    if (saveLoading) return;
    
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login?redirect=' + encodeURIComponent(`/jobs/${id}`));
      return;
    }
    
    setSaveLoading(true);
    
    try {
      if (isSaved) {
        await jobService.removeSavedJob(id);
        setSnackbar({
          open: true,
          message: 'Job removed from saved jobs',
          severity: 'info'
        });
      } else {
        await jobService.saveJob(id);
        setSnackbar({
          open: true,
          message: 'Job saved successfully',
          severity: 'success'
        });
      }
      setIsSaved(!isSaved);
    } catch (error) {
      console.error('Error toggling saved job:', error);
      setSnackbar({
        open: true,
        message: 'Failed to save job',
        severity: 'error'
      });
    } finally {
      setSaveLoading(false);
    }
  };

  const handleShareJob = () => {
    if (navigator.share) {
      navigator.share({
        title: job.title,
        text: `Check out this job: ${job.title} at ${job.company}`,
        url: window.location.href
      }).catch(err => {
        console.error('Error sharing:', err);
        setSnackbar({
          open: true,
          message: 'Failed to share',
          severity: 'error'
        });
      });
    } else {
      navigator.clipboard.writeText(window.location.href);
      setSnackbar({
        open: true,
        message: 'Link copied to clipboard',
        severity: 'success'
      });
    }
  };

  const handleApplyClick = () => {
    const token = localStorage.getItem('token');
    if (!token) {
      navigate('/login?redirect=' + encodeURIComponent(`/jobs/${id}`));
      return;
    }
    
    setApplyModalOpen(true);
  };

  const handleApplyClose = () => {
    setApplyModalOpen(false);
  };

  const formatDate = (dateStr) => {
    try {
      return format(new Date(dateStr), 'MMMM d, yyyy');
    } catch (e) {
      return 'Date not available';
    }
  };

  const handleSnackbarClose = () => {
    setSnackbar({ ...snackbar, open: false });
  };

  if (loading) {
    return (
      <Container maxWidth="lg">
        <JobDetailSkeleton />
      </Container>
    );
  }

  if (error || !job) {
    return (
      <Container maxWidth="lg">
        <Alert severity="error" sx={{ mt: 4 }}>
          {error || 'Job not found'}
        </Alert>
        <Button
          startIcon={<ArrowBackIcon />}
          onClick={() => navigate('/jobs')}
          sx={{ mt: 2 }}
        >
          Back to Jobs
        </Button>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg" sx={{ py: 4 }}>
      <Button
        startIcon={<ArrowBackIcon />}
        onClick={() => navigate('/jobs')}
        sx={{ mb: 2 }}
      >
        Back to Jobs
      </Button>
      
      <Grid container spacing={3}>
        {/* Main Content */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 3, mb: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 2 }}>
              <Avatar
                sx={{
                  bgcolor: stringToColor(job.company || 'Job'),
                  width: 60,
                  height: 60,
                  mr: 2
                }}
              >
                {getCompanyInitials(job.company)}
              </Avatar>
              <Box>
                <Typography variant="h4" gutterBottom>
                  {job.title}
                </Typography>
                <Typography variant="h6" color="text.secondary">
                  {job.company}
                </Typography>
              </Box>
            </Box>

            <Grid container spacing={2} sx={{ mb: 3 }}>
              {job.location && (
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <LocationIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography>{job.location}</Typography>
                  </Box>
                </Grid>
              )}
              
              {job.salary && (
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <AttachMoneyIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography>{job.salary}</Typography>
                  </Box>
                </Grid>
              )}
              
              {job.company && (
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <BusinessIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography>{job.company}</Typography>
                  </Box>
                </Grid>
              )}
              
              {job.postedDate && (
                <Grid item xs={12} sm={6}>
                  <Box sx={{ display: 'flex', alignItems: 'center' }}>
                    <ScheduleIcon sx={{ mr: 1, color: 'text.secondary' }} />
                    <Typography>
                      Posted: {format(new Date(job.postedDate), 'MMM dd, yyyy')}
                    </Typography>
                  </Box>
                </Grid>
              )}
            </Grid>

            <Box sx={{ display: 'flex', mb: 3 }}>
              <Button
                variant="contained"
                color="primary"
                sx={{ mr: 2 }}
                onClick={handleApplyClick}
              >
                Apply Now
              </Button>
              
              <IconButton onClick={toggleSaveJob} color={isSaved ? 'primary' : 'default'}>
                {isSaved ? <BookmarkIcon /> : <BookmarkBorderIcon />}
              </IconButton>
              
              <IconButton onClick={handleShareJob}>
                <ShareIcon />
              </IconButton>
            </Box>

            <Divider sx={{ mb: 3 }} />

            {job.description && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Job Description
                </Typography>
                <Box sx={{ typography: 'body1' }}>
                  {parse(DOMPurify.sanitize(job.description, {
                    USE_PROFILES: { html: true },
                    ALLOWED_TAGS: [
                      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'ul', 'ol', 
                      'li', 'b', 'i', 'strong', 'em', 'strike', 'code', 'hr', 
                      'br', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                      'span'
                    ],
                    ALLOWED_ATTR: ['href', 'target', 'rel', 'style', 'class']
                  }))}
                </Box>
              </Box>
            )}

            {job.responsibilities && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Responsibilities
                </Typography>
                <Box sx={{ typography: 'body1' }}>
                  {parse(DOMPurify.sanitize(job.responsibilities, {
                    USE_PROFILES: { html: true },
                    ALLOWED_TAGS: [
                      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'ul', 'ol', 
                      'li', 'b', 'i', 'strong', 'em', 'strike', 'code', 'hr', 
                      'br', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                      'span'
                    ],
                    ALLOWED_ATTR: ['href', 'target', 'rel', 'style', 'class']
                  }))}
                </Box>
              </Box>
            )}

            {job.requirements && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Requirements
                </Typography>
                <Box sx={{ typography: 'body1' }}>
                  {parse(DOMPurify.sanitize(job.requirements, {
                    USE_PROFILES: { html: true },
                    ALLOWED_TAGS: [
                      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'ul', 'ol', 
                      'li', 'b', 'i', 'strong', 'em', 'strike', 'code', 'hr', 
                      'br', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                      'span'
                    ],
                    ALLOWED_ATTR: ['href', 'target', 'rel', 'style', 'class']
                  }))}
                </Box>
              </Box>
            )}

            {job.benefits && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Benefits
                </Typography>
                <Box sx={{ typography: 'body1' }}>
                  {parse(DOMPurify.sanitize(job.benefits, {
                    USE_PROFILES: { html: true },
                    ALLOWED_TAGS: [
                      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'ul', 'ol', 
                      'li', 'b', 'i', 'strong', 'em', 'strike', 'code', 'hr', 
                      'br', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                      'span'
                    ],
                    ALLOWED_ATTR: ['href', 'target', 'rel', 'style', 'class']
                  }))}
                </Box>
              </Box>
            )}

            {job.skills && job.skills.length > 0 && (
              <Box sx={{ mb: 3 }}>
                <Typography variant="h6" gutterBottom>
                  Required Skills
                </Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                  {job.skills.map((skill, index) => (
                    <Chip key={index} label={skill} />
                  ))}
                </Box>
              </Box>
            )}

            {job.companyDescription && (
              <Box>
                <Typography variant="h6" gutterBottom>
                  About {job.company}
                </Typography>
                <Box sx={{ typography: 'body1' }}>
                  {parse(DOMPurify.sanitize(job.companyDescription, {
                    USE_PROFILES: { html: true },
                    ALLOWED_TAGS: [
                      'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'a', 'ul', 'ol', 
                      'li', 'b', 'i', 'strong', 'em', 'strike', 'code', 'hr', 
                      'br', 'div', 'table', 'thead', 'tbody', 'tr', 'th', 'td',
                      'span'
                    ],
                    ALLOWED_ATTR: ['href', 'target', 'rel', 'style', 'class']
                  }))}
                </Box>
              </Box>
            )}
          </Paper>
        </Grid>

        {/* Sidebar */}
        <Grid item xs={12} md={4}>
          {/* Job Summary Card */}
          <Card sx={{ mb: 3 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Job Summary
              </Typography>
              <List dense>
                {job.jobType && (
                  <ListItem>
                    <ListItemText 
                      primary="Job Type" 
                      secondary={job.jobType} 
                    />
                  </ListItem>
                )}
                {job.experienceLevel && (
                  <ListItem>
                    <ListItemText 
                      primary="Experience Level" 
                      secondary={job.experienceLevel} 
                    />
                  </ListItem>
                )}
                {job.educationLevel && (
                  <ListItem>
                    <ListItemText 
                      primary="Education" 
                      secondary={job.educationLevel} 
                    />
                  </ListItem>
                )}
                {job.industry && (
                  <ListItem>
                    <ListItemText 
                      primary="Industry" 
                      secondary={job.industry} 
                    />
                  </ListItem>
                )}
                {job.applicationDeadline && (
                  <ListItem>
                    <ListItemText 
                      primary="Application Deadline" 
                      secondary={format(new Date(job.applicationDeadline), 'MMM dd, yyyy')} 
                    />
                  </ListItem>
                )}
              </List>
            </CardContent>
          </Card>

          {/* Similar Jobs */}
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Similar Jobs
              </Typography>
              {similarJobs.length > 0 ? (
                <List>
                  {similarJobs.map(similarJob => (
                    <ListItem 
                      key={similarJob.id}
                      button
                      onClick={() => navigate(`/jobs/${similarJob.id}`)}
                      sx={{ 
                        borderBottom: '1px solid',
                        borderColor: 'divider',
                        '&:last-child': { borderBottom: 'none' }
                      }}
                    >
                      <ListItemText
                        primary={similarJob.title}
                        secondary={
                          <React.Fragment>
                            <Typography component="span" variant="body2" color="text.primary">
                              {similarJob.company}
                            </Typography>
                            {similarJob.location && ` — ${similarJob.location}`}
                          </React.Fragment>
                        }
                      />
                    </ListItem>
                  ))}
                </List>
              ) : (
                <Typography color="text.secondary">
                  No similar jobs found
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <ApplyModal 
        open={applyModalOpen} 
        handleClose={handleApplyClose} 
        job={job}
        isPremium={isPremium}
      />

      <Snackbar
        open={snackbar.open}
        autoHideDuration={6000}
        onClose={handleSnackbarClose}
      >
        <Alert onClose={handleSnackbarClose} severity={snackbar.severity}>
          {snackbar.message}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default JobDetail; 