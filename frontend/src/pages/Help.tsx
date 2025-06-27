import React, { useState } from 'react';
import { Search, Mail, MessageCircle, Book, Users, Settings, Shield, CreditCard } from '../components/icons/EmojiIcons';

interface FAQItem {
  question: string;
  answer: string;
}

const faqSections = {
  general: [
    {
      question: "What is Buzz2Remote?",
      answer: "Buzz2Remote is a cutting-edge AI-powered platform designed specifically for remote work opportunities. We connect talented professionals with global companies offering remote positions. Our platform uses advanced algorithms to match job seekers with the most relevant opportunities based on their skills, experience, and preferences. Whether you're a developer, designer, marketer, or any other professional, Buzz2Remote helps you find your perfect remote career opportunity."
    },
    {
      question: "Is Buzz2Remote free to use?",
      answer: "Yes! Buzz2Remote is completely free for job seekers. You can create an account, browse unlimited job listings, apply to positions, track your applications, and access our career resources at no cost. For employers, we offer both free and premium posting options to help companies find the best remote talent."
    },
    {
      question: "How does the AI matching system work?",
      answer: "Our AI analyzes your profile, skills, experience, and job preferences to suggest the most relevant opportunities. The more complete your profile, the better our matching becomes. The system learns from your application patterns and feedback to continuously improve recommendations. It considers factors like skill compatibility, salary expectations, time zone preferences, and company culture fit."
    },
    {
      question: "What types of remote jobs are available?",
      answer: "We feature opportunities across all industries and experience levels: Software Development, Design & UX/UI, Marketing & Sales, Content Creation, Customer Support, Project Management, Data Science & Analytics, Finance & Accounting, HR & Recruiting, Operations, and many more. From entry-level to executive positions, full-time to freelance, we have opportunities for everyone."
    },
    {
      question: "How do I get started?",
      answer: "Getting started is simple: 1) Create your free account with email or Google sign-in, 2) Complete your professional profile with skills and experience, 3) Upload your resume and portfolio (optional), 4) Set your job preferences and salary expectations, 5) Start browsing and applying to jobs! Our onboarding process will guide you through each step."
    }
  ],
  jobSeekers: [
    {
      question: "How do I create an effective profile?",
      answer: "A strong profile includes: A professional photo and compelling headline, detailed work experience with specific achievements, complete skills section with proficiency levels, education and certifications, portfolio samples (if applicable), clear job preferences and salary expectations. The more detailed your profile, the better job matches you'll receive."
    },
    {
      question: "What should I include in my resume?",
      answer: "Your resume should highlight remote work experience, digital collaboration skills, and quantifiable achievements. Include: Contact information and professional summary, relevant work experience with specific accomplishments, technical and soft skills relevant to remote work, education and certifications, languages spoken, and any remote work tools you're proficient with (Slack, Zoom, Asana, etc.)."
    },
    {
      question: "How do I apply for jobs?",
      answer: "Once you find an interesting position: 1) Click 'Apply Now' on the job listing, 2) Review the job requirements and company information, 3) Customize your application message if needed, 4) Submit your application with your profile and resume, 5) Track your application status in your dashboard. Some employers may request additional documents or ask specific questions during application."
    },
    {
      question: "How can I track my applications?",
      answer: "Your dashboard provides complete application tracking: View all submitted applications with status updates, see employer responses and interview invitations, track application dates and deadlines, receive notifications for status changes, and access communication history with employers. You can filter and sort applications by status, date, or company."
    },
    {
      question: "What if I don't hear back from employers?",
      answer: "The remote job market is competitive, but don't get discouraged: Follow up politely after 1-2 weeks if you haven't heard back, continuously improve your profile and resume, apply to multiple positions that match your skills, consider expanding your skill set through online courses, and use our career resources for interview preparation and professional development."
    },
    {
      question: "How do I prepare for remote job interviews?",
      answer: "Remote interview preparation is crucial: Test your technology (camera, microphone, internet connection) beforehand, choose a quiet, well-lit space with professional background, prepare examples of remote work experience and self-management skills, research the company culture and remote work policies, prepare questions about team communication and collaboration tools, and practice answering common remote work questions about time management and independent work style."
    },
    {
      question: "Can I apply from any country?",
      answer: "Most jobs on our platform welcome international applicants, but each position has specific location requirements. Always check: The job's location restrictions and visa/work permit requirements, time zone requirements for team collaboration, whether the company sponsors visas or handles international hiring, tax and legal implications of working for foreign companies. Filter jobs by 'Worldwide Remote' to find truly location-independent opportunities."
    }
  ],
  employers: [
    {
      question: "How do I post a job listing?",
      answer: "Posting jobs is straightforward: 1) Create your employer account and complete company profile, 2) Click 'Post a Job' from your dashboard, 3) Fill in job details: title, description, requirements, salary range, 4) Set application preferences and screening questions, 5) Choose your posting package (free or premium), 6) Review and publish your listing. Premium listings get better visibility and advanced candidate filtering."
    },
    {
      question: "How much does it cost to post jobs?",
      answer: "We offer flexible pricing: Free listings include basic job posting for 30 days and access to applicant profiles. Premium listings ($99/month) include featured placement in search results, advanced candidate filtering and search, priority customer support, detailed analytics and reporting, and extended listing duration (60 days). Enterprise packages available for high-volume hiring."
    },
    {
      question: "How do I manage applications effectively?",
      answer: "Our employer dashboard provides powerful tools: Review all applications with candidate profiles and resumes, use filters to sort by skills, experience, and location, send personalized messages and interview invitations, track candidate progress through your hiring pipeline, collaborate with team members on candidate evaluation, and access interview scheduling tools and feedback forms."
    },
    {
      question: "What makes a good remote job posting?",
      answer: "Effective job postings include: Clear, specific job title and detailed role description, explicit remote work requirements and expectations, company culture and values that attract remote talent, specific skills and experience requirements, transparent salary range and benefits information, information about team structure and communication tools, and growth and development opportunities."
    },
    {
      question: "How do I evaluate remote candidates?",
      answer: "Remote hiring requires different evaluation criteria: Assess communication skills through written applications and video interviews, evaluate self-management and time organization abilities, look for previous remote work experience or relevant independent work, test technical skills with relevant challenges or portfolio reviews, evaluate cultural fit and alignment with company values, and consider time zone compatibility and availability requirements."
    },
    {
      question: "What legal considerations should I know?",
      answer: "Remote hiring involves various legal aspects: Understand employment laws in candidate locations, consider tax implications of hiring international employees, ensure compliance with data protection regulations (GDPR, etc.), clarify intellectual property and confidentiality agreements, understand visa and work permit requirements, and consider using international payroll services for global hiring. Consult legal professionals for complex situations."
    }
  ],
  technical: [
    {
      question: "How do I reset my password?",
      answer: "To reset your password: 1) Go to the login page and click 'Forgot Password', 2) Enter your registered email address, 3) Check your email for the reset link (including spam folder), 4) Click the link and create a new strong password, 5) Log in with your new password. If you don't receive the email within 10 minutes, try again or contact support."
    },
    {
      question: "How do I update my email address?",
      answer: "To change your email: 1) Log into your account and go to Account Settings, 2) Click 'Change Email Address', 3) Enter your new email and confirm it, 4) Verify the change through the confirmation email sent to your new address, 5) Your email will be updated once verified. Note: You'll need to use your new email for future logins."
    },
    {
      question: "How do I manage notification preferences?",
      answer: "Customize your notifications in Settings: Control email notifications for new job matches, application updates, employer messages, weekly job digest, and system announcements. Manage in-app notifications for real-time updates, message alerts, and application status changes. You can set different preferences for different types of notifications and choose frequency (immediate, daily, weekly)."
    },
    {
      question: "Why can't I see certain job listings?",
      answer: "Job visibility depends on several factors: Your profile completeness (incomplete profiles see fewer jobs), location restrictions set by employers, your job preferences and filters, account verification status, and subscription level. To see more jobs: complete your profile 100%, verify your email address, check your location and job type filters, and ensure your skills match job requirements."
    },
    {
      question: "How do I delete my account?",
      answer: "To permanently delete your account: 1) Go to Account Settings and scroll to 'Account Management', 2) Click 'Delete Account' and confirm your decision, 3) Your account and all data will be permanently removed within 7 days, 4) You'll receive a confirmation email. Note: This action cannot be undone. Consider downloading your data first if needed."
    },
    {
      question: "What browsers and devices are supported?",
      answer: "Buzz2Remote works on: Desktop browsers: Chrome, Firefox, Safari, Edge (latest versions), mobile browsers on iOS Safari and Android Chrome, tablet devices with modern browsers. For the best experience, we recommend using Chrome or Firefox on desktop with JavaScript enabled and cookies allowed."
    },
    {
      question: "How do I report a technical issue?",
      answer: "If you encounter problems: 1) Try refreshing the page or logging out and back in, 2) Clear your browser cache and cookies, 3) Check if the issue persists in an incognito/private window, 4) If the problem continues, contact support with: your browser type and version, screenshots of any error messages, steps to reproduce the issue, and your account email. We typically respond within 24 hours."
    }
  ],
  privacy: [
    {
      question: "How is my personal data protected?",
      answer: "We take data protection seriously: All data is encrypted in transit and at rest using industry-standard protocols, access to personal information is strictly limited to authorized personnel, we comply with GDPR, CCPA, and other privacy regulations, regular security audits and vulnerability assessments are conducted, and we never sell your personal information to third parties. You have full control over your data privacy settings."
    },
    {
      question: "Who can see my profile information?",
      answer: "Your profile visibility is under your control: Public information includes basic professional details you choose to make visible, employers with premium accounts can view more detailed profiles of candidates who apply to their jobs, your contact information is never shared without your permission, and you can set your profile to private mode to limit visibility. Always review your privacy settings regularly."
    },
    {
      question: "How do I control data sharing?",
      answer: "Manage your data sharing preferences: Choose which profile information is visible to employers, control whether your profile appears in employer searches, decide if you want to receive marketing communications, manage cookie preferences for analytics and advertising, and opt-out of data processing for marketing purposes while keeping job-related functionality. All settings are in your Privacy Dashboard."
    },
    {
      question: "What happens to my data if I delete my account?",
      answer: "Upon account deletion: All personal profile information is permanently removed, application history is anonymized and retained for legal compliance only, communications with employers are deleted from our systems, and any saved searches or preferences are completely removed. Some anonymized usage data may be retained for analytics purposes but cannot be linked back to you."
    }
  ]
};

