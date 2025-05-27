import React from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, FileText, ArrowLeft } from 'lucide-react';

const TermsConditions: React.FC = () => {
  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-3xl mx-auto bg-white shadow-xl sm:rounded-2xl p-8 md:p-12 border border-gray-200">
        <div className="flex items-center justify-between mb-8">
          <Link to="/" className="flex items-center space-x-3 text-gray-700 hover:text-blue-600">
            <Briefcase className="w-8 h-8 text-blue-600" />
            <span className="text-2xl font-bold">Buzz2Remote</span>
          </Link>
          <button onClick={() => window.history.back()} className="text-sm text-blue-600 hover:underline flex items-center">
            <ArrowLeft className="w-4 h-4 mr-1" />
            Go Back
          </button>
        </div>

        <div className="text-center mb-10">
          <FileText className="w-16 h-16 text-blue-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900">Terms & Conditions</h1>
          <p className="text-gray-500 mt-2">Last updated: {new Date().toLocaleDateString()}</p>
        </div>

        <div className="prose prose-lg max-w-none text-gray-700">
          <p>
            Welcome to Buzz2Remote! These terms and conditions outline the rules and regulations for the use of
            Buzz2Remote's Website, located at buzz2remote.com.
          </p>

          <p>
            By accessing this website we assume you accept these terms and conditions. Do not continue to use Buzz2Remote
            if you do not agree to take all of the terms and conditions stated on this page.
          </p>

          <h2 className="font-semibold text-xl mt-6 mb-3">Cookies</h2>
          <p>
            We employ the use of cookies. By accessing Buzz2Remote, you agreed to use cookies in agreement with the
            Buzz2Remote's Privacy Policy. Most interactive websites use cookies to let us retrieve the user's details
            for each visit. Cookies are used by our website to enable the functionality of certain areas to make it
            easier for people visiting our website. Some of our affiliate/advertising partners may also use cookies.
          </p>

          <h2 className="font-semibold text-xl mt-6 mb-3">License</h2>
          <p>
            Unless otherwise stated, Buzz2Remote and/or its licensors own the intellectual property rights for all
            material on Buzz2Remote. All intellectual property rights are reserved. You may access this from Buzz2Remote
            for your own personal use subjected to restrictions set in these terms and conditions.
          </p>
          <p>You must not:</p>
          <ul>
            <li>Republish material from Buzz2Remote</li>
            <li>Sell, rent or sub-license material from Buzz2Remote</li>
            <li>Reproduce, duplicate or copy material from Buzz2Remote</li>
            <li>Redistribute content from Buzz2Remote</li>
          </ul>

          {/* Add more sections as needed: User Comments, Hyperlinking, iFrames, Content Liability, Reservation of Rights, Disclaimer etc. */}
          <p className="mt-6">
            This is a simplified placeholder. A complete Terms & Conditions document should be drafted by a legal professional.
            Please ensure you have a comprehensive and legally compliant document before launching your platform.
          </p>
          
          <h2 className="font-semibold text-xl mt-6 mb-3">Contact Us</h2>
          <p>If you have any questions about these Terms, please <Link to="/contact" className="text-blue-600 hover:underline">contact us</Link>.</p>
        </div>
      </div>
    </div>
  );
};

export default TermsConditions; 