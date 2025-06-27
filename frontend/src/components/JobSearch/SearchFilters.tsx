import React from 'react';

const SearchFilters = () => {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md sticky top-8">
      <h3 className="text-xl font-bold mb-4 text-gray-800">Filters</h3>
      <form>
        <div className="mb-6">
          <label htmlFor="keywords" className="block text-sm font-medium text-gray-700 mb-1">
            Keywords
          </label>
          <input
            type="text"
            id="keywords"
            placeholder="Product Manager"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <div className="mb-6">
          <label htmlFor="negativeKeywords" className="block text-sm font-medium text-gray-700 mb-1">
            Negative Keywords
          </label>
          <input
            type="text"
            id="negativeKeywords"
            placeholder="e.g. 'intern', 'crypto'"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <div className="mb-6">
          <label htmlFor="location" className="block text-sm font-medium text-gray-700 mb-1">
            Location
          </label>
          <input
            type="text"
            id="location"
            placeholder="City, country, or 'anywhere'"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          />
        </div>

        <div className="mb-6">
          <label htmlFor="postedAge" className="block text-sm font-medium text-gray-700 mb-1">
            Posted within
          </label>
          <select
            id="postedAge"
            className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-indigo-500 focus:border-indigo-500"
          >
            <option value="any">Any time</option>
            <option value="1">Last 24 hours</option>
            <option value="3">Last 3 days</option>
            <option value="7">Last 7 days</option>
            <option value="14">Last 14 days</option>
            <option value="30">Last 30 days</option>
          </select>
        </div>

        <div>
          <h4 className="text-sm font-medium text-gray-700 mb-2">Work type</h4>
          <div className="space-y-2">
            <div className="flex items-center">
              <input
                id="remote"
                name="workType"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="remote" className="ml-3 text-sm text-gray-600">
                Remote
              </label>
            </div>
            <div className="flex items-center">
              <input
                id="hybrid"
                name="workType"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="hybrid" className="ml-3 text-sm text-gray-600">
                Hybrid
              </label>
            </div>
            <div className="flex items-center">
              <input
                id="onsite"
                name="workType"
                type="checkbox"
                className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded"
              />
              <label htmlFor="onsite" className="ml-3 text-sm text-gray-600">
                On-site
              </label>
            </div>
          </div>
        </div>

        <div className="mt-8">
            <button
                type="submit"
                className="w-full bg-indigo-600 text-white py-2 px-4 rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
                Apply Filters
            </button>
        </div>
      </form>
    </div>
  );
};

export default SearchFilters; 