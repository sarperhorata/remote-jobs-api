import React, { useState } from 'react';
import { loadStripe } from '@stripe/stripe-js';
import { useAuth } from '../contexts/AuthContext';
import { Check, X, Star, Crown, Users } from '../components/icons/EmojiIcons';
import Layout from '../components/Layout';

// Initialize Stripe
const stripePromise = loadStripe(process.env.REACT_APP_STRIPE_PUBLIC_KEY || '');

interface PricingPlan {
  id: string;
  name: string;
  price: number;
  originalPrice?: number;
  period: string;
  description: string;
  features: string[];
  limitations?: string[];
  highlight?: boolean;
  icon: React.ReactNode;
  buttonText: string;
  buttonStyle: string;
}

const pricingPlans: PricingPlan[] = [
  {
    id: 'free',
    name: 'Free',
    price: 0,
    period: 'forever',
    description: 'Perfect for getting started with remote job searching',
    features: [
      'Browse all remote job listings',
      'Basic profile creation',
      'Apply to up to 20 jobs per month', // Güncellendi
      'Email notifications for new jobs',
      'Basic search filters',
      'Mobile app access',
      'Community access'
    ],
    limitations: [
      'Limited to 20 applications per month', // Güncellendi
      'No priority support',
      'No advanced analytics'
    ],
    icon: <Users className="w-8 h-8" />, 
    buttonText: 'Get Started Free',
    buttonStyle: 'bg-gray-600 hover:bg-gray-700 text-white'
  },
  {
    id: 'pro',
    name: 'Pro',
    price: 19,
    originalPrice: 29,
    period: 'month',
    description: 'For serious job seekers who want premium features',
    features: [
      'Everything in Free',
      'Unlimited job applications',
      'AI-powered job matching',
      'Advanced search & filters',
      'Priority customer support',
      'Application tracking dashboard',
      'Resume optimization tips',
      'Salary insights & negotiation tips',
      'Interview preparation resources',
      'Personal job alerts',
      'Profile visibility boost',
      'Company research tools'
    ],
    highlight: true,
    icon: <Star className="w-8 h-8" />,
    buttonText: 'Start Pro Trial',
    buttonStyle: 'bg-gradient-to-r from-orange-500 to-yellow-500 hover:from-orange-600 hover:to-yellow-600 text-white'
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    price: 49,
    period: 'month',
    description: 'For teams and advanced professionals',
    features: [
      'Everything in Pro',
      'Team collaboration tools',
      'Bulk application management',
      'Advanced analytics & reporting',
      'Custom integrations',
      'Dedicated account manager',
      'White-label solutions',
      'API access',
      'Custom branding',
      'Advanced security features',
      'Priority job placement',
      'Exclusive networking events'
    ],
    icon: <Crown className="w-8 h-8" />,
    buttonText: 'Contact Sales',
    buttonStyle: 'bg-purple-600 hover:bg-purple-700 text-white'
  }
];

// Karşılaştırma tablosunu daha kapsamlı ve modern hale getir
const comparisonFeatures = [
  { name: 'Job Applications per Month', free: '20', pro: 'Unlimited', enterprise: 'Unlimited' },
  { name: 'AI Job Matching', free: false, pro: true, enterprise: true },
  { name: 'Advanced Search Filters', free: false, pro: true, enterprise: true },
  { name: 'Application Tracking', free: 'Basic', pro: 'Advanced', enterprise: 'Advanced + Analytics' },
  { name: 'Resume Optimization', free: false, pro: true, enterprise: true },
  { name: 'Salary Insights', free: false, pro: true, enterprise: true },
  { name: 'Priority Support', free: false, pro: true, enterprise: 'Dedicated Manager' },
  { name: 'Team Collaboration', free: false, pro: false, enterprise: true },
  { name: 'API Access', free: false, pro: false, enterprise: true },
  { name: 'Custom Integrations', free: false, pro: false, enterprise: true },
  { name: 'Profile Visibility Boost', free: false, pro: true, enterprise: true },
  { name: 'Company Research Tools', free: false, pro: true, enterprise: true },
  { name: 'Mobile App Access', free: true, pro: true, enterprise: true },
  { name: 'Community Access', free: true, pro: true, enterprise: true },
  { name: 'White-label Solutions', free: false, pro: false, enterprise: true },
  { name: 'Exclusive Networking Events', free: false, pro: false, enterprise: true },
];

