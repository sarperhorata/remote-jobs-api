import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getApiUrl } from '../utils/apiConfig';

// Icons temporarily replaced with text
const Search = () => <span>🔍</span>;
const ChevronDown = () => <span>▼</span>;
const X = () => <span>✕</span>;
const Plus = () => <span>+</span>;
const Trash2 = () => <span>🗑️</span>;

interface Position {
  title: string;
  count: number;
  category?: string;
}

interface MultiJobAutocompleteProps {
  selectedPositions: Position[];
  onPositionsChange: (positions: Position[]) => void;
  onSearch?: (positions: Position[]) => void;
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
  const [suggestions, setSuggestions] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();

  // Debug logging
  useEffect(() => {
    console.log('🔄 MultiJobAutocomplete State:', {
      inputValue,
      suggestionsCount: suggestions.length,
      showDropdown,
      isLoading,
      selectedPositions: selectedPositions.map(p => p.title)
    });
  }, [inputValue, suggestions, showDropdown, isLoading, selectedPositions]);

  // Fetch suggestions from API
  const fetchSuggestions = useCallback(async (query: string) => {
    console.log('🔍 Fetching suggestions for:', query);
    
    if (!query || query.length < 2) {
      console.log('❌ Query too short, clearing suggestions');
      setSuggestions([]);
      setShowDropdown(false);
      return;
    }

    setIsLoading(true);
    try {
      const apiUrl = await getApiUrl();
      
      // Safety check: force 8001 if we detect wrong port
      const finalApiUrl = apiUrl.includes('localhost:8002') 
        ? apiUrl.replace('localhost:8002', 'localhost:8001')
        : apiUrl;
      
      console.log('📡 API URL:', finalApiUrl);
      
      const response = await fetch(
        `${finalApiUrl}/jobs/job-titles/search?q=${encodeURIComponent(query)}&limit=20`
      );
      
      console.log('📨 API Response Status:', response.status);
      
      if (!response.ok) {
        console.error(`API request failed with status: ${response.status}`);
        setSuggestions([]);
        setShowDropdown(false);
        return;
      }
      
      const data = await response.json();
      console.log('📦 API Response:', data);
      
      if (!Array.isArray(data)) {
        console.error('API returned non-array data:', data);
        setSuggestions([]);
        setShowDropdown(false);
        return;
      }
      
      const positions = data.map((item: any) => ({
        title: item.title || item,
        count: item.count || 0,
        category: item.category || 'Unknown'
      }));
      
      // Filter out already selected positions
      const filtered = positions.filter((pos: Position) => 
        !selectedPositions.some(selected => 
          selected.title.toLowerCase() === pos.title.toLowerCase()
        )
      );
      
      console.log('✅ Filtered positions:', filtered);
      
      setSuggestions(filtered);
      if (filtered.length > 0) {
        setShowDropdown(true);
      }
    } catch (error) {
      console.error('Error fetching job title suggestions:', error);
      setSuggestions([]);
      setShowDropdown(false);
    } finally {
      setIsLoading(false);
    }
  }, [selectedPositions]);

  // Fetch popular job titles for empty input
  const fetchPopularTitles = useCallback(async () => {
    try {
      const apiUrl = await getApiUrl();
      const finalApiUrl = apiUrl.includes('localhost:8002') 
        ? apiUrl.replace('localhost:8002', 'localhost:8001')
        : apiUrl;
      
      const response = await fetch(`${finalApiUrl}/jobs/statistics`);
      if (response.ok) {
        const data = await response.json();
        const popularTitles = data.positions?.slice(0, 3) || [];
        
        const filtered = popularTitles.filter((pos: Position) => 
          !selectedPositions.some(selected => 
            selected.title.toLowerCase() === pos.title.toLowerCase()
          )
        );
        
        setSuggestions(filtered);
        return filtered.length > 0;
      }
    } catch (error) {
      console.error('Error fetching popular titles:', error);
    }
    
    // Fallback to static popular titles
    const fallbackTitles = [
      { title: 'Software Engineer', count: 1250, category: 'Technology' },
      { title: 'Product Manager', count: 890, category: 'Management' },
      { title: 'Frontend Developer', count: 670, category: 'Technology' }
    ];
    
    const filtered = fallbackTitles.filter((pos: Position) => 
      !selectedPositions.some(selected => 
        selected.title.toLowerCase() === pos.title.toLowerCase()
      )
    );
    
    setSuggestions(filtered);
    return filtered.length > 0;
  }, [selectedPositions]);

  // Handle input focus to show popular titles
  const handleInputFocus = async () => {
    console.log('🎯 Input focused');
    if (!inputValue.trim() && suggestions.length === 0) {
      setIsLoading(true);
      const hasPopular = await fetchPopularTitles();
      setIsLoading(false);
      if (hasPopular) {
        setShowDropdown(true);
      }
    } else if (suggestions.length > 0) {
      setShowDropdown(true);
    }
  };

  // Handle input change with debounce
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    console.log('⌨️ Input changed:', value);
    setInputValue(value);

    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    // Set new timeout for search
    if (value.trim()) {
      console.log('⏱️ Setting debounce timer for search');
      searchTimeoutRef.current = setTimeout(() => {
        console.log('⏰ Debounce timer fired, fetching suggestions');
        fetchSuggestions(value.trim());
      }, 300);
    } else {
      console.log('🧹 Input empty, clearing suggestions');
      setSuggestions([]);
      setShowDropdown(false);
    }
  };

  // Select a position
  const selectPosition = (position: Position) => {
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
    setSuggestions([]);
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

  // Clear all selections
  const clearAll = () => {
    console.log('🗑️ Clearing all selections');
    onPositionsChange([]);
    setInputValue('');
    setSuggestions([]);
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
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        console.log('👆 Click outside detected, closing dropdown');
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

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
              onClick={clearAll}
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

          {/* Dropdown */}
          {showDropdown && (
            <div className="absolute top-full left-0 right-0 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg shadow-lg mt-1 max-h-64 overflow-y-auto z-[9999]">
              {isLoading ? (
                <div className="p-3 text-center text-gray-500 dark:text-gray-400">
                  <div className="animate-spin inline-block w-4 h-4 border-2 border-current border-t-transparent rounded-full mr-2"></div>
                  Searching...
                </div>
              ) : suggestions.length > 0 ? (
                <>
                  {suggestions.map((suggestion, index) => (
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
            </div>
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