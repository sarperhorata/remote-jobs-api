import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, ShieldCheck, ArrowLeft, ChevronDown, ChevronRight, Calendar, Mail, Globe, Eye, Lock, Database, UserCheck } from '../components/icons/EmojiIcons';
import Layout from '../components/Layout';

const PrivacyPolicy: React.FC = () => {
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
      id: "overview",
      title: "1. Overview and Data Controller",
      icon: <Globe className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <p>
            This Privacy Policy describes how Buzz2Remote Ltd. ("we," "us," or "our") collects, uses, processes, and protects your personal information when you use our platform and services. We are committed to protecting your privacy and being transparent about our data practices.
          </p>
          
          <h4 className="font-semibold">Data Controller Information:</h4>
          <div className="bg-gray-50 p-4 rounded-lg">
            <p><strong>Company:</strong> Buzz2Remote Ltd.</p>
            <p><strong>Address:</strong> 123 Remote Work Street, London, UK EC1A 1BB</p>
            <p><strong>Email:</strong> privacy@buzz2remote.com</p>
            <p><strong>Data Protection Officer:</strong> dpo@buzz2remote.com</p>
          </div>

          <p>
            This policy applies to all users of our website, mobile applications, and related services (collectively, "the Platform"). By using our Platform, you agree to the collection and use of information in accordance with this policy.
          </p>

          <h4 className="font-semibold">Legal Basis for Processing:</h4>
          <p>
            We process personal data under various legal bases including consent, contract performance, legitimate interests, and legal obligations as detailed throughout this policy.
          </p>
        </div>
      )
    },
    {
      id: "information-collection",
      title: "2. Information We Collect",
      icon: <Database className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">2.1 Information You Provide Directly</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>Account Information:</strong> Name, email address, password, profile photo</li>
            <li><strong>Profile Information:</strong> Professional background, skills, experience, education, career preferences</li>
            <li><strong>Application Information:</strong> Resumes, cover letters, portfolio items, work samples</li>
            <li><strong>Communication Data:</strong> Messages with employers, support inquiries, feedback</li>
            <li><strong>Payment Information:</strong> Billing details, payment method information (processed by third-party payment processors)</li>
            <li><strong>Identity Verification:</strong> Government-issued ID, proof of address when required</li>
          </ul>

          <h4 className="font-semibold">2.2 Information We Collect Automatically</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>Device Information:</strong> IP address, browser type, operating system, device identifiers</li>
            <li><strong>Usage Data:</strong> Pages visited, time spent, features used, search queries, click patterns</li>
            <li><strong>Location Data:</strong> General geographic location based on IP address</li>
            <li><strong>Performance Data:</strong> Loading times, errors, crash reports</li>
            <li><strong>Referral Information:</strong> How you arrived at our platform</li>
          </ul>

          <h4 className="font-semibold">2.3 Information from Third Parties</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>Social Media:</strong> Profile information when you sign up using social media accounts</li>
            <li><strong>Job Boards:</strong> Publicly available job postings and company information</li>
            <li><strong>Verification Services:</strong> Identity and background check information when required</li>
            <li><strong>Analytics Providers:</strong> Aggregated usage statistics and insights</li>
          </ul>

          <h4 className="font-semibold">2.4 Cookies and Tracking Technologies</h4>
          <p>
            We use cookies, web beacons, and similar technologies to enhance your experience, analyze usage patterns, and provide personalized content. You can control cookie settings through your browser preferences.
          </p>
        </div>
      )
    },
    {
      id: "how-we-use",
      title: "3. How We Use Your Information",
      icon: <UserCheck className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">3.1 Service Provision</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Create and manage your account</li>
            <li>Provide job matching and recommendation services</li>
            <li>Process job applications and facilitate communications</li>
            <li>Deliver personalized content and user experience</li>
            <li>Process payments and manage subscriptions</li>
          </ul>

          <h4 className="font-semibold">3.2 Communication</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Send service-related notifications and updates</li>
            <li>Respond to your inquiries and provide customer support</li>
            <li>Send marketing communications (with your consent)</li>
            <li>Notify you about platform changes and new features</li>
          </ul>

          <h4 className="font-semibold">3.3 Platform Improvement</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Analyze usage patterns to improve our services</li>
            <li>Develop new features and functionalities</li>
            <li>Conduct research and analytics</li>
            <li>Perform A/B testing and optimization</li>
          </ul>

          <h4 className="font-semibold">3.4 Legal and Security</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Comply with legal obligations and regulations</li>
            <li>Prevent fraud, abuse, and security threats</li>
            <li>Enforce our terms of service</li>
            <li>Protect our rights and interests</li>
          </ul>

          <h4 className="font-semibold">3.5 Legal Basis for Processing</h4>
          <div className="bg-blue-50 p-4 rounded-lg">
            <ul className="list-disc list-inside space-y-2">
              <li><strong>Consent:</strong> Marketing communications, non-essential cookies</li>
              <li><strong>Contract Performance:</strong> Account management, service delivery</li>
              <li><strong>Legitimate Interests:</strong> Platform improvement, security, analytics</li>
              <li><strong>Legal Obligation:</strong> Compliance, tax reporting, identity verification</li>
            </ul>
          </div>
        </div>
      )
    },
    {
      id: "sharing-disclosure",
      title: "4. Information Sharing and Disclosure",
      icon: <Eye className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">4.1 With Your Consent</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Profile information shared with potential employers when you apply for jobs</li>
            <li>Information shared with third-party integrations you authorize</li>
            <li>Testimonials and success stories (with explicit permission)</li>
          </ul>

          <h4 className="font-semibold">4.2 Service Providers</h4>
          <p>We share information with trusted third-party service providers who assist us in:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Payment processing (Stripe, PayPal)</li>
            <li>Email delivery and communication services</li>
            <li>Cloud hosting and data storage</li>
            <li>Analytics and performance monitoring</li>
            <li>Customer support and help desk services</li>
            <li>Identity verification and background checks</li>
          </ul>
          
          <h4 className="font-semibold">4.3 Business Transfers</h4>
          <p>
            In the event of a merger, acquisition, or sale of assets, your information may be transferred to the acquiring entity. We will notify you via email and/or prominent notice on our platform before your information is transferred.
          </p>

          <h4 className="font-semibold">4.4 Legal Requirements</h4>
          <p>We may disclose your information when required by law or to:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Comply with legal processes, court orders, or government requests</li>
            <li>Enforce our terms of service and policies</li>
            <li>Protect our rights, property, or safety</li>
            <li>Investigate potential violations or fraud</li>
            <li>Protect the safety and rights of our users</li>
          </ul>

          <h4 className="font-semibold">4.5 Aggregated and De-identified Data</h4>
          <p>
            We may share aggregated, de-identified information that cannot reasonably be used to identify you for research, analytics, marketing, or other business purposes.
          </p>
        </div>
      )
    },
    {
      id: "data-security",
      title: "5. Data Security and Protection",
      icon: <Lock className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">5.1 Security Measures</h4>
          <p>We implement comprehensive security measures to protect your information:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>Encryption:</strong> Data encrypted in transit (TLS 1.3) and at rest (AES-256)</li>
            <li><strong>Access Controls:</strong> Role-based access with multi-factor authentication</li>
            <li><strong>Regular Audits:</strong> Security assessments and penetration testing</li>
            <li><strong>Employee Training:</strong> Regular security and privacy training for all staff</li>
            <li><strong>Incident Response:</strong> Procedures for detecting and responding to security breaches</li>
            <li><strong>Secure Infrastructure:</strong> SOC 2 compliant hosting with regular security updates</li>
          </ul>

          <h4 className="font-semibold">5.2 Data Breach Notification</h4>
          <p>
            In the unlikely event of a data breach affecting your personal information, we will:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Notify relevant authorities within 72 hours (as required by GDPR)</li>
            <li>Inform affected users without undue delay</li>
            <li>Provide clear information about the breach and our response</li>
            <li>Take immediate steps to mitigate any potential harm</li>
          </ul>

          <h4 className="font-semibold">5.3 Your Security Responsibilities</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Use strong, unique passwords for your account</li>
            <li>Enable two-factor authentication when available</li>
            <li>Keep your contact information up to date</li>
            <li>Report suspicious activity immediately</li>
            <li>Log out of shared devices and public computers</li>
          </ul>
        </div>
      )
    },
    {
      id: "your-rights",
      title: "6. Your Privacy Rights",
      icon: <ShieldCheck className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">6.1 GDPR Rights (EU Residents)</h4>
          <p>Under the General Data Protection Regulation, you have the following rights:</p>
          <div className="bg-green-50 p-4 rounded-lg space-y-3">
            <div>
              <strong>Right to Access:</strong> Request copies of your personal data
            </div>
            <div>
              <strong>Right to Rectification:</strong> Request correction of inaccurate or incomplete data
            </div>
            <div>
              <strong>Right to Erasure:</strong> Request deletion of your personal data under certain circumstances
            </div>
            <div>
              <strong>Right to Restrict Processing:</strong> Limit how we use your data
            </div>
            <div>
              <strong>Right to Data Portability:</strong> Receive your data in a structured, machine-readable format
            </div>
            <div>
              <strong>Right to Object:</strong> Object to processing based on legitimate interests
            </div>
            <div>
              <strong>Right to Withdraw Consent:</strong> Withdraw consent for processing at any time
            </div>
            <div>
              <strong>Right to Lodge a Complaint:</strong> File a complaint with your local data protection authority
            </div>
          </div>

          <h4 className="font-semibold">6.2 CCPA Rights (California Residents)</h4>
          <p>Under the California Consumer Privacy Act, you have the right to:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Know what personal information we collect and how it's used</li>
            <li>Delete personal information we have collected</li>
            <li>Opt-out of the sale of personal information (we do not sell personal information)</li>
            <li>Non-discrimination for exercising your privacy rights</li>
          </ul>

          <h4 className="font-semibold">6.3 How to Exercise Your Rights</h4>
          <p>To exercise any of your privacy rights:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Email us at privacy@buzz2remote.com</li>
            <li>Use the privacy settings in your account dashboard</li>
            <li>Contact our Data Protection Officer at dpo@buzz2remote.com</li>
            <li>Submit a request through our online privacy form</li>
          </ul>
          
          <p>
            We will respond to your request within 30 days and may require identity verification to protect your information.
          </p>
        </div>
      )
    },
    {
      id: "data-retention",
      title: "7. Data Retention and Deletion",
      icon: <Database className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">7.1 Retention Periods</h4>
          <p>We retain personal information for the following periods:</p>
          <div className="bg-gray-50 p-4 rounded-lg space-y-3">
            <div>
              <strong>Account Data:</strong> Until account deletion + 30 days for cleanup
            </div>
            <div>
              <strong>Application Data:</strong> 3 years after last application activity
            </div>
            <div>
              <strong>Communication Records:</strong> 3 years for support and quality purposes
            </div>
            <div>
              <strong>Payment Information:</strong> 7 years for tax and accounting requirements
            </div>
            <div>
              <strong>Marketing Data:</strong> Until consent withdrawal + 30 days
            </div>
            <div>
              <strong>Analytics Data:</strong> 26 months in aggregated, anonymized form
            </div>
            <div>
              <strong>Legal/Compliance Data:</strong> As required by applicable laws (typically 6-10 years)
            </div>
          </div>

          <h4 className="font-semibold">7.2 Account Deletion</h4>
          <p>When you delete your account:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Personal information is deleted within 30 days</li>
            <li>Some information may be retained for legal compliance</li>
            <li>Aggregated, anonymized data may be retained for analytics</li>
            <li>Backup copies are permanently deleted within 90 days</li>
          </ul>

          <h4 className="font-semibold">7.3 Automated Deletion</h4>
          <p>
            We have automated systems in place to ensure data is deleted according to our retention schedules. You will receive notifications before any automatic deletion of your account due to inactivity.
          </p>
        </div>
      )
    },
    {
      id: "international-transfers",
      title: "8. International Data Transfers",
      icon: <Globe className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">8.1 Data Transfer Mechanisms</h4>
          <p>
            Your information may be transferred to and processed in countries other than your country of residence. We ensure appropriate safeguards are in place:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Standard Contractual Clauses (SCCs) approved by the European Commission</li>
            <li>Adequacy decisions for countries with adequate protection levels</li>
            <li>Binding Corporate Rules for transfers within our corporate group</li>
            <li>Certification schemes and codes of conduct where applicable</li>
          </ul>

          <h4 className="font-semibold">8.2 Third Country Transfers</h4>
          <p>We may transfer data to the following regions with appropriate safeguards:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>United States:</strong> Under EU-US Data Privacy Framework or SCCs</li>
            <li><strong>Canada:</strong> Under adequacy decision</li>
            <li><strong>Other countries:</strong> Only with appropriate safeguards in place</li>
          </ul>

          <h4 className="font-semibold">8.3 Your Rights Regarding Transfers</h4>
          <p>
            You have the right to obtain information about international transfers and request copies of the safeguards we have in place.
          </p>
        </div>
      )
    },
    {
      id: "cookies-tracking",
      title: "9. Cookies and Tracking Technologies",
      icon: <Eye className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">9.1 Types of Cookies We Use</h4>
          <div className="space-y-3">
            <div className="bg-blue-50 p-3 rounded">
              <strong>Essential Cookies:</strong> Required for basic platform functionality (login, security, preferences)
            </div>
            <div className="bg-green-50 p-3 rounded">
              <strong>Performance Cookies:</strong> Help us understand how you use our platform (with consent)
            </div>
            <div className="bg-yellow-50 p-3 rounded">
              <strong>Functional Cookies:</strong> Remember your preferences and settings (with consent)
            </div>
            <div className="bg-purple-50 p-3 rounded">
              <strong>Marketing Cookies:</strong> Used for personalized advertising (with consent)
            </div>
          </div>

          <h4 className="font-semibold">9.2 Third-Party Cookies</h4>
          <p>We use trusted third-party services that may set cookies:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>Google Analytics:</strong> Website usage analytics</li>
            <li><strong>Hotjar:</strong> User experience analytics</li>
            <li><strong>Intercom:</strong> Customer support chat</li>
            <li><strong>Stripe:</strong> Payment processing</li>
          </ul>

          <h4 className="font-semibold">9.3 Managing Cookie Preferences</h4>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Use our cookie consent banner to manage preferences</li>
            <li>Adjust settings in your browser</li>
            <li>Visit our Cookie Preference Center in your account</li>
            <li>Use browser plugins for additional control</li>
          </ul>

          <p className="text-sm text-gray-600">
            Note: Disabling essential cookies may affect platform functionality.
          </p>
        </div>
      )
    },
    {
      id: "children-privacy",
      title: "10. Children's Privacy",
      icon: <UserCheck className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">10.1 Age Restrictions</h4>
          <p>
            Our platform is intended for users aged 16 and above. We do not knowingly collect personal information from children under 16 years of age.
          </p>

          <h4 className="font-semibold">10.2 Parental Rights</h4>
          <p>If you believe we have collected information from a child under 16:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Contact us immediately at privacy@buzz2remote.com</li>
            <li>We will investigate and delete the information if confirmed</li>
            <li>Parents/guardians have the right to review and request deletion of their child's information</li>
          </ul>

          <h4 className="font-semibold">10.3 Age Verification</h4>
          <p>
            We may implement age verification measures to ensure compliance with this policy and applicable laws.
          </p>
        </div>
      )
    },
    {
      id: "policy-updates",
      title: "11. Policy Updates and Contact",
      icon: <Mail className="w-5 h-5" />,
      content: (
        <div className="space-y-4">
          <h4 className="font-semibold">11.1 Policy Updates</h4>
          <p>
            We may update this Privacy Policy periodically to reflect changes in our practices, technology, legal requirements, or other factors. We will:
          </p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Notify you of material changes via email or platform notification</li>
            <li>Update the "Last Updated" date at the top of this policy</li>
            <li>Provide a summary of significant changes</li>
            <li>Give you the opportunity to review changes before they take effect</li>
          </ul>

          <h4 className="font-semibold">11.2 Contact Information</h4>
          <div className="bg-gray-50 p-4 rounded-lg space-y-2">
            <p><strong>General Privacy Inquiries:</strong> privacy@buzz2remote.com</p>
            <p><strong>Data Protection Officer:</strong> dpo@buzz2remote.com</p>
            <p><strong>Physical Address:</strong> 123 Remote Work Street, London, UK EC1A 1BB</p>
            <p><strong>Phone:</strong> +44 (0) 20 1234 5678</p>
          </div>

          <h4 className="font-semibold">11.3 Supervisory Authority</h4>
          <p>
            If you are in the EU/EEA and have concerns about our data practices, you can contact the Information Commissioner's Office (ICO) or your local data protection authority.
          </p>
        </div>
      )
    }
  ];

  return (
    <Layout>
      <div className="max-w-4xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white shadow-sm rounded-lg p-6 mb-8">
          <div className="flex items-center justify-between mb-4">
            <Link to="/" className="flex items-center space-x-3 text-gray-700 hover:text-green-600 transition-colors">
              <Briefcase className="w-8 h-8 text-green-600" />
              <span className="text-2xl font-bold">Buzz2Remote</span>
            </Link>
            <button 
              onClick={() => window.history.back()} 
              className="text-sm text-green-600 hover:text-green-700 flex items-center transition-colors"
            >
              <ArrowLeft className="w-4 h-4 mr-1" />
              Go Back
            </button>
          </div>

          <div className="text-center">
            <div className="flex items-center justify-center mb-2">
              <ShieldCheck className="w-12 h-12 text-green-500" />
            </div>
            <h1 className="text-3xl font-bold text-gray-900 mb-2">Privacy Policy</h1>
            <div className="flex items-center justify-center text-gray-600 space-x-4">
              <div className="flex items-center">
                <Calendar className="w-4 h-4 mr-2" />
                <span>Last updated: {lastUpdated}</span>
              </div>
              <div className="flex items-center">
                <ShieldCheck className="w-4 h-4 mr-2" />
                <span>GDPR & CCPA Compliant</span>
              </div>
            </div>
          </div>
        </div>

        {/* Privacy Highlights */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-green-50 border border-green-200 rounded-lg p-4 text-center">
            <Lock className="w-8 h-8 text-green-600 mx-auto mb-2" />
            <h3 className="font-semibold text-green-900">Secure by Design</h3>
            <p className="text-sm text-green-800">End-to-end encryption and SOC 2 compliance</p>
          </div>
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 text-center">
            <UserCheck className="w-8 h-8 text-blue-600 mx-auto mb-2" />
            <h3 className="font-semibold text-blue-900">Your Control</h3>
            <p className="text-sm text-blue-800">Full control over your data and privacy settings</p>
          </div>
          <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 text-center">
            <Globe className="w-8 h-8 text-purple-600 mx-auto mb-2" />
            <h3 className="font-semibold text-purple-900">Global Compliance</h3>
            <p className="text-sm text-purple-800">GDPR, CCPA, and other privacy laws</p>
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
                className="text-left text-green-600 hover:text-green-700 text-sm transition-colors flex items-center"
              >
                {section.icon}
                <span className="ml-2">{section.title}</span>
              </button>
            ))}
          </div>
        </div>

        {/* Privacy Policy Content */}
        <div className="bg-white shadow-sm rounded-lg overflow-hidden">
          {sections.map((section, index) => (
            <div key={section.id} className={index > 0 ? "border-t border-gray-200" : ""}>
              <button
                onClick={() => toggleSection(section.id)}
                className="w-full px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-inset hover:bg-gray-50 transition-colors"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center">
                    {section.icon}
                    <h3 className="text-lg font-semibold text-gray-900 ml-3">{section.title}</h3>
                  </div>
                  {expandedSections.has(section.id) ? (
                    <ChevronDown className="w-5 h-5 text-gray-500" />
                  ) : (
                    <ChevronRight className="w-5 h-5 text-gray-500" />
                  )}
                </div>
              </button>
              
              {expandedSections.has(section.id) && (
                <div className="px-6 pb-6 text-gray-700 prose prose-green max-w-none">
                  {section.content}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Contact and Rights Section */}
        <div className="bg-white shadow-sm rounded-lg p-6 mt-8">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">Exercise Your Privacy Rights</h2>
          <p className="text-gray-600 mb-4">
            You have important rights regarding your personal data. Contact us to exercise these rights or if you have any privacy-related questions.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <a
              href="mailto:privacy@buzz2remote.com"
              className="inline-flex items-center justify-center px-4 py-2 border border-green-300 rounded-md text-green-700 bg-green-50 hover:bg-green-100 transition-colors"
            >
              <Mail className="w-4 h-4 mr-2" />
              privacy@buzz2remote.com
            </a>
            <a
              href="mailto:dpo@buzz2remote.com"
              className="inline-flex items-center justify-center px-4 py-2 border border-blue-300 rounded-md text-blue-700 bg-blue-50 hover:bg-blue-100 transition-colors"
            >
              <ShieldCheck className="w-4 h-4 mr-2" />
              Data Protection Officer
            </a>
          </div>
        </div>

        {/* Footer Note */}
        <div className="text-center mt-8 text-sm text-gray-500">
          <p>
            This Privacy Policy is effective as of {lastUpdated} and applies to all users of the Buzz2Remote platform worldwide.
          </p>
          <p className="mt-2">
            For translations of this policy in other languages, please contact us.
          </p>
        </div>
      </div>
    </Layout>
  );
};

export default PrivacyPolicy; 