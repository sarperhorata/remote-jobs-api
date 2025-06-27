import React, { useState, useEffect } from 'react';
import { Autocomplete, TextField, CircularProgress, Chip } from '@mui/material';
import axios from 'axios';

interface Position {
  title: string;
  count: number;
}

interface JobAutocompleteProps {
  onSelectPositions: (positions: string[]) => void;
}

const JobAutocomplete: React.FC<JobAutocompleteProps> = ({ onSelectPositions }) => {
  const [open, setOpen] = useState(false);
  const [options, setOptions] = useState<Position[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedPositions, setSelectedPositions] = useState<Position[]>([]);

  const backendApiUrl = 'https://remote-jobs-api-k9v1.onrender.com/api'; // Canlı backend API URL'si

  useEffect(() => {
    let active = true;

    if (!open) {
      return undefined;
    }

    setLoading(true);

    (async () => {
      try {
        const response = await axios.get(`${backendApiUrl}/jobs/statistics`);
        if (active) {
          setOptions(response.data.positions || []);
        }
      } catch (error) {
        console.error('Error fetching job positions:', error);
        if (active) {
          setOptions([]); // API hatası durumunda boş seçenekler
        }
      } finally {
        if (active) {
          setLoading(false);
        }
      }
    })();

    return () => {
      active = false;
    };
  }, [open]);

  const handleAutocompleteChange = (event: React.SyntheticEvent, value: Position[]) => {
    // En fazla 5 title seçilebilmesini sağla
    if (value.length <= 5) {
      setSelectedPositions(value);
      onSelectPositions(value.map(pos => pos.title));
    } else {
      // Kullanıcı 5'ten fazla seçmeye çalışırsa, son seçimi geri al
      setSelectedPositions(value.slice(0, 5));
      onSelectPositions(value.slice(0, 5).map(pos => pos.title));
    }
  };

  const getOptionLabel = (option: Position) => {
    return option.title ? `${option.title} (${option.count} jobs)` : '';
  };

  return (
    <Autocomplete
      multiple
      open={open}
      onOpen={() => {
        setOpen(true);
      }}
      onClose={() => {
        setOpen(false);
      }}
      isOptionEqualToValue={(option, value) => option.title === value.title}
      getOptionLabel={getOptionLabel}
      options={options}
      loading={loading}
      value={selectedPositions}
      onChange={handleAutocompleteChange}
      renderTags={(value, getTagProps) =>
        value.map((option, index) => (
          <Chip
            key={index}
            label={getOptionLabel(option)}
            {...getTagProps({ index })}
          />
        ))
      }
      renderInput={(params) => (
        <TextField
          {...params}
          label="Job Title"
          placeholder="Search job titles..."
          InputProps={{
            ...params.InputProps,
            endAdornment: (
              <React.Fragment>
                {loading ? <CircularProgress color="inherit" size={20} /> : null}
                {params.InputProps.endAdornment}
              </React.Fragment>
            ),
          }}
        />
      )}
    />
  );
};

export default JobAutocomplete; 