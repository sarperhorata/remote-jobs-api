import React from 'react';

const Footer: React.FC = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-white/5 backdrop-blur-sm border-t border-white/10 text-center py-4">
      <div className="container mx-auto">
        <p className="text-sm text-gray-400">
          &copy; {currentYear} Buzz2Remote. All rights reserved.
        </p>
      </div>
    </footer>
  );
};

export default Footer; 