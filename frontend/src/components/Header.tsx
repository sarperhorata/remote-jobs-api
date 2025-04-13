import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Bars3Icon as MenuIcon } from '@heroicons/react/24/outline';
import { useAuth } from '../contexts/AuthContext';

const Header = () => {
  const [isMenuOpen, setIsMenuOpen] = useState(false);
  const { isAuthenticated, logout } = useAuth();

  return (
    <header className="bg-white shadow-md">
      <div className="container mx-auto px-4 py-3 flex justify-between items-center">
        <div className="flex items-center">
          <Link to="/" className="text-2xl font-bold text-primary">
            RemoteJobs
          </Link>
          <nav className="hidden md:flex ml-8">
            <ul className="flex space-x-6">
              <li>
                <Link to="/" className="text-gray-700 hover:text-primary transition">
                  Home
                </Link>
              </li>
              <li>
                <Link to="/jobs" className="text-gray-700 hover:text-primary transition">
                  Find Jobs
                </Link>
              </li>
              <li>
                <Link to="/about" className="text-gray-700 hover:text-primary transition">
                  About
                </Link>
              </li>
              <li>
                <Link to="/contact" className="text-gray-700 hover:text-primary transition">
                  Contact
                </Link>
              </li>
            </ul>
          </nav>
        </div>

        <div className="flex items-center">
          <Link to="/auth/login" className="text-gray-700 hover:text-primary mr-4 transition">
            Sign In
          </Link>
          
          <Link
            to="/auth/register"
            className="bg-primary text-white py-2 px-4 rounded hover:bg-primary-dark transition"
          >
            Sign Up
          </Link>

          {/* Mobile menu button */}
          <button
            className="ml-4 md:hidden focus:outline-none"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            <MenuIcon className="h-6 w-6 text-gray-700" />
          </button>
        </div>
      </div>

      {/* Mobile menu */}
      {isMenuOpen && (
        <div className="md:hidden bg-white py-2 px-4 shadow-lg">
          <ul className="space-y-2">
            <li>
              <Link
                to="/"
                className="block py-2 text-gray-700 hover:text-primary transition"
                onClick={() => setIsMenuOpen(false)}
              >
                Home
              </Link>
            </li>
            <li>
              <Link
                to="/jobs"
                className="block py-2 text-gray-700 hover:text-primary transition"
                onClick={() => setIsMenuOpen(false)}
              >
                Find Jobs
              </Link>
            </li>
            <li>
              <Link
                to="/about"
                className="block py-2 text-gray-700 hover:text-primary transition"
                onClick={() => setIsMenuOpen(false)}
              >
                About
              </Link>
            </li>
            <li>
              <Link
                to="/contact"
                className="block py-2 text-gray-700 hover:text-primary transition"
                onClick={() => setIsMenuOpen(false)}
              >
                Contact
              </Link>
            </li>
          </ul>
        </div>
      )}
    </header>
  );
};

export default Header; 