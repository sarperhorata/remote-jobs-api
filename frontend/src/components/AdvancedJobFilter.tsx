import React, { useState } from "react";
import { Filter, X, Search } from "lucide-react";

interface FilterProps {
  onFiltersChange: (filters: any) => void;
  onClose: () => void;
}

export const AdvancedJobFilter: React.FC<FilterProps> = ({ onFiltersChange, onClose }) => {
  const [filters, setFilters] = useState({
    location: "",
    salary_min: "",
    salary_max: "",
    experience_level: "",
    job_type: "",
    company_size: "",
    remote_type: "",
    skills: [] as string[]
  });

  const handleSubmit = () => {
    onFiltersChange(filters);
    onClose();
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-lg">
      <div className="flex justify-between items-center mb-4">
        <h3 className="text-lg font-semibold">Advanced Filters</h3>
        <button onClick={onClose}>
          <X className="w-5 h-5" />
        </button>
      </div>
      
      <div className="grid grid-cols-2 gap-4">
        <div>
          <label className="block text-sm font-medium mb-1">Location</label>
          <input
            type="text"
            value={filters.location}
            onChange={(e) => setFilters({...filters, location: e.target.value})}
            className="w-full p-2 border rounded"
            placeholder="e.g., San Francisco"
          />
        </div>
        
        <div>
          <label className="block text-sm font-medium mb-1">Remote Type</label>
          <select
            value={filters.remote_type}
            onChange={(e) => setFilters({...filters, remote_type: e.target.value})}
            className="w-full p-2 border rounded"
          >
            <option value="">Any</option>
            <option value="remote">Remote</option>
            <option value="hybrid">Hybrid</option>
            <option value="onsite">On-site</option>
          </select>
        </div>
      </div>

      <div className="mt-4 flex justify-end space-x-2">
        <button
          onClick={onClose}
          className="px-4 py-2 text-gray-600 border rounded hover:bg-gray-50"
        >
          Cancel
        </button>
        <button
          onClick={handleSubmit}
          className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
        >
          Apply Filters
        </button>
      </div>
    </div>
  );
};
