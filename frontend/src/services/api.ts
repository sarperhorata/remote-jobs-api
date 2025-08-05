import { getApiUrl } from '../utils/apiConfig';

// API response types
export interface FormAnalysisResponse {
  fields: Array<{
    name: string;
    type: string;
    required: boolean;
    label?: string;
    placeholder?: string;
  }>;
  formType: string;
  confidence: number;
}

export interface FormFillResponse {
  success: boolean;
  filledFields: number;
  errors?: string[];
}

export interface FormSubmitResponse {
  success: boolean;
  message: string;
  errors?: string[];
}

export interface BulkApplyResponse {
  task_id: string;
  status: string;
  total_jobs: number;
  estimated_completion: string;
}

export interface BulkApplyStatus {
  task_id: string;
  status: string;
  total_jobs: number;
  completed_jobs: number;
  successful_jobs: number;
  failed_jobs: number;
  in_progress_jobs: number;
  started_at: string;
  completed_at?: string;
  error?: string;
}

// Form Analysis API
export const analyzeForm = async (jobUrl: string, jobTitle: string, companyName: string): Promise<FormAnalysisResponse> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const response = await fetch(`${apiUrl}/api/v1/bulk-apply/analyze-form`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        job_url: jobUrl,
        job_title: jobTitle,
        company_name: companyName
      })
    });

    if (!response.ok) {
      throw new Error(`Form analysis failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Form analysis error:', error);
    throw error;
  }
};

// Form Fill API
export const fillForm = async (
  jobUrl: string,
  formData: Record<string, any>,
  userProfile: Record<string, any>
): Promise<FormFillResponse> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const response = await fetch(`${apiUrl}/api/v1/bulk-apply/fill-form`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        job_url: jobUrl,
        form_data: formData,
        user_profile: userProfile
      })
    });

    if (!response.ok) {
      throw new Error(`Form fill failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Form fill error:', error);
    throw error;
  }
};

// Form Submit API
export const submitForm = async (
  jobUrl: string,
  formData: Record<string, any>
): Promise<FormSubmitResponse> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const response = await fetch(`${apiUrl}/api/v1/bulk-apply/submit-form`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        job_url: jobUrl,
        form_data: formData
      })
    });

    if (!response.ok) {
      throw new Error(`Form submission failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Form submission error:', error);
    throw error;
  }
};

// Start Bulk Apply API
export const startBulkApply = async (
  jobs: Array<{
    id: string;
    title: string;
    company: string;
    url: string;
    location?: string;
    salary?: string;
  }>,
  formConfig: Record<string, any>,
  rateLimit: number = 2000,
  maxRetries: number = 3
): Promise<BulkApplyResponse> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const response = await fetch(`${apiUrl}/api/v1/bulk-apply/start-bulk-apply`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        jobs,
        form_config: formConfig,
        rate_limit: rateLimit,
        max_retries: maxRetries
      })
    });

    if (!response.ok) {
      throw new Error(`Bulk apply start failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Bulk apply start error:', error);
    throw error;
  }
};

// Get Bulk Apply Status API
export const getBulkApplyStatus = async (taskId: string): Promise<BulkApplyStatus> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const response = await fetch(`${apiUrl}/api/v1/bulk-apply/status/${taskId}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Status check failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Status check error:', error);
    throw error;
  }
};

// Cancel Bulk Apply API
export const cancelBulkApply = async (taskId: string): Promise<{ success: boolean; message: string }> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const response = await fetch(`${apiUrl}/api/v1/bulk-apply/cancel/${taskId}`, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`Cancel failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Cancel error:', error);
    throw error;
  }
};

// Get Bulk Apply History API
export const getBulkApplyHistory = async (limit: number = 10, offset: number = 0): Promise<{
  history: BulkApplyStatus[];
  total: number;
}> => {
  try {
    const apiUrl = await getApiUrl();
    const token = localStorage.getItem('token');

    const response = await fetch(`${apiUrl}/api/v1/bulk-apply/history?limit=${limit}&offset=${offset}`, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });

    if (!response.ok) {
      throw new Error(`History fetch failed: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('History fetch error:', error);
    throw error;
  }
};

// Legacy API functions for backward compatibility
export const submitBulkApplication = async (jobData: any): Promise<any> => {
  // This is a legacy function for backward compatibility
  return submitForm(jobData.url, jobData.formData);
};

export const getApplicationStatus = async (taskId: string): Promise<any> => {
  // This is a legacy function for backward compatibility
  return getBulkApplyStatus(taskId);
}; 