const Help: React.FC = () => {
  const [activeSection, setActiveSection] = useState<string>('general');
  const [expandedQuestions, setExpandedQuestions] = useState<Set<string>>(new Set());
  const [searchTerm, setSearchTerm] = useState('');

  const toggleQuestion = (question: string) => {
    const newExpanded = new Set(expandedQuestions);
    if (newExpanded.has(question)) {
      newExpanded.delete(question);
    } else {
      newExpanded.add(question);
    }
    setExpandedQuestions(newExpanded);
  };

  const getSectionIcon = (section: string) => {
    switch (section) {
      case 'general': return <Book className="w-5 h-5" />;
      case 'jobSeekers': return <Users className="w-5 h-5" />;
      case 'employers': return <Settings className="w-5 h-5" />;
      case 'technical': return <Settings className="w-5 h-5" />;
      case 'privacy': return <Shield className="w-5 h-5" />;
      default: return <Book className="w-5 h-5" />;
    }
  };

  const getSectionTitle = (section: string) => {
    switch (section) {
      case 'general': return 'Getting Started';
      case 'jobSeekers': return 'For Job Seekers';
      case 'employers': return 'For Employers';
      case 'technical': return 'Technical Support';
      case 'privacy': return 'Privacy & Security';
      default: return 'General';
    }
  };

  const filteredFAQs = searchTerm
    ? Object.entries(faqSections).reduce((acc, [section, faqs]) => {
        const filtered = faqs.filter(
          faq =>
            faq.question.toLowerCase().includes(searchTerm.toLowerCase()) ||
            faq.answer.toLowerCase().includes(searchTerm.toLowerCase())
        );
        if (filtered.length > 0) {
          acc[section] = filtered;
        }
        return acc;
      }, {} as typeof faqSections)
    : { [activeSection]: faqSections[activeSection as keyof typeof faqSections] };

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-12">
          <h1 className="text-4xl font-extrabold text-gray-900 sm:text-5xl">
            Help & Support Center
          </h1>
          <p className="mt-4 text-xl text-gray-600 max-w-3xl mx-auto">
            Find answers to common questions, learn how to make the most of Buzz2Remote, and get the support you need for your remote career journey.
          </p>
        </div>

        {/* Search Bar */}
        <div className="max-w-2xl mx-auto mb-8">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
            <input
              type="text"
              placeholder="Search for help articles, features, or common questions..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full pl-10 pr-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-orange-500 focus:border-transparent text-sm"
            />
          </div>
        </div>

        {/* Category Navigation */}
        {!searchTerm && (
          <div className="mb-8 flex flex-wrap justify-center gap-4">
            {Object.keys(faqSections).map((section) => (
              <button
                key={section}
                onClick={() => setActiveSection(section)}
                className={`flex items-center space-x-2 px-6 py-3 rounded-lg text-sm font-medium transition-colors ${
                  activeSection === section
                    ? 'bg-orange-600 text-white shadow-lg'
                    : 'bg-white text-gray-700 hover:bg-orange-50 border border-gray-200'
                }`}
              >
                {getSectionIcon(section)}
                <span>{getSectionTitle(section)}</span>
              </button>
            ))}
          </div>
        )}

        {/* FAQ Content */}
        <div className="space-y-6">
          {Object.entries(filteredFAQs).map(([section, faqs]) => (
            <div key={section}>
              {searchTerm && (
                <h2 className="text-2xl font-bold text-gray-900 mb-4 flex items-center space-x-2">
                  {getSectionIcon(section)}
                  <span>{getSectionTitle(section)}</span>
                </h2>
              )}
              <div className="space-y-4">
                {faqs.map((faq: FAQItem, index: number) => (
                  <div
                    key={`${section}-${index}`}
                    className="bg-white shadow-sm rounded-lg overflow-hidden border border-gray-200 hover:shadow-md transition-shadow"
                  >
                    <button
                      onClick={() => toggleQuestion(`${section}-${index}`)}
                      className="w-full px-6 py-4 text-left focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-inset"
                    >
                      <div className="flex items-center justify-between">
                        <h3 className="text-lg font-semibold text-gray-900 pr-4">
                          {faq.question}
                        </h3>
                        <svg
                          className={`h-5 w-5 text-gray-500 transform transition-transform flex-shrink-0 ${
                            expandedQuestions.has(`${section}-${index}`) ? 'rotate-180' : ''
                          }`}
                          fill="none"
                          viewBox="0 0 24 24"
                          stroke="currentColor"
                        >
                          <path
                            strokeLinecap="round"
                            strokeLinejoin="round"
                            strokeWidth={2}
                            d="M19 9l-7 7-7-7"
                          />
                        </svg>
                      </div>
                    </button>
                    {expandedQuestions.has(`${section}-${index}`) && (
                      <div className="px-6 pb-4 border-t border-gray-100">
                        <p className="text-gray-700 leading-relaxed">{faq.answer}</p>
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>

        {/* Contact Support Section */}
        <div className="mt-16 bg-gradient-to-r from-orange-500 to-yellow-500 rounded-2xl shadow-xl overflow-hidden">
          <div className="px-8 py-12 text-center">
            <h2 className="text-3xl font-bold text-white mb-4">
              Still Need Help?
            </h2>
            <p className="text-xl text-orange-100 mb-8 max-w-2xl mx-auto">
              Can't find what you're looking for? Our support team is here to help you succeed in your remote career journey.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a
                href="mailto:support@buzz2remote.com"
                className="inline-flex items-center justify-center space-x-2 bg-white text-orange-600 px-8 py-3 rounded-lg hover:bg-orange-50 transition-colors font-semibold shadow-lg"
              >
                <Mail className="w-5 h-5" />
                <span>Email Support</span>
              </a>
              <a
                href="/contact"
                className="inline-flex items-center justify-center space-x-2 bg-orange-700 text-white px-8 py-3 rounded-lg hover:bg-orange-800 transition-colors font-semibold border border-orange-600"
              >
                <MessageCircle className="w-5 h-5" />
                <span>Live Chat</span>
              </a>
            </div>
            
            {/* Support Info */}
            <div className="mt-8 text-orange-100 text-sm">
              <p>📧 Email response time: Within 24 hours</p>
              <p>💬 Live chat: Monday-Friday, 9 AM - 6 PM UTC</p>
            </div>
          </div>
        </div>

        {/* Additional Resources */}
        <div className="mt-12 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <Book className="w-8 h-8 text-orange-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">User Guide</h3>
            <p className="text-gray-600 text-sm mb-4">
              Comprehensive documentation to help you master the platform.
            </p>
            <a href="/docs" className="text-orange-600 hover:text-orange-700 font-medium text-sm">
              Browse Documentation →
            </a>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <Users className="w-8 h-8 text-blue-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Community</h3>
            <p className="text-gray-600 text-sm mb-4">
              Connect with other remote professionals and share experiences.
            </p>
            <a href="/community" className="text-blue-600 hover:text-blue-700 font-medium text-sm">
              Join Community →
            </a>
          </div>
          
          <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 text-center">
            <CreditCard className="w-8 h-8 text-green-500 mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-gray-900 mb-2">Career Resources</h3>
            <p className="text-gray-600 text-sm mb-4">
              Tips, guides, and tools to advance your remote career.
            </p>
            <a href="/resources" className="text-green-600 hover:text-green-700 font-medium text-sm">
              Explore Resources →
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Help; 