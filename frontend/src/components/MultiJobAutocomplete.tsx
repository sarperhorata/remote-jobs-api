import React, { useState, useEffect, useRef, useCallback } from 'react';
import { API_BASE_URL } from '../utils/apiConfig';

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
  selectedPositions,
  onPositionsChange,
  onSearch,
  placeholder = "Search and select job titles (up to 10)",
  maxSelections = 10
}) => {
  const [inputValue, setInputValue] = useState('');
  const [positions, setPositions] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [isOpen, setIsOpen] = useState(false);
  const [highlightedIndex, setHighlightedIndex] = useState(-1);
  
  const dropdownRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout | null>(null);

  const fetchPositions = useCallback(async (query: string) => {
    if (!query.trim() || query.length < 2) {
      setPositions([]);
      return;
    }

    setIsLoading(true);
    try {
      const apiUrl = API_BASE_URL + '/jobs/job-titles/search';
      console.log('🔍 MultiAutocomplete API URL:', apiUrl);
      const response = await fetch(apiUrl);
      
      if (response.ok) {
        const data = await response.json();
        // Backend returns array directly, not nested in job_titles
        const positions = Array.isArray(data) ? data : data.job_titles || [];
        // Ensure each position has required fields
        const formattedPositions = positions.map((item: any) => ({
          title: item.title,
          count: item.count || 1,
          category: item.category || 'Technology'
        }));
        console.log('🔍 MultiAutocomplete formatted positions:', formattedPositions);
        setPositions(formattedPositions);
      } else {
        console.error('❌ Failed to fetch job titles, status:', response.status);
        setPositions([]);
      }
    } catch (error) {
      console.error('❌ Error fetching job titles:', error);
      console.error('❌ API_BASE_URL:', API_BASE_URL);
      setPositions([]);
    } finally {
      setIsLoading(false);
    }
  }, []);

  // Debounced search effect
  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (inputValue.trim()) {
      searchTimeoutRef.current = setTimeout(() => {
        fetchPositions(inputValue);
      }, 300);
    } else {
      setPositions([]);
    }

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [inputValue, fetchPositions]);

  // Handle input changes
  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setInputValue(value);
    setIsOpen(true);
    setHighlightedIndex(-1);
  };

  // Handle position selection
  const handlePositionSelect = (position: Position) => {
    // Check if position is already selected
    if (selectedPositions.find(p => p.title.toLowerCase() === position.title.toLowerCase())) {
      return; // Already selected
    }

    // Check max selections
    if (selectedPositions.length >= maxSelections) {
      alert(`Maximum ${maxSelections} positions can be selected.`);
      return;
    }

    // Add position to selected list
    const newSelectedPositions = [...selectedPositions, position];
    onPositionsChange(newSelectedPositions);
    
    // Clear input and close dropdown
    setInputValue('');
    setIsOpen(false);
    setPositions([]);
    
    // Focus back to input
    setTimeout(() => {
      inputRef.current?.focus();
    }, 100);
  };

  // Remove selected position
  const removePosition = (positionToRemove: Position) => {
    const newSelectedPositions = selectedPositions.filter(
      p => p.title.toLowerCase() !== positionToRemove.title.toLowerCase()
    );
    onPositionsChange(newSelectedPositions);
  };

  // Clear all selections
  const clearAllSelections = () => {
    onPositionsChange([]);
    setInputValue('');
    setIsOpen(false);
    setPositions([]);
  };

  // Handle keyboard navigation
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (!isOpen) return;

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev < positions.length - 1 ? prev + 1 : 0
        );
        break;
      
      case 'ArrowUp':
        e.preventDefault();
        setHighlightedIndex(prev => 
          prev > 0 ? prev - 1 : positions.length - 1
        );
        break;
      
      case 'Enter':
        e.preventDefault();
        if (highlightedIndex >= 0 && highlightedIndex < positions.length) {
          handlePositionSelect(positions[highlightedIndex]);
        }
        break;
      
      case 'Escape':
        setIsOpen(false);
        setHighlightedIndex(-1);
        break;
    }
  };

  // Handle search button click
  const handleSearch = () => {
    if (selectedPositions.length === 0) {
      alert('Please select at least one job position to search.');
      return;
    }
    
    if (onSearch) {
      onSearch(selectedPositions);
    }
  };

  // Click outside to close dropdown
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
        setHighlightedIndex(-1);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Filter out already selected positions
  const availablePositions = positions.filter(
    pos => !selectedPositions.find(selected => 
      selected.title.toLowerCase() === pos.title.toLowerCase()
    )
  );

  return (
    <div className="w-full" ref={dropdownRef}>
      {/* Selected positions display */}
      {selectedPositions.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">
              Selected Positions ({selectedPositions.length}/{maxSelections}):
            </span>
            <button
              onClick={clearAllSelections}
              className="text-xs text-red-600 hover:text-red-700 flex items-center gap-1"
            >
              <Trash2 />
              Clear All
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {selectedPositions.map((position, index) => (
              <div
                key={index}
                className="flex items-center gap-2 bg-blue-100 text-blue-800 px-3 py-1 rounded-full text-sm"
              >
                <span className="truncate max-w-40">{position.title}</span>
                {position.count && (
                  <span className="text-blue-600 text-xs">({position.count})</span>
                )}
                <button
                  onClick={() => removePosition(position)}
                  className="text-blue-600 hover:text-blue-800 flex-shrink-0"
                >
                  <X />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Search input */}
      <div className="relative">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <div className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 flex items-center justify-center">
              <Search />
            </div>
            <input
              ref={inputRef}
              type="text"
              value={inputValue}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setIsOpen(true)}
              placeholder={placeholder}
              className="w-full pl-10 pr-10 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
              disabled={selectedPositions.length >= maxSelections}
            />
            
            {isLoading && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2">
                <div className="w-5 h-5 border-2 border-blue-500 border-t-transparent rounded-full animate-spin"></div>
              </div>
            )}
            
            {!isLoading && positions.length > 0 && (
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5 flex items-center justify-center">
                <ChevronDown />
              </div>
            )}
          </div>
          
          <button
            onClick={handleSearch}
            disabled={selectedPositions.length === 0}
            className="px-6 py-3 bg-gradient-to-r from-orange-500 to-yellow-500 text-white rounded-lg hover:from-orange-600 hover:to-yellow-600 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors font-medium flex items-center gap-2"
          >
            <Search />
            Search
          </button>
        </div>

        {/* Dropdown */}
        {isOpen && (
          <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-lg shadow-lg max-h-60 overflow-y-auto">
            {isLoading ? (
              <div className="p-4 text-center text-gray-500">
                <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
                Searching positions...
              </div>
            ) : availablePositions.length > 0 ? (
              <>
                <div className="px-3 py-2 text-xs text-gray-500 border-b border-gray-100">
                  {availablePositions.length} position{availablePositions.length !== 1 ? 's' : ''} found
                </div>
                {availablePositions.map((position, index) => (
                  <button
                    key={index}
                    onClick={() => handlePositionSelect(position)}
                    className={`w-full px-4 py-3 text-left hover:bg-gray-50 flex items-center justify-between group ${
                      index === highlightedIndex ? 'bg-blue-50' : ''
                    }`}
                  >
                    <div className="flex-1 min-w-0">
                      <div className="font-medium text-gray-900 truncate">
                        {position.title}
                      </div>
                      {position.category && (
                        <div className="text-sm text-gray-500">
                          {position.category}
                        </div>
                      )}
                    </div>
                    <div className="flex items-center gap-2 ml-3">
                      {position.count && (
                        <span className="text-sm text-gray-500">
                          {position.count} jobs
                        </span>
                      )}
                      <Plus />
                    </div>
                  </button>
                ))}
              </>
            ) : inputValue.trim().length >= 2 && !isLoading ? (
              <div className="p-4 text-center text-gray-500">
                <div className="w-6 h-6 mx-auto mb-2 text-gray-300 flex items-center justify-center">
                  <Search />
                </div>
                No positions found for "{inputValue}"
              </div>
            ) : inputValue.trim().length > 0 && inputValue.trim().length < 2 ? (
              <div className="p-4 text-center text-gray-500">
                Type at least 2 characters to search
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* Help text */}
      <div className="mt-2 text-xs text-gray-500">
        {selectedPositions.length === 0 ? (
          "Start typing to search job positions. You can select up to " + maxSelections + " positions."
        ) : (
          `${selectedPositions.length}/${maxSelections} positions selected. ${selectedPositions.length === maxSelections ? 'Maximum reached.' : 'Add more or search now.'}`
        )}
      </div>
    </div>
  );
};

export default MultiJobAutocomplete; 