import React, { useState } from 'react';
import './App.css';
import JobAutocomplete from './components/JobAutocomplete';

function App() {
  const [selectedTitles, setSelectedTitles] = useState<string[]>([]);

  const handleSelectedPositions = (positions: string[]) => {
    setSelectedTitles(positions);
    console.log('Selected Job Titles:', positions);
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Job Autocomplete Demo</h1>
        <div style={{ width: 500, margin: '20px 0' }}>
          <JobAutocomplete onSelectPositions={handleSelectedPositions} />
        </div>
        {selectedTitles.length > 0 && (
          <div>
            <h2>Selected Titles:</h2>
            <ul>
              {selectedTitles.map((title, index) => (
                <li key={index}>{title}</li>
              ))}
            </ul>
          </div>
        )}
      </header>
    </div>
  );
}

export default App; 