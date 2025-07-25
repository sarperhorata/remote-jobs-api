import React, { useState, useRef, useCallback, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { getApiUrl } from '../utils/apiConfig';

interface Position {
  title: string;
  count: number;
  category?: string;
}

interface MultiJobAutocompleteProps {
  onSelect: (positions: Position[]) => void;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

const MultiJobAutocomplete: React.FC<MultiJobAutocompleteProps> = ({
  onSelect,
  placeholder = "Search keywords (e.g., react, python, remote)",
  className,
  disabled = false
}) => {
  const [inputValue, setInputValue] = useState('');
  const [allSuggestions, setAllSuggestions] = useState<Position[]>([]);
  const [selectedKeywords, setSelectedKeywords] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [isFocused, setIsFocused] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0, width: 0 });
  const [animatedPlaceholder, setAnimatedPlaceholder] = useState(placeholder);
  const [placeholderIndex, setPlaceholderIndex] = useState(0);

  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const placeholders = [
    "Search keywords (e.g., react, python, remote)",
    "Add multiple keywords to narrow results",
    "Type and select keywords to search"
  ];

  // Animated placeholder
  useEffect(() => {
    if (isFocused && !inputValue) {
      const interval = setInterval(() => {
        setPlaceholderIndex((prev) => (prev + 1) % placeholders.length);
      }, 3000);
      return () => clearInterval(interval);
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
        selectedKeywordsCount: selectedKeywords.length,
        showDropdown,
        isLoading,
      });
    }
  }, [inputValue, allSuggestions.length, selectedKeywords.length, showDropdown, isLoading]);

  // Fetch keyword count
  const fetchKeywordCount = useCallback(async (query: string) => {
    if (!query.trim()) return null;
    
    try {
      const finalApiUrl = await getApiUrl();
      const response = await fetch(`${finalApiUrl}/jobs/quick-search-count?q=${encodeURIComponent(query)}`);
      if (response.ok) {
        const data = await response.json();
        return data;
      }
    } catch (error) {
      console.error('Error fetching keyword count:', error);
    }
    return null;
  }, []);

  // Handle input focus
  const handleInputFocus = async () => {
    setIsFocused(true);
    updateDropdownPosition();
  };

  // Handle input blur
  const handleInputBlur = () => {
    // Don't close dropdown on blur - let the click outside handler manage this
    // This prevents the dropdown from closing when clicking on suggestions
  };

  // Handle input change
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    
    // Clear previous timeout
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }
    
    if (value.trim().length >= 1) {
      // For keyword search, show single line result
      searchTimeoutRef.current = setTimeout(async () => {
        const keywordResult = await fetchKeywordCount(value);
        if (keywordResult && keywordResult.count > 0) {
          const suggestion = {
            title: `${value} (${keywordResult.count} jobs)`,
            count: keywordResult.count,
            category: 'keyword'
          };
          console.log('🔍 Setting keyword suggestion:', suggestion);
          setAllSuggestions([suggestion]);
          setShowDropdown(true);
        } else {
          setAllSuggestions([]);
          setShowDropdown(false);
        }
      }, 300);
    } else {
      setAllSuggestions([]);
      setShowDropdown(false);
    }
  };

  // Select a position
  const selectPosition = (position: Position) => {
    console.log('🎯 selectPosition called with:', position);
    console.log('🎯 position.category:', position.category);
    console.log('🎯 position.title:', position.title);
    
    // For keyword searches, add to selected keywords
    if (position.category === 'keyword') {
      console.log('🔍 Keyword search detected, adding to selection...');
      const keyword = position.title.split('(')[0].trim();
      const newKeyword = {
        title: keyword,
        count: position.count,
        category: 'keyword'
      };
      
                  // Check if keyword already selected
            const exists = selectedKeywords.find(k => k.title === keyword);
            if (!exists) {
              const updatedKeywords = [...selectedKeywords, newKeyword];
              setSelectedKeywords(updatedKeywords);
              console.log('✅ Added keyword:', keyword, 'Total selected:', updatedKeywords.length);

              // Automatically search when keyword is selected
              onSelect(updatedKeywords);
            } else {
              console.log('⚠️ Keyword already selected:', keyword);
            }
      
      // Clear input and suggestions
      setInputValue('');
      setAllSuggestions([]);
      setShowDropdown(false);
      return;
    }
    
    // For regular job titles, use the normal flow
    console.log('📝 Regular job title selected, calling onSelect...');
    onSelect([position]);
    setInputValue('');
    setAllSuggestions([]);
    setShowDropdown(false);
  };

  // Remove selected keyword
  const removeKeyword = (keywordToRemove: string) => {
    const updatedKeywords = selectedKeywords.filter(k => k.title !== keywordToRemove);
    setSelectedKeywords(updatedKeywords);
    console.log('🗑️ Removed keyword:', keywordToRemove, 'Total selected:', updatedKeywords.length);
    
    // Call onSelect with updated keywords
    onSelect(updatedKeywords);
  };

  // Clear all selected keywords
  const clearAllKeywords = () => {
    setSelectedKeywords([]);
    console.log('🧹 Cleared all keywords');
    onSelect([]);
  };

  // Update dropdown position
  const updateDropdownPosition = useCallback(() => {
    if (containerRef.current) {
      const rect = containerRef.current.getBoundingClientRect();
      setDropdownPosition({
        top: rect.bottom,
        left: rect.left,
        width: rect.width
      });
    }
  }, []);

  // Handle clicks outside dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (containerRef.current && !containerRef.current.contains(event.target as Node)) {
        // Only close dropdown if there are no suggestions
        if (allSuggestions.length === 0) {
          setShowDropdown(false);
        }
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [allSuggestions.length]);

  // Update dropdown position on scroll and resize
  useEffect(() => {
    if (showDropdown) {
      const handleScroll = () => updateDropdownPosition();
      const handleResize = () => updateDropdownPosition();
      
      window.addEventListener('scroll', handleScroll);
      window.addEventListener('resize', handleResize);
      
      return () => {
        window.removeEventListener('scroll', handleScroll);
        window.removeEventListener('resize', handleResize);
      };
    }
  }, [showDropdown, updateDropdownPosition]);

  // RTL text detection
  const isRTL = (text: string): boolean => {
    const rtlRegex = /[\u0591-\u07FF\uFB1D-\uFDFD\uFE70-\uFEFC]/;
    return rtlRegex.test(text);
  };

  // Handle Enter key
  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && allSuggestions.length > 0) {
      e.preventDefault();
      selectPosition(allSuggestions[0]);
    }
  };

  return (
    <div 
      ref={containerRef}
      className={`relative ${className || ''}`}
      style={{ direction: isRTL(inputValue) ? 'rtl' : 'ltr' }}
    >
              {/* Selected Keywords Display */}
        {selectedKeywords.length > 0 && (
          <div className="mb-3">
            <div className="flex flex-wrap gap-2 mb-3">
              {selectedKeywords.map((keyword, index) => (
                <div
                  key={index}
                  className="flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm font-medium"
                >
                  <span>{keyword.title} ({keyword.count})</span>
                  <button
                    onClick={() => removeKeyword(keyword.title)}
                    className="text-blue-600 hover:text-blue-800 font-bold text-lg leading-none"
                  >
                    ×
                  </button>
                </div>
              ))}
              <button
                onClick={clearAllKeywords}
                className="text-gray-500 hover:text-gray-700 text-sm underline"
              >
                Clear all
              </button>
            </div>
            
            {/* Selected Keywords Summary */}
            <div className="w-full bg-gray-50 border border-gray-200 rounded-lg p-3 text-center">
              <span className="text-sm text-gray-600">
                {selectedKeywords.length} keyword{selectedKeywords.length > 1 ? 's' : ''} selected ({selectedKeywords.reduce((sum, k) => sum + k.count, 0)} jobs)
              </span>
            </div>
          </div>
        )}

      <div className="relative">
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={handleInputChange}
          onFocus={handleInputFocus}
          onBlur={handleInputBlur}
          onKeyDown={handleKeyDown}
          placeholder={animatedPlaceholder}
          disabled={disabled}
          className={`
            w-full px-4 py-3 text-lg border-2 border-gray-300 rounded-lg
            focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-200
            transition-all duration-200 ease-in-out
            ${disabled ? 'bg-gray-100 cursor-not-allowed' : 'bg-white'}
            ${isRTL(inputValue) ? 'text-right' : 'text-left'}
          `}
        />
        
        {isLoading && (
          <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
            <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-500"></div>
          </div>
        )}
      </div>

      {/* Dropdown */}
      {showDropdown && allSuggestions.length > 0 && createPortal(
        <div
          ref={dropdownRef}
          className="absolute z-50 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto"
          style={{
            top: dropdownPosition.top + 5,
            left: dropdownPosition.left,
            width: dropdownPosition.width,
            minWidth: '200px'
          }}
        >
          {allSuggestions.map((suggestion, index) => (
            <div
              key={index}
              className="px-4 py-3 hover:bg-gray-50 cursor-pointer border-b border-gray-100 last:border-b-0 transition-colors duration-150"
              onClick={() => {
                console.log('🖱️ Clicked on suggestion:', suggestion);
                selectPosition(suggestion);
              }}
            >
              <div className="flex justify-between items-center">
                <span className="font-medium text-gray-800">
                  {suggestion.title}
                </span>
                <span className="text-sm text-gray-500">
                  {suggestion.count} jobs
                </span>
              </div>
            </div>
          ))}
        </div>,
        document.body
      )}
    </div>
  );
};

export default MultiJobAutocomplete;