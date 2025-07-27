// API Mock Data
export const mockJobs = [
  {
    id: 1,
    title: 'Software Engineer',
    company: 'Tech Corp',
    location: 'Remote',
    salary: '$80,000 - $120,000',
    description: 'We are looking for a talented software engineer...',
    requirements: ['React', 'TypeScript', 'Node.js'],
    posted_date: '2024-01-15',
    work_type: 'remote',
    job_type: 'full-time',
    experience_level: 'mid-level'
  },
  {
    id: 2,
    title: 'Frontend Developer',
    company: 'Startup Inc',
    location: 'New York',
    salary: '$70,000 - $100,000',
    description: 'Join our growing team...',
    requirements: ['React', 'JavaScript', 'CSS'],
    posted_date: '2024-01-14',
    work_type: 'hybrid',
    job_type: 'full-time',
    experience_level: 'junior'
  }
];

export const mockJob = mockJobs[0];

export const mockUser = {
  id: 1,
  email: 'test@example.com',
  name: 'Test User',
  isAuthenticated: true
};

export const mockApiResponse = {
  jobs: mockJobs,
  total: 2,
  total_pages: 1
};

export const mockErrorResponse = {
  error: 'Something went wrong',
  status: 500
};

// Mock fetch responses
export const setupMockFetch = (response: any, status: number = 200) => {
  (global.fetch as jest.Mock).mockResolvedValue({
    ok: status >= 200 && status < 300,
    status,
    json: async () => response,
    text: async () => JSON.stringify(response)
  });
};

export const setupMockFetchError = (error: string = 'Network error') => {
  (global.fetch as jest.Mock).mockRejectedValue(new Error(error));
};