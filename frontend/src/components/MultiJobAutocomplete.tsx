import React, { useState, useRef, useCallback, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { ChevronDown, X, Search } from 'lucide-react';
import { getApiUrl } from '../utils/apiConfig';

interface AutocompleteItem {
  title: string;
  count: number;
  category?: string;
}

interface MultiJobAutocompleteProps {
  selectedPositions: AutocompleteItem[];
  onPositionsChange: (positions: AutocompleteItem[]) => void;
  onSearch?: (positions: AutocompleteItem[]) => void;
  placeholder?: string;
  maxSelections?: number;
}

const MultiJobAutocomplete: React.FC<MultiJobAutocompleteProps> = ({
  selectedPositions = [],
  onPositionsChange,
  onSearch,
  placeholder = "Search and select job titles (up to 10)",
  maxSelections = 10
}) => {
  const [inputValue, setInputValue] = useState('');
  const [allSuggestions, setAllSuggestions] = useState<AutocompleteItem[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0, width: 0 });
  
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Debug logging
  useEffect(() => {
    if (process.env.NODE_ENV === 'development') {
      console.log('🔄 MultiJobAutocomplete State:', {
        inputValue,
        suggestionsCount: allSuggestions.length,
        showDropdown,
        isLoading,
        selectedPositions: selectedPositions.length
      });
    }
  }, [inputValue, allSuggestions.length, showDropdown, isLoading, selectedPositions.length]);

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
      
      const filtered = popularTitles.filter((pos: AutocompleteItem) => 
        !selectedPositions.some(selected => 
          selected.title.toLowerCase() === pos.title.toLowerCase()
        )
      );
      
      setAllSuggestions(filtered);
      setShowDropdown(filtered.length > 0);
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
  }, [selectedPositions]);

  // Handle input focus to show popular titles
  const handleInputFocus = async () => {
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
  const selectPosition = (position: AutocompleteItem) => {
    console.log('🎯 selectPosition called with:', position);
    
    if (selectedPositions.length >= maxSelections) {
      console.log('⚠️ Max selections reached');
      alert(`Maximum ${maxSelections} positions can be selected.`);
      return;
    }

    console.log('➕ Adding position to selected');
    const newPositions = [...selectedPositions, position];
    onPositionsChange(newPositions);
    
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

  // Remove a selected position
  const removePosition = (index: number) => {
    console.log('➖ Removing position at index:', index);
    const newPositions = selectedPositions.filter((_, i) => i !== index);
    onPositionsChange(newPositions);
  };



  // Clear all selected positions
  const clearAllPositions = () => {
    onPositionsChange([]);
    setInputValue('');
    setAllSuggestions([]);
    setShowDropdown(false);
  };

  // Handle search button click
  const handleSearchClick = () => {
    console.log('🔍 Search button clicked with positions:', selectedPositions.map(p => p.title));
    
    if (selectedPositions.length === 0) {
      alert('Please select at least one job position to search.');
      return;
    }
    onSearch?.(selectedPositions);
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

  return (
    <div className="w-full" ref={containerRef}>
      {/* Selected positions display */}
      {selectedPositions.length > 0 && (
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
              Selected Positions ({selectedPositions.length}/{maxSelections}):
            </span>
            <button
              type="button"
              onClick={clearAllPositions}
              className="text-xs text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300 transition-colors"
            >
              Clear All
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedPositions.map((position, index) => (
              <div
                key={`${position.title}-${index}`}
                className="inline-flex items-center gap-2 px-3 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded-full text-sm"
              >
                <span>{position.title}</span>
                <button
                  type="button"
                  onClick={() => removePosition(index)}
                  className="text-blue-600 dark:text-blue-300 hover:text-blue-800 dark:hover:text-blue-100 font-bold"
                  aria-label={`Remove ${position.title}`}
                >
                  ×
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search input and button */}
      <div className="flex gap-2">
        <div className="relative flex-1">
          <input
            ref={inputRef}
            type="text"
            value={inputValue}
            onChange={handleInputChange}
            onFocus={handleInputFocus}
            placeholder={selectedPositions.length >= maxSelections ? "Maximum selections reached" : placeholder}
            disabled={selectedPositions.length >= maxSelections}
            className="w-full px-4 py-3 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed"
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
              className="fixed bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-2xl mt-1 max-h-64 overflow-y-auto"
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
                      className="px-4 py-2 hover:bg-blue-50 dark:hover:bg-gray-700 cursor-pointer border-b border-gray-100 dark:border-gray-600 last:border-b-0"
                      onClick={() => selectPosition(suggestion)}
                    >
                      <div className={`flex justify-between items-center ${isRTL(suggestion.title) ? 'text-right' : 'text-left'}`}>
                        <span className="text-gray-900 dark:text-white font-medium">
                          {suggestion.title}
                        </span>
                        <span className="text-sm text-gray-500 dark:text-gray-400 ml-2">
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

        <button
          type="button"
          onClick={handleSearchClick}
          disabled={selectedPositions.length === 0}
          className="px-6 py-3 bg-gradient-to-r from-orange-500 to-yellow-500 text-white rounded-lg hover:from-orange-600 hover:to-yellow-600 disabled:from-gray-300 disabled:to-gray-300 disabled:cursor-not-allowed transition-all font-semibold shadow-md disabled:shadow-none"
        >
          Search Jobs
        </button>
      </div>

      {/* Help text */}
      <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">
        {selectedPositions.length === 0
          ? "Start typing to search job positions. You can select up to " + maxSelections + " positions."
          : selectedPositions.length === maxSelections
          ? "Maximum selections reached."
          : `${maxSelections - selectedPositions.length} more selection${maxSelections - selectedPositions.length !== 1 ? 's' : ''} available.`}
      </div>
    </div>
  );
};

export default MultiJobAutocomplete;