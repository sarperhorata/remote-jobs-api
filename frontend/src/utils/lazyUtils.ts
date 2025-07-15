import { lazy, ComponentType } from 'react';

/**
 * Enhanced lazy loading with retry functionality
 */
export const lazyWithRetry = <T extends ComponentType<any>>(
  componentImport: () => Promise<{ default: T }>,
  retries = 3
): ComponentType<any> => {
  return lazy(() => {
    return new Promise<{ default: T }>((resolve, reject) => {
      let attempts = 0;
      
      const attemptImport = async () => {
        try {
          const component = await componentImport();
          resolve(component);
        } catch (error) {
          attempts++;
          if (attempts >= retries) {
            reject(error);
          } else {
            // Exponential backoff
            setTimeout(attemptImport, Math.pow(2, attempts) * 1000);
          }
        }
      };
      
      attemptImport();
    });
  });
};

/**
 * Preload a component
 */
export const preloadComponent = (componentImport: () => Promise<any>) => {
  try {
    componentImport();
  } catch (error) {
    // Silently ignore preload errors
    console.warn('Failed to preload component:', error);
  }
};

/**
 * Lazy loading with intersection observer
 */
export class LazyLoader {
  private observer: IntersectionObserver;
  private elements: Map<Element, () => void> = new Map();

  constructor(options?: IntersectionObserverInit) {
    this.observer = new IntersectionObserver((entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          const callback = this.elements.get(entry.target);
          if (callback) {
            callback();
            this.unobserve(entry.target);
          }
        }
      });
    }, options);
  }

  observe(element: Element, callback: () => void) {
    this.elements.set(element, callback);
    this.observer.observe(element);
  }

  unobserve(element: Element) {
    this.elements.delete(element);
    this.observer.unobserve(element);
  }

  disconnect() {
    this.observer.disconnect();
    this.elements.clear();
  }
} 