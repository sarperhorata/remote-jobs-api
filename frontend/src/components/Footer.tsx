import React from 'react';
import { Link } from 'react-router-dom';
import { 
  Heart, 
  Twitter, 
  Linkedin, 
  Github, 
  Mail, 
  MapPin
} from 'lucide-react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gradient-to-r from-gray-900 via-purple-900 to-gray-900 text-white">
      <div className="container mx-auto px-4 py-12">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          {/* Company Info */}
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center space-x-2 mb-4">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-yellow-400 via-orange-500 to-red-500 flex items-center justify-center">
                <span className="text-white font-bold text-lg">🐝</span>
              </div>
              <div>
                <h3 className="text-xl font-bold bg-gradient-to-r from-yellow-400 to-orange-500 bg-clip-text text-transparent">
                  Buzz2Remote
                </h3>
                <p className="text-sm text-gray-300">Find Remote Jobs 🚀</p>
              </div>
            </div>
            <p className="text-gray-300 mb-6 max-w-md">
              Your gateway to the best remote opportunities worldwide. Connect with top companies 
              and find your perfect remote job with our advanced search and AI-powered matching.
            </p>
            <div className="flex space-x-4">
              <a href="https://twitter.com/buzz2remote" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                <Twitter className="w-5 h-5" />
              </a>
              <a href="https://linkedin.com/company/buzz2remote" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                <Linkedin className="w-5 h-5" />
              </a>
              <a href="https://github.com/buzz2remote" target="_blank" rel="noopener noreferrer" className="text-gray-400 hover:text-white transition-colors">
                <Github className="w-5 h-5" />
              </a>
              <a href="mailto:contact@buzz2remote.com" className="text-gray-400 hover:text-white transition-colors">
                <Mail className="w-5 h-5" />
              </a>
            </div>
          </div>

          {/* Quick Links */}
          <div>
            <h4 className="font-semibold mb-4 text-white">For Job Seekers</h4>
            <ul className="space-y-2">
              <li><Link to="/jobs" className="text-gray-300 hover:text-white transition-colors">Browse Jobs</Link></li>
              <li><Link to="/profile" className="text-gray-300 hover:text-white transition-colors">Create Profile</Link></li>
              <li><Link to="/career-tips" className="text-gray-300 hover:text-white transition-colors">Career Tips</Link></li>
              <li><Link to="/remote-tips" className="text-gray-300 hover:text-white transition-colors">Remote Tips</Link></li>
            </ul>
          </div>

          {/* Company */}
          <div>
            <h4 className="font-semibold mb-4 text-white">Company</h4>
            <ul className="space-y-2">
              <li><Link to="/about" className="text-gray-300 hover:text-white transition-colors">About Us</Link></li>
              <li><Link to="/contact" className="text-gray-300 hover:text-white transition-colors">Contact</Link></li>
              <li><Link to="/privacy" className="text-gray-300 hover:text-white transition-colors">Privacy Policy</Link></li>
              <li><Link to="/terms" className="text-gray-300 hover:text-white transition-colors">Terms of Service</Link></li>
            </ul>
          </div>
        </div>

        {/* Bottom Section */}
        <div className="border-t border-gray-700 mt-8 pt-8 flex flex-col md:flex-row justify-between items-center">
          <div className="flex items-center space-x-2 text-gray-400 mb-4 md:mb-0">
            <Heart className="w-4 h-4 text-red-500" />
            <span className="text-sm">Made with love for remote workers everywhere</span>
          </div>
          <div className="flex items-center space-x-6 text-sm text-gray-400">
            <span>&copy; {currentYear} Buzz2Remote. All rights reserved.</span>
            <div className="flex items-center space-x-2">
              <MapPin className="w-4 h-4" />
              <span>Global</span>
            </div>
          </div>
        </div>
      </div>
    </footer>
  );
};

export default Footer; 