import React from 'react';

const Dashboard: React.FC = () => {
  return (
    <div className="dashboard-page">
      <h1>Dashboard</h1>
      
      <div className="dashboard-grid">
        <div className="dashboard-card">
          <h2>Job Applications</h2>
          <p className="stat">12</p>
          <p>Applications submitted</p>
        </div>
        
        <div className="dashboard-card">
          <h2>Interviews</h2>
          <p className="stat">3</p>
          <p>Upcoming interviews</p>
        </div>
        
        <div className="dashboard-card">
          <h2>Saved Jobs</h2>
          <p className="stat">8</p>
          <p>Jobs saved for later</p>
        </div>
        
        <div className="dashboard-card">
          <h2>Profile Strength</h2>
          <p className="stat">75%</p>
          <p>Complete your profile</p>
        </div>
      </div>
      
      <div className="recent-activity">
        <h2>Recent Activity</h2>
        <ul className="activity-list">
          <li className="activity-item">
            <span className="activity-date">May 15, 2023</span>
            <span className="activity-title">Applied to Senior Developer at Tech Corp</span>
          </li>
          <li className="activity-item">
            <span className="activity-date">May 12, 2023</span>
            <span className="activity-title">Interview scheduled with Global Solutions</span>
          </li>
          <li className="activity-item">
            <span className="activity-date">May 10, 2023</span>
            <span className="activity-title">Updated resume</span>
          </li>
        </ul>
      </div>
    </div>
  );
};

export default Dashboard; 