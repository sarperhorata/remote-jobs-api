import React from 'react';

const salaryData = [
  { title: 'Frontend Developer', min: 35000, max: 70000, avg: 52000, currency: 'USD', location: 'Remote/Global' },
  { title: 'Backend Developer', min: 40000, max: 80000, avg: 60000, currency: 'USD', location: 'Remote/Global' },
  { title: 'Full Stack Developer', min: 45000, max: 90000, avg: 65000, currency: 'USD', location: 'Remote/Global' },
  { title: 'Product Manager', min: 50000, max: 110000, avg: 80000, currency: 'USD', location: 'Remote/Global' },
  { title: 'Data Scientist', min: 55000, max: 120000, avg: 90000, currency: 'USD', location: 'Remote/Global' },
  { title: 'UI/UX Designer', min: 30000, max: 65000, avg: 45000, currency: 'USD', location: 'Remote/Global' },
  { title: 'DevOps Engineer', min: 50000, max: 100000, avg: 75000, currency: 'USD', location: 'Remote/Global' },
  { title: 'QA Engineer', min: 30000, max: 60000, avg: 42000, currency: 'USD', location: 'Remote/Global' },
];

const SalaryGuide: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-yellow-50 dark:from-gray-900 dark:to-gray-800 py-12 px-4">
      <div className="max-w-4xl mx-auto bg-white dark:bg-gray-900 rounded-2xl shadow-xl p-8">
        <h1 className="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-4 text-center">Salary Guide</h1>
        <p className="text-gray-600 dark:text-gray-300 mb-8 text-center max-w-2xl mx-auto">
          This salary guide provides an overview of average annual salaries for popular remote tech roles. Salaries may vary by experience, company, and location. Data is based on global remote job market trends and user submissions.
        </p>
        <div className="overflow-x-auto">
          <table className="min-w-full border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
            <thead className="bg-gray-100 dark:bg-gray-800">
              <tr>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Position</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Min</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Max</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Average</th>
                <th className="px-4 py-3 text-left text-xs font-semibold text-gray-700 dark:text-gray-300 uppercase">Location</th>
              </tr>
            </thead>
            <tbody>
              {salaryData.map((row, idx) => (
                <tr key={row.title} className={idx % 2 === 0 ? 'bg-white dark:bg-gray-900' : 'bg-gray-50 dark:bg-gray-800'}>
                  <td className="px-4 py-3 font-medium text-gray-900 dark:text-white">{row.title}</td>
                  <td className="px-4 py-3 text-green-700 dark:text-green-300">{row.min.toLocaleString()} {row.currency}</td>
                  <td className="px-4 py-3 text-red-700 dark:text-red-300">{row.max.toLocaleString()} {row.currency}</td>
                  <td className="px-4 py-3 text-blue-700 dark:text-blue-300 font-semibold">{row.avg.toLocaleString()} {row.currency}</td>
                  <td className="px-4 py-3 text-gray-600 dark:text-gray-400">{row.location}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <div className="mt-8 text-sm text-gray-500 dark:text-gray-400 text-center">
          <p>Want to contribute? <span className="underline cursor-pointer text-blue-600 dark:text-blue-400">Submit your salary data</span> anonymously to help improve this guide.</p>
        </div>
      </div>
    </div>
  );
};

export default SalaryGuide; 