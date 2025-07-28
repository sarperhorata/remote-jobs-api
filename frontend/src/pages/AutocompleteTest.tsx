import React from 'react';
import MultiJobAutocomplete from '../components/MultiJobAutocomplete';

interface Position {
  title: string;
  count: number;
  category?: string;
}

const AutocompleteTest: React.FC = () => {
  const handleSelect = (positions: Position[]) => {
    console.log('🎯 Test page received positions:', positions);
    alert(`Selected: ${positions.map(p => p.title).join(', ')}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-2xl mx-auto">
        <h1 className="text-3xl font-bold mb-8 text-center">Autocomplete Test</h1>
        
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4">Test MultiJobAutocomplete</h2>
          <p className="text-gray-600 mb-6">
            Type keywords like "react", "python", "remote" to test the autocomplete functionality.
          </p>
          
          <MultiJobAutocomplete
            onSelect={handleSelect}
            placeholder="Type to test autocomplete..."
          />
          
          <div className="mt-6 p-4 bg-gray-50 rounded-lg">
            <h3 className="font-semibold mb-2">Instructions:</h3>
            <ul className="text-sm text-gray-600 space-y-1">
              <li>• Type at least 1 character to trigger search</li>
              <li>• Wait 300ms for API call</li>
              <li>• Click on suggestion to select</li>
              <li>• Check browser console for debug logs</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AutocompleteTest; 