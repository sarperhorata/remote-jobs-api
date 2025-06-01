import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { useAuth } from '../contexts/AuthContext';

// Initialize Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || '');

const Pricing: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);

  const handlePurchase = async (planType: 'monthly' | 'annual') => {
    if (!isAuthenticated) {
      // Redirect to login or show auth modal
      window.location.href = '/login';
      return;
    }

    try {
      setLoading(planType);
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          planType,
        }),
      });

      const { sessionId } = await response.json();
      const stripe = await stripePromise;
      
      if (stripe) {
        const { error } = await stripe.redirectToCheckout({
          sessionId,
        });

        if (error) {
          console.error('Stripe error:', error);
        }
      }
    } catch (error) {
      console.error('Error:', error);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-3xl font-bold text-center mb-8 text-gray-800 dark:text-white">Pricing Plans</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto">
        {/* Monthly Plan */}
        <div className="border border-gray-200 dark:border-gray-700 rounded-lg p-6 shadow-lg text-center bg-white dark:bg-gray-800">
          <h2 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">Monthly Plan</h2>
          <p className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">$9.99 <span className="text-lg font-normal text-gray-500 dark:text-gray-400">/ month</span></p>
          <ul className="text-left space-y-2 mb-6 text-gray-600 dark:text-gray-300">
            <li>✅ Access to all job listings</li>
            <li>✅ Basic profile features</li>
            <li>✅ Email notifications</li>
          </ul>
          <button 
            onClick={() => handlePurchase('monthly')}
            disabled={loading === 'monthly'}
            className="w-full py-2 px-4 bg-primary-600 hover:bg-primary-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === 'monthly' ? 'Processing...' : 'Choose Monthly'}
          </button>
        </div>

        {/* Annual Plan */}
        <div className="border border-primary-500 dark:border-primary-400 rounded-lg p-6 shadow-lg text-center bg-white dark:bg-gray-800 relative">
          <span className="absolute top-0 right-0 bg-primary-600 text-white text-xs font-semibold px-3 py-1 rounded-bl-lg">Popular</span>
          <h2 className="text-xl font-semibold mb-4 text-gray-700 dark:text-gray-200">Annual Plan</h2>
          <p className="text-4xl font-bold mb-4 text-gray-900 dark:text-white">$7.99 <span className="text-lg font-normal text-gray-500 dark:text-gray-400">/ month</span></p>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">(Billed annually at $95.88)</p>
          <ul className="text-left space-y-2 mb-6 text-gray-600 dark:text-gray-300">
            <li>✅ Access to all job listings</li>
            <li>✅ Premium profile features</li>
            <li>✅ Advanced search filters</li>
            <li>✅ Priority email notifications</li>
            <li>✅ Automatic application preparation (Coming Soon)</li>
          </ul>
          <button 
            onClick={() => handlePurchase('annual')}
            disabled={loading === 'annual'}
            className="w-full py-2 px-4 bg-primary-600 hover:bg-primary-700 text-white rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading === 'annual' ? 'Processing...' : 'Choose Annual'}
          </button>
        </div>
      </div>
    </div>
  );
};

export default Pricing; 