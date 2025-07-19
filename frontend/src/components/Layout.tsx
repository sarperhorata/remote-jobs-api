import React from 'react';
import Header from './Header';
import Footer from './Footer';
import CookieDisclaimer from './CookieDisclaimer';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="flex flex-col min-h-screen bg-gray-50 dark:bg-gray-900">
      <Header />
      <main className="flex-grow pt-16">
        {children}
      </main>
      <Footer />
      <CookieDisclaimer />
    </div>
  );
};

export default Layout; 