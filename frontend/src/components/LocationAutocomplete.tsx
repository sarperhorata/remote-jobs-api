import React, { useState, useRef, useCallback, useEffect } from 'react';
import { createPortal } from 'react-dom';
import { getApiUrl } from '../utils/apiConfig';

interface Location {
  name: string;
  country?: string;
  type?: 'city' | 'country' | 'continent' | 'remote' | 'worldwide';
  cached_at?: string;
  flag?: string;
}

interface LocationAutocompleteProps {
  onSelect?: (location: Location | null) => void;
  onLocationChange?: (location: Location | null) => void;
  selectedLocation?: Location | null;
  placeholder?: string;
  className?: string;
  disabled?: boolean;
}

// Country flag emojis
const countryFlags: { [key: string]: string } = {
  'united states': '🇺🇸',
  'usa': '🇺🇸',
  'us': '🇺🇸',
  'united kingdom': '🇬🇧',
  'uk': '🇬🇧',
  'germany': '🇩🇪',
  'deutschland': '🇩🇪',
  'canada': '🇨🇦',
  'france': '🇫🇷',
  'spain': '🇪🇸',
  'italy': '🇮🇹',
  'netherlands': '🇳🇱',
  'sweden': '🇸🇪',
  'norway': '🇳🇴',
  'denmark': '🇩🇰',
  'finland': '🇫🇮',
  'switzerland': '🇨🇭',
  'austria': '🇦🇹',
  'belgium': '🇧🇪',
  'poland': '🇵🇱',
  'czech republic': '🇨🇿',
  'hungary': '🇭🇺',
  'romania': '🇷🇴',
  'bulgaria': '🇧🇬',
  'greece': '🇬🇷',
  'portugal': '🇵🇹',
  'ireland': '🇮🇪',
  'australia': '🇦🇺',
  'new zealand': '🇳🇿',
  'japan': '🇯🇵',
  'south korea': '🇰🇷',
  'singapore': '🇸🇬',
  'india': '🇮🇳',
  'brazil': '🇧🇷',
  'mexico': '🇲🇽',
  'argentina': '🇦🇷',
  'chile': '🇨🇱',
  'colombia': '🇨🇴',
  'peru': '🇵🇪',
  'venezuela': '🇻🇪',
  'uruguay': '🇺🇾',
  'paraguay': '🇵🇾',
  'bolivia': '🇧🇴',
  'ecuador': '🇪🇨',
  'guyana': '🇬🇾',
  'suriname': '🇸🇷',
  'french guiana': '🇬🇫',
  'russia': '🇷🇺',
  'ukraine': '🇺🇦',
  'belarus': '🇧🇾',
  'moldova': '🇲🇩',
  'latvia': '🇱🇻',
  'lithuania': '🇱🇹',
  'estonia': '🇪🇪',
  'georgia': '🇬🇪',
  'armenia': '🇦🇲',
  'azerbaijan': '🇦🇿',
  'kazakhstan': '🇰🇿',
  'uzbekistan': '🇺🇿',
  'turkmenistan': '🇹🇲',
  'kyrgyzstan': '🇰🇬',
  'tajikistan': '🇹🇯',
  'china': '🇨🇳',
  'taiwan': '🇹🇼',
  'hong kong': '🇭🇰',
  'macau': '🇲🇴',
  'mongolia': '🇲🇳',
  'north korea': '🇰🇵',
  'vietnam': '🇻🇳',
  'thailand': '🇹🇭',
  'malaysia': '🇲🇾',
  'indonesia': '🇮🇩',
  'philippines': '🇵🇭',
  'cambodia': '🇰🇭',
  'laos': '🇱🇦',
  'myanmar': '🇲🇲',
  'brunei': '🇧🇳',
  'east timor': '🇹🇱',
  'pakistan': '🇵🇰',
  'bangladesh': '🇧🇩',
  'sri lanka': '🇱🇰',
  'nepal': '🇳🇵',
  'bhutan': '🇧🇹',
  'maldives': '🇲🇻',
  'afghanistan': '🇦🇫',
  'iran': '🇮🇷',
  'iraq': '🇮🇶',
  'syria': '🇸🇾',
  'lebanon': '🇱🇧',
  'jordan': '🇯🇴',
  'israel': '🇮🇱',
  'palestine': '🇵🇸',
  'saudi arabia': '🇸🇦',
  'yemen': '🇾🇪',
  'oman': '🇴🇲',
  'uae': '🇦🇪',
  'united arab emirates': '🇦🇪',
  'qatar': '🇶🇦',
  'kuwait': '🇰🇼',
  'bahrain': '🇧🇭',
  'egypt': '🇪🇬',
  'libya': '🇱🇾',
  'tunisia': '🇹🇳',
  'algeria': '🇩🇿',
  'morocco': '🇲🇦',
  'sudan': '🇸🇩',
  'south sudan': '🇸🇸',
  'ethiopia': '🇪🇹',
  'somalia': '🇸🇴',
  'djibouti': '🇩🇯',
  'eritrea': '🇪🇷',
  'kenya': '🇰🇪',
  'tanzania': '🇹🇿',
  'uganda': '🇺🇬',
  'rwanda': '🇷🇼',
  'burundi': '🇧🇮',
  'congo': '🇨🇬',
  'dr congo': '🇨🇩',
  'democratic republic of the congo': '🇨🇩',
  'central african republic': '🇨🇫',
  'chad': '🇹🇩',
  'cameroon': '🇨🇲',
  'gabon': '🇬🇦',
  'equatorial guinea': '🇬🇶',
  'sao tome and principe': '🇸🇹',
  'nigeria': '🇳🇬',
  'niger': '🇳🇪',
  'mali': '🇲🇱',
  'burkina faso': '🇧🇫',
  'senegal': '🇸🇳',
  'gambia': '🇬🇲',
  'guinea-bissau': '🇬🇼',
  'guinea': '🇬🇳',
  'sierra leone': '🇸🇱',
  'liberia': '🇱🇷',
  'ivory coast': '🇨🇮',
  'cote d\'ivoire': '🇨🇮',
  'ghana': '🇬🇭',
  'togo': '🇹🇬',
  'benin': '🇧🇯',
  'angola': '🇦🇴',
  'namibia': '🇳🇦',
  'botswana': '🇧🇼',
  'zimbabwe': '🇿🇼',
  'zambia': '🇿🇲',
  'malawi': '🇲🇼',
  'mozambique': '🇲🇿',
  'madagascar': '🇲🇬',
  'mauritius': '🇲🇺',
  'seychelles': '🇸🇨',
  'comoros': '🇰🇲',
  'mayotte': '🇾🇹',
  'reunion': '🇷🇪',
  'south africa': '🇿🇦',
  'lesotho': '🇱🇸',
  'eswatini': '🇸🇿',
  'swaziland': '🇸🇿',
  'turkey': '🇹🇷',
  'türkiye': '🇹🇷'
};

