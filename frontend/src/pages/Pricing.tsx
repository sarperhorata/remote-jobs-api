import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import CheckCircleIcon from '@mui/icons-material/CheckCircle';
import CancelIcon from '@mui/icons-material/Cancel';
import InfoIcon from '@mui/icons-material/Info';
import { useAuth } from '../contexts/AuthContext';

const Pricing: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'yearly'>('monthly');

  // Pricing configuration
  const pricing = {
    free: {
      name: 'Free',
      price: {
        monthly: 0,
        yearly: 0
      },
      features: [
        { name: 'Basic job search', included: true },
        { name: 'Browse jobs by category', included: true },
        { name: 'View company details', included: true },
        { name: 'Limited application (5/month)', included: true },
        { name: 'Email notifications', included: true },
        { name: 'Create profile', included: true },
        { name: 'Save jobs (unlimited)', included: true },
        { name: 'Advanced filters', included: false },
        { name: 'Early access to jobs', included: false },
        { name: 'Profile featured for employers', included: false },
        { name: 'Application tracking', included: false },
        { name: 'Resume builder', included: false },
        { name: 'Skill assessments', included: false },
        { name: 'Unlimited applications', included: false },
        { name: 'Priority support', included: false }
      ]
    },
    premium: {
      name: 'Premium',
      price: {
        monthly: 9.99,
        yearly: 7.99  // monthly price when paid yearly
      },
      features: [
        { name: 'Basic job search', included: true },
        { name: 'Browse jobs by category', included: true },
        { name: 'View company details', included: true },
        { name: 'Limited application (5/month)', included: true, replaced: 'Unlimited applications' },
        { name: 'Email notifications', included: true },
        { name: 'Create profile', included: true },
        { name: 'Save jobs (unlimited)', included: true },
        { name: 'Advanced filters', included: true },
        { name: 'Early access to jobs', included: true },
        { name: 'Profile featured for employers', included: true },
        { name: 'Application tracking', included: true },
        { name: 'Resume builder', included: true },
        { name: 'Skill assessments', included: true },
        { name: 'Unlimited applications', included: true },
        { name: 'Priority support', included: true }
      ]
    }
  };

  // Get yearly discount percentage
  const yearlyDiscount = Math.round(100 - (pricing.premium.price.yearly * 12 / pricing.premium.price.monthly / 12 * 100));

  return (
    <div className="min-h-screen bg-gray-50 py-16">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="text-center mb-16">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">Simple, Transparent Pricing</h1>
          <p className="text-xl text-gray-600 max-w-3xl mx-auto">
            Choose the plan that works best for your job search. Upgrade anytime to unlock premium features.
          </p>
          
          {/* Billing Period Toggle */}
          <div className="mt-8 inline-flex items-center bg-gray-100 p-1 rounded-full">
            <button
              onClick={() => setBillingPeriod('monthly')}
              className={`py-2 px-6 rounded-full text-sm font-medium ${
                billingPeriod === 'monthly' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              Monthly
            </button>
            <button
              onClick={() => setBillingPeriod('yearly')}
              className={`py-2 px-6 rounded-full text-sm font-medium ${
                billingPeriod === 'yearly' 
                  ? 'bg-white text-blue-600 shadow-sm' 
                  : 'text-gray-500 hover:text-gray-900'
              }`}
            >
              Yearly <span className="text-green-600 font-semibold">Save {yearlyDiscount}%</span>
            </button>
          </div>
        </div>
        
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {/* Free Plan */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden transition-all hover:shadow-xl">
            <div className="p-8 border-b">
              <h2 className="text-2xl font-bold text-gray-900">{pricing.free.name}</h2>
              <div className="mt-4 flex items-baseline">
                <span className="text-5xl font-extrabold text-gray-900">$0</span>
                <span className="ml-1 text-xl font-medium text-gray-500">/month</span>
              </div>
              <p className="mt-4 text-gray-600">Perfect for job seekers who want to explore opportunities.</p>
            </div>
            <div className="p-8">
              <ul className="space-y-4">
                {pricing.free.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    {feature.included ? (
                      <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                    ) : (
                      <CancelIcon className="h-5 w-5 text-gray-300 mt-0.5 mr-2 flex-shrink-0" />
                    )}
                    <span className={feature.included ? 'text-gray-800' : 'text-gray-400'}>
                      {feature.name}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link 
                  to={isAuthenticated ? "/dashboard" : "/signup"}
                  className="block text-center py-3 px-4 rounded-lg border-2 border-blue-600 text-blue-600 font-medium hover:bg-blue-50 transition-colors"
                >
                  {isAuthenticated ? 'Access Free Features' : 'Sign Up for Free'}
                </Link>
              </div>
            </div>
          </div>
          
          {/* Premium Plan */}
          <div className="bg-white rounded-2xl shadow-lg overflow-hidden border-2 border-blue-600 transition-all hover:shadow-xl relative">
            <div className="absolute top-0 right-0 bg-blue-600 text-white px-4 py-1 rounded-bl-lg text-sm font-bold">
              RECOMMENDED
            </div>
            <div className="p-8 border-b">
              <h2 className="text-2xl font-bold text-gray-900">{pricing.premium.name}</h2>
              <div className="mt-4 flex items-baseline">
                <span className="text-5xl font-extrabold text-gray-900">
                  ${billingPeriod === 'monthly' ? pricing.premium.price.monthly.toFixed(2) : pricing.premium.price.yearly.toFixed(2)}
                </span>
                <span className="ml-1 text-xl font-medium text-gray-500">/month</span>
              </div>
              <p className="mt-4 text-gray-600">
                {billingPeriod === 'yearly' ? 'Billed annually at $' + (pricing.premium.price.yearly * 12).toFixed(2) + '/year' : 'Billed monthly'}
              </p>
            </div>
            <div className="p-8">
              <ul className="space-y-4">
                {pricing.premium.features.map((feature, index) => (
                  <li key={index} className="flex items-start">
                    <CheckCircleIcon className="h-5 w-5 text-green-500 mt-0.5 mr-2 flex-shrink-0" />
                    <span className="text-gray-800">
                      {feature.replaced || feature.name}
                    </span>
                  </li>
                ))}
              </ul>
              <div className="mt-8">
                <Link 
                  to={isAuthenticated ? "/upgrade" : "/signup?plan=premium"}
                  className="block text-center py-3 px-4 rounded-lg bg-blue-600 text-white font-medium hover:bg-blue-700 transition-colors"
                >
                  {isAuthenticated ? 'Upgrade Now' : 'Get Started'}
                </Link>
              </div>
            </div>
          </div>
        </div>
        
        {/* FAQ Section */}
        <div className="mt-20 max-w-4xl mx-auto">
          <h2 className="text-3xl font-bold text-center mb-12">Frequently Asked Questions</h2>
          
          <div className="space-y-8">
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-3">Can I cancel my premium subscription anytime?</h3>
              <p className="text-gray-600">Yes, you can cancel your subscription at any time. Your premium features will remain active until the end of your billing period.</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-3">How does the "Early access to jobs" feature work?</h3>
              <p className="text-gray-600">Premium members get access to new job listings 24 hours before they become available to free users, giving you a competitive advantage in applying early.</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-3">What happens when I exceed my monthly application limit on the free plan?</h3>
              <p className="text-gray-600">Once you reach your monthly application limit, you'll need to wait until the next month for your quota to reset, or upgrade to Premium for unlimited applications.</p>
            </div>
            
            <div className="bg-white p-6 rounded-lg shadow-md">
              <h3 className="text-xl font-semibold mb-3">Do you offer any discounts for students or non-profits?</h3>
              <p className="text-gray-600">Yes, we offer special discounts for students and non-profit organizations. Please contact our support team to learn more about these offers.</p>
            </div>
          </div>
          
          <div className="mt-12 text-center">
            <p className="text-gray-600 mb-4">Still have questions about our pricing plans?</p>
            <Link to="/contact" className="text-blue-600 font-medium hover:text-blue-800 flex items-center justify-center">
              <InfoIcon className="h-5 w-5 mr-1" />
              Contact our support team
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Pricing; 