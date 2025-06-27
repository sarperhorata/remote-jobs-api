import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, X } from './icons/EmojiIcons';

interface FilterBarProps {
  filters: {
    location?: string;
    type?: string[];
    category?: string;
    company?: string;
    [key: string]: any;
  };
  onFilterChange: (filters: any) => void;
}

export const FilterBar: React.FC<FilterBarProps> = ({ filters, onFilterChange }) => {
  const [isTypeDropdownOpen, setIsTypeDropdownOpen] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);
  
  const locations = ['Remote', 'US Remote', 'Europe Remote', 'Asia Pacific Remote'];
  const types = ['Full-time', 'Part-time', 'Contract', 'Freelance', 'Internship', 'Temporary'];
  const categories = ['Software Development', 'Data Science', 'DevOps', 'Product Management', 'UX/UI Design'];

  const selectedTypes = filters.type || [];

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsTypeDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  const handleTypeToggle = (type: string) => {
    const currentTypes = [...selectedTypes];
    const index = currentTypes.indexOf(type);
    
    if (index > -1) {
      currentTypes.splice(index, 1);
    } else {
      currentTypes.push(type);
    }
    
    onFilterChange({ ...filters, type: currentTypes });
  };

  const removeType = (type: string) => {
    const newTypes = selectedTypes.filter(t => t !== type);
    onFilterChange({ ...filters, type: newTypes });
  };

  const clearAllTypes = () => {
    onFilterChange({ ...filters, type: [] });
  };

  return (
    <div className="bg-white p-4 rounded-lg shadow-sm border border-gray-200">
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Location
          </label>
          <select
            value={filters.location || ''}
            onChange={(e) => onFilterChange({ ...filters, location: e.target.value })}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Locations</option>
            {locations.map((location) => (
              <option key={location} value={location}>
                {location}
              </option>
            ))}
          </select>
        </div>

        <div className="relative" ref={dropdownRef}>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Job Type
          </label>
          <button
            type="button"
            onClick={() => setIsTypeDropdownOpen(!isTypeDropdownOpen)}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500 bg-white text-left flex items-center justify-between"
          >
            <span className="text-gray-900">
              {selectedTypes.length === 0 ? 'All Types' : `${selectedTypes.length} selected`}
            </span>
            <ChevronDown className={`w-4 h-4 transition-transform ${isTypeDropdownOpen ? 'rotate-180' : ''}`} />
          </button>
          
          {isTypeDropdownOpen && (
            <div className="absolute z-10 mt-1 w-full bg-white border border-gray-300 rounded-md shadow-lg">
              <div className="py-1">
                {types.map((type) => (
                  <label key={type} className="flex items-center px-3 py-2 hover:bg-gray-50 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={selectedTypes.includes(type)}
                      onChange={() => handleTypeToggle(type)}
                      className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                    />
                    <span className="text-sm text-gray-900">{type}</span>
                  </label>
                ))}
                {selectedTypes.length > 0 && (
                  <div className="border-t border-gray-100 px-3 py-2">
                    <button
                      onClick={clearAllTypes}
                      className="text-sm text-red-600 hover:text-red-800"
                    >
                      Clear all
                    </button>
                  </div>
                )}
              </div>
            </div>
          )}
          
          {/* Selected Types Display */}
          {selectedTypes.length > 0 && (
            <div className="mt-2 flex flex-wrap gap-1">
              {selectedTypes.map((type) => (
                <span
                  key={type}
                  className="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                >
                  {type}
                  <button
                    type="button"
                    onClick={() => removeType(type)}
                    className="ml-1 h-3 w-3 rounded-full inline-flex items-center justify-center text-blue-400 hover:bg-blue-200 hover:text-blue-600 focus:outline-none"
                  >
                    <X className="h-2 w-2" />
                  </button>
                </span>
              ))}
            </div>
          )}
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Category
          </label>
          <select
            value={filters.category || ''}
            onChange={(e) => onFilterChange({ ...filters, category: e.target.value })}
            className="block w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">All Categories</option>
            {categories.map((category) => (
              <option key={category} value={category}>
                {category}
              </option>
            ))}
          </select>
        </div>
      </div>
    </div>
  );
}; 