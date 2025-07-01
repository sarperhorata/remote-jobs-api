import React, { useState } from 'react';
import JobAutocomplete from '../components/JobAutocomplete';

interface Position {
  title: string;
  count: number;
}

const AutocompleteTest: React.FC = () => {
  const [value, setValue] = useState('');
  const [selectedPosition, setSelectedPosition] = useState<Position | null>(null);

  const handleSelect = (position: Position) => {
    console.log('Selected position:', position);
    setSelectedPosition(position);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Autocomplete Test</h1>
        
        <div className="bg-white p-6 rounded-lg shadow-md mb-6">
          <h2 className="text-xl font-semibold mb-4">Job Title Autocomplete</h2>
          
          <JobAutocomplete
            value={value}
            onChange={setValue}
            onSelect={handleSelect}
            placeholder="Start typing 'Product Manager'..."
          />
          
          <div className="mt-4 p-4 bg-gray-50 rounded">
            <h3 className="font-medium mb-2">Current State:</h3>
            <p><strong>Input Value:</strong> {value || 'Empty'}</p>
            <p><strong>Selected Position:</strong> {selectedPosition ? JSON.stringify(selectedPosition, null, 2) : 'None'}</p>
          </div>
        </div>

        <div className="bg-white p-6 rounded-lg shadow-md">
          <h2 className="text-xl font-semibold mb-4">Test Instructions:</h2>
          <ol className="list-decimal list-inside space-y-2">
            <li>Type "Product Manager" in the input field</li>
            <li>Wait for the dropdown to appear (should show 5 results)</li>
            <li>Click on "Product Manager" (first option)</li>
            <li>Check if the input updates and the selection is recorded</li>
          </ol>
        </div>
      </div>
    </div>
  );
};

export default AutocompleteTest; 