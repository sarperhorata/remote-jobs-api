import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Card,
  CardContent,
  CardActions,
  Typography,
  Box,
  Chip,
  IconButton,
  Tooltip,
  Divider,
  Avatar,
  Skeleton
} from '@mui/material';
import {
  LocationOn as LocationIcon,
  Work as WorkIcon,
  AttachMoney as SalaryIcon,
  Schedule as ScheduleIcon,
  BookmarkBorder as BookmarkBorderIcon,
  Bookmark as BookmarkIcon,
  OpenInNew as OpenInNewIcon
} from '@mui/icons-material';
import { format, formatDistanceToNow } from 'date-fns';
import axios from 'axios';

// Helper function to generate company logo (for companies without logos)
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

const getCompanyInitials = (companyName) => {
  if (!companyName) return '?';
  return companyName
    .split(' ')
    .slice(0, 2)
    .map(word => word[0])
    .join('')
    .toUpperCase();
};

// Loading skeleton for JobCard
export const JobCardSkeleton = () => (
  <Card variant="outlined" sx={{ mb: 2, borderRadius: 2 }}>
    <CardContent>
      <Box sx={{ display: 'flex', gap: 2 }}>
        <Skeleton variant="rectangular" width={60} height={60} sx={{ borderRadius: 1 }} />
        <Box sx={{ width: '100%' }}>
          <Skeleton variant="text" width="60%" height={28} />
          <Skeleton variant="text" width="40%" height={24} />
          <Box sx={{ display: 'flex', gap: 1, mt: 1 }}>
            <Skeleton variant="rectangular" width={90} height={24} sx={{ borderRadius: 16 }} />
            <Skeleton variant="rectangular" width={90} height={24} sx={{ borderRadius: 16 }} />
          </Box>
        </Box>
      </Box>
      <Skeleton variant="text" sx={{ mt: 2 }} />
      <Skeleton variant="text" width="80%" />
    </CardContent>
    <Divider />
    <CardActions sx={{ justifyContent: 'space-between' }}>
      <Skeleton variant="rectangular" width={90} height={28} sx={{ borderRadius: 16 }} />
      <Box sx={{ display: 'flex' }}>
        <Skeleton variant="circular" width={36} height={36} sx={{ mx: 0.5 }} />
        <Skeleton variant="circular" width={36} height={36} />
      </Box>
    </CardActions>
  </Card>
);

