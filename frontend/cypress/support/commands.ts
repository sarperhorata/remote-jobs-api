/// <reference types="cypress" />

// Custom command for login
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/');
  cy.get('[data-testid="login-button"]').click();
  cy.get('[data-testid="email-input"]').type(email);
  cy.get('[data-testid="password-input"]').type(password);
  cy.get('[data-testid="login-submit"]').click();
  cy.get('[data-testid="user-menu"]').should('be.visible');
});

// Custom command for logout
Cypress.Commands.add('logout', () => {
  cy.get('[data-testid="user-menu"]').click();
  cy.get('[data-testid="logout-button"]').click();
  cy.get('[data-testid="login-button"]').should('be.visible');
});

// Custom command for creating a job application
Cypress.Commands.add('createJobApplication', (jobId: string, applicationData: any) => {
  cy.visit(`/jobs/${jobId}`);
  cy.get('[data-testid="apply-button"]').click();
  
  cy.get('[data-testid="name-input"]').type(applicationData.name);
  cy.get('[data-testid="email-input"]').type(applicationData.email);
  cy.get('[data-testid="cover-letter"]').type(applicationData.coverLetter);
  
  if (applicationData.resume) {
    cy.fixture(applicationData.resume).then(fileContent => {
      cy.get('[data-testid="resume-upload"]').attachFile({
        fileContent: fileContent.toString(),
        fileName: applicationData.resume,
        mimeType: 'application/pdf'
      });
    });
  }
  
  cy.get('[data-testid="submit-application"]').click();
  cy.get('[data-testid="application-success"]').should('be.visible');
});

// Custom command for searching jobs
Cypress.Commands.add('searchJobs', (query: string, filters?: any) => {
  cy.visit('/jobs');
  cy.get('[data-testid="job-search-input"]').type(query);
  cy.get('[data-testid="search-button"]').click();
  
  if (filters) {
    if (filters.location) {
      cy.get('[data-testid="location-filter"]').click();
      cy.get('[data-testid="filter-option"]').contains(filters.location).click();
    }
    
    if (filters.jobType) {
      cy.get('[data-testid="job-type-filter"]').click();
      cy.get('[data-testid="filter-option"]').contains(filters.jobType).click();
    }
    
    cy.get('[data-testid="apply-filters"]').click();
  }
  
  cy.get('[data-testid="job-results"]').should('be.visible');
});

// Custom command for saving job to favorites
Cypress.Commands.add('saveJobToFavorites', (jobId: string) => {
  cy.visit(`/jobs/${jobId}`);
  cy.get('[data-testid="favorite-button"]').click();
  cy.get('[data-testid="favorite-success"]').should('be.visible');
});

// Custom command for checking application status
Cypress.Commands.add('checkApplicationStatus', (applicationId: string) => {
  cy.visit('/applications');
  cy.get(`[data-testid="application-${applicationId}"]`).click();
  cy.get('[data-testid="application-status"]').should('be.visible');
});

// Custom command for updating profile
Cypress.Commands.add('updateProfile', (profileData: any) => {
  cy.visit('/profile');
  cy.get('[data-testid="edit-profile"]').click();
  
  if (profileData.name) {
    cy.get('[data-testid="name-input"]').clear().type(profileData.name);
  }
  
  if (profileData.bio) {
    cy.get('[data-testid="bio-input"]').clear().type(profileData.bio);
  }
  
  if (profileData.location) {
    cy.get('[data-testid="location-input"]').clear().type(profileData.location);
  }
  
  cy.get('[data-testid="save-profile"]').click();
  cy.get('[data-testid="profile-updated"]').should('be.visible');
});

// Custom command for uploading resume
Cypress.Commands.add('uploadResume', (fileName: string) => {
  cy.visit('/profile');
  cy.get('[data-testid="resume-section"]').click();
  
  cy.fixture(fileName).then(fileContent => {
    cy.get('[data-testid="upload-resume"]').attachFile({
      fileContent: fileContent.toString(),
      fileName: fileName,
      mimeType: 'application/pdf'
    });
  });
  
  cy.get('[data-testid="resume-upload-success"]').should('be.visible');
});

