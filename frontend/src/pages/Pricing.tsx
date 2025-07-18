import React, { useState } from 'react';
import Layout from '../components/Layout';
import { 
  Check, 
  Star, 
  Zap, 
  Crown, 
  Users, 
  Building, 
  DollarSign,
  ArrowRight,
  Badge,
  Shield,
  Clock,
  Target
} from 'lucide-react';

const Pricing: React.FC = () => {
  const [isAnnual, setIsAnnual] = useState(false);

  const jobSeekerPlans = [
    {
      name: "Free",
      price: 0,
      period: "Forever",
      description: "Perfect for getting started with remote work",
      features: [
        "Access to 10,000+ remote jobs",
        "Basic job search and filters",
        "Email job alerts",
        "Basic profile creation",
        "Community access"
      ],
      popular: false,
      icon: <Star className="w-8 h-8" />,
      color: "from-gray-400 to-gray-600"
    },
    {
      name: "Pro",
      price: isAnnual ? 99 : 12,
      period: isAnnual ? "per year" : "per month",
      description: "For serious remote job seekers",
      features: [
        "Unlimited job access",
        "Advanced search filters",
        "Resume builder & templates",
        "Salary insights & negotiations",
        "AI-powered cover letter generation",
        "Priority customer support"
      ],
      popular: true,
      icon: <Zap className="w-8 h-8" />,
      color: "from-blue-500 to-purple-600"
    },
    {
      name: "Premium",
      price: isAnnual ? 199 : 25,
      period: isAnnual ? "per year" : "per month",
      description: "Complete remote work solution",
      features: [
        "Everything in Pro",
        "AI-powered job matching",
        "Personal career advisor",
        "Exclusive remote job listings",
        "Automatic cover letter generation",
        "Automatic job application",
        "Resume optimization service",
        "Priority customer support"
      ],
      popular: false,
      icon: <Crown className="w-8 h-8" />,
      color: "from-yellow-400 to-orange-500"
    }
  ];

  const employerPlans = [
    {
      name: "Starter",
      price: isAnnual ? 299 : 39,
      period: isAnnual ? "per year" : "per month",
      description: "Perfect for small teams",
      features: [
        "Post up to 5 job listings",
        "Basic candidate search",
        "Email notifications",
        "Company profile",
        "Basic analytics"
      ],
      popular: false,
      icon: <Building className="w-8 h-8" />,
      color: "from-green-400 to-green-600"
    },
    {
      name: "Business",
      price: isAnnual ? 599 : 79,
      period: isAnnual ? "per year" : "per month",
      description: "For growing companies",
      features: [
        "Post up to 20 job listings",
        "Advanced candidate search",
        "AI-powered candidate matching",
        "Interview scheduling tools",
        "Advanced analytics & reporting",
        "Priority support",
        "Branded job pages",
        "Team collaboration tools"
      ],
      popular: true,
      icon: <Users className="w-8 h-8" />,
      color: "from-blue-500 to-purple-600"
    },
    {
      name: "Enterprise",
      price: "Custom",
      period: "Contact us",
      description: "For large organizations",
      features: [
        "Unlimited job listings",
        "Custom integrations",
        "Dedicated account manager",
        "Advanced security features",
        "Custom branding",
        "API access",
        "White-label solutions",
        "24/7 priority support"
      ],
      popular: false,
      icon: <Crown className="w-8 h-8" />,
      color: "from-purple-500 to-pink-600"
    }
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-gray-50 via-white to-blue-50">
        {/* Hero Section */}
        <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 via-purple-600 to-indigo-800 text-white py-20">
          <div className="absolute inset-0 bg-black/20"></div>
          <div className="relative container mx-auto px-4 text-center">
            <div className="max-w-4xl mx-auto">
              <h1 className="text-4xl md:text-6xl font-bold mb-6">
                Simple, Transparent Pricing 💰
              </h1>
              <p className="text-xl md:text-2xl opacity-90 mb-8">
                Choose the perfect plan for your remote work journey
              </p>
              
              {/* Billing Toggle */}
              <div className="flex items-center justify-center space-x-4 mb-8">
                <span className={`text-sm ${!isAnnual ? 'text-white' : 'text-white/70'}`}>Monthly</span>
                <button
                  onClick={() => setIsAnnual(!isAnnual)}
                  className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                    isAnnual ? 'bg-white' : 'bg-white/30'
                  }`}
                >
                  <span
                    className={`inline-block h-4 w-4 transform rounded-full bg-blue-600 transition-transform ${
                      isAnnual ? 'translate-x-6' : 'translate-x-1'
                    }`}
                  />
                </button>
                <span className={`text-sm ${isAnnual ? 'text-white' : 'text-white/70'}`}>
                  Annual <span className="bg-green-500 text-white px-2 py-1 rounded-full text-xs ml-2">Save 20%</span>
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Job Seeker Plans */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                For Job Seekers 🚀
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Find your perfect remote job with our comprehensive plans
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {jobSeekerPlans.map((plan, index) => (
                <div
                  key={index}
                  className={`relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-200 border-2 ${
                    plan.popular ? 'border-blue-500 scale-105' : 'border-gray-100'
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-blue-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        Most Popular
                      </span>
                    </div>
                  )}
                  
                  <div className={`w-16 h-16 rounded-xl bg-gradient-to-r ${plan.color} flex items-center justify-center text-white mb-6`}>
                    {plan.icon}
                  </div>
                  
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-6">{plan.description}</p>
                  
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-gray-900">
                      {typeof plan.price === 'number' ? `$${plan.price}` : plan.price}
                    </span>
                    <span className="text-gray-600 ml-2">{plan.period}</span>
                  </div>
                  
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center space-x-3">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <button className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200 ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}>
                    {plan.name === "Free" ? "Get Started" : "Choose Plan"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Employer Plans */}
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                For Employers 🏢
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                Find the best remote talent for your organization
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-6xl mx-auto">
              {employerPlans.map((plan, index) => (
                <div
                  key={index}
                  className={`relative bg-white rounded-2xl p-8 shadow-lg hover:shadow-xl transition-all duration-200 border-2 ${
                    plan.popular ? 'border-blue-500 scale-105' : 'border-gray-100'
                  }`}
                >
                  {plan.popular && (
                    <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                      <span className="bg-blue-500 text-white px-4 py-2 rounded-full text-sm font-semibold">
                        Most Popular
                      </span>
                    </div>
                  )}
                  
                  <div className={`w-16 h-16 rounded-xl bg-gradient-to-r ${plan.color} flex items-center justify-center text-white mb-6`}>
                    {plan.icon}
                  </div>
                  
                  <h3 className="text-2xl font-bold text-gray-900 mb-2">{plan.name}</h3>
                  <p className="text-gray-600 mb-6">{plan.description}</p>
                  
                  <div className="mb-6">
                    <span className="text-4xl font-bold text-gray-900">
                      {typeof plan.price === 'number' ? `$${plan.price}` : plan.price}
                    </span>
                    <span className="text-gray-600 ml-2">{plan.period}</span>
                  </div>
                  
                  <ul className="space-y-3 mb-8">
                    {plan.features.map((feature, featureIndex) => (
                      <li key={featureIndex} className="flex items-center space-x-3">
                        <Check className="w-5 h-5 text-green-500 flex-shrink-0" />
                        <span className="text-gray-700">{feature}</span>
                      </li>
                    ))}
                  </ul>
                  
                  <button className={`w-full py-3 px-6 rounded-lg font-semibold transition-all duration-200 ${
                    plan.popular
                      ? 'bg-gradient-to-r from-blue-500 to-purple-600 text-white hover:from-blue-600 hover:to-purple-700'
                      : 'bg-gray-100 text-gray-900 hover:bg-gray-200'
                  }`}>
                    {plan.name === "Enterprise" ? "Contact Sales" : "Choose Plan"}
                  </button>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Features Comparison */}
        <section className="py-16">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Why Choose Buzz2Remote? 🐝
              </h2>
              <p className="text-lg text-gray-600 max-w-2xl mx-auto">
                We're not just another job board - we're your remote work partner
              </p>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Target className="w-8 h-8 text-blue-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Smart Matching</h3>
                <p className="text-gray-600 text-sm">AI-powered job matching based on your skills and preferences</p>
              </div>
              
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-green-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Shield className="w-8 h-8 text-green-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Verified Jobs</h3>
                <p className="text-gray-600 text-sm">All jobs are verified and vetted for quality and legitimacy</p>
              </div>
              
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-purple-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Clock className="w-8 h-8 text-purple-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Real-time Updates</h3>
                <p className="text-gray-600 text-sm">Get instant notifications when new matching jobs are posted</p>
              </div>
              
              <div className="text-center p-6">
                <div className="w-16 h-16 bg-orange-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <Badge className="w-8 h-8 text-orange-600" />
                </div>
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Premium Support</h3>
                <p className="text-gray-600 text-sm">Dedicated support team to help you succeed in remote work</p>
              </div>
            </div>
          </div>
        </section>

        {/* FAQ Section */}
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4">
            <div className="text-center mb-12">
              <h2 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
                Frequently Asked Questions ❓
              </h2>
            </div>
            
            <div className="max-w-3xl mx-auto space-y-6">
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Can I cancel my subscription anytime?</h3>
                <p className="text-gray-600">Yes, you can cancel your subscription at any time. No long-term contracts or hidden fees.</p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Do you offer refunds?</h3>
                <p className="text-gray-600">We offer a 30-day money-back guarantee for all paid plans. If you're not satisfied, we'll refund your payment.</p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">What payment methods do you accept?</h3>
                <p className="text-gray-600">We accept all major credit cards, PayPal, and bank transfers for enterprise plans.</p>
              </div>
              
              <div className="bg-white rounded-lg p-6 shadow-sm">
                <h3 className="text-lg font-semibold text-gray-900 mb-2">Is my data secure?</h3>
                <p className="text-gray-600">Yes, we use industry-standard encryption and security measures to protect your personal and payment information.</p>
              </div>
            </div>
          </div>
        </section>

        {/* Call to Action */}
        <section className="py-16">
          <div className="container mx-auto px-4 text-center">
            <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-2xl p-8 text-white">
              <h3 className="text-2xl md:text-3xl font-bold mb-4">
                Ready to Start Your Remote Work Journey?
              </h3>
              <p className="text-lg opacity-90 mb-6">
                Join thousands of professionals who've found their dream remote jobs
              </p>
              <button className="bg-white text-blue-600 font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors flex items-center space-x-2 mx-auto">
                <span>Get Started Today</span>
                <ArrowRight className="w-5 h-5" />
              </button>
            </div>
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default Pricing; 