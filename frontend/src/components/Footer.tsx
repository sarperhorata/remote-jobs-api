import React from 'react';
import { Link } from 'react-router-dom';
import { Twitter, Linkedin, Mail } from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  const scrollToTop = () => {
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  return (
    <footer className="bg-gradient-to-r from-slate-900 via-blue-900 to-slate-900 border-t border-white/10 backdrop-blur-lg">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center mb-4">
              <div className="w-8 h-8 bg-gradient-to-br from-yellow-400 to-orange-500 rounded-lg flex items-center justify-center mr-3">
                <span className="text-lg animate-pulse hover:animate-none transition-all duration-300">🐝</span>
              </div>
              <h3 className="text-xl font-bold bg-gradient-to-r from-yellow-400 via-orange-400 to-pink-500 bg-clip-text text-transparent">
                Buzz2Remote
              </h3>
            </div>
            <p className="text-gray-300 text-sm mb-4">
              Your gateway to the best remote job opportunities worldwide. 
              Connect with top companies and find your dream remote position.
            </p>
            <div className="flex space-x-4">
              <a
                href="https://twitter.com/buzz2remote"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                <Twitter className="w-5 h-5" />
              </a>
              <a
                href="https://linkedin.com/company/buzz2remote"
                target="_blank"
                rel="noopener noreferrer"
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                <Linkedin className="w-5 h-5" />
              </a>
              <a
                href="mailto:hello@buzz2remote.com"
                className="text-gray-400 hover:text-white transition-colors duration-200"
              >
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="text-white font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/" onClick={scrollToTop} className="text-gray-300 hover:text-white transition-colors duration-200 text-sm">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/jobs/search" onClick={scrollToTop} className="text-gray-300 hover:text-white transition-colors duration-200 text-sm">
                  Find Jobs
                </Link>
              </li>
              <li>
                <Link to="/pricing" onClick={scrollToTop} className="text-gray-300 hover:text-white transition-colors duration-200 text-sm">
                  Pricing
                </Link>
              </li>
              <li>
                <Link to="/help" onClick={scrollToTop} className="text-gray-300 hover:text-white transition-colors duration-200 text-sm">
                  Help Center
                </Link>
              </li>
            </ul>
          </div>

          {/* Legal */}
          <div>
            <h4 className="text-white font-semibold mb-4">Legal</h4>
            <ul className="space-y-2">
              <li>
                <Link to="/privacy-policy" onClick={scrollToTop} className="text-gray-300 hover:text-white transition-colors duration-200 text-sm">
                  Privacy Policy
                </Link>
              </li>
              <li>
                <Link to="/terms-conditions" onClick={scrollToTop} className="text-gray-300 hover:text-white transition-colors duration-200 text-sm">
                  Terms & Conditions
                </Link>
              </li>
            </ul>
          </div>
        </div>

        <div className="border-t border-white/10 mt-8 pt-6">
          <p className="text-gray-400 text-sm text-center">
            &copy; {currentYear} Buzz2Remote. All rights reserved.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 