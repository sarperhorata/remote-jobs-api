import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, FileText, ArrowLeft, ChevronDown, ChevronRight, Calendar, Mail, Shield, AlertTriangle } from '../components/icons/EmojiIcons';
import Layout from '../components/Layout';

const TermsConditions: React.FC = () => {
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
      id: "acceptance",
      title: "1. Acceptance of Terms",
      content: (
        <div className="space-y-4">
          <p>
            By accessing and using Buzz2Remote ("the Platform," "our Service," "we," "us," or "our"), you accept and agree to be bound by these Terms and Conditions ("Terms"). If you do not agree to these Terms, please do not use our Platform.
          </p>
          <p>
            These Terms constitute a legally binding agreement between you ("User," "you," or "your") and Buzz2Remote Ltd., a company incorporated under the laws of the United Kingdom.
          </p>
          <p>
            We reserve the right to modify these Terms at any time. Changes will be effective immediately upon posting. Your continued use of the Platform after any changes indicates your acceptance of the modified Terms.
          </p>
        </div>
      )
    },
    {
      id: "definitions",
      title: "2. Definitions and Interpretation",
      content: (
        <div className="space-y-4">
          <p>For the purposes of these Terms, the following definitions apply:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>"Platform"</strong> means the Buzz2Remote website, mobile applications, and all related services</li>
            <li><strong>"User"</strong> means any individual or entity using our Platform</li>
            <li><strong>"Job Seeker"</strong> means a User seeking employment opportunities</li>
            <li><strong>"Employer"</strong> means a User posting job opportunities</li>
            <li><strong>"Content"</strong> means all text, data, information, software, graphics, or other materials</li>
            <li><strong>"Personal Data"</strong> means any information relating to an identified or identifiable individual</li>
            <li><strong>"Services"</strong> means all features, functionalities, and services provided through the Platform</li>
          </ul>
        </div>
      )
    },
    {
      id: "eligibility",
      title: "3. User Eligibility and Account Registration",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">3.1 Eligibility Requirements</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>You must be at least 16 years old to use our Platform</li>
            <li>You must have the legal capacity to enter into binding contracts</li>
            <li>Your use must comply with all applicable laws and regulations</li>
            <li>You must not be prohibited from using our Services under any applicable law</li>
          </ul>
          
          <h4 className="font-semibold">3.2 Account Registration</h4>
          <p>
            To access certain features, you must create an account by providing accurate, complete, and current information. You are responsible for:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Maintaining the confidentiality of your account credentials</li>
            <li>All activities that occur under your account</li>
            <li>Notifying us immediately of any unauthorized use</li>
            <li>Keeping your account information up to date</li>
          </ul>

          <h4 className="font-semibold">3.3 Account Verification</h4>
          <p>
            We may require identity verification for certain account features. You agree to provide truthful and accurate verification documents when requested.
          </p>
        </div>
      )
    },
    {
      id: "services",
      title: "4. Description of Services",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">4.1 Platform Services</h4>
          <p>Buzz2Remote provides an online platform that connects job seekers with remote employment opportunities. Our services include:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Job listing aggregation and search functionality</li>
            <li>AI-powered job matching algorithms</li>
            <li>Profile creation and management tools</li>
            <li>Application tracking and management</li>
            <li>Communication tools between employers and job seekers</li>
            <li>Career resources and educational content</li>
          </ul>

          <h4 className="font-semibold">4.2 Free and Paid Services</h4>
          <p>
            We offer both free and premium subscription services. Free services may have limitations on usage, features, or functionality. Premium services require payment and provide enhanced features as described in our pricing plans.
          </p>

          <h4 className="font-semibold">4.3 Service Availability</h4>
          <p>
            While we strive to maintain continuous service availability, we do not guarantee uninterrupted access. We may temporarily suspend services for maintenance, updates, or technical issues.
          </p>
        </div>
      )
    },
    {
      id: "user-obligations",
      title: "5. User Obligations and Prohibited Conduct",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">5.1 General Obligations</h4>
          <p>You agree to:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Use the Platform only for lawful purposes</li>
            <li>Provide accurate and truthful information</li>
            <li>Respect the intellectual property rights of others</li>
            <li>Maintain the security of your account</li>
            <li>Comply with all applicable laws and regulations</li>
          </ul>

          <h4 className="font-semibold">5.2 Prohibited Activities</h4>
          <p>You must not:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Post false, misleading, or fraudulent job listings or profiles</li>
            <li>Engage in discriminatory practices in hiring or job seeking</li>
            <li>Spam, harass, or send unsolicited communications to other users</li>
            <li>Attempt to circumvent security measures or access restrictions</li>
            <li>Use automated tools to scrape or collect data from the Platform</li>
            <li>Post content that is illegal, offensive, or infringes on rights</li>
            <li>Impersonate another person or entity</li>
            <li>Distribute malware, viruses, or other harmful code</li>
          </ul>

          <h4 className="font-semibold">5.3 Content Standards</h4>
          <p>All content you submit must:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Be accurate and not misleading</li>
            <li>Comply with applicable employment laws</li>
            <li>Not contain offensive, discriminatory, or inappropriate material</li>
            <li>Respect intellectual property rights</li>
            <li>Not violate any third-party rights</li>
          </ul>
        </div>
      )
    },
    {
      id: "payment-terms",
      title: "6. Payment Terms and Billing",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">6.1 Subscription Fees</h4>
          <p>
            Premium services require payment of subscription fees as outlined in our pricing plans. All fees are non-refundable except as specifically stated in our refund policy.
          </p>

          <h4 className="font-semibold">6.2 Billing and Payment</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Fees are billed in advance on a monthly or annual basis</li>
            <li>Payment is due immediately upon subscription activation</li>
            <li>We accept major credit cards and other payment methods as specified</li>
            <li>All payments are processed securely through third-party payment processors</li>
          </ul>

          <h4 className="font-semibold">6.3 Price Changes</h4>
          <p>
            We may change our pricing at any time. Price changes for existing subscriptions will take effect at the next billing cycle, with at least 30 days' advance notice.
          </p>

          <h4 className="font-semibold">6.4 Refund Policy</h4>
          <p>
            We offer a 14-day money-back guarantee for new subscribers. Refund requests must be submitted within 14 days of initial payment. Refunds are not available for renewals or partial billing periods.
          </p>
        </div>
      )
    },
    {
      id: "intellectual-property",
      title: "7. Intellectual Property Rights",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">7.1 Our Intellectual Property</h4>
          <p>
            All content, features, and functionality of the Platform, including but not limited to text, graphics, logos, icons, images, audio clips, video clips, data compilations, and software, are the exclusive property of Buzz2Remote or its licensors and are protected by copyright, trademark, and other intellectual property laws.
          </p>

          <h4 className="font-semibold">7.2 User-Generated Content</h4>
          <p>
            You retain ownership of content you submit to the Platform. However, by submitting content, you grant us a worldwide, non-exclusive, royalty-free license to use, reproduce, modify, adapt, publish, and distribute such content for the purposes of operating and improving our Platform.
          </p>

          <h4 className="font-semibold">7.3 Trademark Rights</h4>
          <p>
            "Buzz2Remote" and related logos are trademarks of Buzz2Remote Ltd. You may not use our trademarks without our prior written consent.
          </p>

          <h4 className="font-semibold">7.4 Copyright Infringement</h4>
          <p>
            We respect intellectual property rights and expect users to do the same. If you believe your copyright has been infringed, please contact us with detailed information about the alleged infringement.
          </p>
        </div>
      )
    },
    {
      id: "privacy-data",
      title: "8. Privacy and Data Protection",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">8.1 Privacy Policy</h4>
          <p>
            Our collection, use, and protection of your personal data are governed by our Privacy Policy, which is incorporated into these Terms by reference. Please review our Privacy Policy to understand our practices.
          </p>

          <h4 className="font-semibold">8.2 GDPR Compliance</h4>
          <p>
            We comply with the General Data Protection Regulation (GDPR) and other applicable data protection laws. You have the right to:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Access your personal data</li>
            <li>Rectify inaccurate data</li>
            <li>Erase your data under certain circumstances</li>
            <li>Restrict processing of your data</li>
            <li>Data portability</li>
            <li>Object to processing</li>
            <li>Withdraw consent where applicable</li>
          </ul>

          <h4 className="font-semibold">8.3 Data Retention</h4>
          <p>
            We retain personal data only as long as necessary for the purposes outlined in our Privacy Policy or as required by law. Upon account deletion, we will delete your personal data within 30 days, except where retention is required for legal compliance.
          </p>
        </div>
      )
    },
    {
      id: "disclaimers",
      title: "9. Disclaimers and Limitations of Liability",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">9.1 Service Disclaimer</h4>
          <p>
            THE PLATFORM IS PROVIDED "AS IS" AND "AS AVAILABLE" WITHOUT ANY WARRANTIES OF ANY KIND, WHETHER EXPRESS OR IMPLIED. WE DISCLAIM ALL WARRANTIES, INCLUDING BUT NOT LIMITED TO MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT.
          </p>

          <h4 className="font-semibold">9.2 Employment Disclaimer</h4>
          <p>
            We do not guarantee employment or hiring success. Job listings are provided by third parties, and we do not verify the accuracy or legitimacy of all postings. Users are responsible for conducting their own due diligence.
          </p>

          <h4 className="font-semibold">9.3 Limitation of Liability</h4>
          <p>
            TO THE MAXIMUM EXTENT PERMITTED BY LAW, BUZZ2REMOTE SHALL NOT BE LIABLE FOR ANY INDIRECT, INCIDENTAL, SPECIAL, CONSEQUENTIAL, OR PUNITIVE DAMAGES, OR ANY LOSS OF PROFITS OR REVENUES, WHETHER INCURRED DIRECTLY OR INDIRECTLY.
          </p>

          <h4 className="font-semibold">9.4 Indemnification</h4>
          <p>
            You agree to indemnify and hold harmless Buzz2Remote from any claims, damages, losses, costs, and expenses arising from your use of the Platform or violation of these Terms.
          </p>
        </div>
      )
    },
    {
      id: "termination",
      title: "10. Termination",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">10.1 Termination by You</h4>
          <p>
            You may terminate your account at any time by following the account deletion process in your settings. Termination does not relieve you of any obligations incurred prior to termination.
          </p>

          <h4 className="font-semibold">10.2 Termination by Us</h4>
          <p>
            We may suspend or terminate your account immediately, without prior notice, for any reason, including but not limited to:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Violation of these Terms</li>
            <li>Suspected fraudulent or illegal activity</li>
            <li>Non-payment of fees</li>
            <li>Extended periods of inactivity</li>
            <li>At our sole discretion</li>
          </ul>

          <h4 className="font-semibold">10.3 Effect of Termination</h4>
          <p>
            Upon termination, your right to use the Platform will cease immediately. We may delete your account data, although we may retain certain information as required by law or for legitimate business purposes.
          </p>
        </div>
      )
    },
    {
      id: "general-provisions",
      title: "11. General Provisions",
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">11.1 Governing Law</h4>
          <p>
            These Terms are governed by and construed in accordance with the laws of England and Wales, without regard to conflict of law principles.
          </p>

          <h4 className="font-semibold">11.2 Dispute Resolution</h4>
          <p>
            Any disputes arising from these Terms will be subject to the exclusive jurisdiction of the courts of England and Wales. We encourage users to contact us first to resolve disputes amicably.
          </p>

          <h4 className="font-semibold">11.3 Severability</h4>
          <p>
            If any provision of these Terms is found to be unenforceable, the remaining provisions will remain in full force and effect.
          </p>

          <h4 className="font-semibold">11.4 Entire Agreement</h4>
          <p>
            These Terms, together with our Privacy Policy, constitute the entire agreement between you and Buzz2Remote regarding the use of the Platform.
          </p>

          <h4 className="font-semibold">11.5 Assignment</h4>
          <p>
            We may assign these Terms without your consent. You may not assign your rights or obligations under these Terms without our written consent.
          </p>

          <h4 className="font-semibold">11.6 Force Majeure</h4>
          <p>
            We will not be liable for any delay or failure to perform due to causes beyond our reasonable control, including natural disasters, war, terrorism, strikes, or government regulations.
          </p>
        </div>
      )
    }
  ];

  return (
    <Layout>
      {/* Header */}
      <div className="bg-white shadow-sm rounded-lg p-6 mb-8">
        <div className="flex items-center justify-between mb-6">
          <Link to="/" className="flex items-center space-x-3 text-gray-700 hover:text-orange-600 transition-colors">
            <Briefcase className="w-8 h-8 text-orange-600" />
            <span className="text-2xl font-bold">Buzz2Remote</span>
          </Link>
          <button 
            onClick={() => window.history.back()} 
            className="text-sm text-orange-600 hover:text-orange-700 flex items-center transition-colors"
          >
            <ArrowLeft className="w-4 h-4 mr-1" />
            Go Back
          </button>
        </div>

        <div className="text-center">
          <div className="flex items-center justify-center mb-4">
            <FileText className="w-16 h-16 text-orange-500" />
          </div>
          <h1 className="text-4xl font-bold text-gray-900 mb-2">Terms & Conditions</h1>
          <div className="flex items-center justify-center text-gray-600 space-x-4">
            <div className="flex items-center">
              <Calendar className="w-4 h-4 mr-2" />
              <span>Last updated: {lastUpdated}</span>
            </div>
            <div className="flex items-center">
              <Shield className="w-4 h-4 mr-2" />
              <span>GDPR Compliant</span>
            </div>
          </div>
        </div>
      </div>

      {/* Important Notice */}
      <div className="bg-orange-50 border border-orange-200 rounded-lg p-6 mb-8">
        <div className="flex items-start">
          <AlertTriangle className="w-6 h-6 text-orange-600 mr-3 mt-0.5" />
          <div>
            <h3 className="font-semibold text-orange-900 mb-2">Important Notice</h3>
            <p className="text-orange-800 text-sm">
              Please read these Terms and Conditions carefully before using our Platform. By accessing or using Buzz2Remote, you agree to be bound by these terms. These terms include important information about your rights and obligations, as well as limitations and exclusions that may apply to you.
            </p>
          </div>
        </div>
      </div>

      {/* Table of Contents */}
      <div className="bg-white shadow-sm rounded-lg p-6 mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Table of Contents</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
          {sections.map((section) => (
            <button
              key={section.id}
              onClick={() => toggleSection(section.id)}
              className="text-left text-orange-600 hover:text-orange-700 text-sm transition-colors"
            >
              {section.title}
            </button>
          ))}
        </div>
      </div>

      {/* Terms Content */}
      <div className="bg-white shadow-sm rounded-lg overflow-hidden">
        {sections.map((section, index) => (
          <div key={section.id} className={index > 0 ? "border-t border-gray-200" : ""}>
            <button
              onClick={() => toggleSection(section.id)}
              className="w-full px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-inset hover:bg-gray-50 transition-colors"
            >
              <div className="flex items-center justify-between">
                <h3 className="text-lg font-semibold text-gray-900">{section.title}</h3>
                {expandedSections.has(section.id) ? (
                  <ChevronDown className="w-5 h-5 text-gray-500" />
                ) : (
                  <ChevronRight className="w-5 h-5 text-gray-500" />
                )}
              </div>
            </button>
            
            {expandedSections.has(section.id) && (
              <div className="px-6 pb-6 text-gray-700 prose prose-orange max-w-none">
                {section.content}
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Contact Information */}
      <div className="bg-white shadow-sm rounded-lg p-6 mt-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Questions About These Terms?</h2>
        <p className="text-gray-600 mb-4">
          If you have any questions about these Terms and Conditions, please don't hesitate to contact us.
        </p>
        <div className="flex flex-col sm:flex-row gap-4">
          <a
            href="mailto:legal@buzz2remote.com"
            className="inline-flex items-center justify-center px-4 py-2 border border-orange-300 rounded-md text-orange-700 bg-orange-50 hover:bg-orange-100 transition-colors"
          >
            <Mail className="w-4 h-4 mr-2" />
            legal@buzz2remote.com
          </a>
          <Link
            to="/help"
            className="inline-flex items-center justify-center px-4 py-2 border border-gray-300 rounded-md text-gray-700 bg-gray-50 hover:bg-gray-100 transition-colors"
          >
            Visit Help Center
          </Link>
        </div>
      </div>

      {/* Footer Note */}
      <div className="text-center mt-8 text-sm text-gray-500">
        <p>
          These Terms and Conditions are effective as of {lastUpdated} and apply to all users of the Buzz2Remote platform.
        </p>
      </div>
    </Layout>
  );
};

export default TermsConditions; 