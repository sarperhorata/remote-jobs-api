import React, { useState, useRef, useCallback, useEffect } from 'react';
import { createPortal } from 'react-dom';
// Unused imports removed for cleaner code
import { getApiUrl } from '../utils/apiConfig';

interface Position {
  title: string;
  count: number;
  category?: string;
}

interface MultiJobAutocompleteProps {
  onSelect: (position: Position) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

const MultiJobAutocomplete: React.FC<MultiJobAutocompleteProps> = ({
  onSelect,
  placeholder = "Search and select job titles (up to 10)",
  className,
  disabled = false
}) => {
  const [inputValue, setInputValue] = useState('');
  const [allSuggestions, setAllSuggestions] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0, width: 0 });
  const [isFocused, setIsFocused] = useState(false);
  const [animatedPlaceholder, setAnimatedPlaceholder] = useState('');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Typing animation for placeholder
  useEffect(() => {
    if (!isFocused && !inputValue) {
      const interval = setInterval(() => {
        setPlaceholderIndex(prev => {
          if (prev >= placeholder.length) {
            setTimeout(() => setPlaceholderIndex(0), 2000); // Pause at end
            return prev;
          }
          return prev + 1;
        });
      }, 100);

      return () => clearInterval(interval);
    }
  }, [isFocused, inputValue, placeholder]);

  // Update animated placeholder
  useEffect(() => {
    if (!isFocused && !inputValue) {
      setAnimatedPlaceholder(placeholder.slice(0, placeholderIndex));
    } else {
      setAnimatedPlaceholder(placeholder);
    }
  }, [placeholderIndex, isFocused, inputValue, placeholder]);

  // Debug logging
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🔄 MultiJobAutocomplete State:', {
        inputValue,
        suggestionsCount: allSuggestions.length,
        showDropdown,
        isLoading,
      });
    }
  }, [inputValue, allSuggestions.length, showDropdown, isLoading]);

  // Fetch suggestions when user types
  const fetchSuggestions = useCallback(async (query: string) => {
    if (!query.trim() || query.length < 2) {
      setAllSuggestions([]);
      setShowDropdown(false);
      return;
    }

    setIsLoading(true);
    try {
      const finalApiUrl = await getApiUrl();
      
      const response = await fetch(`${finalApiUrl}/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=20`, {
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });
      
      if (!response.ok) {
        throw new Error(`API request failed with status ${response.status}`);
      }
      
      const data = await response.json();
      if (Array.isArray(data)) {
        setAllSuggestions(data);
        setShowDropdown(data.length > 0);
      } else {
        console.warn('Invalid API response format:', data);
        setAllSuggestions([]);
        setShowDropdown(false);
      }
    } catch (error: any) {
      console.error('Error fetching job title suggestions:', error);
      setAllSuggestions([]);
      setShowDropdown(false);
      
      // Don't show error to user for network timeouts
      if (!error.message?.includes('timeout') && !error.message?.includes('Failed to fetch')) {
        console.warn('API temporarily unavailable');
      }
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Fetch popular job titles
  const fetchPopularTitles = useCallback(async () => {
    try {
      const finalApiUrl = await getApiUrl();
      
      const response = await fetch(`${finalApiUrl}/jobs/statistics`, {
        signal: AbortSignal.timeout(10000), // 10 second timeout
      });
      
      if (!response.ok) {
        throw new Error(`Statistics API failed with status ${response.status}`);
      }
      
      const data = await response.json();
      const popularTitles = data.positions?.slice(0, 5) || []; // 5 popular positions
      
      setAllSuggestions(popularTitles);
      setShowDropdown(popularTitles.length > 0);
    } catch (error: any) {
      console.error('Error fetching popular titles:', error);
      
      // Fallback popular titles
      const fallbackTitles = [
        { title: "Software Engineer", count: 100, category: "Technology" },
        { title: "Product Manager", count: 80, category: "Management" },
        { title: "Data Scientist", count: 60, category: "Technology" },
        { title: "DevOps Engineer", count: 50, category: "Technology" },
        { title: "UX Designer", count: 40, category: "Design" }
      ];
      
      setAllSuggestions(fallbackTitles);
      setShowDropdown(true);
    }
  }, []);

  // Handle input focus to show popular titles
  const handleInputFocus = async () => {
    setIsFocused(true);
    if (process.env.NODE_ENV === 'development') {
      console.log('🎯 Input focused');
    }
    if (!inputValue.trim() && allSuggestions.length === 0) {
      setIsLoading(true);
      await fetchPopularTitles();
      setIsLoading(false);
    } else if (allSuggestions.length > 0) {
      setShowDropdown(true);
    }
  };

  const handleInputBlur = () => {
    setIsFocused(false);
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    if (value.trim().length >= 2) {
      fetchSuggestions(value);
    } else {
      if (process.env.NODE_ENV === 'development') {
        console.log('🧹 Input empty, clearing suggestions');
      }
      setAllSuggestions([]);
      setShowDropdown(false);
    }
  };

  // Select a position
  const selectPosition = (position: Position) => {
    console.log('🎯 selectPosition called with:', position);
    
    onSelect(position);
    
    // Clear and reset
    console.log('🧹 Clearing input and closing dropdown');
    setInputValue('');
    setAllSuggestions([]);
    setShowDropdown(false);
    
    // Focus back to input
    setTimeout(() => {
      console.log('🎯 Focusing back to input');
      inputRef.current?.focus();
    }, 50);
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // Check if click is outside both the container and the dropdown
      if (
        containerRef.current && 
        !containerRef.current.contains(event.target as Node) &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
        console.log('👆 Click outside detected, closing dropdown');
        setShowDropdown(false);
      }
    };

    if (showDropdown) {
      document.addEventListener('mousedown', handleClickOutside);
      return () => {
        document.removeEventListener('mousedown', handleClickOutside);
      };
    }
  }, [showDropdown]);

  // Cleanup timeout on unmount
  useEffect(() => {
    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, []);

  // Add helper function for RTL detection
  const isRTL = (text: string): boolean => {
    const rtlChars = /[\u0590-\u083F]|[\u08A0-\u08FF]|[\uFB1D-\uFDFF]|[\uFE70-\uFEFF]/mg;
    return rtlChars.test(text);
  };

  // Calculate dropdown position
  const updateDropdownPosition = useCallback(() => {
    if (!inputRef.current) return;

    const inputRect = inputRef.current.getBoundingClientRect();
    const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
    const scrollLeft = window.pageXOffset || document.documentElement.scrollLeft;

    setDropdownPosition({
      top: inputRect.bottom + scrollTop,
      left: inputRect.left + scrollLeft,
      width: inputRect.width
    });
  }, []);

  // Update position when dropdown opens or window resizes
  useEffect(() => {
    if (showDropdown) {
      updateDropdownPosition();
      
      const handleScroll = () => updateDropdownPosition();
      const handleResize = () => updateDropdownPosition();
      
      window.addEventListener('scroll', handleScroll, true);
      window.addEventListener('resize', handleResize);
      
      return () => {
        window.removeEventListener('scroll', handleScroll, true);
        window.removeEventListener('resize', handleResize);
      };
    }
  }, [showDropdown, updateDropdownPosition]);

  // Country suggestions removed - implemented in separate component

  return (
    <div className={`w-full ${className || ''}`} ref={containerRef}>
      {/* Search input and button */}
      <div className="flex gap-2">
        <div className="relative flex-1 group">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            onBlur={handleInputBlur}
            placeholder={animatedPlaceholder}
            disabled={disabled}
            className="w-full px-4 py-3 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-[1.02] focus:scale-[1.02] shadow-sm hover:shadow-md focus:shadow-lg"
          />
          
          {/* Loading spinner */}
          {isLoading && (
            <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
              <div className="w-5 h-5 border-2 border-blue-500 dark:border-blue-400 border-t-transparent rounded-full animate-spin" />
            </div>
          )}

          {/* Dropdown Portal */}
          {showDropdown && createPortal(
            <div 
              ref={dropdownRef}
              className="fixed bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-2xl mt-1 max-h-64 overflow-y-auto animate-in slide-in-from-top-2 duration-300"
              style={{
                top: `${dropdownPosition.top + 4}px`,
                left: `${dropdownPosition.left}px`,
                width: `${dropdownPosition.width}px`,
                zIndex: 999999,
                boxShadow: '0 10px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)'
              }}
            >
              {isLoading ? (
                <div className="p-3 text-center text-gray-500 dark:text-gray-400">
                  <div className="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full mr-2"></div>
                  Searching...
                </div>
              ) : allSuggestions.length > 0 ? (
                <>
                  {allSuggestions.map((suggestion, index) => (
                    <div
                      key={index}
                      className="px-4 py-2 hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-600 last:border-b-0 transition-all duration-200 transform hover:scale-[1.02]"
                      onClick={() => selectPosition(suggestion)}
                    >
                      <div className={`flex justify-between items-center ${isRTL(suggestion.title) ? 'text-right' : 'text-left'}`}>
                        <span className="text-gray-900 dark:text-white font-medium">
                          {suggestion.title}
                        </span>
                        <span className="text-sm text-gray-500 dark:text-gray-400 ml-2 transition-all duration-200 hover:scale-105">
                          {suggestion.count} jobs
                        </span>
                      </div>
                    </div>
                  ))}
                </>
              ) : inputValue.length >= 2 ? (
                <div className="p-3 text-center text-gray-500 dark:text-gray-400">
                  No job titles found
                </div>
              ) : (
                <div className="p-3 text-center text-gray-500 dark:text-gray-400">
                  Type for more relevant job ads
                </div>
              )}
            </div>,
            document.body
          )}
        </div>
      </div>
    </div>
  );
};

export default MultiJobAutocomplete;