// Get flag emoji for location
const getFlagEmoji = (locationName: string, locationType?: string): string => {
  if (locationType === 'remote') return '🌍';
  
  const name = locationName.toLowerCase();
  
  // Check exact match first
  if (countryFlags[name]) {
    return countryFlags[name];
  }
  
  // Check partial matches
  for (const [country, flag] of Object.entries(countryFlags)) {
    if (name.includes(country) || country.includes(name)) {
      return flag;
    }
  }
  
  // Default flags for continents/regions
  if (name.includes('europe')) return '🇪🇺';
  if (name.includes('asia')) return '🌏';
  if (name.includes('africa')) return '🌍';
  if (name.includes('america')) return '🌎';
  if (name.includes('oceania')) return '🌏';
  
  // Default for cities
  return '🏙️';
};

// Capitalize first letter only
const capitalizeFirst = (str: string): string => {
  return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
};

const LocationAutocomplete: React.FC<LocationAutocompleteProps> = ({
  onSelect,
  onLocationChange,
  selectedLocation,
  placeholder = "Location",
  className,
  disabled = false
}) => {
  const [inputValue, setInputValue] = useState(selectedLocation?.name || '');
  const [suggestions, setSuggestions] = useState<Location[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [showDropdown, setShowDropdown] = useState(false);
  const [dropdownPosition, setDropdownPosition] = useState({ top: 0, left: 0, width: 0 });
  const [isFocused, setIsFocused] = useState(false);
  const [isCached, setIsCached] = useState(false);
  const [searchValue, setSearchValue] = useState('');
  
  const containerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLButtonElement>(null);
  const searchTimeoutRef = useRef<NodeJS.Timeout>();
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Update inputValue when selectedLocation changes
  useEffect(() => {
    setInputValue(selectedLocation?.name || '');
  }, [selectedLocation]);

  // Default locations list
  const defaultLocations: Location[] = [
    { name: '🌍 Worldwide', type: 'worldwide' },
    { name: '🌍 Europe', type: 'continent' },
    { name: '🌍 North America', type: 'continent' },
    { name: '🌍 Asia', type: 'continent' },
    { name: '🌍 South America', type: 'continent' },
    { name: '🌍 Africa', type: 'continent' },
    { name: '🌍 Oceania', type: 'continent' },
    { name: '🇹🇷 Türkiye', type: 'country' },
    { name: '🇺🇸 United States', type: 'country' },
    { name: '🇬🇧 United Kingdom', type: 'country' },
    { name: '🇩🇪 Germany', type: 'country' },
    { name: '🇫🇷 France', type: 'country' },
    { name: '🇳🇱 Netherlands', type: 'country' },
    { name: '🇨🇦 Canada', type: 'country' },
    { name: '🇦🇺 Australia', type: 'country' },
    { name: '🇯🇵 Japan', type: 'country' },
    { name: '🇸🇬 Singapore', type: 'country' },
    { name: '🇧🇷 Brazil', type: 'country' },
    { name: '🇲🇽 Mexico', type: 'country' },
    { name: '🇿🇦 South Africa', type: 'country' },
    { name: '🇪🇸 Spain', type: 'country' },
    { name: '🇮🇹 Italy', type: 'country' },
    { name: '🇸🇪 Sweden', type: 'country' },
    { name: '🇳🇴 Norway', type: 'country' },
    { name: '🇩🇰 Denmark', type: 'country' },
    { name: '🇫🇮 Finland', type: 'country' },
    { name: '🇨🇭 Switzerland', type: 'country' },
    { name: '🇦🇹 Austria', type: 'country' },
    { name: '🇧🇪 Belgium', type: 'country' },
    { name: '🇵🇱 Poland', type: 'country' },
    { name: '🇨🇿 Czech Republic', type: 'country' },
    { name: '🇭🇺 Hungary', type: 'country' },
    { name: '🇷🇴 Romania', type: 'country' },
    { name: '🇧🇬 Bulgaria', type: 'country' },
    { name: '🇬🇷 Greece', type: 'country' },
    { name: '🇵🇹 Portugal', type: 'country' },
    { name: '🇮🇪 Ireland', type: 'country' },
    { name: '🇳🇿 New Zealand', type: 'country' },
    { name: '🇰🇷 South Korea', type: 'country' },
    { name: '🇮🇳 India', type: 'country' },
    { name: '🇦🇷 Argentina', type: 'country' },
    { name: '🇨🇱 Chile', type: 'country' },
    { name: '🇨🇴 Colombia', type: 'country' },
    { name: '🇵🇪 Peru', type: 'country' },
    { name: '🇻🇪 Venezuela', type: 'country' },
    { name: '🇺🇾 Uruguay', type: 'country' },
    { name: '🇵🇾 Paraguay', type: 'country' },
    { name: '🇧🇴 Bolivia', type: 'country' },
    { name: '🇪🇨 Ecuador', type: 'country' },
    { name: '🇷🇺 Russia', type: 'country' },
    { name: '🇺🇦 Ukraine', type: 'country' },
    { name: '🇧🇾 Belarus', type: 'country' },
    { name: '🇲🇩 Moldova', type: 'country' },
    { name: '🇱🇻 Latvia', type: 'country' },
    { name: '🇱🇹 Lithuania', type: 'country' },
    { name: '🇪🇪 Estonia', type: 'country' },
    { name: '🇬🇪 Georgia', type: 'country' },
    { name: '🇦🇲 Armenia', type: 'country' },
    { name: '🇦🇿 Azerbaijan', type: 'country' },
    { name: '🇰🇿 Kazakhstan', type: 'country' },
    { name: '🇺🇿 Uzbekistan', type: 'country' },
    { name: '🇹🇲 Turkmenistan', type: 'country' },
    { name: '🇰🇬 Kyrgyzstan', type: 'country' },
    { name: '🇹🇯 Tajikistan', type: 'country' },
    { name: '🇨🇳 China', type: 'country' },
    { name: '🇹🇼 Taiwan', type: 'country' },
    { name: '🇭🇰 Hong Kong', type: 'country' },
    { name: '🇲🇴 Macau', type: 'country' },
    { name: '🇲🇳 Mongolia', type: 'country' },
    { name: '🇰🇵 North Korea', type: 'country' },
    { name: '🇻🇳 Vietnam', type: 'country' },
    { name: '🇹🇭 Thailand', type: 'country' },
    { name: '🇲🇾 Malaysia', type: 'country' },
    { name: '🇮🇩 Indonesia', type: 'country' },
    { name: '🇵🇭 Philippines', type: 'country' },
    { name: '🇰🇭 Cambodia', type: 'country' },
    { name: '🇱🇦 Laos', type: 'country' },
    { name: '🇲🇲 Myanmar', type: 'country' },
    { name: '🇧🇳 Brunei', type: 'country' },
    { name: '🇹🇱 East Timor', type: 'country' },
    { name: '🇵🇰 Pakistan', type: 'country' },
    { name: '🇧🇩 Bangladesh', type: 'country' },
    { name: '🇱🇰 Sri Lanka', type: 'country' },
    { name: '🇳🇵 Nepal', type: 'country' },
    { name: '🇧🇹 Bhutan', type: 'country' },
    { name: '🇲🇻 Maldives', type: 'country' },
    { name: '🇦🇫 Afghanistan', type: 'country' },
    { name: '🇮🇷 Iran', type: 'country' },
    { name: '🇮🇶 Iraq', type: 'country' },
    { name: '🇸🇾 Syria', type: 'country' },
    { name: '🇱🇧 Lebanon', type: 'country' },
    { name: '🇯🇴 Jordan', type: 'country' },
    { name: '🇮🇱 Israel', type: 'country' },
    { name: '🇵🇸 Palestine', type: 'country' },
    { name: '🇸🇦 Saudi Arabia', type: 'country' },
    { name: '🇾🇪 Yemen', type: 'country' },
    { name: '🇴🇲 Oman', type: 'country' },
    { name: '🇦🇪 United Arab Emirates', type: 'country' },
    { name: '🇶🇦 Qatar', type: 'country' },
    { name: '🇰🇼 Kuwait', type: 'country' },
    { name: '🇧🇭 Bahrain', type: 'country' },
    { name: '🇪🇬 Egypt', type: 'country' },
    { name: '🇱🇾 Libya', type: 'country' },
    { name: '🇹🇳 Tunisia', type: 'country' },
    { name: '🇩🇿 Algeria', type: 'country' },
    { name: '🇲🇦 Morocco', type: 'country' },
    { name: '🇸🇩 Sudan', type: 'country' },
    { name: '🇸🇸 South Sudan', type: 'country' },
    { name: '🇪🇹 Ethiopia', type: 'country' },
    { name: '🇸🇴 Somalia', type: 'country' },
    { name: '🇩🇯 Djibouti', type: 'country' },
    { name: '🇪🇷 Eritrea', type: 'country' },
    { name: '🇰🇪 Kenya', type: 'country' },
    { name: '🇹🇿 Tanzania', type: 'country' },
    { name: '🇺🇬 Uganda', type: 'country' },
    { name: '🇷🇼 Rwanda', type: 'country' },
    { name: '🇧🇮 Burundi', type: 'country' },
    { name: '🇨🇬 Congo', type: 'country' },
    { name: '🇨🇩 Democratic Republic of the Congo', type: 'country' },
    { name: '🇨🇫 Central African Republic', type: 'country' },
    { name: '🇹🇩 Chad', type: 'country' },
    { name: '🇨🇲 Cameroon', type: 'country' },
    { name: '🇬🇦 Gabon', type: 'country' },
    { name: '🇬🇶 Equatorial Guinea', type: 'country' },
    { name: '🇸🇹 Sao Tome and Principe', type: 'country' },
    { name: '🇳🇬 Nigeria', type: 'country' },
    { name: '🇳🇪 Niger', type: 'country' },
    { name: '🇲🇱 Mali', type: 'country' },
    { name: '🇧🇫 Burkina Faso', type: 'country' },
    { name: '🇸🇳 Senegal', type: 'country' },
    { name: '🇬🇲 Gambia', type: 'country' },
    { name: '🇬🇼 Guinea-Bissau', type: 'country' },
    { name: '🇬🇳 Guinea', type: 'country' },
    { name: '🇸🇱 Sierra Leone', type: 'country' },
    { name: '🇱🇷 Liberia', type: 'country' },
    { name: '🇨🇮 Ivory Coast', type: 'country' },
    { name: '🇬🇭 Ghana', type: 'country' },
    { name: '🇹🇬 Togo', type: 'country' },
    { name: '🇧🇯 Benin', type: 'country' },
    { name: '🇦🇴 Angola', type: 'country' },
    { name: '🇳🇦 Namibia', type: 'country' },
    { name: '🇧🇼 Botswana', type: 'country' },
    { name: '🇿🇼 Zimbabwe', type: 'country' },
    { name: '🇿🇲 Zambia', type: 'country' },
    { name: '🇲🇼 Malawi', type: 'country' },
    { name: '🇲🇿 Mozambique', type: 'country' },
    { name: '🇲�� Madagascar', type: 'country' },
    { name: '🇲🇺 Mauritius', type: 'country' },
    { name: '🇸🇨 Seychelles', type: 'country' },
    { name: '🇰🇲 Comoros', type: 'country' },
    { name: '🇾🇹 Mayotte', type: 'country' },
    { name: '🇷🇪 Reunion', type: 'country' },
    { name: '🇱🇸 Lesotho', type: 'country' },
    { name: '🇸🇿 Eswatini', type: 'country' }
  ];

  // Handle dropdown toggle
  const handleDropdownToggle = () => {
    if (!showDropdown) {
      setSuggestions(defaultLocations);
      setSearchValue('');
    }
    setShowDropdown(!showDropdown);
  };

  // Handle search input change
  const handleSearchChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setSearchValue(value);
    
    if (!value.trim()) {
      setSuggestions(defaultLocations);
      return;
    }
    
    // Filter default locations based on search
    const filtered = defaultLocations.filter(location => 
      location.name.toLowerCase().includes(value.toLowerCase())
    );
    setSuggestions(filtered);
  };

  // Detect user's country on component mount - REMOVED AUTO-SELECTION
  useEffect(() => {
    // No longer auto-select user's country
    // User will manually select from dropdown
  }, []);

  // Fetch suggestions when user types - REMOVED API CALLS
  const fetchSuggestions = useCallback(async (query: string) => {
    // No longer needed - using static list
  }, []);

  // Handle input focus - REMOVED
  const handleInputFocus = useCallback(() => {
    // No longer needed
  }, []);

  const handleInputBlur = () => {
    // No longer needed
  };

  // Handle input change - REMOVED
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    // No longer needed
  }, []);

  const selectLocation = (location: Location) => {
    onSelect?.(location);
    onLocationChange?.(location);
    setInputValue(capitalizeFirst(location.name));
    setSuggestions([]);
    setShowDropdown(false);
    setSearchValue('');
    
    // Focus input after selection
    setTimeout(() => {
      inputRef.current?.blur();
    }, 100);
  };

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        containerRef.current && 
        !containerRef.current.contains(event.target as Node) &&
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node)
      ) {
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
    <div className={`w-full ${className || ''}`} ref={containerRef}>
      {/* Location dropdown button */}
      <button
        ref={inputRef}
        onClick={handleDropdownToggle}
        className="w-full px-4 py-3 pr-10 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent bg-white dark:bg-gray-800 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 disabled:bg-gray-100 dark:disabled:bg-gray-700 disabled:cursor-not-allowed transition-all duration-300 transform hover:scale-[1.02] focus:scale-[1.02] shadow-sm hover:shadow-md focus:shadow-lg flex items-center justify-between"
      >
        <div className="flex items-center space-x-2">
          {inputValue ? (
            <>
              <span className="text-lg">{getFlagEmoji(inputValue, 'country')}</span>
              <span className="font-medium">{capitalizeFirst(inputValue)}</span>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  setInputValue('');
                  onLocationChange?.(null);
                  onSelect?.(null);
                }}
                className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors"
              >
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </>
          ) : (
            <>
              <span className="text-lg">🌍</span>
              <span className="text-gray-500">Location</span>
            </>
          )}
        </div>
      </button>

      {/* Dropdown panel */}
      {showDropdown && createPortal(
        <div 
          ref={dropdownRef}
          className="absolute z-50 w-full mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg max-h-96 overflow-hidden"
          style={{
            top: dropdownPosition.top,
            left: dropdownPosition.left,
            width: dropdownPosition.width,
            maxHeight: '400px'
          }}
        >
          {/* Search input */}
          <div className="p-3 border-b border-gray-200 dark:border-gray-700">
            <input
              type="text"
              placeholder="Search locations..."
              value={searchValue}
              onChange={handleSearchChange}
              className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              autoFocus
            />
          </div>

          {/* Suggestions list */}
          <div className="max-h-80 overflow-y-auto">
            {suggestions.length > 0 ? (
              suggestions.map((suggestion, index) => (
                <button
                  key={index}
                  onClick={() => selectLocation(suggestion)}
                  className="w-full px-4 py-3 text-left hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors flex items-start space-x-3"
                >
                  <span className="text-lg flex-shrink-0 mt-0.5">{suggestion.name.split(' ')[0]}</span>
                  <span className="font-medium text-sm leading-tight break-words">
                    {suggestion.name.split(' ').slice(1).join(' ')}
                  </span>
                </button>
              ))
            ) : (
              <div className="p-4 text-center text-gray-500 dark:text-gray-400">
                No locations found
              </div>
            )}
          </div>
        </div>,
        document.body
      )}
    </div>
  );
};

export default LocationAutocomplete; 