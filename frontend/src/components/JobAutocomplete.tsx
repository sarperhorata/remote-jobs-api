import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, ChevronDown } from './icons/EmojiIcons';
import { getApiUrl } from '../utils/apiConfig';

interface Position {
  title: string;
  count: number;
  category?: string;
}

interface JobTitle {
  id?: string;
  title: string;
  count?: number;
  category?: string;
}

interface JobAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect?: (position: Position) => void;
  placeholder?: string;
  maxResults?: number;
}

const JobAutocomplete: React.FC<JobAutocompleteProps> = ({
  value,
  onChange,
  onSelect,
  placeholder = "e.g. Software Engineer, Product Manager, Data Scientist",
  maxResults = 50
}) => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  const [isFocused, setIsFocused] = useState(false);
  const [animatedPlaceholder, setAnimatedPlaceholder] = useState('');
  const [placeholderIndex, setPlaceholderIndex] = useState(0);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const loadingRef = useRef(false);
  const isSelectingRef = useRef(false);

  // Typing animation for placeholder
  useEffect(() => {
    if (!isFocused && !value) {
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
  }, [isFocused, value, placeholder]);

  // Update animated placeholder
  useEffect(() => {
    if (!isFocused && !value) {
      setAnimatedPlaceholder(placeholder.slice(0, placeholderIndex));
    } else {
      setAnimatedPlaceholder(placeholder);
    }
  }, [placeholderIndex, isFocused, value, placeholder]);

  // Stable fetch function that doesn't cause re-renders
  const fetchPositions = useCallback(async (searchValue: string) => {
    console.log('🔍 JobAutocomplete fetchPositions called with:', searchValue);
    
    if (loadingRef.current || searchValue.length < 2) {
      console.log('❌ Skipping fetch - loading or query too short:', { loading: loadingRef.current, queryLength: searchValue.length });
      return;
    }
    
    loadingRef.current = true;
    setIsLoading(true);
    
    try {
      const apiBaseUrl = await getApiUrl();
      const apiUrl = `${apiBaseUrl}/jobs/job-titles/search?q=${encodeURIComponent(searchValue)}&limit=${maxResults}`;
      console.log('🔍 JobAutocomplete API URL:', apiUrl);
      
      const response = await fetch(apiUrl);
      console.log('📡 JobAutocomplete Response status:', response.status);
      
      if (!response.ok) {
        console.error('❌ Failed to fetch job titles, status:', response.status);
        setPositions([]);
        setIsDropdownOpen(false);
        return;
      }
      
      const data: JobTitle[] = await response.json();
      console.log('✅ JobAutocomplete raw API response:', data);
      
      // Convert job titles to position format and limit results
      const formattedPositions = data
        .slice(0, maxResults)
        .map((item: JobTitle) => ({
          title: item.title,
          count: item.count || 1,
          category: item.category || 'Technology'
        }));
      
      console.log('🔄 JobAutocomplete formatted positions:', formattedPositions);
      setPositions(formattedPositions);
      
      if (formattedPositions.length > 0) {
        console.log('✅ Opening dropdown with', formattedPositions.length, 'positions');
        setIsDropdownOpen(true);
        setHighlightedIndex(-1); // Reset highlighted index
      } else {
        console.log('⚠️ No positions found, keeping dropdown closed');
        setIsDropdownOpen(false);
      }
      
    } catch (error) {
      console.error("❌ JobAutocomplete error fetching job titles:", error);
      setPositions([]);
      setIsDropdownOpen(false);
    } finally {
      setIsLoading(false);
      loadingRef.current = false;
    }
  }, [maxResults]);

  // Debounced search effect
  useEffect(() => {
    if (value.length >= 2) {
      const timeoutId = setTimeout(() => {
        fetchPositions(value);
      }, 300);
      
      return () => clearTimeout(timeoutId);
    } else {
      setPositions([]);
      setIsDropdownOpen(false);
      setHighlightedIndex(-1);
    }
  }, [value, fetchPositions]);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isDropdownOpen || positions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < positions.length - 1 ? prev + 1 : 0
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : positions.length - 1);
        break;
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < positions.length) {
          handleSelect(positions[highlightedIndex]);
        }
        break;
      case 'Escape':
        setIsDropdownOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // Handle position selection
  const handleSelect = (position: Position) => {
    console.log('🎯 JobAutocomplete handleSelect called with:', position);
    
    // Set selection flag to prevent outside click interference
    isSelectingRef.current = true;
    
    // Update the input value with selected position
    onChange(position.title);
    
    // Close dropdown and reset state
    setIsDropdownOpen(false);
    setHighlightedIndex(-1);
    setPositions([]);
    
    // Call the onSelect callback if provided
    if (onSelect) {
      onSelect(position);
    }
    
    // Reset selection flag after a small delay
    setTimeout(() => {
      isSelectingRef.current = false;
    }, 100);
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      // Don't close if we're in the middle of selecting
      if (isSelectingRef.current) {
        return;
      }
      
      if (
        isDropdownOpen &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [isDropdownOpen]);

  const handleInputFocus = () => {
    setIsFocused(true);
    if (positions.length > 0 && value.length >= 2) {
      setIsDropdownOpen(true);
    }
  };

  const handleInputBlur = () => {
    setIsFocused(false);
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value;
    onChange(newValue);
    
    // Reset highlight when typing
    setHighlightedIndex(-1);
    
    // Show dropdown if we have positions and enough chars
    if (newValue.length >= 2 && positions.length > 0) {
      setIsDropdownOpen(true);
    }
  };

  return (
    <div className="relative w-full">
      <div className="relative group">
        <Search className={`absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 transition-all duration-300 ${
          isFocused ? 'text-orange-500 scale-110' : 'text-gray-400'
        }`} />
        <input
          ref={inputRef}
          type="text"
          placeholder={animatedPlaceholder}
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm transition-all duration-300 transform hover:scale-[1.02] focus:scale-[1.02] bg-white hover:bg-gray-50 focus:bg-white shadow-sm hover:shadow-md focus:shadow-lg"
        />
        {isLoading && (
          <div className="absolute right-8 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-500"></div>
          </div>
        )}
        <ChevronDown className={`absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 transition-all duration-300 ${
          isDropdownOpen ? 'rotate-180 text-orange-500' : ''
        } ${isFocused ? 'text-orange-500' : ''}`} />
      </div>
      
      {/* Dropdown - Show when open and has content to display */}
      {isDropdownOpen && (positions.length > 0 || isLoading || (value.length >= 2 && !isLoading)) && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto animate-in slide-in-from-top-2 duration-300"
        >
          {isLoading ? (
            // Loading state
            <div className="px-4 py-6 text-center">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-orange-500 mx-auto mb-2"></div>
              <div className="text-sm text-gray-600">Searching for jobs...</div>
            </div>
          ) : positions.length > 0 ? (
            // Results found
            <>
              {positions.map((position, index) => (
                <div
                  key={`${position.title}-${index}`}
                  onMouseDown={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleSelect(position);
                  }}
                  onMouseEnter={() => setHighlightedIndex(index)}
                  className={`px-4 py-3 cursor-pointer flex justify-between items-center hover:bg-gray-50 transition-all duration-200 transform hover:scale-[1.02] ${
                    index === highlightedIndex ? 'bg-orange-50 border-l-4 border-orange-500' : ''
                  } ${index === 0 ? 'rounded-t-lg' : ''} ${index === positions.length - 1 ? 'rounded-b-lg' : 'border-b border-gray-100'}`}
                >
                  <div className="flex-1 text-left">
                    <div className="font-medium text-gray-900 text-sm">
                      {position.title}
                    </div>
                    {position.category && (
                      <div className="text-xs text-gray-500 mt-1">
                        {position.category}
                      </div>
                    )}
                  </div>
                  <div className="ml-3 px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full transition-all duration-200 hover:bg-orange-200 hover:scale-105">
                    {position.count} jobs
                  </div>
                </div>
              ))}
              
              {/* Debug info footer - remove in production */}
              {process.env.NODE_ENV === 'development' && (
                <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 text-xs text-gray-500 text-center">
                  Showing {positions.length} results
                </div>
              )}
            </>
          ) : (
            // No results found
            <div className="px-4 py-6 text-center">
              <div className="text-gray-500 mb-2">
                <svg className="w-8 h-8 mx-auto text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.172 16.172a4 4 0 015.656 0M9 12h6m-6-4h6m2 5.291A7.962 7.962 0 0112 15c-2.34 0-4.47-.881-6.08-2.33" />
                </svg>
              </div>
              <div className="text-sm font-medium text-gray-900 mb-1">No jobs found</div>
              <div className="text-xs text-gray-500">Try different keywords or browse all jobs</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JobAutocomplete; 