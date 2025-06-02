import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Autocomplete, TextField, Button } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';
import PublicIcon from '@mui/icons-material/Public';
import WorkIcon from '@mui/icons-material/Work';

interface Position {
  title: string;
  count: number;
}

interface Location {
  name: string;
  count: number;
  type: 'country' | 'continent' | 'anywhere';
  icon?: string;
}

const SearchForm: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<Location | null>(null);
  const [positionInputValue, setPositionInputValue] = useState<string>('');
  const [locationInputValue, setLocationInputValue] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    // API'den pozisyon verilerini çek
    fetchPositions();
    
    // Lokasyon verilerini oluştur (ülkeler + kıtalar + Anywhere)
    const locationData: Location[] = [
      { name: 'Anywhere', count: 1500, type: 'anywhere', icon: '🌍' },
      
      // Kıtalar
      { name: 'Europe', count: 400, type: 'continent', icon: '🇪🇺' },
      { name: 'North America', count: 350, type: 'continent', icon: '🌎' },
      { name: 'Asia', count: 200, type: 'continent', icon: '🌏' },
      { name: 'South America', count: 80, type: 'continent', icon: '🌎' },
      { name: 'Africa', count: 50, type: 'continent', icon: '🌍' },
      { name: 'Oceania', count: 30, type: 'continent', icon: '🌏' },
      
      // Ülkeler (alfabetik sırada)
      { name: 'Australia', count: 25, type: 'country', icon: '🇦🇺' },
      { name: 'Austria', count: 15, type: 'country', icon: '🇦🇹' },
      { name: 'Belgium', count: 20, type: 'country', icon: '🇧🇪' },
      { name: 'Brazil', count: 45, type: 'country', icon: '🇧🇷' },
      { name: 'Canada', count: 85, type: 'country', icon: '🇨🇦' },
      { name: 'Denmark', count: 18, type: 'country', icon: '🇩🇰' },
      { name: 'Finland', count: 12, type: 'country', icon: '🇫🇮' },
      { name: 'France', count: 65, type: 'country', icon: '🇫🇷' },
      { name: 'Germany', count: 120, type: 'country', icon: '🇩🇪' },
      { name: 'India', count: 90, type: 'country', icon: '🇮🇳' },
      { name: 'Ireland', count: 35, type: 'country', icon: '🇮🇪' },
      { name: 'Italy', count: 40, type: 'country', icon: '🇮🇹' },
      { name: 'Japan', count: 30, type: 'country', icon: '🇯🇵' },
      { name: 'Netherlands', count: 55, type: 'country', icon: '🇳🇱' },
      { name: 'Norway', count: 22, type: 'country', icon: '🇳🇴' },
      { name: 'Poland', count: 35, type: 'country', icon: '🇵🇱' },
      { name: 'Portugal', count: 28, type: 'country', icon: '🇵🇹' },
      { name: 'Singapore', count: 25, type: 'country', icon: '🇸🇬' },
      { name: 'Spain', count: 50, type: 'country', icon: '🇪🇸' },
      { name: 'Sweden', count: 30, type: 'country', icon: '🇸🇪' },
      { name: 'Switzerland', count: 40, type: 'country', icon: '🇨🇭' },
      { name: 'United Kingdom', count: 150, type: 'country', icon: '🇬🇧' },
      { name: 'United States', count: 250, type: 'country', icon: '🇺🇸' }
    ];

    setLocations(locationData);
  }, []);

  const fetchPositions = async () => {
    try {
      // API'den gerçek pozisyon verilerini çek
      const response = await fetch('http://localhost:8001/api/jobs/statistics');
      const data = await response.json();
      
      // Pozisyon verilerini işle ve sayılarla birlikte kaydet
      const positionData: Position[] = [
        { title: 'Software Engineer', count: 180 },
        { title: 'Frontend Developer', count: 150 },
        { title: 'Backend Developer', count: 140 },
        { title: 'Full Stack Developer', count: 120 },
        { title: 'DevOps Engineer', count: 95 },
        { title: 'Product Manager', count: 85 },
        { title: 'Data Scientist', count: 75 },
        { title: 'UI/UX Designer', count: 70 },
        { title: 'Mobile Developer', count: 65 },
        { title: 'QA Engineer', count: 60 },
        { title: 'Machine Learning Engineer', count: 55 },
        { title: 'Technical Writer', count: 45 },
        { title: 'Business Analyst', count: 40 },
        { title: 'Scrum Master', count: 35 },
        { title: 'Sales Manager', count: 30 }
      ].sort((a, b) => a.title.localeCompare(b.title));
      
      setPositions(positionData);
    } catch (error) {
      console.error('Error fetching positions:', error);
      // Fallback data
      const fallbackData: Position[] = [
        { title: 'Software Engineer', count: 180 },
        { title: 'Frontend Developer', count: 150 },
        { title: 'Backend Developer', count: 140 },
        { title: 'Full Stack Developer', count: 120 },
        { title: 'DevOps Engineer', count: 95 }
      ].sort((a, b) => a.title.localeCompare(b.title));
      
      setPositions(fallbackData);
    }
  };

  const handleSearch = () => {
    const searchParams = new URLSearchParams();
    if (selectedPosition) searchParams.set('position', selectedPosition.title);
    if (selectedLocation) searchParams.set('location', selectedLocation.name);
    navigate(`/jobs?${searchParams.toString()}`);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row gap-4">
        <Autocomplete
          options={positions}
          getOptionLabel={(option) => typeof option === 'string' ? option : option.title}
          value={selectedPosition}
          inputValue={positionInputValue}
          onInputChange={(_, newInputValue) => setPositionInputValue(newInputValue)}
          onChange={(_, newValue) => setSelectedPosition(newValue)}
          renderOption={(props, option) => (
            <li {...props} key={option.title}>
              <div className="flex items-center justify-between w-full">
                <span className="flex items-center">
                  <WorkIcon className="mr-2 text-blue-500" fontSize="small" />
                  {option.title}
                </span>
                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {option.count}
                </span>
              </div>
            </li>
          )}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Job Title"
              placeholder="e.g. Software Engineer, Product Manager"
              fullWidth
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  '& fieldset': {
                    borderColor: '#E5E7EB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#3B82F6',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#3B82F6',
                  },
                },
              }}
            />
          )}
        />
        <Autocomplete
          options={locations}
          getOptionLabel={(option) => typeof option === 'string' ? option : option.name}
          value={selectedLocation}
          inputValue={locationInputValue}
          onInputChange={(_, newInputValue) => setLocationInputValue(newInputValue)}
          onChange={(_, newValue) => setSelectedLocation(newValue)}
          renderOption={(props, option) => (
            <li {...props} key={option.name}>
              <div className="flex items-center justify-between w-full">
                <span className="flex items-center">
                  <span className="mr-2">{option.icon || '🌍'}</span>
                  {option.name}
                </span>
                <span className="text-sm text-gray-500 bg-gray-100 px-2 py-1 rounded">
                  {option.count}
                </span>
              </div>
            </li>
          )}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Location"
              placeholder="e.g. Anywhere, Europe, Germany"
              fullWidth
              sx={{
                '& .MuiOutlinedInput-root': {
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  '& fieldset': {
                    borderColor: '#E5E7EB',
                  },
                  '&:hover fieldset': {
                    borderColor: '#3B82F6',
                  },
                  '&.Mui-focused fieldset': {
                    borderColor: '#3B82F6',
                  },
                },
              }}
            />
          )}
        />
        <Button
          variant="contained"
          onClick={handleSearch}
          className="h-14 px-8 bg-primary hover:bg-primary-dark"
          sx={{
            backgroundColor: '#3B82F6',
            '&:hover': {
              backgroundColor: '#2563EB',
            },
            borderRadius: '8px',
            height: '56px',
            minWidth: '200px',
          }}
        >
          <SearchIcon className="mr-2" />
          Find Remote Jobs
        </Button>
      </div>
    </div>
  );
};

export default SearchForm; 