import axios from 'axios';

const baseURL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Create an axios instance with default config
const api = axios.create({
  baseURL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor for authentication
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// API endpoints
export const jobsApi = {
  getAllJobs: async () => {
    const response = await api.get('/jobs');
    return response.data;
  },
  
  getJobById: async (id: string) => {
    const response = await api.get(`/jobs/${id}`);
    return response.data;
  },
  
  searchJobs: async (searchTerm: string) => {
    const response = await api.get(`/jobs/search?q=${encodeURIComponent(searchTerm)}`);
    return response.data;
  },
};

export const authApi = {
  login: async (username: string, password: string) => {
    const response = await api.post('/token', { username, password });
    return response.data;
  },
  
  register: async (email: string, username: string, password: string) => {
    const response = await api.post('/users', { email, username, password });
    return response.data;
  },
  
  getApiKey: async () => {
    const response = await api.post('/api-keys');
    return response.data;
  },
};

export const systemApi = {
  getStatus: async () => {
    const response = await api.get('/health');
    return response.data;
  },
};

export default api; 