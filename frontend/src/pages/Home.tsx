import React from 'react';
import { Link } from 'react-router-dom';

const Home: React.FC = () => {
  return (
    <div className="home-page">
      <header className="hero">
        <h1>Find Your Dream Remote Job</h1>
        <p>Discover remote opportunities from top companies around the world.</p>
        <Link to="/jobs" className="cta-button">Browse Jobs</Link>
      </header>
      
      <section className="features">
        <div className="feature">
          <h2>Curated Jobs</h2>
          <p>We carefully select remote job opportunities from trusted companies.</p>
        </div>
        <div className="feature">
          <h2>Always Fresh</h2>
          <p>Our automated system regularly updates the job listings.</p>
        </div>
        <div className="feature">
          <h2>Track Applications</h2>
          <p>Keep track of your job applications and their status.</p>
        </div>
      </section>
      
      <section className="cta">
        <h2>Ready to Start Your Remote Career?</h2>
        <Link to="/jobs" className="cta-button">Find Jobs Now</Link>
      </section>
    </div>
  );
};

export default Home; 