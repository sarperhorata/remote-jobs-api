describe('Job Application Flow E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
    // Login before each test
    cy.login('test@example.com', 'password123');
  });

  describe('Job Search and Selection', () => {
    it('should search for jobs and view details', () => {
      cy.get('[data-testid="job-search-input"]').type('React Developer');
      cy.get('[data-testid="search-button"]').click();
      
      cy.get('[data-testid="job-results"]').should('be.visible');
      cy.get('[data-testid="job-card"]').first().click();
      
      cy.get('[data-testid="job-detail-page"]').should('be.visible');
      cy.get('[data-testid="job-title"]').should('contain', 'React');
    });

    it('should filter jobs by location and type', () => {
      cy.visit('/jobs');
      
      cy.get('[data-testid="location-filter"]').click();
      cy.get('[data-testid="filter-option"]').contains('Remote').click();
      
      cy.get('[data-testid="job-type-filter"]').click();
      cy.get('[data-testid="filter-option"]').contains('Full-time').click();
      
      cy.get('[data-testid="apply-filters"]').click();
      
      cy.url().should('include', 'location=Remote');
      cy.url().should('include', 'job_type=Full-time');
    });

    it('should save job to favorites', () => {
      cy.visit('/jobs');
      cy.get('[data-testid="job-card"]').first().within(() => {
        cy.get('[data-testid="favorite-button"]').click();
      });
      
      cy.get('[data-testid="favorite-success"]').should('be.visible');
      
      // Check favorites page
      cy.visit('/favorites');
      cy.get('[data-testid="favorite-job"]').should('have.length.at.least', 1);
    });
  });

  describe('Job Application Process', () => {
    beforeEach(() => {
      // Navigate to a specific job
      cy.visit('/jobs/1');
    });

    it('should display application form', () => {
      cy.get('[data-testid="apply-button"]').click();
      cy.get('[data-testid="application-form"]').should('be.visible');
      
      cy.get('[data-testid="name-input"]').should('be.visible');
      cy.get('[data-testid="email-input"]').should('be.visible');
      cy.get('[data-testid="resume-upload"]').should('be.visible');
      cy.get('[data-testid="cover-letter"]').should('be.visible');
    });

    it('should validate application form fields', () => {
      cy.get('[data-testid="apply-button"]').click();
      cy.get('[data-testid="submit-application"]').click();
      
      cy.get('[data-testid="name-error"]').should('be.visible');
      cy.get('[data-testid="email-error"]').should('be.visible');
      cy.get('[data-testid="resume-error"]').should('be.visible');
    });

    it('should upload resume file', () => {
      cy.get('[data-testid="apply-button"]').click();
      
      cy.fixture('resume.pdf').then(fileContent => {
        cy.get('[data-testid="resume-upload"]').attachFile({
          fileContent: fileContent.toString(),
          fileName: 'resume.pdf',
          mimeType: 'application/pdf'
        });
      });
      
      cy.get('[data-testid="file-upload-success"]').should('be.visible');
    });

    it('should submit application successfully', () => {
      cy.get('[data-testid="apply-button"]').click();
      
      // Fill form
      cy.get('[data-testid="name-input"]').type('John Doe');
      cy.get('[data-testid="email-input"]').type('john@example.com');
      cy.get('[data-testid="cover-letter"]').type('I am interested in this position...');
      
      // Upload resume
      cy.fixture('resume.pdf').then(fileContent => {
        cy.get('[data-testid="resume-upload"]').attachFile({
          fileContent: fileContent.toString(),
          fileName: 'resume.pdf',
          mimeType: 'application/pdf'
        });
      });
      
      cy.get('[data-testid="submit-application"]').click();
      
      cy.get('[data-testid="application-success"]').should('be.visible');
      cy.get('[data-testid="application-id"]').should('be.visible');
    });

    it('should show application confirmation', () => {
      // Complete application process
      cy.get('[data-testid="apply-button"]').click();
      cy.get('[data-testid="name-input"]').type('John Doe');
      cy.get('[data-testid="email-input"]').type('john@example.com');
      cy.get('[data-testid="cover-letter"]').type('I am interested in this position...');
      
      cy.fixture('resume.pdf').then(fileContent => {
        cy.get('[data-testid="resume-upload"]').attachFile({
          fileContent: fileContent.toString(),
          fileName: 'resume.pdf',
          mimeType: 'application/pdf'
        });
      });
      
      cy.get('[data-testid="submit-application"]').click();
      
      // Check confirmation page
      cy.get('[data-testid="confirmation-page"]').should('be.visible');
      cy.get('[data-testid="application-number"]').should('be.visible');
      cy.get('[data-testid="next-steps"]').should('be.visible');
    });
  });

  describe('Application Management', () => {
    it('should view application history', () => {
      cy.visit('/applications');
      cy.get('[data-testid="applications-list"]').should('be.visible');
      cy.get('[data-testid="application-item"]').should('have.length.at.least', 1);
    });

    it('should view application details', () => {
      cy.visit('/applications');
      cy.get('[data-testid="application-item"]').first().click();
      
      cy.get('[data-testid="application-detail"]').should('be.visible');
      cy.get('[data-testid="application-status"]').should('be.visible');
      cy.get('[data-testid="application-date"]').should('be.visible');
    });

    it('should withdraw application', () => {
      cy.visit('/applications');
      cy.get('[data-testid="application-item"]').first().within(() => {
        cy.get('[data-testid="withdraw-button"]').click();
      });
      
      cy.get('[data-testid="withdraw-confirmation"]').should('be.visible');
      cy.get('[data-testid="confirm-withdraw"]').click();
      
      cy.get('[data-testid="withdraw-success"]').should('be.visible');
    });

    it('should track application status', () => {
      cy.visit('/applications');
      cy.get('[data-testid="application-item"]').first().within(() => {
        cy.get('[data-testid="status-badge"]').should('be.visible');
        cy.get('[data-testid="status-timeline"]').should('be.visible');
      });
    });
  });

  describe('Profile and Resume Management', () => {
    it('should update profile information', () => {
      cy.visit('/profile');
      cy.get('[data-testid="edit-profile"]').click();
      
      cy.get('[data-testid="name-input"]').clear().type('Updated Name');
      cy.get('[data-testid="bio-input"]').type('Updated bio information');
      cy.get('[data-testid="save-profile"]').click();
      
      cy.get('[data-testid="profile-updated"]').should('be.visible');
    });

    it('should upload and manage resumes', () => {
      cy.visit('/profile');
      cy.get('[data-testid="resume-section"]').click();
      
      // Upload new resume
      cy.fixture('new-resume.pdf').then(fileContent => {
        cy.get('[data-testid="upload-resume"]').attachFile({
          fileContent: fileContent.toString(),
          fileName: 'new-resume.pdf',
          mimeType: 'application/pdf'
        });
      });
      
      cy.get('[data-testid="resume-upload-success"]').should('be.visible');
      
      // Set as default
      cy.get('[data-testid="set-default-resume"]').click();
      cy.get('[data-testid="default-resume-set"]').should('be.visible');
    });

    it('should manage cover letter templates', () => {
      cy.visit('/profile');
      cy.get('[data-testid="cover-letters"]').click();
      
      cy.get('[data-testid="new-template"]').click();
      cy.get('[data-testid="template-name"]').type('Software Developer Template');
      cy.get('[data-testid="template-content"]').type('Dear Hiring Manager...');
      cy.get('[data-testid="save-template"]').click();
      
      cy.get('[data-testid="template-saved"]').should('be.visible');
    });
  });

  describe('Notifications and Communication', () => {
    it('should receive application status updates', () => {
      cy.visit('/notifications');
      cy.get('[data-testid="notifications-list"]').should('be.visible');
      
      // Check for application status notifications
      cy.get('[data-testid="status-notification"]').should('have.length.at.least', 1);
    });

    it('should manage notification preferences', () => {
      cy.visit('/settings');
      cy.get('[data-testid="notification-settings"]').click();
      
      cy.get('[data-testid="email-notifications"]').uncheck();
      cy.get('[data-testid="push-notifications"]').check();
      cy.get('[data-testid="save-preferences"]').click();
      
      cy.get('[data-testid="preferences-saved"]').should('be.visible');
    });
  });
});