// Custom command for checking page performance
Cypress.Commands.add('checkPagePerformance', () => {
  cy.window().then((win) => {
    const performance = win.performance;
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    
    // Check if page load time is reasonable
    expect(navigation.loadEventEnd - navigation.loadEventStart).to.be.lessThan(3000);
    
    // Check if DOM content loaded is reasonable
    expect(navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart).to.be.lessThan(2000);
  });
});

// Custom command for checking accessibility
Cypress.Commands.add('checkAccessibility', () => {
  cy.injectAxe();
  cy.checkA11y();
});

// Custom command for checking responsive design
Cypress.Commands.add('checkResponsive', () => {
  const viewports = [
    { width: 375, height: 667, name: 'mobile' },
    { width: 768, height: 1024, name: 'tablet' },
    { width: 1920, height: 1080, name: 'desktop' }
  ];
  
  viewports.forEach(viewport => {
    cy.viewport(viewport.width, viewport.height);
    cy.get('body').should('be.visible');
  });
});

// Custom command for checking API responses
Cypress.Commands.add('checkApiResponse', (method: string, url: string, expectedStatus: number = 200) => {
  cy.intercept(method, url).as('apiCall');
  cy.wait('@apiCall').its('response.statusCode').should('eq', expectedStatus);
});

// Custom command for checking localStorage
Cypress.Commands.add('checkLocalStorage', (key: string, expectedValue?: any) => {
  cy.window().then((win) => {
    const value = win.localStorage.getItem(key);
    if (expectedValue) {
      expect(value).to.equal(expectedValue);
    } else {
      expect(value).to.not.be.null;
    }
  });
});

// Custom command for checking sessionStorage
Cypress.Commands.add('checkSessionStorage', (key: string, expectedValue?: any) => {
  cy.window().then((win) => {
    const value = win.sessionStorage.getItem(key);
    if (expectedValue) {
      expect(value).to.equal(expectedValue);
    } else {
      expect(value).to.not.be.null;
    }
  });
});

// Custom command for checking cookies
Cypress.Commands.add('checkCookie', (name: string, expectedValue?: any) => {
  cy.getCookie(name).then((cookie) => {
    if (expectedValue) {
      expect(cookie?.value).to.equal(expectedValue);
    } else {
      expect(cookie).to.not.be.null;
    }
  });
});

// Custom command for waiting for loading states
Cypress.Commands.add('waitForLoading', (selector: string) => {
  cy.get(selector).should('be.visible');
  cy.get(selector).should('not.exist');
});

// Custom command for checking error handling
Cypress.Commands.add('checkErrorHandling', (action: () => void, expectedError: string) => {
  cy.on('window:alert', (text) => {
    expect(text).to.include(expectedError);
  });
  
  action();
});

// Type definitions for custom commands
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      logout(): Chainable<void>;
      createJobApplication(jobId: string, applicationData: any): Chainable<void>;
      searchJobs(query: string, filters?: any): Chainable<void>;
      saveJobToFavorites(jobId: string): Chainable<void>;
      checkApplicationStatus(applicationId: string): Chainable<void>;
      updateProfile(profileData: any): Chainable<void>;
      uploadResume(fileName: string): Chainable<void>;
      checkPagePerformance(): Chainable<void>;
      checkAccessibility(): Chainable<void>;
      checkResponsive(): Chainable<void>;
      checkApiResponse(method: string, url: string, expectedStatus?: number): Chainable<void>;
      checkLocalStorage(key: string, expectedValue?: any): Chainable<void>;
      checkSessionStorage(key: string, expectedValue?: any): Chainable<void>;
      checkCookie(name: string, expectedValue?: any): Chainable<void>;
      waitForLoading(selector: string): Chainable<void>;
      checkErrorHandling(action: () => void, expectedError: string): Chainable<void>;
    }
  }
}