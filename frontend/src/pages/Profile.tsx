import React, { useState } from 'react';

const Profile: React.FC = () => {
  const [activeTab, setActiveTab] = useState('profile');
  
  return (
    <div className="profile-page">
      <h1>My Profile</h1>
      
      <div className="profile-tabs">
        <button 
          className={`tab-button ${activeTab === 'profile' ? 'active' : ''}`}
          onClick={() => setActiveTab('profile')}
        >
          Profile
        </button>
        <button 
          className={`tab-button ${activeTab === 'skills' ? 'active' : ''}`}
          onClick={() => setActiveTab('skills')}
        >
          Skills
        </button>
        <button 
          className={`tab-button ${activeTab === 'resumes' ? 'active' : ''}`}
          onClick={() => setActiveTab('resumes')}
        >
          Resumes
        </button>
        <button 
          className={`tab-button ${activeTab === 'jobs' ? 'active' : ''}`}
          onClick={() => setActiveTab('jobs')}
        >
          Saved Jobs
        </button>
      </div>
      
      {activeTab === 'profile' && (
        <div className="profile-content">
          <h2>Personal Information</h2>
          <form className="profile-form">
            <div className="form-group">
              <label>Full Name</label>
              <input type="text" defaultValue="John Doe" />
            </div>
            <div className="form-group">
              <label>Email</label>
              <input type="email" defaultValue="john.doe@example.com" />
            </div>
            <div className="form-group">
              <label>Location</label>
              <input type="text" defaultValue="New York, USA" />
            </div>
            <div className="form-group">
              <label>About Me</label>
              <textarea defaultValue="Experienced software developer with a passion for creating clean, efficient code."></textarea>
            </div>
            <button type="submit" className="save-button">Save Changes</button>
          </form>
        </div>
      )}
      
      {activeTab === 'skills' && (
        <div className="skills-content">
          <h2>My Skills</h2>
          <div className="skills-list">
            <div className="skill-tag">JavaScript</div>
            <div className="skill-tag">React</div>
            <div className="skill-tag">Node.js</div>
            <div className="skill-tag">TypeScript</div>
            <div className="skill-tag">Python</div>
          </div>
          <div className="add-skill">
            <input type="text" placeholder="Add a new skill" />
            <button>Add</button>
          </div>
        </div>
      )}
      
      {activeTab === 'resumes' && (
        <div className="resumes-content">
          <h2>My Resumes</h2>
          <div className="resume-list">
            <div className="resume-item">
              <span className="resume-name">Software_Developer_Resume.pdf</span>
              <div className="resume-actions">
                <button>View</button>
                <button>Edit</button>
                <button>Delete</button>
              </div>
            </div>
            <div className="resume-item">
              <span className="resume-name">Frontend_Developer_Resume.pdf</span>
              <div className="resume-actions">
                <button>View</button>
                <button>Edit</button>
                <button>Delete</button>
              </div>
            </div>
          </div>
          <button className="upload-button">Upload New Resume</button>
        </div>
      )}
      
      {activeTab === 'jobs' && (
        <div className="saved-jobs-content">
          <h2>Saved Jobs</h2>
          <div className="saved-jobs-list">
            <div className="job-card">
              <h3>Frontend Developer</h3>
              <p className="company">Tech Solutions Inc.</p>
              <div className="job-actions">
                <button>View</button>
                <button>Apply</button>
                <button>Remove</button>
              </div>
            </div>
            <div className="job-card">
              <h3>React Developer</h3>
              <p className="company">Digital Innovations</p>
              <div className="job-actions">
                <button>View</button>
                <button>Apply</button>
                <button>Remove</button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Profile; 