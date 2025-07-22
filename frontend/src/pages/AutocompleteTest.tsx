import React, { useState, useEffect } from 'react';
import JobAutocomplete from '../components/JobAutocomplete';
import LocationDropdown from '../components/LocationDropdown';

interface Position {
  title: string;
  count: number;
  category?: string;
}

interface Job {
  _id: string;
  title: string;
  company: string;
  location: string;
  job_type: string;
  work_type: string;
  salary?: string;
  description?: string;
  created_at: string;
}

const AutocompleteTest: React.FC = () => {
  const [selectedPosition, setSelectedPosition] = useState<string>('');
  const [selectedPositionData, setSelectedPositionData] = useState<Position | null>(null);
  const [selectedLocation, setSelectedLocation] = useState<string>('');
  const [testResults, setTestResults] = useState<string[]>([]);
  const [jobResults, setJobResults] = useState<Job[]>([]);
  const [loadingJobs, setLoadingJobs] = useState<boolean>(false);
  const [jobCount, setJobCount] = useState<number>(0);

  const handlePositionSelect = (position: Position) => {
    console.log('Selected position:', position);
    setSelectedPositionData(position);
    setSelectedPosition(position.title);
    addTestResult(`✅ Position selected: ${position.title} (${position.count} jobs)`);
    
    // Fetch jobs for selected position
    fetchJobsForPosition(position.title);
  };

  const handleLocationSelect = (location: string) => {
    console.log('Selected location:', location);
    setSelectedLocation(location);
    addTestResult(`🌍 Location selected: ${location}`);
  };

  const fetchJobsForPosition = async (position: string) => {
    setLoadingJobs(true);
    addTestResult(`🔍 Fetching jobs for: ${position}`);
    
    try {
      const response = await fetch(`http://localhost:8001/api/v1/jobs/search?q=${encodeURIComponent(position)}&limit=1`, {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        const data = await response.json();
        const totalJobs = data.total || 0;
        setJobResults([]); // Don't store individual jobs
        setJobCount(totalJobs);
        addTestResult(`📊 Found ${totalJobs} jobs for "${position}"`);
      } else {
        addTestResult(`❌ Error fetching jobs: ${response.status}`);
        setJobResults([]);
        setJobCount(0);
      }
    } catch (error) {
      console.error('Error fetching jobs:', error);
      addTestResult(`❌ Network error: ${error instanceof Error ? error.message : 'Unknown error'}`);
      setJobResults([]);
      setJobCount(0);
    } finally {
      setLoadingJobs(false);
    }
  };

  const addTestResult = (result: string) => {
    setTestResults(prev => [...prev, `${new Date().toLocaleTimeString()}: ${result}`]);
  };

  const clearTestResults = () => {
    setTestResults([]);
    setJobResults([]);
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-6xl mx-auto">
        <h1 className="text-3xl font-bold text-gray-800 mb-8">Autocomplete Test Page</h1>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Job Autocomplete Test */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Job Title Autocomplete</h2>
            <div className="space-y-4">
              <JobAutocomplete
                value={selectedPosition}
                onChange={setSelectedPosition}
                onSelect={handlePositionSelect}
                placeholder="Search for job positions..."
                maxResults={10}
              />
              
              {selectedPositionData && (
                <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
                  <h3 className="font-semibold text-green-800">Selected Position:</h3>
                  <p className="text-green-700">
                    <strong>{selectedPositionData.title}</strong>
                    {selectedPositionData.category && (
                      <span className="text-green-600 ml-2">({selectedPositionData.category})</span>
                    )}
                  </p>
                  <p className="text-green-600 text-sm">
                    {selectedPositionData.count} jobs available
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Location Dropdown Test */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4 text-gray-800">Location Dropdown</h2>
            <div className="space-y-4">
              <LocationDropdown
                value={selectedLocation}
                onChange={handleLocationSelect}
              />
              
              {selectedLocation && (
                <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                  <h3 className="font-semibold text-blue-800">Selected Location:</h3>
                  <p className="text-blue-700">
                    <strong>{selectedLocation}</strong>
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Job Results */}
        {selectedPositionData && (
          <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-semibold text-gray-800">
                Job Results for "{selectedPositionData.title}"
              </h2>
              {loadingJobs && (
                <div className="flex items-center text-blue-600">
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600 mr-2"></div>
                  Loading...
                </div>
              )}
            </div>
            
            {jobCount > 0 ? (
              <div className="text-center py-8">
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <div className="text-3xl font-bold text-blue-600 mb-2">{jobCount}</div>
                  <div className="text-lg text-gray-700 mb-1">jobs found for</div>
                  <div className="text-xl font-semibold text-gray-800">"{selectedPositionData.title}"</div>
                  <div className="text-sm text-gray-500 mt-2">
                    💡 Try selecting a different position to see more results
                  </div>
                </div>
              </div>
            ) : !loadingJobs ? (
              <div className="text-center py-8 text-gray-500">
                <p>No jobs found for this position.</p>
                <p className="text-sm mt-2">Try selecting a different position or check the backend API.</p>
              </div>
            ) : null}
          </div>
        )}

        {/* Test Results */}
        <div className="mt-8 bg-white rounded-lg shadow-lg p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold text-gray-800">Test Results</h2>
            <button
              onClick={clearTestResults}
              className="px-4 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
            >
              Clear Results
            </button>
          </div>
          
          <div className="bg-gray-100 rounded-lg p-4 max-h-64 overflow-y-auto">
            {testResults.length === 0 ? (
              <p className="text-gray-500 text-center">No test results yet. Try using the autocomplete components above.</p>
            ) : (
              <div className="space-y-2">
                {testResults.map((result, index) => (
                  <div key={index} className="text-sm text-gray-700 font-mono">
                    {result}
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* Instructions */}
        <div className="mt-8 bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="font-semibold text-yellow-800 mb-2">Test Instructions:</h3>
          <ul className="text-yellow-700 space-y-1 text-sm">
            <li>• <strong>Job Autocomplete:</strong> Click on the input to see popular positions, or type 3+ characters to search</li>
            <li>• <strong>Location Dropdown:</strong> Click to see all available locations, including Turkey (TR)</li>
            <li>• <strong>IP Detection:</strong> Your location should be automatically detected and selected</li>
            <li>• <strong>Job Results:</strong> When you select a position, real job listings will appear below</li>
            <li>• <strong>Test Results:</strong> All interactions will be logged below</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default AutocompleteTest; 