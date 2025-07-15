// Dinamik API URL detection sistemi
// Backend için 8xxx portları (8001, 8000, 8002, vb.) kontrol eder
// Frontend için 5xxx portları ile çalışabilir

interface PortConfig {
  backendPorts: number[];
  frontendPorts: number[];
}

const portConfig: PortConfig = {
  backendPorts: [8001, 8002, 8000, 8003, 8004], // 8001'i ilk sıraya aldım - active port
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

// Debug bilgilerini göstermek için
const logApiDetection = (message: string, data?: any) => {
  console.log(`🔗 [API Config] ${message}`, data || '');
};

// Backend port detection
const detectBackendPort = async (): Promise<string> => {
  logApiDetection('Starting backend port detection...');
  
  // Environment variable varsa ama yanlış port gösteriyorsa düzelt
  if (process.env.REACT_APP_API_URL) {
    let apiUrl = process.env.REACT_APP_API_URL;
    logApiDetection('Found environment variable:', apiUrl);
    
    // Trailing slash'i temizle
    apiUrl = apiUrl.replace(/\/$/, '');
    
    // /api/v1 veya /api kısmını kaldır - sadece base URL döndür
    apiUrl = apiUrl.replace(/\/api\/v1$/, '').replace(/\/api$/, '');
    
    return apiUrl;
  }

  // Test environment check - force port 8000 for tests
  if (process.env.NODE_ENV === 'test') {
    logApiDetection('Test mode - forcing port 8000');
    return 'http://localhost:8000';
  }

  // Backend portlarını sırayla test et
  for (const port of portConfig.backendPorts) {
    try {
      logApiDetection(`Testing backend on port ${port}...`);
      // /health endpoint'i /api/v1 dışında
      const healthCheckUrl = `http://localhost:${port}/health`;
      const response = await fetch(healthCheckUrl, {
        method: 'GET',
        signal: AbortSignal.timeout(3000), // 3 saniye timeout
      });
      
      if (response.ok) {
        const healthData = await response.json();
        logApiDetection(`✅ Backend detected on port ${port}`, healthData);
        return `http://localhost:${port}`;
      }
      logApiDetection(`❌ Port ${port} returned status ${response.status}`);
    } catch (error: any) {
      // Port ulaşılabilir değil, bir sonrakini dene
      logApiDetection(`❌ Backend not found on port ${port}:`, error.message);
    }
  }

  // Hiçbir port çalışmıyorsa varsayılan port
  const fallbackUrl = 'http://localhost:8001';
  logApiDetection(`⚠️ No backend found, using default URL: ${fallbackUrl}`);
  return fallbackUrl;
};

export const getApiUrl = async (): Promise<string> => {
  if (process.env.NODE_ENV === 'production') {
    // Production'da her zaman canlı API adresini kullan
    return 'https://buzz2remote.com';
  }

  // Development ortamında, çalışan portu dinamik olarak bul
  if (cachedApiUrl) {
    logApiDetection('Returning cached API URL:', cachedApiUrl);
    return cachedApiUrl;
  }

  if (apiUrlPromise) {
    logApiDetection('Waiting for existing API detection promise...');
    return apiUrlPromise;
  }

  apiUrlPromise = detectBackendPort();
  
  try {
    cachedApiUrl = await apiUrlPromise;
    return cachedApiUrl;
  } finally {
    apiUrlPromise = null;
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

// Force cache temizleme - development'ta her sayfa yüklemesinde
if (typeof window !== 'undefined') {
  console.log('🔄 Page load - forcing cache clear for fresh API detection');
  clearApiUrlCache();
  
  // Development'ta immediate test yapıp sonucu logla
  if (process.env.NODE_ENV === 'development') {
    setTimeout(async () => {
      try {
        const detectedUrl = await getApiUrl();
        console.log('🎯 API URL detected successfully:', detectedUrl);
        
        // Test API endpoint
        const testResponse = await fetch(`${detectedUrl}/api/v1/jobs/job-titles/search?q=test&limit=1`);
        if (testResponse.ok) {
          console.log('✅ Autocomplete API endpoint working!');
        } else {
          console.error('❌ Autocomplete API endpoint failed, status:', testResponse.status);
        }
      } catch (error) {
        console.error('❌ API detection failed:', error);
      }
    }, 1000);
  }
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