const Pricing: React.FC = () => {
  const { isAuthenticated } = useAuth();
  const [loading, setLoading] = useState<string | null>(null);
  const [billingPeriod, setBillingPeriod] = useState<'monthly' | 'annual'>('monthly');

  const handlePurchase = async (planId: string) => {
    if (planId === 'free') {
      // Redirect to signup for free plan
      window.location.href = '/register';
      return;
    }

    if (planId === 'enterprise') {
      // Redirect to contact page for enterprise
      window.location.href = '/contact';
      return;
    }

    if (!isAuthenticated) {
      // Redirect to login or show auth modal
      window.location.href = '/login';
      return;
    }

    try {
      setLoading(planId);
      const response = await fetch('/api/create-checkout-session', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          planId,
          billingPeriod,
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

  const getAnnualPrice = (monthlyPrice: number) => {
    return Math.round(monthlyPrice * 12 * 0.8); // 20% discount for annual
  };

  return (
    <Layout>
      <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
        <div className="max-w-7xl mx-auto">
          {/* Header */}
          <div className="text-center mb-16">
            <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
              Simple, Transparent Pricing
            </h1>
            <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
              Choose the perfect plan to accelerate your remote career. Start free and upgrade as you grow.
            </p>
            
            {/* Billing Toggle */}
            <div className="mt-8 flex items-center justify-center">
              <span className={`text-sm font-medium ${billingPeriod === 'monthly' ? 'text-gray-900' : 'text-gray-500'}`}>
                Monthly
              </span>
              <button
                onClick={() => setBillingPeriod(billingPeriod === 'monthly' ? 'annual' : 'monthly')}
                className="mx-3 relative inline-flex h-6 w-11 flex-shrink-0 cursor-pointer rounded-full border-2 border-transparent bg-orange-500 transition-colors duration-200 ease-in-out focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2"
              >
                <span
                  className={`pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow ring-0 transition duration-200 ease-in-out ${
                    billingPeriod === 'annual' ? 'translate-x-5' : 'translate-x-0'
                  }`}
                />
              </button>
              <span className={`text-sm font-medium ${billingPeriod === 'annual' ? 'text-gray-900' : 'text-gray-500'}`}>
                Annual
                <span className="ml-1 inline-flex items-center rounded-full bg-green-100 px-2.5 py-0.5 text-xs font-medium text-green-800">
                  Save 20%
                </span>
              </span>
            </div>
          </div>

          {/* Pricing Cards */}
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 mb-16">
            {pricingPlans.map((plan) => (
              <div
                key={plan.id}
                className={`relative rounded-2xl border ${
                  plan.highlight
                    ? 'border-orange-500 shadow-2xl scale-105'
                    : 'border-gray-200 shadow-lg'
                } bg-white overflow-hidden`}
              >
                {plan.highlight && (
                  <div className="absolute top-0 left-0 right-0 bg-gradient-to-r from-orange-500 to-yellow-500 px-6 py-2 text-center">
                    <span className="text-sm font-semibold text-white">Most Popular</span>
                  </div>
                )}
                
                <div className={`px-6 ${plan.highlight ? 'pt-10' : 'pt-6'} pb-6`}>
                  {/* Plan Header */}
                  <div className="text-center mb-6">
                    <div className="flex items-center justify-center mb-4">
                      <div className={`p-3 rounded-full ${
                        plan.highlight ? 'bg-orange-100 text-orange-600' : 'bg-gray-100 text-gray-600'
                      }`}>
                        {plan.icon}
                      </div>
                    </div>
                    <h3 className="text-2xl font-bold text-gray-900">{plan.name}</h3>
                    <p className="mt-2 text-gray-600">{plan.description}</p>
                  </div>

                  {/* Pricing */}
                  <div className="text-center mb-6">
                    <div className="flex items-center justify-center">
                      <span className="text-4xl font-extrabold text-gray-900">
                        ${billingPeriod === 'annual' && plan.price > 0 
                          ? Math.round(plan.price * 0.8) 
                          : plan.price}
                      </span>
                      {plan.price > 0 && (
                        <span className="text-lg font-medium text-gray-500 ml-1">
                          /{billingPeriod === 'annual' ? 'month' : plan.period}
                        </span>
                      )}
                    </div>
                    {billingPeriod === 'annual' && plan.price > 0 && (
                      <p className="text-sm text-gray-500 mt-1">
                        Billed annually (${getAnnualPrice(plan.price)}/year)
                      </p>
                    )}
                    {plan.originalPrice && billingPeriod === 'monthly' && (
                      <p className="text-sm text-gray-500 mt-1">
                        <span className="line-through">${plan.originalPrice}</span> /month
                      </p>
                    )}
                  </div>

                  {/* Features */}
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, index) => (
                      <li key={index} className="flex items-start">
                        <Check className="w-5 h-5 text-green-500 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                    {plan.limitations?.map((limitation, index) => (
                      <li key={`limit-${index}`} className="flex items-start opacity-60">
                        <X className="w-5 h-5 text-gray-400 mr-3 mt-0.5 flex-shrink-0" />
                        <span className="text-gray-600">{limitation}</span>
                      </li>
                    ))}
                  </ul>

                  {/* CTA Button */}
                  <button
                    onClick={() => handlePurchase(plan.id)}
                    disabled={loading === plan.id}
                    className={`w-full py-3 px-4 rounded-lg font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed ${plan.buttonStyle}`}
                  >
                    {loading === plan.id ? 'Processing...' : plan.buttonText}
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Feature Comparison Table */}
          <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
            <div className="px-6 py-8 border-b border-gray-200">
              <h2 className="text-3xl font-bold text-gray-900 text-center">
                Compare Plans
              </h2>
              <p className="mt-2 text-gray-600 text-center">
                See exactly what you get with each plan
              </p>
            </div>
            
            <div className="overflow-x-auto">
              <table className="w-full">
                <thead>
                  <tr className="border-b border-gray-200">
                    <th className="px-6 py-4 text-left text-sm font-medium text-gray-900 w-1/2">
                      Features
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-medium text-gray-900">
                      Free
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-medium text-gray-900 bg-orange-50">
                      Pro
                    </th>
                    <th className="px-6 py-4 text-center text-sm font-medium text-gray-900">
                      Enterprise
                    </th>
                  </tr>
                </thead>
                <tbody>
                  {comparisonFeatures.map((feature, index) => (
                    <tr key={index} className="border-b border-gray-100">
                      <td className="px-6 py-4 text-sm text-gray-900 font-medium">
                        {feature.name}
                      </td>
                      <td className="px-6 py-4 text-center text-sm text-gray-600">
                        {typeof feature.free === 'boolean' ? (
                          feature.free ? (
                            <Check className="w-5 h-5 text-green-500 mx-auto" />
                          ) : (
                            <X className="w-5 h-5 text-gray-400 mx-auto" />
                          )
                        ) : (
                          feature.free
                        )}
                      </td>
                      <td className="px-6 py-4 text-center text-sm text-gray-600 bg-orange-50">
                        {typeof feature.pro === 'boolean' ? (
                          feature.pro ? (
                            <Check className="w-5 h-5 text-green-500 mx-auto" />
                          ) : (
                            <X className="w-5 h-5 text-gray-400 mx-auto" />
                          )
                        ) : (
                          feature.pro
                        )}
                      </td>
                      <td className="px-6 py-4 text-center text-sm text-gray-600">
                        {typeof feature.enterprise === 'boolean' ? (
                          feature.enterprise ? (
                            <Check className="w-5 h-5 text-green-500 mx-auto" />
                          ) : (
                            <X className="w-5 h-5 text-gray-400 mx-auto" />
                          )
                        ) : (
                          feature.enterprise
                        )}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* FAQ Section */}
          <div className="mt-16 text-center">
            <h2 className="text-3xl font-bold text-gray-900 mb-8">
              Frequently Asked Questions
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 max-w-4xl mx-auto text-left">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Can I cancel my subscription anytime?
                </h3>
                <p className="text-gray-600">
                  Yes, you can cancel your subscription at any time. You'll continue to have access to premium features until the end of your billing period.
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Do you offer refunds?
                </h3>
                <p className="text-gray-600">
                  We offer a 14-day money-back guarantee for all paid plans. If you're not satisfied, contact our support team for a full refund.
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  What payment methods do you accept?
                </h3>
                <p className="text-gray-600">
                  We accept all major credit cards (Visa, MasterCard, American Express) and PayPal. All payments are processed securely through Stripe.
                </p>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">
                  Can I upgrade or downgrade my plan?
                </h3>
                <p className="text-gray-600">
                  Yes, you can change your plan at any time. Upgrades take effect immediately, while downgrades take effect at the next billing cycle.
                </p>
              </div>
            </div>
          </div>

          {/* CTA Section */}
          <div className="mt-16 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-2xl px-8 py-12 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Ready to Find Your Dream Remote Job?
            </h2>
            <p className="text-xl text-orange-100 mb-8">
              Join thousands of professionals who've found their perfect remote career with Buzz2Remote.
            </p>
            <button
              onClick={() => handlePurchase('free')}
              className="bg-white text-orange-600 px-8 py-3 rounded-lg hover:bg-orange-50 transition-colors font-semibold text-lg shadow-lg"
            >
              Start Your Free Account Today
            </button>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default Pricing; 