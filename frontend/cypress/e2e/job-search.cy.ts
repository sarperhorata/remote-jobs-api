describe('Job Search E2E Tests', () => {
  beforeEach(() => {
    // Visit homepage before each test
    cy.visit('/');
    
    // Wait for the page to load
    cy.get('[data-testid="hero-section"]', { timeout: 10000 }).should('be.visible');
  });

  describe('Homepage', () => {
    it('displays the main hero section', () => {
      cy.get('h1').should('contain', 'Uzaktan Çalışma Hayallerini Gerçeğe Dönüştür');
      cy.get('.hero-section').should('be.visible');
    });

    it('shows job statistics', () => {
      cy.get('[data-testid="job-stats"]').should('be.visible');
      cy.get('[data-testid="total-jobs"]').should('contain.text', '38,');
      cy.get('[data-testid="active-jobs"]').should('be.visible');
      cy.get('[data-testid="companies"]').should('be.visible');
      cy.get('[data-testid="remote-jobs"]').should('be.visible');
    });

    it('has functional search form', () => {
      // Check if search form exists
      cy.get('[data-testid="job-search-form"]').should('be.visible');
      
      // Check if autocomplete is working
      cy.get('[data-testid="job-autocomplete"]').type('developer');
      cy.get('[data-testid="autocomplete-dropdown"]').should('be.visible');
      
      // Check location input
      cy.get('[data-testid="location-input"]').type('Istanbul');
      
      // Submit search
      cy.get('[data-testid="search-button"]').click();
      
      // Should navigate to search results
      cy.url().should('include', '/jobs');
    });

    it('displays top positions', () => {
      cy.get('[data-testid="top-positions"]').should('be.visible');
      cy.get('[data-testid="position-card"]').should('have.length.at.least', 3);
      
      // Click on a position
      cy.get('[data-testid="position-card"]').first().click();
      cy.url().should('include', '/jobs');
    });

    it('shows features section', () => {
      cy.get('[data-testid="features-section"]').should('be.visible');
      cy.get('[data-testid="feature-card"]').should('have.length', 4);
    });

    it('has working newsletter signup', () => {
      cy.get('[data-testid="newsletter-form"]').should('be.visible');
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="subscribe-button"]').click();
      
      // Should show success message
      cy.get('[data-testid="success-message"]').should('be.visible');
    });
  });

  describe('Job Search Results', () => {
    beforeEach(() => {
      // Navigate to job search page
      cy.visit('/jobs?q=developer');
      cy.get('[data-testid="job-results"]', { timeout: 10000 }).should('be.visible');
    });

    it('displays search results', () => {
      cy.get('[data-testid="job-card"]').should('have.length.at.least', 1);
      cy.get('[data-testid="results-count"]').should('be.visible');
    });

    it('has working filters', () => {
      // Test location filter
      cy.get('[data-testid="location-filter"]').click();
      cy.get('[data-testid="filter-option"]').contains('Remote').click();
      cy.get('[data-testid="apply-filters"]').click();
      
      // Check if results updated
      cy.url().should('include', 'location=Remote');
      
      // Test job type filter
      cy.get('[data-testid="job-type-filter"]').click();
      cy.get('[data-testid="filter-option"]').contains('Full-time').click();
      cy.get('[data-testid="apply-filters"]').click();
      
      cy.url().should('include', 'job_type=Full-time');
    });

    it('has working pagination', () => {
      // Check if pagination exists (if there are enough results)
      cy.get('body').then(($body) => {
        if ($body.find('[data-testid="pagination"]').length > 0) {
          cy.get('[data-testid="next-page"]').click();
          cy.url().should('include', 'page=2');
          
          cy.get('[data-testid="prev-page"]').click();
          cy.url().should('include', 'page=1');
        }
      });
    });

    it('allows job application', () => {
      cy.get('[data-testid="job-card"]').first().within(() => {
        cy.get('[data-testid="apply-button"]').click();
      });
      
      // Should open application modal or navigate to external site
      cy.get('[data-testid="application-modal"]').should('be.visible');
    });

    it('allows saving jobs', () => {
      cy.get('[data-testid="job-card"]').first().within(() => {
        cy.get('[data-testid="save-button"]').click();
      });
      
      // Should show saved state
      cy.get('[data-testid="save-button"]').should('have.class', 'saved');
    });

    it('shows job details modal', () => {
      cy.get('[data-testid="job-card"]').first().click();
      cy.get('[data-testid="job-modal"]').should('be.visible');
      
      // Check modal content
      cy.get('[data-testid="job-title"]').should('be.visible');
      cy.get('[data-testid="job-description"]').should('be.visible');
      cy.get('[data-testid="job-requirements"]').should('be.visible');
      
      // Close modal
      cy.get('[data-testid="close-modal"]').click();
      cy.get('[data-testid="job-modal"]').should('not.exist');
    });
  });

  describe('Search Functionality', () => {
    it('performs basic search', () => {
      cy.get('[data-testid="job-autocomplete"]').type('React Developer{enter}');
      cy.url().should('include', 'q=React%20Developer');
      
      // Should show relevant results
      cy.get('[data-testid="job-card"]').each(($card) => {
        cy.wrap($card).should('contain.text', 'React');
      });
    });

    it('handles empty search gracefully', () => {
      cy.get('[data-testid="search-button"]').click();
      cy.url().should('include', '/jobs');
      
      // Should show all jobs or appropriate message
      cy.get('[data-testid="job-results"]').should('be.visible');
    });

    it('shows no results message when appropriate', () => {
      cy.visit('/jobs?q=nonexistentjobtype12345');
      
      cy.get('[data-testid="no-results"]').should('be.visible');
      cy.get('[data-testid="no-results"]').should('contain', 'Aradığınız kriterlere uygun iş bulunamadı');
    });

    it('has working autocomplete suggestions', () => {
      cy.get('[data-testid="job-autocomplete"]').type('dev');
      cy.get('[data-testid="autocomplete-dropdown"]').should('be.visible');
      cy.get('[data-testid="autocomplete-option"]').should('have.length.at.least', 1);
      
      // Select first suggestion
      cy.get('[data-testid="autocomplete-option"]').first().click();
      cy.get('[data-testid="job-autocomplete"]').should('have.value');
    });
  });

  describe('User Authentication', () => {
    it('opens auth modal when clicking sign up', () => {
      cy.get('[data-testid="auth-modal-trigger"]').click();
      cy.get('[data-testid="auth-modal"]').should('be.visible');
    });

    it('can switch between login and register', () => {
      cy.get('[data-testid="auth-modal-trigger"]').click();
      cy.get('[data-testid="auth-modal"]').should('be.visible');
      
      // Should be on login by default
      cy.get('[data-testid="login-form"]').should('be.visible');
      
      // Switch to register
      cy.get('[data-testid="switch-to-register"]').click();
      cy.get('[data-testid="register-form"]').should('be.visible');
      
      // Switch back to login
      cy.get('[data-testid="switch-to-login"]').click();
      cy.get('[data-testid="login-form"]').should('be.visible');
    });
  });

  describe('Responsive Design', () => {
    it('works on mobile viewport', () => {
      cy.viewport('iphone-6');
      
      // Check mobile navigation
      cy.get('[data-testid="mobile-menu-button"]').should('be.visible');
      cy.get('[data-testid="mobile-menu-button"]').click();
      cy.get('[data-testid="mobile-menu"]').should('be.visible');
      
      // Check search form on mobile
      cy.get('[data-testid="job-search-form"]').should('be.visible');
    });

    it('works on tablet viewport', () => {
      cy.viewport('ipad-2');
      
      // Check layout on tablet
      cy.get('[data-testid="hero-section"]').should('be.visible');
      cy.get('[data-testid="job-stats"]').should('be.visible');
    });
  });

  describe('Performance', () => {
    it('loads homepage within acceptable time', () => {
      const start = Date.now();
      cy.visit('/');
      cy.get('[data-testid="hero-section"]').should('be.visible');
      
      cy.then(() => {
        const loadTime = Date.now() - start;
        expect(loadTime).to.be.lessThan(5000); // 5 seconds
      });
    });

    it('handles search without significant delay', () => {
      cy.get('[data-testid="job-autocomplete"]').type('developer');
      
      const start = Date.now();
      cy.get('[data-testid="search-button"]').click();
      cy.get('[data-testid="job-results"]').should('be.visible');
      
      cy.then(() => {
        const searchTime = Date.now() - start;
        expect(searchTime).to.be.lessThan(3000); // 3 seconds
      });
    });
  });

  describe('Accessibility', () => {
    it('has proper heading structure', () => {
      cy.get('h1').should('exist');
      cy.get('h2').should('exist');
    });

    it('has accessible form labels', () => {
      cy.get('[data-testid="job-autocomplete"]').should('have.attr', 'aria-label');
      cy.get('[data-testid="location-input"]').should('have.attr', 'aria-label');
    });

    it('supports keyboard navigation', () => {
      // Tab through main elements
      cy.get('body').tab();
      cy.focused().should('be.visible');
      
      // Enter on search button
      cy.get('[data-testid="search-button"]').focus().type('{enter}');
      cy.url().should('include', '/jobs');
    });

    it('has proper ARIA attributes', () => {
      cy.get('[data-testid="job-stats"]').should('have.attr', 'role');
      cy.get('[data-testid="top-positions"]').should('have.attr', 'aria-label');
    });
  });

  describe('Error Handling', () => {
    it('handles network errors gracefully', () => {
      // Intercept API calls and simulate error
      cy.intercept('GET', '/api/v1/jobs/search*', { statusCode: 500 }).as('getJobsError');
      
      cy.visit('/jobs?q=developer');
      cy.wait('@getJobsError');
      
      // Should show error message
      cy.get('[data-testid="error-message"]').should('be.visible');
      cy.get('[data-testid="retry-button"]').should('be.visible');
    });

    it('handles slow API responses', () => {
      // Intercept and delay API response
      cy.intercept('GET', '/api/v1/jobs/search*', (req) => {
        req.reply((res) => {
          res.delay(2000); // 2 second delay
          res.send({ fixture: 'jobs.json' });
        });
      }).as('getJobsSlow');
      
      cy.visit('/jobs?q=developer');
      
      // Should show loading state
      cy.get('[data-testid="loading-spinner"]').should('be.visible');
      
      cy.wait('@getJobsSlow');
      cy.get('[data-testid="job-results"]').should('be.visible');
      cy.get('[data-testid="loading-spinner"]').should('not.exist');
    });
  });
}); 