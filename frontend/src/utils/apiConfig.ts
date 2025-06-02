// Dinamik API URL detection sistemi
// Backend için 8xxx portları (8000, 8001, 8002, vb.) kontrol eder
// Frontend için 5xxx portları ile çalışabilir

interface PortConfig {
  backendPorts: number[];
  frontendPorts: number[];
}

const portConfig: PortConfig = {
  backendPorts: [8001, 8000, 8002, 8003, 8004], // Backend için öncelik sırası
  frontendPorts: [3001, 3000, 5000, 5001, 5173], // Frontend için öncelik sırası
};

// Backend port detection
const detectBackendPort = async (): Promise<string> => {
  console.log('🔍 Starting backend port detection...');
  
  // Environment variable varsa onu kullan
  if (process.env.REACT_APP_API_URL) {
    console.log('✅ Using environment variable:', process.env.REACT_APP_API_URL);
    return process.env.REACT_APP_API_URL;
  }

  // Test environment check
  if (process.env.NODE_ENV === 'test') {
    console.log('🧪 Test mode - using port 8001');
    return 'http://localhost:8001/api';
  }

  // Backend portlarını sırayla test et
  for (const port of portConfig.backendPorts) {
    try {
      console.log(`🔍 Testing backend on port ${port}...`);
      const response = await fetch(`http://localhost:${port}/health`, {
        method: 'GET',
        signal: AbortSignal.timeout(2000), // 2 saniye timeout
      });
      
      if (response.ok) {
        console.log(`✅ Backend detected on port ${port}`);
        return `http://localhost:${port}/api`;
      }
    } catch (error) {
      // Port ulaşılabilir değil, bir sonrakini dene
      console.log(`❌ Backend not found on port ${port}:`, error.message);
    }
  }

  // Hiçbir port çalışmıyorsa varsayılan port
  console.warn('⚠️ No backend found, using default port 8001');
  return 'http://localhost:8001/api';
};

// API URL cache
let cachedApiUrl: string | null = null;
let apiUrlPromise: Promise<string> | null = null;

// Production API configuration for Buzz2Remote
// Backend is deployed on Render.com

const PRODUCTION_API_URL = 'https://remote-jobs-api-k9v1.onrender.com/api';

// Simple and direct API URL - no complex port detection needed in production
export const getApiUrl = async (): Promise<string> => {
  // Always use production URL
  return PRODUCTION_API_URL;
};

// For development, you can uncomment this and use localhost
// const DEVELOPMENT_API_URL = 'http://localhost:8001/api';

// Manuel cache temizleme (gerektiğinde kullan)
export const clearApiUrlCache = () => {
  console.log('🧹 Clearing API URL cache');
  cachedApiUrl = null;
  apiUrlPromise = null;
};

// Force clear cache on first load
if (typeof window !== 'undefined') {
  console.log('🔄 Force clearing cache on page load');
  clearApiUrlCache();
}

// Development/Production mode detection
export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = process.env.NODE_ENV === 'production';
export const isTest = process.env.NODE_ENV === 'test';

// Current frontend port detection
export const getCurrentPort = (): number => {
  const port = parseInt(window.location.port);
  return port || (window.location.protocol === 'https:' ? 443 : 80);
};

// Backend health check
export const checkBackendHealth = async (apiUrl?: string): Promise<boolean> => {
  try {
    const url = apiUrl || await getApiUrl();
    const healthUrl = url.replace('/api', '/health');
    
    const response = await fetch(healthUrl, {
      method: 'GET',
      signal: AbortSignal.timeout(5000),
    });
    
    return response.ok;
  } catch (error) {
    console.error('Backend health check failed:', error);
    return false;
  }
};

export default {
  getApiUrl,
  clearApiUrlCache,
  checkBackendHealth,
  getCurrentPort,
  isDevelopment,
  isProduction,
  isTest,
  PRODUCTION_API_URL
}; 