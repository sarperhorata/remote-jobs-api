// Dinamik API URL detection sistemi
// Backend için 8xxx portları (8001, 8000, 8002, vb.) kontrol eder
// Frontend için 5xxx portları ile çalışabilir

interface PortConfig {
  backendPorts: number[];
  frontendPorts: number[];
}

const portConfig: PortConfig = {
  backendPorts: [8001, 8000, 8002, 8003, 8004], // Backend için öncelik sırası
  frontendPorts: [3001, 3000, 5000, 5001, 5173], // Frontend için öncelik sırası
};

// API URL cache - Global değişkenler
let cachedApiUrl: string | null = null;
let apiUrlPromise: Promise<string> | null = null;

// Cache temizleme fonksiyonu
export const clearApiUrlCache = () => {
  console.log('🧹 Clearing API URL cache');
  cachedApiUrl = null;
  apiUrlPromise = null;
};

// Backend port detection
const detectBackendPort = async (): Promise<string> => {
  console.log('🔍 Starting backend port detection...');
  
  // Environment variable varsa onu kullan
  if (process.env.REACT_APP_API_URL) {
    console.log('✅ Using environment variable:', process.env.REACT_APP_API_URL);
    return process.env.REACT_APP_API_URL;
  }

  // Test environment check - force port 8001
  if (process.env.NODE_ENV === 'test') {
    console.log('🧪 Test mode - forcing port 8001');
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
    } catch (error: any) {
      // Port ulaşılabilir değil, bir sonrakini dene
      console.log(`❌ Backend not found on port ${port}:`, error.message);
    }
  }

  // Hiçbir port çalışmıyorsa varsayılan port
  console.warn('⚠️ No backend found, using default port 8001');
  return 'http://localhost:8001/api';
};

export const getApiUrl = async (): Promise<string> => {
  console.log('📡 getApiUrl called, cachedApiUrl:', cachedApiUrl);
  
  // Test ortamında her zaman cache'i temizle
  if (process.env.NODE_ENV === 'test') {
    console.log('🧪 Test mode - clearing cache for fresh detection');
    clearApiUrlCache();
  }
  
  // Cache varsa onu kullan
  if (cachedApiUrl) {
    console.log('📋 Using cached API URL:', cachedApiUrl);
    return cachedApiUrl;
  }

  // Zaten bir detection çalışıyorsa aynı promise'i bekle
  if (apiUrlPromise) {
    console.log('⏳ Detection already in progress, waiting...');
    return apiUrlPromise;
  }

  // Yeni detection başlat
  console.log('🚀 Starting new detection...');
  apiUrlPromise = detectBackendPort();
  
  try {
    cachedApiUrl = await apiUrlPromise;
    console.log('✅ Detection complete, cached URL:', cachedApiUrl);
    return cachedApiUrl;
  } catch (error) {
    console.error('❌ Backend detection failed:', error);
    cachedApiUrl = 'http://localhost:8001/api'; // Fallback
    console.log('🔄 Using fallback URL:', cachedApiUrl);
    return cachedApiUrl;
  } finally {
    apiUrlPromise = null; // Promise'i temizle
  }
};

// Development/Production mode detection
export const isDevelopment = process.env.NODE_ENV === 'development';
export const isProduction = process.env.NODE_ENV === 'production';
export const isTest = process.env.NODE_ENV === 'test';

// Current frontend port detection
export const getCurrentPort = (): number => {
  if (typeof window === 'undefined') return 3000; // SSR or test environment
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

// Force cache temizleme - sadece gerekli durumlarda
if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'test') {
  console.log('🔄 Initial page load - clearing API URL cache');
  clearApiUrlCache();
}

// Test ortamında export edilen konfigürasyon objesi
const apiConfig = {
  getApiUrl,
  clearApiUrlCache,
  checkBackendHealth,
  getCurrentPort,
  isDevelopment,
  isProduction,
  isTest,
};

export default apiConfig; 