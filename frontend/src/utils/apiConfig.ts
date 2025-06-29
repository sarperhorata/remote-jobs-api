// Dinamik API URL detection sistemi
// Backend için 8xxx portları (8001, 8000, 8002, vb.) kontrol eder
// Frontend için 5xxx portları ile çalışabilir

interface PortConfig {
  backendPorts: number[];
  frontendPorts: number[];
}

const portConfig: PortConfig = {
  backendPorts: [8002, 8001, 8000, 8003, 8004], // 8002'yi ilk sıraya aldım - active port
  frontendPorts: [3001, 3000, 5000, 5001, 5173], // Frontend için öncelik sırası
};

// API URL cache - Global değişkenler
let cachedApiUrl: string | null = null;
let apiUrlPromise: Promise<string> | null = null;

// Sync API Base URL - fallback for components that need immediate access
export const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8001';

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
    let apiUrl = process.env.REACT_APP_API_URL;
    console.log('✅ Using environment variable:', apiUrl);
    
    // Trailing slash'i temizle
    apiUrl = apiUrl.replace(/\/$/, '');
    
    // Eğer zaten /api/v1 ile bitiyorsa olduğu gibi döndür
    if (apiUrl.endsWith('/api/v1')) {
      return apiUrl;
    }
    // Eğer /api ile bitiyorsa sadece /v1 ekle
    if (apiUrl.endsWith('/api')) {
      return `${apiUrl}/v1`;
    }
    // Hiçbiri yoksa /api/v1 ekle
    return `${apiUrl}/api/v1`;
  }

  // Test environment check - force port 8000 for tests
  if (process.env.NODE_ENV === 'test') {
    console.log('🧪 Test mode - forcing port 8000');
    return 'http://localhost:8000/api/v1';
  }

  // Backend portlarını sırayla test et
  for (const port of portConfig.backendPorts) {
    try {
      console.log(`🔍 Testing backend on port ${port}...`);
      // /health endpoint'i /api/v1 dışında
      const healthCheckUrl = `http://localhost:${port}/health`;
      const response = await fetch(healthCheckUrl, {
        method: 'GET',
        signal: AbortSignal.timeout(2000), // 2 saniye timeout
      });
      
      if (response.ok) {
        console.log(`✅ Backend detected on port ${port}`);
        return `http://localhost:${port}/api/v1`;
      }
    } catch (error: any) {
      // Port ulaşılabilir değil, bir sonrakini dene
      console.log(`❌ Backend not found on port ${port}:`, error.message);
    }
  }

  // Hiçbir port çalışmıyorsa varsayılan port
  const fallbackUrl = 'http://localhost:8001/api/v1';
  console.warn(`⚠️ No backend found, using default URL: ${fallbackUrl}`);
  return fallbackUrl;
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
    cachedApiUrl = 'http://localhost:8001/api/v1'; // Fallback
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
    // API URL'den base URL'i çıkar ve /health ekle
    const baseUrl = url.replace(/\/api\/v1$/, '');
    const healthUrl = `${baseUrl}/health`;
    
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