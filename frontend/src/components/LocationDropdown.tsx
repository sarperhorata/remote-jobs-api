import React, { useState, useEffect, useRef } from 'react';
import { ChevronDown, Globe, MapPin } from 'lucide-react';

interface Location {
  code: string;
  name: string;
  flag: string;
  type: 'country' | 'continent';
}

const continents: Location[] = [
  { code: 'worldwide', name: 'Worldwide', flag: '🌍', type: 'continent' },
  { code: 'europe', name: 'Europe', flag: '🇪🇺', type: 'continent' },
  { code: 'america', name: 'America', flag: '🌎', type: 'continent' },
  { code: 'africa', name: 'Africa', flag: '🌍', type: 'continent' },
  { code: 'asia', name: 'Asia', flag: '🌏', type: 'continent' },
  { code: 'australia', name: 'Australia', flag: '🇦🇺', type: 'continent' },
];

const countries: Location[] = [
  { code: 'us', name: 'United States', flag: '🇺🇸', type: 'country' as const },
  { code: 'uk', name: 'United Kingdom', flag: '🇬🇧', type: 'country' as const },
  { code: 'ca', name: 'Canada', flag: '🇨🇦', type: 'country' as const },
  { code: 'de', name: 'Germany', flag: '🇩🇪', type: 'country' as const },
  { code: 'fr', name: 'France', flag: '🇫🇷', type: 'country' as const },
  { code: 'nl', name: 'Netherlands', flag: '🇳🇱', type: 'country' as const },
  { code: 'se', name: 'Sweden', flag: '🇸🇪', type: 'country' as const },
  { code: 'no', name: 'Norway', flag: '🇳🇴', type: 'country' as const },
  { code: 'dk', name: 'Denmark', flag: '🇩🇰', type: 'country' as const },
  { code: 'fi', name: 'Finland', flag: '🇫🇮', type: 'country' as const },
  { code: 'ch', name: 'Switzerland', flag: '🇨🇭', type: 'country' as const },
  { code: 'at', name: 'Austria', flag: '🇦🇹', type: 'country' as const },
  { code: 'be', name: 'Belgium', flag: '🇧🇪', type: 'country' as const },
  { code: 'ie', name: 'Ireland', flag: '🇮🇪', type: 'country' as const },
  { code: 'es', name: 'Spain', flag: '🇪🇸', type: 'country' as const },
  { code: 'it', name: 'Italy', flag: '🇮🇹', type: 'country' as const },
  { code: 'pt', name: 'Portugal', flag: '🇵🇹', type: 'country' as const },
  { code: 'pl', name: 'Poland', flag: '🇵🇱', type: 'country' as const },
  { code: 'cz', name: 'Czech Republic', flag: '🇨🇿', type: 'country' as const },
  { code: 'hu', name: 'Hungary', flag: '🇭🇺', type: 'country' as const },
  { code: 'ro', name: 'Romania', flag: '🇷🇴', type: 'country' as const },
  { code: 'bg', name: 'Bulgaria', flag: '🇧🇬', type: 'country' as const },
  { code: 'hr', name: 'Croatia', flag: '🇭🇷', type: 'country' as const },
  { code: 'si', name: 'Slovenia', flag: '🇸🇮', type: 'country' as const },
  { code: 'sk', name: 'Slovakia', flag: '🇸🇰', type: 'country' as const },
  { code: 'lt', name: 'Lithuania', flag: '🇱🇹', type: 'country' as const },
  { code: 'lv', name: 'Latvia', flag: '🇱🇻', type: 'country' as const },
  { code: 'ee', name: 'Estonia', flag: '🇪🇪', type: 'country' as const },
  { code: 'tr', name: 'Turkey', flag: '🇹🇷', type: 'country' as const },
  { code: 'au', name: 'Australia', flag: '🇦🇺', type: 'country' as const },
  { code: 'nz', name: 'New Zealand', flag: '🇳🇿', type: 'country' as const },
  { code: 'jp', name: 'Japan', flag: '🇯🇵', type: 'country' as const },
  { code: 'kr', name: 'South Korea', flag: '🇰🇷', type: 'country' as const },
  { code: 'sg', name: 'Singapore', flag: '🇸🇬', type: 'country' as const },
  { code: 'in', name: 'India', flag: '🇮🇳', type: 'country' as const },
  { code: 'br', name: 'Brazil', flag: '🇧🇷', type: 'country' as const },
  { code: 'mx', name: 'Mexico', flag: '🇲🇽', type: 'country' as const },
  { code: 'ar', name: 'Argentina', flag: '🇦🇷', type: 'country' as const },
  { code: 'cl', name: 'Chile', flag: '🇨🇱', type: 'country' as const },
  { code: 'co', name: 'Colombia', flag: '🇨🇴', type: 'country' as const },
  { code: 'pe', name: 'Peru', flag: '🇵🇪', type: 'country' as const },
  { code: 'uy', name: 'Uruguay', flag: '🇺🇾', type: 'country' as const },
  { code: 'za', name: 'South Africa', flag: '🇿🇦', type: 'country' as const },
  { code: 'ng', name: 'Nigeria', flag: '🇳🇬', type: 'country' as const },
  { code: 'ke', name: 'Kenya', flag: '🇰🇪', type: 'country' as const },
  { code: 'gh', name: 'Ghana', flag: '🇬🇭', type: 'country' as const },
  { code: 'ug', name: 'Uganda', flag: '🇺🇬', type: 'country' as const },
  { code: 'tz', name: 'Tanzania', flag: '🇹🇿', type: 'country' as const },
  { code: 'et', name: 'Ethiopia', flag: '🇪🇹', type: 'country' as const },
  { code: 'ma', name: 'Morocco', flag: '🇲🇦', type: 'country' as const },
  { code: 'eg', name: 'Egypt', flag: '🇪🇬', type: 'country' as const },
  { code: 'tn', name: 'Tunisia', flag: '🇹🇳', type: 'country' as const },
  { code: 'dz', name: 'Algeria', flag: '🇩🇿', type: 'country' as const },
  { code: 'ly', name: 'Libya', flag: '🇱🇾', type: 'country' as const },
  { code: 'sd', name: 'Sudan', flag: '🇸🇩', type: 'country' as const },
  { code: 'cm', name: 'Cameroon', flag: '🇨🇲', type: 'country' as const },
  { code: 'ci', name: 'Ivory Coast', flag: '🇨🇮', type: 'country' as const },
  { code: 'sn', name: 'Senegal', flag: '🇸🇳', type: 'country' as const },
  { code: 'ml', name: 'Mali', flag: '🇲🇱', type: 'country' as const },
  { code: 'bf', name: 'Burkina Faso', flag: '🇧🇫', type: 'country' as const },
  { code: 'ne', name: 'Niger', flag: '🇳🇪', type: 'country' as const },
  { code: 'td', name: 'Chad', flag: '🇹🇩', type: 'country' as const },
  { code: 'cf', name: 'Central African Republic', flag: '🇨🇫', type: 'country' as const },
  { code: 'cg', name: 'Republic of the Congo', flag: '🇨🇬', type: 'country' as const },
  { code: 'cd', name: 'Democratic Republic of the Congo', flag: '🇨🇩', type: 'country' as const },
  { code: 'ao', name: 'Angola', flag: '🇦🇴', type: 'country' as const },
  { code: 'zm', name: 'Zambia', flag: '🇿🇲', type: 'country' as const },
  { code: 'zw', name: 'Zimbabwe', flag: '🇿🇼', type: 'country' as const },
  { code: 'bw', name: 'Botswana', flag: '🇧🇼', type: 'country' as const },
  { code: 'na', name: 'Namibia', flag: '🇳🇦', type: 'country' as const },
  { code: 'sz', name: 'Eswatini', flag: '🇸🇿', type: 'country' as const },
  { code: 'ls', name: 'Lesotho', flag: '🇱🇸', type: 'country' as const },
  { code: 'mg', name: 'Madagascar', flag: '🇲🇬', type: 'country' as const },
  { code: 'mu', name: 'Mauritius', flag: '🇲🇺', type: 'country' as const },
  { code: 'sc', name: 'Seychelles', flag: '🇸🇨', type: 'country' as const },
  { code: 'km', name: 'Comoros', flag: '🇰🇲', type: 'country' as const },
  { code: 'dj', name: 'Djibouti', flag: '🇩🇯', type: 'country' as const },
  { code: 'so', name: 'Somalia', flag: '🇸🇴', type: 'country' as const },
  { code: 'er', name: 'Eritrea', flag: '🇪🇷', type: 'country' as const },
  { code: 'ss', name: 'South Sudan', flag: '🇸🇸', type: 'country' as const },
  { code: 'rw', name: 'Rwanda', flag: '🇷🇼', type: 'country' as const },
  { code: 'bi', name: 'Burundi', flag: '🇧🇮', type: 'country' as const },
  { code: 'mw', name: 'Malawi', flag: '🇲🇼', type: 'country' as const },
  { code: 'mz', name: 'Mozambique', flag: '🇲🇿', type: 'country' as const },
].sort((a, b) => a.name.localeCompare(b.name));

