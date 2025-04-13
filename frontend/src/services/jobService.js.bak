import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

/**
 * Service for handling all job-related API calls
 */
const jobService = {
  /**
   * Fetch jobs with filtering and pagination
   * @param {Object} filters - Filters to apply (search, location, jobType, etc.)
   * @param {Number} page - Page number
   * @param {Number} limit - Number of jobs per page
   * @returns {Promise} - Promise with job data
   */
  async fetchJobs(filters = {}, page = 1, limit = 10) {
    try {
      const params = { ...filters, page, limit };
      const response = await axios.get(`${API_URL}/jobs`, { params });
      return response.data;
    } catch (error) {
      console.error('Error fetching jobs:', error);
      throw error;
    }
  },

  /**
   * Fetch a single job by ID
   * @param {String} jobId - The ID of the job to fetch
   * @returns {Promise} - Promise with job data
   */
  async fetchJobById(jobId) {
    try {
      const response = await axios.get(`${API_URL}/jobs/${jobId}`);
      return response.data;
    } catch (error) {
      console.error(`Error fetching job with ID ${jobId}:`, error);
      throw error;
    }
  },

  /**
   * Fetch similar jobs based on skills for a given job
   * @param {String} jobId - The ID of the reference job
   * @param {Number} limit - Maximum number of similar jobs to return
   * @returns {Promise} - Promise with similar jobs data
   */
  async fetchSimilarJobs(jobId, limit = 4) {
    try {
      const response = await axios.get(`${API_URL}/jobs/${jobId}/similar`, {
        params: { limit }
      });
      return response.data;
    } catch (error) {
      console.error(`Error fetching similar jobs for job ID ${jobId}:`, error);
      throw error;
    }
  },

  /**
   * Save a job to the user's saved jobs
   * @param {String} jobId - The ID of the job to save
   * @returns {Promise} - Promise with save result
   */
  async saveJob(jobId) {
    try {
      // Get authentication token
      const token = localStorage.getItem('token');
      
      if (!token) {
        // If no token, save to local storage instead
        const savedJobs = JSON.parse(localStorage.getItem('savedJobs') || '[]');
        
        // Check if job is already saved
        if (!savedJobs.some(job => job.id === jobId)) {
          // Get job details to save
          const jobDetails = await this.fetchJobById(jobId);
          savedJobs.push({
            id: jobId,
            title: jobDetails.title,
            company: jobDetails.company,
            location: jobDetails.location,
            savedAt: new Date().toISOString()
          });
          localStorage.setItem('savedJobs', JSON.stringify(savedJobs));
        }
        
        return { success: true };
      }
      
      // If token exists, use API
      const response = await axios.post(
        `${API_URL}/jobs/${jobId}/save`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error(`Error saving job ${jobId}:`, error);
      throw error;
    }
  },

  /**
   * Remove a job from user's saved jobs
   * @param {String} jobId - The ID of the job to remove
   * @returns {Promise} - Promise with remove result
   */
  async removeSavedJob(jobId) {
    try {
      // Get authentication token
      const token = localStorage.getItem('token');
      
      if (!token) {
        // If no token, remove from local storage
        const savedJobs = JSON.parse(localStorage.getItem('savedJobs') || '[]');
        const updatedSavedJobs = savedJobs.filter(job => job.id !== jobId);
        localStorage.setItem('savedJobs', JSON.stringify(updatedSavedJobs));
        return { success: true };
      }
      
      // If token exists, use API
      const response = await axios.delete(
        `${API_URL}/jobs/${jobId}/save`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error(`Error removing saved job ${jobId}:`, error);
      throw error;
    }
  },

  /**
   * Get all saved jobs
   * @returns {Promise} - Promise with saved jobs data
   */
  async getSavedJobs() {
    try {
      // Get authentication token
      const token = localStorage.getItem('token');
      
      if (!token) {
        // If no token, get from local storage
        const savedJobs = JSON.parse(localStorage.getItem('savedJobs') || '[]');
        return savedJobs;
      }
      
      // If token exists, use API
      const response = await axios.get(
        `${API_URL}/jobs/saved`,
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error('Error fetching saved jobs:', error);
      throw error;
    }
  },

  /**
   * Apply for a job
   * @param {String} jobId - The ID of the job to apply for
   * @returns {Promise} - Promise with application result
   */
  async applyForJob(jobId) {
    try {
      // Get authentication token
      const token = localStorage.getItem('token');
      
      if (!token) {
        throw new Error('Authentication required to apply for jobs');
      }
      
      const response = await axios.post(
        `${API_URL}/jobs/${jobId}/apply`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      return response.data;
    } catch (error) {
      console.error(`Error applying for job ${jobId}:`, error);
      throw error;
    }
  }
};

export default jobService; 