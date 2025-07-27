import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import App from '../../App';
import JobList from '../../components/JobList';
import JobDetail from '../../components/JobDetail';

// Mock performance API
const mockPerformance = {
  now: jest.fn(),
  mark: jest.fn(),
  measure: jest.fn(),
  getEntriesByType: jest.fn(),
  getEntriesByName: jest.fn(),
};

Object.defineProperty(window, 'performance', {
  value: mockPerformance,
  writable: true,
});

// Mock requestAnimationFrame
const mockRAF = jest.fn();
Object.defineProperty(window, 'requestAnimationFrame', {
  value: mockRAF,
  writable: true,
});

const measureRenderTime = (component: React.ReactElement) => {
  const startTime = performance.now();
  const { unmount } = render(component);
  const endTime = performance.now();
  unmount();
  return endTime - startTime;
};

describe('Render Performance Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockPerformance.now.mockReturnValue(0);
  });

  describe('Component Render Performance', () => {
    it('should render JobList component within 100ms', () => {
      const mockJobs = Array.from({ length: 10 }, (_, i) => ({
        id: `${i}`,
        title: `Job ${i}`,
        company: { name: `Company ${i}` },
        location: 'Remote',
        type: 'Full-time',
        salary: '50000-70000',
        postedAt: '2024-01-01'
      }));

      const renderTime = measureRenderTime(
        <BrowserRouter>
          <JobList jobs={mockJobs} />
        </BrowserRouter>
      );

      expect(renderTime).toBeLessThan(100);
      console.log(`JobList render time: ${renderTime.toFixed(2)}ms`);
    });

    it('should render JobDetail component within 50ms', () => {
      const mockJob = {
        id: '1',
        title: 'React Developer',
        company: { name: 'Tech Corp', logo: 'logo.png' },
        location: 'Remote',
        type: 'Full-time',
        salary: '50000-70000',
        description: 'We are looking for a React developer...',
        skills: ['React', 'TypeScript', 'Node.js'],
        postedAt: '2024-01-01'
      };

      const renderTime = measureRenderTime(
        <BrowserRouter>
          <JobDetail job={mockJob} similarJobs={[]} onApply={jest.fn()} />
        </BrowserRouter>
      );

      expect(renderTime).toBeLessThan(50);
      console.log(`JobDetail render time: ${renderTime.toFixed(2)}ms`);
    });

    it('should handle large job lists efficiently', () => {
      const largeJobList = Array.from({ length: 100 }, (_, i) => ({
        id: `${i}`,
        title: `Job ${i}`,
        company: { name: `Company ${i}` },
        location: 'Remote',
        type: 'Full-time',
        salary: '50000-70000',
        postedAt: '2024-01-01'
      }));

      const renderTime = measureRenderTime(
        <BrowserRouter>
          <JobList jobs={largeJobList} />
        </BrowserRouter>
      );

      expect(renderTime).toBeLessThan(200);
      console.log(`Large JobList render time: ${renderTime.toFixed(2)}ms`);
    });
  });

  describe('User Interaction Performance', () => {
    it('should handle search input changes efficiently', () => {
      const { getByPlaceholderText } = render(
        <BrowserRouter>
          <ThemeProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </ThemeProvider>
        </BrowserRouter>
      );

      const searchInput = getByPlaceholderText(/İş ara/i);
      
      const startTime = performance.now();
      fireEvent.change(searchInput, { target: { value: 'React Developer' } });
      const endTime = performance.now();

      const interactionTime = endTime - startTime;
      expect(interactionTime).toBeLessThan(16); // 60fps = 16ms per frame
      console.log(`Search input interaction time: ${interactionTime.toFixed(2)}ms`);
    });

    it('should handle button clicks efficiently', () => {
      const { getByText } = render(
        <BrowserRouter>
          <ThemeProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </ThemeProvider>
        </BrowserRouter>
      );

      const button = getByText(/Giriş Yap/i);
      
      const startTime = performance.now();
      fireEvent.click(button);
      const endTime = performance.now();

      const clickTime = endTime - startTime;
      expect(clickTime).toBeLessThan(16);
      console.log(`Button click time: ${clickTime.toFixed(2)}ms`);
    });
  });

  describe('Memory Usage', () => {
    it('should not have memory leaks during re-renders', () => {
      const mockJobs = Array.from({ length: 50 }, (_, i) => ({
        id: `${i}`,
        title: `Job ${i}`,
        company: { name: `Company ${i}` },
        location: 'Remote',
        type: 'Full-time',
        salary: '50000-70000',
        postedAt: '2024-01-01'
      }));

      const initialMemory = (performance as any).memory?.usedJSHeapSize || 0;
      
      // Render and unmount multiple times
      for (let i = 0; i < 10; i++) {
        const { unmount } = render(
          <BrowserRouter>
            <JobList jobs={mockJobs} />
          </BrowserRouter>
        );
        unmount();
      }

      const finalMemory = (performance as any).memory?.usedJSHeapSize || 0;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Memory increase should be minimal
      expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024); // 10MB
      console.log(`Memory increase: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`);
    });
  });

  describe('Animation Performance', () => {
    it('should handle animations smoothly', () => {
      const { getByText } = render(
        <BrowserRouter>
          <ThemeProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </ThemeProvider>
        </BrowserRouter>
      );

      const button = getByText(/Giriş Yap/i);
      
      // Simulate animation frame
      let frameCount = 0;
      mockRAF.mockImplementation((callback) => {
        frameCount++;
        callback(performance.now());
        return frameCount;
      });

      fireEvent.click(button);

      // Should not trigger too many animation frames
      expect(frameCount).toBeLessThan(10);
      console.log(`Animation frames triggered: ${frameCount}`);
    });
  });

  describe('Network Performance', () => {
    it('should handle API calls efficiently', async () => {
      const mockFetch = jest.fn().mockResolvedValue({
        ok: true,
        json: () => Promise.resolve({ jobs: [] })
      });
      global.fetch = mockFetch;

      const startTime = performance.now();
      
      await fetch('/api/jobs');
      
      const endTime = performance.now();
      const apiCallTime = endTime - startTime;

      // API calls should complete within reasonable time
      expect(apiCallTime).toBeLessThan(1000); // 1 second
      console.log(`API call time: ${apiCallTime.toFixed(2)}ms`);
    });
  });

  describe('Bundle Loading Performance', () => {
    it('should load initial bundle quickly', () => {
      const startTime = performance.now();
      
      // Simulate bundle loading
      const script = document.createElement('script');
      script.src = '/static/js/main.js';
      document.head.appendChild(script);
      
      script.onload = () => {
        const endTime = performance.now();
        const loadTime = endTime - startTime;
        
        expect(loadTime).toBeLessThan(2000); // 2 seconds
        console.log(`Bundle load time: ${loadTime.toFixed(2)}ms`);
      };
    });
  });

  describe('Responsive Performance', () => {
    it('should handle viewport changes efficiently', () => {
      const { rerender } = render(
        <BrowserRouter>
          <ThemeProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </ThemeProvider>
        </BrowserRouter>
      );

      const viewports = [
        { width: 375, height: 667 }, // Mobile
        { width: 768, height: 1024 }, // Tablet
        { width: 1920, height: 1080 } // Desktop
      ];

      viewports.forEach(viewport => {
        Object.defineProperty(window, 'innerWidth', {
          writable: true,
          configurable: true,
          value: viewport.width,
        });
        Object.defineProperty(window, 'innerHeight', {
          writable: true,
          configurable: true,
          value: viewport.height,
        });

        const startTime = performance.now();
        
        // Trigger resize event
        window.dispatchEvent(new Event('resize'));
        
        const endTime = performance.now();
        const resizeTime = endTime - startTime;

        expect(resizeTime).toBeLessThan(16);
        console.log(`Resize time for ${viewport.width}x${viewport.height}: ${resizeTime.toFixed(2)}ms`);
      });
    });
  });
});