import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { 
  Box, Container, Typography, Paper, Grid, TextField, Button, 
  Divider, CircularProgress, FormControlLabel, Switch,
  Autocomplete, Chip, InputLabel, FormHelperText, MenuItem, Select,
  FormControl, Alert, Snackbar
} from '@mui/material';
import { 
  ArrowBack as ArrowBackIcon,
  Save as SaveIcon,
  Cancel as CancelIcon,
  AddCircle as AddCircleIcon,
  Language as LanguageIcon
} from '@mui/icons-material';
import MDEditor from '@uiw/react-md-editor';
import { format } from 'date-fns';
import axios from 'axios';

const JOB_TYPES = [
  'Full Time',
  'Part Time',
  'Contract',
  'Freelance',
  'Internship'
];

const EXPERIENCE_LEVELS = [
  'Entry Level',
  'Mid Level',
  'Senior',
  'Lead',
  'Manager'
];

const JobForm = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const isEditMode = Boolean(id);
  const [isLoading, setIsLoading] = useState(isEditMode);
  const [isSaving, setIsSaving] = useState(false);
  const [showAlert, setShowAlert] = useState(false);
  const [alertMessage, setAlertMessage] = useState('');
  const [alertSeverity, setAlertSeverity] = useState('success');
  const [scrapedData, setScrapedData] = useState(null);

  // Form fields
  const [formData, setFormData] = useState({
    title: '',
    company: '',
    location: '',
    is_remote: false,
    description: '',
    salary: '',
    apply_url: '',
    url: '',
    job_type: '',
    experience_level: '',
    is_active: true,
    tags: [],
    source: 'manual'
  });

  // Validation errors
  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (isEditMode) {
      fetchJobDetails();
    }
  }, [id]);

  const fetchJobDetails = async () => {
    try {
      const response = await axios.get(`${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${id}`);
      const jobData = response.data;
      
      setFormData({
        title: jobData.title || '',
        company: jobData.company || '',
        location: jobData.location || '',
        is_remote: jobData.is_remote || false,
        description: jobData.description || '',
        salary: jobData.salary || '',
        apply_url: jobData.apply_url || '',
        url: jobData.url || '',
        job_type: jobData.job_type || '',
        experience_level: jobData.experience_level || '',
        is_active: jobData.is_active !== false,
        tags: jobData.tags || [],
        source: jobData.source || 'manual'
      });
    } catch (error) {
      console.error('Error fetching job details:', error);
      showNotification('Failed to load job details', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const handleInputChange = (event) => {
    const { name, value, type, checked } = event.target;
    setFormData({
      ...formData,
      [name]: type === 'checkbox' ? checked : value
    });
    
    // Clear validation error when field is updated
    if (errors[name]) {
      setErrors({
        ...errors,
        [name]: null
      });
    }
  };

  const handleDescriptionChange = (value) => {
    setFormData({
      ...formData,
      description: value || ''
    });
    
    if (errors.description) {
      setErrors({
        ...errors,
        description: null
      });
    }
  };

  const handleTagsChange = (event, newValue) => {
    setFormData({
      ...formData,
      tags: newValue
    });
  };

  const handleAddTag = (event) => {
    if (event.key === 'Enter' && event.target.value) {
      const newTag = event.target.value.trim();
      if (newTag && !formData.tags.includes(newTag)) {
        setFormData({
          ...formData,
          tags: [...formData.tags, newTag]
        });
        event.target.value = '';
      }
    }
  };

  const scrapeJobPage = async () => {
    if (!formData.url) {
      showNotification('Please enter a job URL to scrape', 'error');
      return;
    }
    
    setIsLoading(true);
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/scrape`,
        { url: formData.url }
      );
      
      const scrapedJobData = response.data;
      setScrapedData(scrapedJobData);
      
      // Update form data with scraped values
      setFormData(prevData => ({
        ...prevData,
        title: scrapedJobData.title || prevData.title,
        company: scrapedJobData.company || prevData.company,
        location: scrapedJobData.location || prevData.location,
        description: scrapedJobData.description || prevData.description,
        salary: scrapedJobData.salary || prevData.salary,
        apply_url: scrapedJobData.apply_url || prevData.apply_url,
        tags: scrapedJobData.tags?.length ? scrapedJobData.tags : prevData.tags,
        job_type: scrapedJobData.job_type || prevData.job_type,
        source: 'scraped'
      }));
      
      showNotification('Job data scraped successfully!', 'success');
    } catch (error) {
      console.error('Error scraping job page:', error);
      showNotification('Failed to scrape job data', 'error');
    } finally {
      setIsLoading(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};
    
    if (!formData.title.trim()) {
      newErrors.title = 'Title is required';
    }
    
    if (!formData.company.trim()) {
      newErrors.company = 'Company is required';
    }
    
    if (!formData.description.trim()) {
      newErrors.description = 'Description is required';
    }
    
    if (formData.apply_url && !/^https?:\/\/.+/.test(formData.apply_url)) {
      newErrors.apply_url = 'Valid URL is required (https://...)';
    }
    
    if (formData.url && !/^https?:\/\/.+/.test(formData.url)) {
      newErrors.url = 'Valid URL is required (https://...)';
    }
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    
    if (!validateForm()) {
      showNotification('Please fix the errors in the form', 'error');
      return;
    }
    
    setIsSaving(true);
    try {
      if (isEditMode) {
        await axios.put(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs/${id}`,
          formData
        );
        showNotification('Job updated successfully!', 'success');
      } else {
        const response = await axios.post(
          `${process.env.REACT_APP_API_URL || 'http://localhost:8000'}/api/jobs`,
          formData
        );
        showNotification('Job created successfully!', 'success');
        // Navigate to the edit page of the newly created job
        navigate(`/admin/jobs/${response.data._id}`);
      }
    } catch (error) {
      console.error('Error saving job:', error);
      showNotification('Failed to save job', 'error');
    } finally {
      setIsSaving(false);
    }
  };

  const showNotification = (message, severity = 'success') => {
    setAlertMessage(message);
    setAlertSeverity(severity);
    setShowAlert(true);
  };

  const handleAlertClose = () => {
    setShowAlert(false);
  };

  if (isLoading) {
    return (
      <Container maxWidth="lg">
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 8 }}>
          <CircularProgress />
        </Box>
      </Container>
    );
  }

  return (
    <Container maxWidth="lg">
      <Box sx={{ py: 4 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
          <Typography variant="h4" component="h1">
            {isEditMode ? 'Edit Job' : 'Add New Job'}
          </Typography>
          <Button 
            component={Link} 
            to="/admin/jobs"
            startIcon={<ArrowBackIcon />}
          >
            Back to Jobs
          </Button>
        </Box>

        <Paper component="form" onSubmit={handleSubmit} sx={{ p: 3 }}>
          <Grid container spacing={3}>
            {/* URL Scraper section */}
            <Grid item xs={12}>
              <Box 
                sx={{ 
                  p: 2, 
                  mb: 3, 
                  border: '1px dashed', 
                  borderColor: 'divider',
                  borderRadius: 1,
                  bgcolor: 'action.hover'
                }}
              >
                <Typography variant="subtitle1" gutterBottom>
                  <LanguageIcon sx={{ verticalAlign: 'middle', mr: 1 }} />
                  Scrape job details from URL
                </Typography>
                <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                  <TextField
                    name="url"
                    label="Job Post URL"
                    placeholder="https://example.com/jobs/12345"
                    value={formData.url}
                    onChange={handleInputChange}
                    error={!!errors.url}
                    helperText={errors.url}
                    fullWidth
                    sx={{ mr: 2 }}
                  />
                  <Button
                    variant="contained"
                    color="secondary"
                    onClick={scrapeJobPage}
                    disabled={!formData.url || isLoading}
                  >
                    Scrape
                  </Button>
                </Box>
                <FormHelperText>
                  Enter a job post URL to automatically extract details
                </FormHelperText>
              </Box>
            </Grid>

            {/* Basic Information */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom>
                Basic Information
              </Typography>
              <Divider sx={{ mb: 2 }} />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                name="title"
                label="Job Title"
                value={formData.title}
                onChange={handleInputChange}
                error={!!errors.title}
                helperText={errors.title}
                required
                fullWidth
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                name="company"
                label="Company"
                value={formData.company}
                onChange={handleInputChange}
                error={!!errors.company}
                helperText={errors.company}
                required
                fullWidth
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                name="location"
                label="Location"
                value={formData.location}
                onChange={handleInputChange}
                fullWidth
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControlLabel
                control={
                  <Switch
                    name="is_remote"
                    checked={formData.is_remote}
                    onChange={handleInputChange}
                    color="primary"
                  />
                }
                label="Remote Job"
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="job-type-label">Job Type</InputLabel>
                <Select
                  labelId="job-type-label"
                  name="job_type"
                  value={formData.job_type}
                  onChange={handleInputChange}
                  label="Job Type"
                >
                  <MenuItem value=""><em>None</em></MenuItem>
                  {JOB_TYPES.map(type => (
                    <MenuItem key={type} value={type}>{type}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                name="salary"
                label="Salary"
                placeholder="e.g. $50,000 - $70,000 / year"
                value={formData.salary}
                onChange={handleInputChange}
                fullWidth
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <FormControl fullWidth>
                <InputLabel id="experience-level-label">Experience Level</InputLabel>
                <Select
                  labelId="experience-level-label"
                  name="experience_level"
                  value={formData.experience_level}
                  onChange={handleInputChange}
                  label="Experience Level"
                >
                  <MenuItem value=""><em>None</em></MenuItem>
                  {EXPERIENCE_LEVELS.map(level => (
                    <MenuItem key={level} value={level}>{level}</MenuItem>
                  ))}
                </Select>
              </FormControl>
            </Grid>

            <Grid item xs={12} md={6}>
              <TextField
                name="apply_url"
                label="Apply URL"
                placeholder="https://example.com/apply/12345"
                value={formData.apply_url}
                onChange={handleInputChange}
                error={!!errors.apply_url}
                helperText={errors.apply_url}
                fullWidth
              />
            </Grid>

            <Grid item xs={12}>
              <Autocomplete
                multiple
                freeSolo
                options={[]}
                value={formData.tags}
                onChange={handleTagsChange}
                renderTags={(value, getTagProps) =>
                  value.map((option, index) => (
                    <Chip 
                      variant="outlined" 
                      label={option} 
                      {...getTagProps({ index })} 
                    />
                  ))
                }
                renderInput={(params) => (
                  <TextField
                    {...params}
                    label="Tags"
                    placeholder="Add tags"
                    helperText="Press enter to add a new tag"
                    onKeyDown={handleAddTag}
                  />
                )}
              />
            </Grid>

            {/* Description */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Job Description
              </Typography>
              <Divider sx={{ mb: 2 }} />
              
              <InputLabel htmlFor="job-description" sx={{ mb: 1 }}>
                Description (Markdown supported)
              </InputLabel>
              <MDEditor
                value={formData.description}
                onChange={handleDescriptionChange}
                height={400}
              />
              {errors.description && (
                <FormHelperText error>{errors.description}</FormHelperText>
              )}
            </Grid>

            {/* Settings */}
            <Grid item xs={12}>
              <Typography variant="h6" gutterBottom sx={{ mt: 2 }}>
                Job Settings
              </Typography>
              <Divider sx={{ mb: 2 }} />
            </Grid>

            <Grid item xs={12}>
              <FormControlLabel
                control={
                  <Switch
                    name="is_active"
                    checked={formData.is_active}
                    onChange={handleInputChange}
                    color="primary"
                  />
                }
                label="Active (job will be visible on the site)"
              />
            </Grid>

            {/* Submit buttons */}
            <Grid item xs={12} sx={{ mt: 2, display: 'flex', justifyContent: 'flex-end' }}>
              <Button
                component={Link}
                to="/admin/jobs"
                startIcon={<CancelIcon />}
                sx={{ mr: 2 }}
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="contained"
                color="primary"
                startIcon={<SaveIcon />}
                disabled={isSaving}
              >
                {isSaving ? 'Saving...' : (isEditMode ? 'Update Job' : 'Create Job')}
              </Button>
            </Grid>
          </Grid>
        </Paper>
      </Box>

      <Snackbar 
        open={showAlert} 
        autoHideDuration={6000} 
        onClose={handleAlertClose}
        anchorOrigin={{ vertical: 'bottom', horizontal: 'center' }}
      >
        <Alert onClose={handleAlertClose} severity={alertSeverity} sx={{ width: '100%' }}>
          {alertMessage}
        </Alert>
      </Snackbar>
    </Container>
  );
};

export default JobForm; 