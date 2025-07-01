import React, { useState, useEffect, useRef, useCallback } from 'react';
import { Search, ChevronDown } from './icons/EmojiIcons';
import { getApiUrl } from '../utils/apiConfig';

interface Position {
  title: string;
  count: number;
}

interface JobTitle {
  id: string;
  title: string;
  count?: number;
  category?: string;
}

interface JobAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect?: (position: Position) => void;
  placeholder?: string;
}

const JobAutocompleteFixed: React.FC<JobAutocompleteProps> = ({
  value,
  onChange,
  onSelect,
  placeholder = "e.g. Software Engineer, Product Manager, Data Scientist"
}) => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [isDropdownOpen, setIsDropdownOpen] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const loadingRef = useRef(false);

  // Stable fetch function that doesn't cause re-renders
  const fetchPositions = useCallback(async (searchValue: string) => {
    if (loadingRef.current || searchValue.length < 2) {
      return;
    }
    
    loadingRef.current = true;
    setIsLoading(true);
    
    try {
      const apiBaseUrl = await getApiUrl();
      const response = await fetch(`${apiBaseUrl}/jobs/job-titles/search?q=${encodeURIComponent(searchValue)}&limit=20`);
      
      if (!response.ok) {
        console.error('❌ Failed to fetch job titles, status:', response.status);
        setPositions([]);
        setIsDropdownOpen(false);
        return;
      }
      
      const data: JobTitle[] = await response.json();
      console.log('✅ Autocomplete suggestions fetched:', data.length, 'results for:', searchValue);
      
      // Convert job titles to position format
      const formattedPositions = data.map((item: JobTitle) => ({
        title: item.title,
        count: item.count || 1,
        category: item.category || 'Technology'
      }));
      
      setPositions(formattedPositions);
      if (formattedPositions.length > 0) {
        setIsDropdownOpen(true);
      }
      
    } catch (error) {
      console.error("Error fetching job titles:", error);
      setPositions([]);
      setIsDropdownOpen(false);
    } finally {
      setIsLoading(false);
      loadingRef.current = false;
    }
  }, []);

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
    }
  }, [value, fetchPositions]);

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isDropdownOpen || positions.length === 0) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < positions.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => prev > 0 ? prev - 1 : -1);
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
    onChange(position.title);
    setIsDropdownOpen(false);
    setHighlightedIndex(-1);
    onSelect?.(position);
    inputRef.current?.blur();
  };

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        !inputRef.current?.contains(event.target as Node)
      ) {
        setIsDropdownOpen(false);
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div className="relative w-full">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
        <input
          ref={inputRef}
          type="text"
          placeholder={placeholder}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={() => {
            if (positions.length > 0 && value.length >= 2) {
              setIsDropdownOpen(true);
            }
          }}
          className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
        />
        {isLoading && (
          <div className="absolute right-8 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-orange-500"></div>
          </div>
        )}
        <ChevronDown className={`absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4 transition-transform ${isDropdownOpen ? 'rotate-180' : ''}`} />
      </div>
      
      {/* Dropdown - Show only if open and has positions */}
      {isDropdownOpen && positions.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-xl max-h-60 overflow-y-auto"
        >
          {positions.slice(0, 8).map((position, index) => (
            <div
              key={`${position.title}-${index}`}
              onClick={() => handleSelect(position)}
              onMouseEnter={() => setHighlightedIndex(index)}
              className={`px-4 py-3 cursor-pointer flex justify-between items-center hover:bg-gray-50 text-left ${
                index === highlightedIndex ? 'bg-orange-50 border-l-4 border-orange-500' : ''
              } ${index === 0 ? 'rounded-t-lg' : ''} ${index === Math.min(7, positions.length - 1) ? 'rounded-b-lg' : 'border-b border-gray-100'}`}
            >
              <div className="flex-1 text-left">
                <div className="font-medium text-gray-900 text-sm text-left">
                  {position.title}
                </div>
              </div>
              <div className="ml-3 px-2 py-1 bg-orange-100 text-orange-700 text-xs font-medium rounded-full">
                {position.count} jobs
              </div>
            </div>
          ))}
          
          {/* Show "showing X of Y" footer */}
          {positions.length > 8 && (
            <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 text-xs text-gray-500 text-center">
              Showing 8 of {positions.length} matches
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default JobAutocompleteFixed; 