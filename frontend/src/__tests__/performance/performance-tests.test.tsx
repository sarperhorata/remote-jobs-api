import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';

// Mock performance API
const mockPerformance = {
  now: jest.fn(() => Date.now()),
  mark: jest.fn(),
  measure: jest.fn(),
  getEntriesByType: jest.fn(() => []),
  getEntriesByName: jest.fn(() => []),
  clearMarks: jest.fn(),
  clearMeasures: jest.fn(),
};

Object.defineProperty(window, 'performance', {
  value: mockPerformance,
  writable: true,
});

// Mock requestAnimationFrame
global.requestAnimationFrame = jest.fn(callback => {
  setTimeout(callback, 0);
  return 1;
});

// Mock setTimeout for performance testing
jest.useFakeTimers();

describe('Performance Tests', () => {
  beforeEach(() => {
    jest.clearAllMocks();
    jest.clearAllTimers();
  });

  describe('Component Rendering Performance', () => {
    it('should render large lists efficiently', async () => {
      const startTime = performance.now();
      
      const MockLargeList = () => {
        const items = Array.from({ length: 1000 }, (_, i) => ({
          id: i,
          title: `Item ${i}`,
          description: `Description for item ${i}`
        }));

        return (
          <div data-testid="large-list">
            {items.map(item => (
              <div key={item.id} data-testid={`item-${item.id}`}>
                <h3>{item.title}</h3>
                <p>{item.description}</p>
              </div>
            ))}
          </div>
        );
      };

      render(<MockLargeList />);
      
      const endTime = performance.now();
      const renderTime = endTime - startTime;

      // Should render within reasonable time (adjust threshold as needed)
      expect(renderTime).toBeLessThan(1000); // 1 second
      
      // Verify all items are rendered
      expect(screen.getByTestId('large-list')).toBeInTheDocument();
      expect(screen.getByTestId('item-0')).toBeInTheDocument();
      expect(screen.getByTestId('item-999')).toBeInTheDocument();
    });

    it('should handle rapid state updates efficiently', async () => {
      const MockStateUpdateComponent = () => {
        const [count, setCount] = React.useState(0);
        const [updates, setUpdates] = React.useState(0);

        const handleRapidUpdates = () => {
          for (let i = 0; i < 100; i++) {
            setCount(prev => prev + 1);
            setUpdates(prev => prev + 1);
          }
        };

        return (
          <div>
            <div data-testid="count">{count}</div>
            <div data-testid="updates">{updates}</div>
            <button data-testid="update-button" onClick={handleRapidUpdates}>
              Rapid Update
            </button>
          </div>
        );
      };

      render(<MockStateUpdateComponent />);

      const updateButton = screen.getByTestId('update-button');
      const startTime = performance.now();
      
      fireEvent.click(updateButton);
      
      const endTime = performance.now();
      const updateTime = endTime - startTime;

      // Should handle rapid updates efficiently
      expect(updateTime).toBeLessThan(100); // 100ms
      
      // Verify final state
      await waitFor(() => {
        expect(screen.getByTestId('count')).toHaveTextContent('100');
        expect(screen.getByTestId('updates')).toHaveTextContent('100');
      });
    });
  });

  describe('Memory Usage Tests', () => {
    it('should not create memory leaks with event listeners', async () => {
      const mockAddEventListener = jest.fn();
      const mockRemoveEventListener = jest.fn();
      
      Object.defineProperty(window, 'addEventListener', {
        value: mockAddEventListener,
        writable: true,
      });
      
      Object.defineProperty(window, 'removeEventListener', {
        value: mockRemoveEventListener,
        writable: true,
      });

      const MockEventListenerComponent = () => {
        React.useEffect(() => {
          const handleResize = () => console.log('resized');
          window.addEventListener('resize', handleResize);
          
          return () => {
            window.removeEventListener('resize', handleResize);
          };
        }, []);

        return <div data-testid="event-component">Event Component</div>;
      };

      const { unmount } = render(<MockEventListenerComponent />);
      
      // Verify event listener was added
      expect(mockAddEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
      
      // Unmount component
      unmount();
      
      // Verify event listener was removed
      expect(mockRemoveEventListener).toHaveBeenCalledWith('resize', expect.any(Function));
    });

    it('should clean up timers properly', async () => {
      const mockSetTimeout = jest.spyOn(global, 'setTimeout');
      const mockClearTimeout = jest.spyOn(global, 'clearTimeout');

      const MockTimerComponent = () => {
        React.useEffect(() => {
          const timer = setTimeout(() => console.log('timer'), 1000);
          
          return () => {
            clearTimeout(timer);
          };
        }, []);

        return <div data-testid="timer-component">Timer Component</div>;
      };

      const { unmount } = render(<MockTimerComponent />);
      
      // Verify timer was set
      expect(mockSetTimeout).toHaveBeenCalled();
      
      // Unmount component
      unmount();
      
      // Verify timer was cleared
      expect(mockClearTimeout).toHaveBeenCalled();
      
      mockSetTimeout.mockRestore();
      mockClearTimeout.mockRestore();
    });
  });

  describe('Network Performance Tests', () => {
    it('should handle API response timeouts gracefully', async () => {
      const mockFetch = jest.fn();
      global.fetch = mockFetch;

      const MockAPITimeoutComponent = () => {
        const [data, setData] = React.useState(null);
        const [loading, setLoading] = React.useState(false);
        const [error, setError] = React.useState(null);

        const fetchData = async () => {
          setLoading(true);
          setError(null);
          
          try {
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 5000); // 5s timeout
            
            const response = await fetch('/api/data', { 
              signal: controller.signal 
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
              const result = await response.json();
              setData(result);
            } else {
              throw new Error('API Error');
            }
          } catch (err) {
            setError(err.message);
          } finally {
            setLoading(false);
          }
        };

        return (
          <div>
            <button data-testid="fetch-button" onClick={fetchData}>
              Fetch Data
            </button>
            {loading && <div data-testid="loading">Loading...</div>}
            {error && <div data-testid="error">{error}</div>}
            {data && <div data-testid="data">Data loaded</div>}
          </div>
        );
      };

      render(<MockAPITimeoutComponent />);

      const fetchButton = screen.getByTestId('fetch-button');
      fireEvent.click(fetchButton);

      // Should show loading state
      expect(screen.getByTestId('loading')).toBeInTheDocument();

      // Simulate timeout
      mockFetch.mockImplementation(() => 
        new Promise((_, reject) => 
          setTimeout(() => reject(new Error('Timeout')), 6000)
        )
      );

      // Wait for timeout
      await waitFor(() => {
        expect(screen.getByTestId('error')).toBeInTheDocument();
      }, { timeout: 7000 });
    });

    it('should implement request debouncing', async () => {
      const mockSearchAPI = jest.fn();
      
              const MockDebouncedSearch = () => {
          const [query, setQuery] = React.useState('');
          const [results, setResults] = React.useState<any[]>([]);
          const [searchCount, setSearchCount] = React.useState(0);

          React.useEffect(() => {
            if (query.length < 3) return;

            const timeoutId = setTimeout(async () => {
              try {
                const response = await mockSearchAPI(query);
                setResults(response || []);
                setSearchCount(prev => prev + 1);
              } catch (error) {
                console.error('Search failed:', error);
                setResults([]);
              }
            }, 300); // 300ms debounce

            return () => clearTimeout(timeoutId);
          }, [query]);

          return (
            <div>
              <input
                data-testid="search-input"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="Search..."
              />
              <div data-testid="search-count">Searches: {searchCount}</div>
              <div data-testid="results-count">Results: {results.length}</div>
            </div>
          );
        };

      render(<MockDebouncedSearch />);

      const searchInput = screen.getByTestId('search-input');

      // Type rapidly
      fireEvent.change(searchInput, { target: { value: 'r' } });
      fireEvent.change(searchInput, { target: { value: 're' } });
      fireEvent.change(searchInput, { target: { value: 'rea' } });
      fireEvent.change(searchInput, { target: { value: 'reac' } });
      fireEvent.change(searchInput, { target: { value: 'react' } });

      // Should only make one API call due to debouncing
      await waitFor(() => {
        expect(mockSearchAPI).toHaveBeenCalledTimes(1);
        expect(mockSearchAPI).toHaveBeenCalledWith('react');
      });
    });
  });

  describe('Animation Performance Tests', () => {
    it('should handle smooth animations without blocking', async () => {
      const MockAnimatedComponent = () => {
        const [isAnimating, setIsAnimating] = React.useState(false);
        const [animationCount, setAnimationCount] = React.useState(0);

        const startAnimation = () => {
          setIsAnimating(true);
          setAnimationCount(prev => prev + 1);
          
          // Simulate animation duration
          setTimeout(() => {
            setIsAnimating(false);
          }, 1000);
        };

        return (
          <div>
            <button data-testid="animate-button" onClick={startAnimation}>
              Start Animation
            </button>
            <div 
              data-testid="animated-element"
              style={{
                transition: 'all 1s ease',
                transform: isAnimating ? 'scale(1.2)' : 'scale(1)',
                backgroundColor: isAnimating ? 'red' : 'blue'
              }}
            >
              Animated Element
            </div>
            <div data-testid="animation-count">Animations: {animationCount}</div>
          </div>
        );
      };

      render(<MockAnimatedComponent />);

      const animateButton = screen.getByTestId('animate-button');
      const animatedElement = screen.getByTestId('animated-element');

      // Start animation
      fireEvent.click(animateButton);

      // Should show animation state
      expect(animatedElement).toHaveStyle({ backgroundColor: 'red' });

      // Should be able to interact during animation
      fireEvent.click(animateButton);
      fireEvent.click(animateButton);

      // Wait for animations to complete
      await waitFor(() => {
        expect(screen.getByTestId('animation-count')).toHaveTextContent('Animations: 3');
      }, { timeout: 3000 });
    });

    it('should optimize re-renders with React.memo', async () => {
      const renderCount = { count: 0 };
      
      const MockOptimizedComponent = React.memo(() => {
        renderCount.count++;
        return <div data-testid="optimized-component">Optimized Component</div>;
      });

      const MockParentComponent = () => {
        const [parentState, setParentState] = React.useState(0);

        return (
          <div>
            <button data-testid="parent-button" onClick={() => setParentState(prev => prev + 1)}>
              Update Parent
            </button>
            <div data-testid="parent-state">Parent State: {parentState}</div>
            <MockOptimizedComponent />
          </div>
        );
      };

      render(<MockParentComponent />);

      const parentButton = screen.getByTestId('parent-button');
      const initialRenderCount = renderCount.count;

      // Update parent state multiple times
      fireEvent.click(parentButton);
      fireEvent.click(parentButton);
      fireEvent.click(parentButton);

      // Optimized component should not re-render when parent state changes
      expect(renderCount.count).toBe(initialRenderCount);
      expect(screen.getByTestId('parent-state')).toHaveTextContent('Parent State: 3');
    });
  });

  describe('Bundle Size Optimization Tests', () => {
    it('should lazy load components efficiently', async () => {
      const MockLazyComponent = React.lazy(() => 
        new Promise(resolve => {
          setTimeout(() => {
            resolve({
              default: () => <div data-testid="lazy-component">Lazy Loaded Component</div>
            });
          }, 100);
        })
      );

      const MockLazyLoader = () => {
        const [showLazy, setShowLazy] = React.useState(false);

        return (
          <div>
            <button data-testid="load-button" onClick={() => setShowLazy(true)}>
              Load Lazy Component
            </button>
            {showLazy && (
              <React.Suspense fallback={<div data-testid="loading">Loading...</div>}>
                <MockLazyComponent />
              </React.Suspense>
            )}
          </div>
        );
      };

      render(<MockLazyLoader />);

      const loadButton = screen.getByTestId('load-button');
      fireEvent.click(loadButton);

      // Should show loading state
      expect(screen.getByTestId('loading')).toBeInTheDocument();

      // Should load component after delay
      await waitFor(() => {
        expect(screen.getByTestId('lazy-component')).toBeInTheDocument();
      }, { timeout: 200 });
    });
  });
});