const JobCard = ({ job, isSaved, onToggleSave, showActions = true }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  
  const handleToggleSave = async (e) => {
    e.stopPropagation();
    if (loading) return;
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login?redirect=' + encodeURIComponent('/jobs'));
        return;
      }
      
      onToggleSave(job._id);
    } catch (error) {
      console.error('Error toggling saved job:', error);
    } finally {
      setLoading(false);
    }
  };
  
  const handleCardClick = () => {
    navigate(`/jobs/${job._id}`);
  };
  
  const handleExternalLinkClick = (e) => {
    e.stopPropagation();
    window.open(job.url, '_blank', 'noopener,noreferrer');
  };
  
  const formatPostedDate = (dateString) => {
    try {
      const date = new Date(dateString);
      const now = new Date();
      const diffDays = Math.floor((now - date) / (1000 * 60 * 60 * 24));
      
      if (diffDays < 30) {
        return formatDistanceToNow(date, { addSuffix: true });
      }
      return format(date, 'MMM d, yyyy');
    } catch (e) {
      return 'Date not available';
    }
  };
  
  // Format salary for display
  const formatSalary = (salary) => {
    if (!salary) return null;
    
    // Try to return the salary as provided if it looks like a formatted string
    if (typeof salary === 'string' && (salary.includes('$') || salary.includes('€') || salary.includes('£'))) {
      return salary;
    }
    
    // Otherwise, try to format it
    try {
      const salaryNum = parseFloat(salary);
      if (isNaN(salaryNum)) return salary;
      
      return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD',
        maximumFractionDigits: 0
      }).format(salaryNum);
    } catch (e) {
      return salary;
    }
  };
  
  const logoColor = stringToColor(job.company || 'Company');
  
  return (
    <Card 
      variant="outlined" 
      sx={{ 
        mb: 2, 
        cursor: 'pointer',
        transition: 'all 0.2s',
        borderRadius: 2,
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: 3
        }
      }}
      onClick={handleCardClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', gap: 2 }}>
          {job.company_logo ? (
            <Avatar 
              src={job.company_logo} 
              alt={job.company} 
              sx={{ width: 60, height: 60, borderRadius: 1 }}
            />
          ) : (
            <Avatar 
              sx={{ 
                width: 60, 
                height: 60, 
                borderRadius: 1,
                bgcolor: logoColor,
                color: 'white',
                fontSize: '1.2rem',
                fontWeight: 'bold'
              }}
            >
              {getCompanyInitials(job.company)}
            </Avatar>
          )}
          
          <Box sx={{ width: '100%' }}>
            <Typography variant="h6" component="h2" noWrap>
              {job.title}
            </Typography>
            
            <Typography variant="subtitle1" color="text.secondary" noWrap>
              {job.company}
            </Typography>
            
            <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
              {job.is_remote && (
                <Chip 
                  size="small" 
                  color="primary" 
                  label="Remote" 
                  variant="outlined"
                />
              )}
              
              {job.location && (
                <Chip 
                  size="small"
                  icon={<LocationIcon fontSize="small" />}
                  label={job.location}
                  variant="outlined"
                />
              )}
              
              {job.job_type && (
                <Chip 
                  size="small"
                  icon={<WorkIcon fontSize="small" />}
                  label={job.job_type}
                  variant="outlined"
                />
              )}
              
              {job.salary && (
                <Chip 
                  size="small"
                  icon={<SalaryIcon fontSize="small" />}
                  label={formatSalary(job.salary)}
                  variant="outlined"
                  color="success"
                />
              )}
            </Box>
          </Box>
        </Box>
        
        <Typography variant="body2" color="text.secondary" sx={{ mt: 2, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
          {job.description ? job.description.substring(0, 150) + '...' : 'No description available.'}
        </Typography>
        
        {job.tags && job.tags.length > 0 && (
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5, mt: 1 }}>
            {job.tags.slice(0, 5).map((tag, index) => (
              <Chip 
                key={index}
                label={tag}
                size="small"
                onClick={(e) => {
                  e.stopPropagation();
                  navigate(`/jobs?search=${encodeURIComponent(tag)}`);
                }}
                sx={{ fontSize: '0.7rem' }}
              />
            ))}
            {job.tags.length > 5 && (
              <Chip 
                label={`+${job.tags.length - 5} more`}
                size="small"
                variant="outlined"
                sx={{ fontSize: '0.7rem' }}
              />
            )}
          </Box>
        )}
      </CardContent>
      
      <Divider />
      
      <CardActions sx={{ justifyContent: 'space-between' }}>
        <Chip 
          icon={<ScheduleIcon fontSize="small" />}
          label={job.date_posted ? formatPostedDate(job.date_posted) : 'Date not available'}
          size="small"
          variant="outlined"
        />
        
        {showActions && (
          <Box>
            {isSaved !== undefined && (
              <Tooltip title={isSaved ? "Remove from saved" : "Save job"}>
                <IconButton onClick={handleToggleSave} disabled={loading}>
                  {isSaved ? <BookmarkIcon color="primary" /> : <BookmarkBorderIcon />}
                </IconButton>
              </Tooltip>
            )}
            
            {job.url && (
              <Tooltip title="Open original job posting">
                <IconButton onClick={handleExternalLinkClick}>
                  <OpenInNewIcon />
                </IconButton>
              </Tooltip>
            )}
          </Box>
        )}
      </CardActions>
    </Card>
  );
};

export default JobCard; 