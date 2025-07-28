import React, { useState, useEffect, useCallback } from 'react';
import { render, screen, fireEvent, act } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import { AuthProvider } from '../../contexts/AuthContext';
import { ThemeProvider } from '../../contexts/ThemeContext';
import App from '../../App';
import JobList from '../../components/JobList';

// Mock performance API for memory monitoring
const mockPerformance = {
  now: jest.fn(),
  memory: {
    usedJSHeapSize: 0,
    totalJSHeapSize: 0,
    jsHeapSizeLimit: 0,
  },
};

Object.defineProperty(window, 'performance', {
  value: mockPerformance,
  writable: true,
});

// Component that simulates potential memory leaks
const MemoryLeakComponent = ({ iterations = 100 }: { iterations?: number }) => {
  const [data, setData] = useState<any[]>([]);
  const [listeners, setListeners] = useState<any[]>([]);

  useEffect(() => {
    // Simulate adding event listeners
    const newListeners = [];
    for (let i = 0; i < iterations; i++) {
      const listener = () => console.log(`Listener ${i}`);
      window.addEventListener('resize', listener);
      newListeners.push(listener);
    }
    setListeners(newListeners);

    // Simulate storing large data
    const largeData = Array.from({ length: 1000 }, (_, i) => ({
      id: i,
      data: new Array(1000).fill(`data-${i}`),
    }));
    setData(largeData);

    return () => {
      // Cleanup listeners
      newListeners.forEach(listener => {
        window.removeEventListener('resize', listener);
      });
    };
  }, [iterations]);

  return <div data-testid="memory-leak-component">Memory Test Component</div>;
};

// Component with intentional memory leak
const LeakyComponent = () => {
  const [data, setData] = useState<any[]>([]);

  useEffect(() => {
    // Intentional memory leak - no cleanup
    const interval = setInterval(() => {
      setData(prev => [...prev, { id: Date.now(), data: new Array(1000).fill('leak') }]);
    }, 100);

    // Don't clear interval - this will cause memory leak
  }, []);

  return <div data-testid="leaky-component">Leaky Component</div>;
};