interface LocationDropdownProps {
  value: string;
  onChange: (location: string) => void;
  className?: string;
}

const LocationDropdown: React.FC<LocationDropdownProps> = ({ value, onChange, className = '' }) => {
  const [isOpen, setIsOpen] = useState(false);
  const [searchTerm, setSearchTerm] = useState('');
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Get user's IP country (default to US for now)
  const [userCountry, setUserCountry] = useState('us');
  const [isDetectingLocation, setIsDetectingLocation] = useState(true);

  useEffect(() => {
    // Detect user's country from IP with multiple fallback APIs
    const detectUserLocation = async () => {
      setIsDetectingLocation(true);
      
      try {
        // Try multiple IP geolocation APIs for better reliability
        // These APIs work better for client-side detection
        const apis = [
          'https://api.ipify.org?format=json', // Get IP first
          'https://ipapi.co/json/',
          'https://api.myip.com/',
          'https://api.ip.sb/geoip'
        ];
        
        let detectedCountry = null;
        let userIP = null;
        
        // First, get the user's IP address
        try {
          const ipResponse = await fetch('https://api.ipify.org?format=json', {
            method: 'GET',
            signal: AbortSignal.timeout(3000)
          });
          
          if (ipResponse.ok) {
            const ipData = await ipResponse.json();
            userIP = ipData.ip;
            console.log('🌍 User IP detected:', userIP);
          }
        } catch (error) {
          console.log('⚠️ IP detection failed:', error);
        }
        
        // Then get location data using the IP
        for (const api of apis.slice(1)) { // Skip ipify since we already used it
          try {
            const url = userIP ? `${api}${userIP}` : api;
            const response = await fetch(url, { 
              method: 'GET',
              headers: { 'Accept': 'application/json' },
              signal: AbortSignal.timeout(3000) // 3 second timeout
            });
            
            if (response.ok) {
              const data = await response.json();
              detectedCountry = data.country_code || data.countryCode || data.country || data.country_code_iso3;
              
              if (detectedCountry) {
                console.log('🌍 Location detected:', detectedCountry, 'from API:', api);
                break;
              }
            }
          } catch (error) {
            console.log('⚠️ Location API failed:', api, error);
            continue;
          }
        }
        
        if (detectedCountry) {
          const countryCode = detectedCountry.toLowerCase();
          setUserCountry(countryCode);
          
          // Only set as default if no value is already selected
          if (!value) {
            onChange(countryCode);
          }
        } else {
          // Fallback to TR (Turkey) if all APIs fail
          console.log('🌍 Using fallback location: TR (Turkey)');
          setUserCountry('tr');
          if (!value) {
            onChange('tr');
          }
        }
      } catch (error) {
        console.error('❌ IP location detection failed:', error);
        // Fallback to TR (Turkey) if detection fails
        setUserCountry('tr');
        if (!value) {
          onChange('tr');
        }
      } finally {
        setIsDetectingLocation(false);
      }
    };

    detectUserLocation();
  }, [value, onChange]);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const allLocations = [...continents, ...countries];
  
  const filteredLocations = allLocations.filter(location =>
    location.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    location.code.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const selectedLocation = allLocations.find(loc => loc.code === value) || 
    { code: 'worldwide', name: 'Worldwide', flag: '🌍', type: 'continent' as const };

  const handleSelect = (location: Location) => {
    onChange(location.code);
    setIsOpen(false);
    setSearchTerm('');
  };

  return (
    <div className={`relative ${className}`} ref={dropdownRef}>
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full flex items-center justify-between px-3 py-2 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-colors"
      >
        <div className="flex items-center space-x-2">
          {isDetectingLocation ? (
            <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
          ) : (
            <span className="text-lg">{selectedLocation.flag}</span>
          )}
          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
            {isDetectingLocation ? 'Detecting location...' : selectedLocation.name}
          </span>
        </div>
        <ChevronDown className={`w-4 h-4 text-gray-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
      </button>

      {isOpen && (
        <div className="absolute top-full left-0 right-0 mt-1 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-lg shadow-lg z-50 max-h-80 overflow-hidden">
          {/* Search Input */}
          <div className="p-3 border-b border-gray-200 dark:border-gray-600">
            <div className="relative">
              <MapPin className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
              <input
                type="text"
                placeholder="Search locations..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                autoFocus
              />
            </div>
          </div>

          {/* Locations List */}
          <div className="max-h-64 overflow-y-auto">
            {/* Continents Section */}
            {!searchTerm && (
              <div>
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-700">
                  Continents & Regions
                </div>
                {continents.map((continent) => (
                  <button
                    key={continent.code}
                    onClick={() => handleSelect(continent)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      value === continent.code ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-gray-900 dark:text-white'
                    }`}
                  >
                    <span className="text-lg">{continent.flag}</span>
                    <span className="text-sm font-medium">{continent.name}</span>
                  </button>
                ))}
              </div>
            )}

            {/* Countries Section */}
            <div>
              {!searchTerm && (
                <div className="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider bg-gray-50 dark:bg-gray-700">
                  Countries
                </div>
              )}
              {filteredLocations
                .filter(location => searchTerm || location.type === 'country')
                .map((location) => (
                  <button
                    key={location.code}
                    onClick={() => handleSelect(location)}
                    className={`w-full flex items-center space-x-3 px-3 py-2 text-left hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors ${
                      value === location.code ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-600 dark:text-blue-400' : 'text-gray-900 dark:text-white'
                    }`}
                  >
                    <span className="text-lg">{location.flag}</span>
                    <span className="text-sm font-medium">{location.name}</span>
                    {location.code === userCountry && (
                      <span className="ml-auto text-xs bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-400 px-2 py-1 rounded-full">
                        Your Location
                      </span>
                    )}
                  </button>
                ))}
            </div>

            {/* No Results */}
            {filteredLocations.length === 0 && (
              <div className="px-3 py-4 text-center text-gray-500 dark:text-gray-400">
                <Globe className="w-8 h-8 mx-auto mb-2 opacity-50" />
                <p className="text-sm">No locations found</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
};

export default LocationDropdown; 