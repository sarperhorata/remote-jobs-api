import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import Layout from '../components/Layout';
import { ShieldCheck, ArrowLeft, ChevronDown, ChevronUp, Calendar, Mail, Globe, Eye, Lock, Database, UserCheck, Cookie } from '../components/icons/EmojiIcons';

const CookiePolicy: React.FC = () => {
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set());

  const toggleSection = (sectionId: string) => {
    const newExpanded = new Set(expandedSections);
    if (newExpanded.has(sectionId)) {
      newExpanded.delete(sectionId);
    } else {
      newExpanded.add(sectionId);
    }
    setExpandedSections(newExpanded);
  };

  const lastUpdated = "December 3, 2024";

  const sections = [
    {
      id: "what-are-cookies",
      title: "What Are Cookies?",
      icon: Cookie,
      content: `Cookies are small text files that are placed on your device when you visit our website. They help us provide you with a better experience by remembering your preferences and analyzing how you use our site.`
    },
    {
      id: "types-of-cookies",
      title: "Types of Cookies We Use",
      icon: Database,
      content: `We use several types of cookies:
      
• Essential Cookies: Required for basic website functionality
• Performance Cookies: Help us understand how visitors interact with our website
• Functionality Cookies: Remember your preferences and settings
• Marketing Cookies: Used to deliver relevant advertisements`
    },
    {
      id: "essential-cookies",
      title: "Essential Cookies",
      icon: Lock,
      content: `These cookies are necessary for the website to function properly. They enable basic functions like page navigation, access to secure areas, and form submissions. The website cannot function properly without these cookies.`
    },
    {
      id: "performance-cookies",
      title: "Performance Cookies",
      icon: Eye,
      content: `These cookies help us understand how visitors interact with our website by collecting and reporting information anonymously. This helps us improve our website's performance and user experience.`
    },
    {
      id: "functionality-cookies",
      title: "Functionality Cookies",
      icon: UserCheck,
      content: `These cookies allow the website to remember choices you make and provide enhanced, more personal features. They may be set by us or by third-party providers whose services we have added to our pages.`
    },
    {
      id: "marketing-cookies",
      title: "Marketing Cookies",
      icon: Globe,
      content: `These cookies are used to track visitors across websites. The intention is to display ads that are relevant and engaging for individual users and thereby more valuable for publishers and third-party advertisers.`
    },
    {
      id: "third-party-cookies",
      title: "Third-Party Cookies",
      icon: Mail,
      content: `We may use third-party services that set their own cookies. These services include:
      
• Google Analytics: For website analytics
• Google Ads: For advertising purposes
• Social media platforms: For social sharing features
• Payment processors: For secure transactions`
    },
    {
      id: "cookie-management",
      title: "Managing Your Cookie Preferences",
      icon: ShieldCheck,
      content: `You can control and manage cookies in several ways:

• Browser Settings: Most browsers allow you to manage cookies through their settings
• Cookie Consent: Use our cookie consent banner to manage preferences
• Third-Party Opt-Out: Visit third-party websites to opt out of their cookies
• Contact Us: Reach out to us for assistance with cookie management`
    },
    {
      id: "cookie-retention",
      title: "Cookie Retention Periods",
      icon: Calendar,
      content: `Different cookies have different retention periods:

• Session Cookies: Deleted when you close your browser
• Persistent Cookies: Remain on your device for a set period (usually 1-2 years)
• Analytics Cookies: Typically retained for 26 months
• Marketing Cookies: Usually retained for 13 months`
    }
  ];

  return (
    <Layout>
      <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
        {/* Hero Section */}
        <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white py-16">
          <div className="container mx-auto px-4">
            <div className="flex items-center mb-6">
              <Link to="/" className="flex items-center text-white/80 hover:text-white transition-colors">
                <ArrowLeft className="w-5 h-5 mr-2" />
                Back to Home
              </Link>
            </div>
            <div className="max-w-4xl mx-auto text-center">
              <div className="flex justify-center mb-6">
                <Cookie className="w-16 h-16 text-yellow-300" />
              </div>
              <h1 className="text-4xl md:text-5xl font-bold mb-4">
                Cookie Policy
              </h1>
              <p className="text-xl text-blue-100 mb-6">
                Learn how we use cookies to enhance your experience on Buzz2Remote
              </p>
              <div className="flex items-center justify-center text-sm text-blue-200">
                <Calendar className="w-4 h-4 mr-2" />
                Last updated: {lastUpdated}
              </div>
            </div>
          </div>
        </div>

        {/* Content Section */}
        <div className="container mx-auto px-4 py-12">
          <div className="max-w-4xl mx-auto">
            {/* Introduction */}
            <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
              <h2 className="text-2xl font-bold text-gray-800 mb-4">
                Understanding Our Cookie Policy
              </h2>
              <p className="text-gray-600 leading-relaxed">
                At Buzz2Remote, we believe in transparency about how we collect and use information. 
                This Cookie Policy explains how we use cookies and similar technologies to provide, 
                protect, and improve our services. By using our website, you agree to our use of cookies 
                as described in this policy.
              </p>
            </div>

            {/* Sections */}
            <div className="space-y-6">
              {sections.map((section) => {
                const IconComponent = section.icon;
                const isExpanded = expandedSections.has(section.id);
                
                return (
                  <div key={section.id} className="bg-white rounded-xl shadow-lg overflow-hidden">
                    <button
                      onClick={() => toggleSection(section.id)}
                      className="w-full px-8 py-6 flex items-center justify-between text-left hover:bg-gray-50 transition-colors"
                    >
                      <div className="flex items-center">
                        <IconComponent className="w-6 h-6 text-blue-600 mr-4" />
                        <h3 className="text-xl font-semibold text-gray-800">
                          {section.title}
                        </h3>
                      </div>
                      {isExpanded ? (
                        <ChevronUp className="w-5 h-5 text-gray-500" />
                      ) : (
                        <ChevronDown className="w-5 h-5 text-gray-500" />
                      )}
                    </button>
                    
                    {isExpanded && (
                      <div className="px-8 pb-6">
                        <div className="border-t border-gray-200 pt-6">
                          <div className="text-gray-600 leading-relaxed whitespace-pre-line">
                            {section.content}
                          </div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>

            {/* Contact Section */}
            <div className="bg-gradient-to-r from-blue-50 to-purple-50 rounded-xl p-8 mt-12">
              <div className="text-center">
                <h3 className="text-2xl font-bold text-gray-800 mb-4">
                  Questions About Our Cookie Policy?
                </h3>
                <p className="text-gray-600 mb-6">
                  If you have any questions about our use of cookies or this Cookie Policy, 
                  please don't hesitate to contact us.
                </p>
                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                  <Link
                    to="/contact"
                    className="inline-flex items-center px-6 py-3 bg-blue-600 text-white font-medium rounded-lg hover:bg-blue-700 transition-colors"
                  >
                    <Mail className="w-5 h-5 mr-2" />
                    Contact Us
                  </Link>
                  <Link
                    to="/privacy-policy"
                    className="inline-flex items-center px-6 py-3 bg-gray-600 text-white font-medium rounded-lg hover:bg-gray-700 transition-colors"
                  >
                    <ShieldCheck className="w-5 h-5 mr-2" />
                    Privacy Policy
                  </Link>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CookiePolicy; 