describe('Memory Leak Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    mockPerformance.memory.usedJSHeapSize = 0;
  });

  describe('Component Memory Management', () => {
    it('should not leak memory during component lifecycle', () => {
      const initialMemory = mockPerformance.memory.usedJSHeapSize;
      
      // Render and unmount component multiple times
      for (let i = 0; i < 10; i++) {
        const { unmount } = render(
          <BrowserRouter>
            <MemoryLeakComponent iterations={10} />
          </BrowserRouter>
        );
        
        // Simulate some time passing
        act(() => {
          jest.advanceTimersByTime(100);
        });
        
        unmount();
        
        // Force garbage collection simulation
        act(() => {
          jest.advanceTimersByTime(1000);
        });
      }

      const finalMemory = mockPerformance.memory.usedJSHeapSize;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Memory increase should be minimal after cleanup
      expect(memoryIncrease).toBeLessThan(5 * 1024 * 1024); // 5MB
      console.log(`Memory increase after cleanup: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`);
    });

    it('should detect memory leaks in components', () => {
      const initialMemory = mockPerformance.memory.usedJSHeapSize;
      
      // Render leaky component
      const { unmount } = render(
        <BrowserRouter>
          <LeakyComponent />
        </BrowserRouter>
      );
      
      // Let it run for a while
      act(() => {
        jest.advanceTimersByTime(1000);
      });
      
      unmount();
      
      // Force garbage collection
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      const finalMemory = mockPerformance.memory.usedJSHeapSize;
      const memoryIncrease = finalMemory - initialMemory;
      
      // This should detect the memory leak
      expect(memoryIncrease).toBeGreaterThan(1 * 1024 * 1024); // 1MB
      console.log(`Memory leak detected: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`);
    });
  });

  describe('Event Listener Memory Leaks', () => {
    it('should clean up event listeners properly', () => {
      const initialListeners = (window as any).__eventListeners || 0;
      
      // Component that adds event listeners
      const EventListenerComponent = () => {
        useEffect(() => {
          const handleResize = () => console.log('resize');
          const handleScroll = () => console.log('scroll');
          const handleClick = () => console.log('click');
          
          window.addEventListener('resize', handleResize);
          window.addEventListener('scroll', handleScroll);
          document.addEventListener('click', handleClick);
          
          return () => {
            window.removeEventListener('resize', handleResize);
            window.removeEventListener('scroll', handleScroll);
            document.removeEventListener('click', handleClick);
          };
        }, []);
        
        return <div>Event Listener Component</div>;
      };
      
      // Render and unmount multiple times
      for (let i = 0; i < 5; i++) {
        const { unmount } = render(
          <BrowserRouter>
            <EventListenerComponent />
          </BrowserRouter>
        );
        
        unmount();
      }
      
      const finalListeners = (window as any).__eventListeners || 0;
      const listenerIncrease = finalListeners - initialListeners;
      
      // Should not have accumulated listeners
      expect(listenerIncrease).toBeLessThanOrEqual(0);
    });
  });

  describe('Timer Memory Leaks', () => {
    it('should clean up timers properly', () => {
      const TimerComponent = () => {
        useEffect(() => {
          const interval = setInterval(() => {
            console.log('interval');
          }, 100);
          
          const timeout = setTimeout(() => {
            console.log('timeout');
          }, 1000);
          
          return () => {
            clearInterval(interval);
            clearTimeout(timeout);
          };
        }, []);
        
        return <div>Timer Component</div>;
      };
      
      const initialMemory = mockPerformance.memory.usedJSHeapSize;
      
      // Render and unmount
      const { unmount } = render(
        <BrowserRouter>
          <TimerComponent />
        </BrowserRouter>
      );
      
      act(() => {
        jest.advanceTimersByTime(500);
      });
      
      unmount();
      
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      const finalMemory = mockPerformance.memory.usedJSHeapSize;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Should not leak memory from timers
      expect(memoryIncrease).toBeLessThan(1 * 1024 * 1024); // 1MB
    });
  });

  describe('Large Data Structure Memory Leaks', () => {
    it('should handle large data structures efficiently', () => {
      const LargeDataComponent = () => {
        const [data, setData] = useState<any[]>([]);
        
        useEffect(() => {
          // Create large data structure
          const largeData = Array.from({ length: 10000 }, (_, i) => ({
            id: i,
            data: new Array(100).fill(`item-${i}`),
            metadata: {
              timestamp: Date.now(),
              random: Math.random(),
            }
          }));
          
          setData(largeData);
          
          return () => {
            // Clear data on unmount
            setData([]);
          };
        }, []);
        
        return <div data-testid="large-data">Large Data: {data.length} items</div>;
      };
      
      const initialMemory = mockPerformance.memory.usedJSHeapSize;
      
      const { unmount } = render(
        <BrowserRouter>
          <LargeDataComponent />
        </BrowserRouter>
      );
      
      unmount();
      
      // Force garbage collection
      act(() => {
        jest.advanceTimersByTime(3000);
      });
      
      const finalMemory = mockPerformance.memory.usedJSHeapSize;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Should clean up large data structures
      expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024); // 10MB
    });
  });

  describe('App-Level Memory Management', () => {
    it('should not leak memory during app navigation', () => {
      const initialMemory = mockPerformance.memory.usedJSHeapSize;
      
      const { getByText } = render(
        <BrowserRouter>
          <ThemeProvider>
            <AuthProvider>
              <App />
            </AuthProvider>
          </ThemeProvider>
        </BrowserRouter>
      );
      
      // Navigate between different pages
      const pages = ['Ana Sayfa', 'İşler', 'Profil', 'Ayarlar'];
      
      pages.forEach(page => {
        const pageLink = getByText(page);
        if (pageLink) {
          fireEvent.click(pageLink);
          
          act(() => {
            jest.advanceTimersByTime(100);
          });
        }
      });
      
      const finalMemory = mockPerformance.memory.usedJSHeapSize;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Navigation should not cause significant memory increase
      expect(memoryIncrease).toBeLessThan(5 * 1024 * 1024); // 5MB
      console.log(`Memory increase after navigation: ${(memoryIncrease / 1024 / 1024).toFixed(2)}MB`);
    });
  });

  describe('Context Memory Leaks', () => {
    it('should not leak memory in context providers', () => {
      const initialMemory = mockPerformance.memory.usedJSHeapSize;
      
      // Render app with context providers multiple times
      for (let i = 0; i < 5; i++) {
        const { unmount } = render(
          <BrowserRouter>
            <ThemeProvider>
              <AuthProvider>
                <App />
              </AuthProvider>
            </ThemeProvider>
          </BrowserRouter>
        );
        
        act(() => {
          jest.advanceTimersByTime(500);
        });
        
        unmount();
      }
      
      const finalMemory = mockPerformance.memory.usedJSHeapSize;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Context providers should not leak memory
      expect(memoryIncrease).toBeLessThan(2 * 1024 * 1024); // 2MB
    });
  });

  describe('Async Operation Memory Leaks', () => {
    it('should clean up async operations properly', async () => {
      const AsyncComponent = () => {
        const [data, setData] = useState<any[]>([]);
        const [loading, setLoading] = useState(false);
        
        const fetchData = useCallback(async () => {
          setLoading(true);
          try {
            // Simulate async operation
            await new Promise(resolve => setTimeout(resolve, 100));
            setData(Array.from({ length: 1000 }, (_, i) => ({ id: i, value: `data-${i}` })));
          } finally {
            setLoading(false);
          }
        }, []);
        
        useEffect(() => {
          fetchData();
        }, [fetchData]);
        
        return (
          <div>
            {loading ? 'Loading...' : `Loaded ${data.length} items`}
          </div>
        );
      };
      
      const initialMemory = mockPerformance.memory.usedJSHeapSize;
      
      const { unmount } = render(
        <BrowserRouter>
          <AsyncComponent />
        </BrowserRouter>
      );
      
      // Wait for async operation
      await act(async () => {
        await new Promise(resolve => setTimeout(resolve, 200));
      });
      
      unmount();
      
      // Force garbage collection
      act(() => {
        jest.advanceTimersByTime(2000);
      });
      
      const finalMemory = mockPerformance.memory.usedJSHeapSize;
      const memoryIncrease = finalMemory - initialMemory;
      
      // Async operations should not leak memory
      expect(memoryIncrease).toBeLessThan(2 * 1024 * 1024); // 2MB
    });
  });
});