import React, { useState } from 'react';
import MultiJobAutocomplete from './MultiJobAutocomplete';

interface Position {
  title: string;
  count: number;
  category?: string;
}

const TestAutocomplete: React.FC = () => {
  const [selectedPositions, setSelectedPositions] = useState<Position[]>([]);

  const handleSearch = (positions: Position[]) => {
    console.log('🔥 TEST: Search triggered with positions:', positions);
    alert(`Search triggered with ${positions.length} positions: ${positions.map(p => p.title).join(', ')}`);
  };

  return (
    <div className="min-h-screen bg-gray-100 p-8">
      <div className="max-w-3xl mx-auto">
        <h1 className="text-3xl font-bold mb-8">Autocomplete Test</h1>
        
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-xl font-semibold mb-4">Multi Job Autocomplete Component</h2>
          
          <MultiJobAutocomplete
            selectedPositions={selectedPositions}
            onPositionsChange={setSelectedPositions}
            onSearch={handleSearch}
            placeholder="Type 'dev' or 'manager' to test..."
            maxSelections={5}
          />
          
          <div className="mt-8 p-4 bg-gray-50 rounded">
            <h3 className="font-semibold mb-2">Debug Info:</h3>
            <pre className="text-xs overflow-auto">
              {JSON.stringify({ selectedPositions }, null, 2)}
            </pre>
          </div>
        </div>

        <div className="mt-8 bg-blue-50 p-4 rounded">
          <h3 className="font-semibold mb-2">Instructions:</h3>
          <ul className="list-disc list-inside text-sm space-y-1">
            <li>Type at least 2 characters (e.g., "dev", "man", "eng")</li>
            <li>Wait for dropdown to appear</li>
            <li>Click on a suggestion to select it</li>
            <li>Select multiple positions</li>
            <li>Click "Search Jobs" to test the search callback</li>
            <li>Check browser console for debug logs</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default TestAutocomplete; 