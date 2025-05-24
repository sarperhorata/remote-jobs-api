import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Autocomplete, TextField, Button } from '@mui/material';
import SearchIcon from '@mui/icons-material/Search';

interface Position {
  title: string;
  count: number;
}

interface Location {
  name: string;
  count: number;
}

const SearchForm: React.FC = () => {
  const [positions, setPositions] = useState<Position[]>([]);
  const [locations, setLocations] = useState<Location[]>([]);
  const [selectedPosition, setSelectedPosition] = useState<string>('');
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const navigate = useNavigate();

  useEffect(() => {
    // Burada API'den pozisyon ve lokasyon verilerini çekeceğiz
    // Şimdilik örnek veriler kullanıyoruz
    setPositions([
      { title: 'Frontend Developer', count: 150 },
      { title: 'Backend Developer', count: 120 },
      { title: 'Full Stack Developer', count: 100 },
      { title: 'DevOps Engineer', count: 80 },
      { title: 'UI/UX Designer', count: 60 },
    ].sort((a, b) => a.title.localeCompare(b.title)));

    setLocations([
      { name: 'Remote', count: 500 },
      { name: 'Europe', count: 300 },
      { name: 'United States', count: 250 },
      { name: 'United Kingdom', count: 150 },
      { name: 'Germany', count: 100 },
    ].sort((a, b) => a.name.localeCompare(b.name)));
  }, []);

  const handleSearch = () => {
    const searchParams = new URLSearchParams();
    if (selectedPosition) searchParams.set('position', selectedPosition);
    if (selectedLocation) searchParams.set('location', selectedLocation);
    navigate(`/jobs?${searchParams.toString()}`);
  };

  return (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="flex flex-col md:flex-row gap-4">
        <Autocomplete
          freeSolo
          options={positions.map(pos => pos.title)}
          value={selectedPosition}
          onChange={(_, newValue) => setSelectedPosition(newValue || '')}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Position, title, keywords"
              placeholder="e.g. developer, react, python"
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
          freeSolo
          options={locations.map(loc => loc.name)}
          value={selectedLocation}
          onChange={(_, newValue) => setSelectedLocation(newValue || '')}
          renderInput={(params) => (
            <TextField
              {...params}
              label="Location"
              placeholder="e.g. Remote or Europe"
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