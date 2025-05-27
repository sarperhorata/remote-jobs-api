import React from 'react';
import { Link } from 'react-router-dom';
import { Briefcase, ShieldCheck, ArrowLeft } from 'lucide-react';

const PrivacyPolicy: React.FC = () => {
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
          <ShieldCheck className="w-16 h-16 text-green-500 mx-auto mb-4" />
          <h1 className="text-3xl font-bold text-gray-900">Privacy Policy</h1>
          <p className="text-gray-500 mt-2">Last updated: {new Date().toLocaleDateString()}</p>
        </div>

        <div className="prose prose-lg max-w-none text-gray-700">
          <p>
            Welcome to Buzz2Remote! This Privacy Policy explains how we collect, use, disclose, and safeguard your
            information when you visit our website buzz2remote.com, including any other media form, media channel,
            mobile website, or mobile application related or connected thereto (collectively, the "Site"). Please read
            this privacy policy carefully. If you do not agree with the terms of this privacy policy, please do not
            access the site.
          </p>

          <h2 className="font-semibold text-xl mt-6 mb-3">Collection of Your Information</h2>
          <p>
            We may collect information about you in a variety of ways. The information we may collect on the Site includes:
          </p>
          <h3 className="font-medium text-lg mt-4 mb-2">Personal Data</h3>
          <p>
            Personally identifiable information, such as your name, email address, and telephone number, and demographic
            information, such as your age, gender, hometown, and interests, that you voluntarily give to us when you
            register with the Site or when you choose to participate in various activities related to the Site, such as
            online chat and message boards.
          </p>
          <h3 className="font-medium text-lg mt-4 mb-2">Derivative Data</h3>
          <p>
            Information our servers automatically collect when you access the Site, such as your IP address, your browser
            type, your operating system, your access times, and the pages you have viewed directly before and after
            accessing the Site.
          </p>
          
          <h2 className="font-semibold text-xl mt-6 mb-3">Use of Your Information</h2>
          <p>
            Having accurate information about you permits us to provide you with a smooth, efficient, and customized
            experience. Specifically, we may use information collected about you via the Site to:
          </p>
          <ul>
            <li>Create and manage your account.</li>
            <li>Email you regarding your account or order.</li>
            <li>Enable user-to-user communications.</li>
            <li>Generate a personal profile about you to make future visits to the Site more personalized.</li>
            <li>Increase the efficiency and operation of the Site.</li>
            {/* Add more uses as needed */}
          </ul>

          {/* Add more sections as needed: Disclosure of Your Information, Tracking Technologies, Security of Your Information, Policy for Children, Controls for Do-Not-Track Features, GDPR Rights etc. */}
          <p className="mt-6">
            This is a simplified placeholder. A complete Privacy Policy document should be drafted by a legal professional.
            Please ensure you have a comprehensive and legally compliant document, especially regarding GDPR, CCPA, etc.
          </p>
          
          <h2 className="font-semibold text-xl mt-6 mb-3">Contact Us</h2>
          <p>If you have questions or comments about this Privacy Policy, please <Link to="/contact" className="text-blue-600 hover:underline">contact us</Link>.</p>
        </div>
      </div>
    </div>
  );
};

export default PrivacyPolicy; 