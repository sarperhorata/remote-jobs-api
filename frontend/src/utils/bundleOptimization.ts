/**
 * Bundle Optimization Utilities
 * Provides helpers for dynamic imports, preloading, and bundle optimization
 */

// Dynamic import wrapper with retry mechanism
export const dynamicImport = async <T = any>(
  importFn: () => Promise<{ default: T }>,
  retries = 3,
  delay = 1000
): Promise<T> => {
  try {
    const module = await importFn();
    return module.default;
  } catch (error) {
    if (retries > 0) {
      await new Promise(resolve => setTimeout(resolve, delay));
      return dynamicImport(importFn, retries - 1, delay * 2);
    }
    throw error;
  }
};

// Preload a module
export const preloadModule = (importFn: () => Promise<any>): Promise<any> => {
  if (typeof window !== 'undefined' && 'requestIdleCallback' in window) {
    return new Promise((resolve) => {
      window.requestIdleCallback(() => {
        resolve(importFn());
      });
    });
  }
  return importFn();
};

// Preload critical route modules
export const preloadCriticalRoutes = () => {
  if (typeof window === 'undefined') return;

  // Preload critical pages that are likely to be visited
  const criticalRoutes = [
    () => import('../pages/Home'),
    () => import('../pages/JobSearchResults'),
    () => import('../pages/JobDetailPage'),
    () => import('../pages/Login'),
  ];

  criticalRoutes.forEach(route => {
    preloadModule(route).catch(() => {
      // Silently handle preload errors
    });
  });
};

// Component registry for dynamic loading
class ComponentRegistry {
  private components = new Map<string, Promise<any>>();
  private loadedComponents = new Set<string>();

  register(name: string, importFn: () => Promise<any>) {
    if (!this.components.has(name)) {
      this.components.set(name, importFn());
    }
  }

  async load(name: string): Promise<any> {
    const component = this.components.get(name);
    if (!component) {
      throw new Error(`Component ${name} not registered`);
    }

    const loadedComponent = await component;
    this.loadedComponents.add(name);
    return loadedComponent.default;
  }

  isLoaded(name: string): boolean {
    return this.loadedComponents.has(name);
  }

  getLoadedComponents(): string[] {
    return Array.from(this.loadedComponents);
  }
}

export const componentRegistry = new ComponentRegistry();

// Resource hints for better loading
export const addResourceHint = (url: string, type: 'preload' | 'prefetch' | 'preconnect') => {
  if (typeof document === 'undefined') return;

  const link = document.createElement('link');
  link.rel = type;
  link.href = url;
  
  if (type === 'preload') {
    link.as = 'script';
  }
  
  document.head.appendChild(link);
};

// Lazy image loading with intersection observer
export const createLazyImageLoader = () => {
  if (typeof window === 'undefined' || !('IntersectionObserver' in window)) {
    return { observe: () => {}, disconnect: () => {} };
  }

  const imageObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        const img = entry.target as HTMLImageElement;
        const src = img.dataset.src;
        
        if (src) {
          img.src = src;
          img.classList.remove('lazy');
          imageObserver.unobserve(img);
        }
      }
    });
  }, {
    threshold: 0.1,
    rootMargin: '50px'
  });

  return {
    observe: (img: HTMLImageElement) => imageObserver.observe(img),
    disconnect: () => imageObserver.disconnect()
  };
};

// Bundle size tracker
export const bundleTracker = {
  trackPageLoad: (pageName: string) => {
    if (typeof window === 'undefined') return;
    
    const startTime = performance.now();
    
    window.addEventListener('load', () => {
      const loadTime = performance.now() - startTime;
      
      // Send to analytics (replace with your analytics service)
      console.log(`Page ${pageName} loaded in ${loadTime.toFixed(2)}ms`);
      
      // Track bundle size if available
      if ('getEntriesByType' in performance) {
        const resources = performance.getEntriesByType('navigation') as PerformanceNavigationTiming[];
        if (resources.length > 0) {
          const { transferSize, encodedBodySize, decodedBodySize } = resources[0];
          console.log('Bundle size metrics:', {
            transferSize,
            encodedBodySize,
            decodedBodySize,
            compressionRatio: ((encodedBodySize - transferSize) / encodedBodySize * 100).toFixed(2) + '%'
          });
        }
      }
    });
  },

  trackChunkLoad: (chunkName: string) => {
    const startTime = performance.now();
    
    return () => {
      const loadTime = performance.now() - startTime;
      console.log(`Chunk ${chunkName} loaded in ${loadTime.toFixed(2)}ms`);
    };
  }
};

// Code splitting helper for feature flags
export const conditionalImport = async <T>(
  condition: boolean,
  importFn: () => Promise<{ default: T }>,
  fallback?: T
): Promise<T> => {
  if (condition) {
    try {
      const module = await importFn();
      return module.default;
    } catch (error) {
      console.warn('Conditional import failed:', error);
      if (fallback !== undefined) {
        return fallback;
      }
      throw error;
    }
  }
  
  if (fallback !== undefined) {
    return fallback;
  }
  
  throw new Error('Condition not met and no fallback provided');
};

// Service worker for caching optimization
export const registerServiceWorker = async () => {
  if (typeof window === 'undefined' || !('serviceWorker' in navigator)) {
    return null;
  }

  try {
    const registration = await navigator.serviceWorker.register('/sw.js');
    console.log('Service Worker registered successfully:', registration);
    return registration;
  } catch (error) {
    console.log('Service Worker registration failed:', error);
    return null;
  }
};

// Performance monitoring
export const performanceMonitor = {
  measureRender: (componentName: string) => {
    const startTime = performance.now();
    
    return () => {
      const renderTime = performance.now() - startTime;
      console.log(`${componentName} render time: ${renderTime.toFixed(2)}ms`);
      
      // Send to analytics if needed
      if (renderTime > 100) {
        console.warn(`Slow render detected for ${componentName}: ${renderTime.toFixed(2)}ms`);
      }
    };
  },

  measureAsyncOperation: async <T>(
    operationName: string,
    operation: () => Promise<T>
  ): Promise<T> => {
    const startTime = performance.now();
    
    try {
      const result = await operation();
      const duration = performance.now() - startTime;
      console.log(`${operationName} completed in ${duration.toFixed(2)}ms`);
      return result;
    } catch (error) {
      const duration = performance.now() - startTime;
      console.error(`${operationName} failed after ${duration.toFixed(2)}ms:`, error);
      throw error;
    }
  }
};

// Initialize optimization utilities
export const initializeBundleOptimization = () => {
  // Preload critical resources
  preloadCriticalRoutes();
  
  // Register service worker
  registerServiceWorker();
  
  // Add performance observer if available
  if (typeof window !== 'undefined' && 'PerformanceObserver' in window) {
    const observer = new PerformanceObserver((list) => {
      const entries = list.getEntries();
      entries.forEach(entry => {
        if (entry.entryType === 'largest-contentful-paint') {
          console.log('LCP:', entry.startTime);
        }
        if (entry.entryType === 'first-input') {
          const fidEntry = entry as any; // First Input Delay entry
          console.log('FID:', fidEntry.processingStart - entry.startTime);
        }
      });
    });
    
    observer.observe({ entryTypes: ['largest-contentful-paint', 'first-input'] });
  }
  
  console.log('Bundle optimization initialized');
}; 