import React, { useState, useEffect } from 'react';
import { FaStar, FaThumbsUp, FaThumbsDown, FaUser, FaCalendar, FaFilter, FaSort } from 'react-icons/fa';

interface EmployeeReviewsTabProps {
  companyId: string;
}

interface Review {
  id: string;
  employeeName: string;
  position: string;
  location: string;
  rating: number;
  pros: string;
  cons: string;
  advice: string;
  date: string;
  helpfulCount: number;
  notHelpfulCount: number;
  employmentStatus: 'current' | 'former';
  lengthOfEmployment: string;
  jobTitle: string;
}

const EmployeeReviewsTab: React.FC<EmployeeReviewsTabProps> = ({ companyId }) => {
  const [reviews, setReviews] = useState<Review[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filterRating, setFilterRating] = useState<number | null>(null);
  const [sortBy, setSortBy] = useState<'date' | 'rating' | 'helpful'>('date');
  const [showFilters, setShowFilters] = useState(false);

  useEffect(() => {
    const fetchReviews = async () => {
      try {
        setLoading(true);
        // Mock data - gerçek implementasyonda Glassdoor API'den gelecek
        const mockReviews: Review[] = [
          {
            id: '1',
            employeeName: 'Sarah Johnson',
            position: 'Software Engineer',
            location: 'San Francisco, CA',
            rating: 5,
            pros: 'Great work-life balance, excellent benefits, supportive management, opportunities for growth',
            cons: 'Sometimes meetings can run long, occasional tight deadlines',
            advice: 'Be prepared to work in a fast-paced environment and take initiative on projects.',
            date: '2024-01-15',
            helpfulCount: 24,
            notHelpfulCount: 2,
            employmentStatus: 'current',
            lengthOfEmployment: '2 years',
            jobTitle: 'Senior Software Engineer'
          },
          {
            id: '2',
            employeeName: 'Michael Chen',
            position: 'Product Manager',
            location: 'New York, NY',
            rating: 4,
            pros: 'Innovative projects, collaborative team, good compensation, remote work options',
            cons: 'High expectations, can be stressful during product launches',
            advice: 'Make sure to communicate clearly with stakeholders and stay organized.',
            date: '2024-01-10',
            helpfulCount: 18,
            notHelpfulCount: 1,
            employmentStatus: 'current',
            lengthOfEmployment: '1.5 years',
            jobTitle: 'Product Manager'
          },
          {
            id: '3',
            employeeName: 'Emily Rodriguez',
            position: 'UX Designer',
            location: 'Austin, TX',
            rating: 4,
            pros: 'Creative freedom, user-centered approach, good team dynamics, flexible hours',
            cons: 'Sometimes unclear project requirements, occasional scope creep',
            advice: 'Always advocate for user needs and document your design decisions.',
            date: '2024-01-05',
            helpfulCount: 15,
            notHelpfulCount: 0,
            employmentStatus: 'former',
            lengthOfEmployment: '3 years',
            jobTitle: 'Senior UX Designer'
          },
          {
            id: '4',
            employeeName: 'David Kim',
            position: 'Data Scientist',
            location: 'Seattle, WA',
            rating: 5,
            pros: 'Cutting-edge technology, data-driven culture, excellent learning opportunities, competitive salary',
            cons: 'Complex projects can be challenging, requires continuous learning',
            advice: 'Stay updated with the latest technologies and be ready to learn new tools.',
            date: '2023-12-28',
            helpfulCount: 31,
            notHelpfulCount: 3,
            employmentStatus: 'current',
            lengthOfEmployment: '1 year',
            jobTitle: 'Data Scientist'
          },
          {
            id: '5',
            employeeName: 'Lisa Thompson',
            position: 'Marketing Manager',
            location: 'Chicago, IL',
            rating: 3,
            pros: 'Good team, interesting projects, decent benefits',
            cons: 'Limited career growth, sometimes unclear direction from leadership',
            advice: 'Be proactive about your career development and seek feedback regularly.',
            date: '2023-12-20',
            helpfulCount: 8,
            notHelpfulCount: 2,
            employmentStatus: 'former',
            lengthOfEmployment: '2 years',
            jobTitle: 'Marketing Manager'
          }
        ];
        
        // Simulate API delay
        await new Promise(resolve => setTimeout(resolve, 100));
        setReviews(mockReviews);
      } catch (err) {
        setError('Failed to load employee reviews');
        console.error('Error fetching reviews:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchReviews();
  }, [companyId]);

  const renderRatingStars = (rating: number) => {
    return (
      <div className="flex items-center gap-1">
        {[1, 2, 3, 4, 5].map((star) => (
          <FaStar
            key={star}
            className={`w-4 h-4 ${
              star <= rating
                ? 'text-yellow-400 fill-current'
                : 'text-gray-300'
            }`}
          />
        ))}
      </div>
    );
  };

  const filteredAndSortedReviews = reviews
    .filter(review => !filterRating || review.rating === filterRating)
    .sort((a, b) => {
      switch (sortBy) {
        case 'rating':
          return b.rating - a.rating;
        case 'helpful':
          return b.helpfulCount - a.helpfulCount;
        case 'date':
        default:
          return new Date(b.date).getTime() - new Date(a.date).getTime();
      }
    });

  const averageRating = reviews.length > 0 
    ? reviews.reduce((sum, review) => sum + review.rating, 0) / reviews.length 
    : 0;

  const ratingDistribution = [5, 4, 3, 2, 1].map(rating => ({
    rating,
    count: reviews.filter(r => r.rating === rating).length,
    percentage: reviews.length > 0 
      ? (reviews.filter(r => r.rating === rating).length / reviews.length) * 100 
      : 0
  }));

  if (loading) {
    return (
      <div className="animate-pulse space-y-6">
        <div className="h-8 bg-gray-200 rounded w-1/3"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map((i) => (
            <div key={i} className="h-20 bg-gray-200 rounded"></div>
          ))}
        </div>
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-32 bg-gray-200 rounded"></div>
          ))}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <div className="text-red-500 mb-2">
          <FaUser className="w-12 h-12 mx-auto mb-4" />
        </div>
        <h3 className="text-lg font-medium text-gray-900 mb-2">
          Reviews Unavailable
        </h3>
        <p className="text-gray-600">
          We couldn't load employee reviews at this time.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overall Rating Summary */}
      <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-2xl font-bold text-gray-900">Employee Reviews</h2>
          <div className="text-right">
            <div className="text-3xl font-bold text-blue-600">
              {averageRating.toFixed(1)}
            </div>
            <div className="text-sm text-gray-600">Average Rating</div>
          </div>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Rating Distribution */}
          <div>
            <h3 className="font-medium text-gray-900 mb-3">Rating Distribution</h3>
            <div className="space-y-2">
              {ratingDistribution.map(({ rating, count, percentage }) => (
                <div key={rating} className="flex items-center gap-3">
                  <div className="flex items-center gap-1 w-16">
                    <span className="text-sm font-medium text-gray-600">{rating}</span>
                    <FaStar className="w-3 h-3 text-yellow-400 fill-current" />
                  </div>
                  <div className="flex-1 bg-gray-200 rounded-full h-2">
                    <div
                      className="bg-yellow-400 h-2 rounded-full"
                      style={{ width: `${percentage}%` }}
                    />
                  </div>
                  <span className="text-sm text-gray-600 w-12 text-right">{count}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Stats */}
          <div>
            <h3 className="font-medium text-gray-900 mb-3">Quick Stats</h3>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Total Reviews</span>
                <span className="text-sm font-medium">{reviews.length}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Current Employees</span>
                <span className="text-sm font-medium">
                  {reviews.filter(r => r.employmentStatus === 'current').length}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-sm text-gray-600">Former Employees</span>
                <span className="text-sm font-medium">
                  {reviews.filter(r => r.employmentStatus === 'former').length}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Filters and Sort */}
      <div className="bg-white rounded-lg p-4 border border-gray-200">
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div className="flex items-center gap-4">
            <button
              onClick={() => setShowFilters(!showFilters)}
              className="flex items-center gap-2 px-3 py-2 text-sm font-medium text-gray-700 bg-gray-100 rounded-md hover:bg-gray-200 transition-colors"
            >
              <FaFilter className="w-4 h-4" />
              Filters
            </button>
            
            <div className="flex items-center gap-2">
              <FaSort className="w-4 h-4 text-gray-400" />
              <select
                value={sortBy}
                onChange={(e) => setSortBy(e.target.value as 'date' | 'rating' | 'helpful')}
                className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="date">Most Recent</option>
                <option value="rating">Highest Rated</option>
                <option value="helpful">Most Helpful</option>
              </select>
            </div>
          </div>

          {showFilters && (
            <div className="flex items-center gap-2">
              <span className="text-sm text-gray-600">Filter by rating:</span>
              <select
                value={filterRating || ''}
                onChange={(e) => setFilterRating(e.target.value ? Number(e.target.value) : null)}
                className="text-sm border border-gray-300 rounded-md px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
              >
                <option value="">All Ratings</option>
                <option value="5">5 Stars</option>
                <option value="4">4 Stars</option>
                <option value="3">3 Stars</option>
                <option value="2">2 Stars</option>
                <option value="1">1 Star</option>
              </select>
            </div>
          )}
        </div>
      </div>

      {/* Reviews List */}
      <div className="space-y-4">
        {filteredAndSortedReviews.length === 0 ? (
          <div className="text-center py-8">
            <FaUser className="w-12 h-12 text-gray-300 mx-auto mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Reviews Found</h3>
            <p className="text-gray-600">
              No reviews match your current filters.
            </p>
          </div>
        ) : (
          filteredAndSortedReviews.map((review) => (
            <div key={review.id} className="bg-white rounded-lg p-6 border border-gray-200 hover:shadow-md transition-shadow">
              {/* Review Header */}
              <div className="flex items-start justify-between mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-blue-100 rounded-full flex items-center justify-center">
                    <FaUser className="w-5 h-5 text-blue-600" />
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">{review.employeeName}</h4>
                    <p className="text-sm text-gray-600">{review.jobTitle}</p>
                    <div className="flex items-center gap-2 text-xs text-gray-500">
                      <FaCalendar className="w-3 h-3" />
                      <span>{new Date(review.date).toLocaleDateString()}</span>
                      <span>•</span>
                      <span>{review.location}</span>
                      <span>•</span>
                      <span className={`px-2 py-1 rounded-full text-xs ${
                        review.employmentStatus === 'current' 
                          ? 'bg-green-100 text-green-800' 
                          : 'bg-gray-100 text-gray-800'
                      }`}>
                        {review.employmentStatus === 'current' ? 'Current' : 'Former'}
                      </span>
                    </div>
                  </div>
                </div>
                <div className="text-right">
                  {renderRatingStars(review.rating)}
                  <p className="text-xs text-gray-500 mt-1">{review.lengthOfEmployment}</p>
                </div>
              </div>

              {/* Review Content */}
              <div className="space-y-4">
                {/* Pros */}
                <div>
                  <h5 className="font-medium text-green-700 mb-2 flex items-center gap-2">
                    <div className="w-2 h-2 bg-green-500 rounded-full"></div>
                    Pros
                  </h5>
                  <p className="text-gray-700 text-sm">{review.pros}</p>
                </div>

                {/* Cons */}
                <div>
                  <h5 className="font-medium text-red-700 mb-2 flex items-center gap-2">
                    <div className="w-2 h-2 bg-red-500 rounded-full"></div>
                    Cons
                  </h5>
                  <p className="text-gray-700 text-sm">{review.cons}</p>
                </div>

                {/* Advice */}
                <div>
                  <h5 className="font-medium text-blue-700 mb-2 flex items-center gap-2">
                    <div className="w-2 h-2 bg-blue-500 rounded-full"></div>
                    Advice to Management
                  </h5>
                  <p className="text-gray-700 text-sm">{review.advice}</p>
                </div>
              </div>

              {/* Review Actions */}
              <div className="flex items-center justify-between mt-4 pt-4 border-t border-gray-100">
                <div className="flex items-center gap-4">
                  <button className="flex items-center gap-1 text-sm text-gray-600 hover:text-green-600 transition-colors">
                    <FaThumbsUp className="w-4 h-4" />
                    <span>Helpful ({review.helpfulCount})</span>
                  </button>
                  <button className="flex items-center gap-1 text-sm text-gray-600 hover:text-red-600 transition-colors">
                    <FaThumbsDown className="w-4 h-4" />
                    <span>Not Helpful ({review.notHelpfulCount})</span>
                  </button>
                </div>
              </div>
            </div>
          ))
        )}
      </div>

      {/* Load More Button */}
      {filteredAndSortedReviews.length > 0 && (
        <div className="text-center">
          <button className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">
            Load More Reviews
          </button>
        </div>
      )}
    </div>
  );
};

export default EmployeeReviewsTab; 