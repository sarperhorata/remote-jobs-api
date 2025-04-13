describe('Job Detail Page', () => {
  beforeEach(() => {
    // Mock API responses
    cy.intercept('GET', '/api/jobs/*', { fixture: 'job.json' }).as('getJob')
    cy.intercept('GET', '/api/jobs/*/similar', { fixture: 'similarJobs.json' }).as('getSimilarJobs')
  })

  it('displays job details correctly', () => {
    cy.visit('/jobs/123')
    cy.wait('@getJob')

    // Check main content
    cy.get('h1').should('contain', 'Senior Frontend Developer')
    cy.get('[data-testid="company-name"]').should('contain', 'Tech Corp')
    cy.get('[data-testid="job-location"]').should('contain', 'Remote')
    cy.get('[data-testid="job-type"]').should('contain', 'Full-time')

    // Check job description sections
    cy.get('[data-testid="job-description"]').should('exist')
    cy.get('[data-testid="responsibilities"]').should('exist')
    cy.get('[data-testid="requirements"]').should('exist')
    cy.get('[data-testid="benefits"]').should('exist')

    // Check skills
    cy.get('[data-testid="skills"]').within(() => {
      cy.get('[data-testid="skill-chip"]').should('have.length.at.least', 1)
    })
  })

  it('handles save job functionality', () => {
    cy.visit('/jobs/123')
    cy.wait('@getJob')

    // Click save button
    cy.get('[data-testid="save-button"]').click()
    cy.get('[data-testid="save-button"]').should('have.attr', 'aria-pressed', 'true')

    // Click again to unsave
    cy.get('[data-testid="save-button"]').click()
    cy.get('[data-testid="save-button"]').should('have.attr', 'aria-pressed', 'false')
  })

  it('displays similar jobs', () => {
    cy.visit('/jobs/123')
    cy.wait(['@getJob', '@getSimilarJobs'])

    cy.get('[data-testid="similar-jobs"]').within(() => {
      cy.get('[data-testid="similar-job-card"]').should('have.length.at.least', 1)
    })
  })

  it('handles share functionality', () => {
    cy.visit('/jobs/123')
    cy.wait('@getJob')

    // Mock navigator.share
    cy.window().then((win) => {
      cy.stub(win.navigator, 'share').resolves()
    })

    cy.get('[data-testid="share-button"]').click()
    cy.window().its('navigator.share').should('be.called')
  })

  it('handles error states', () => {
    // Mock failed API response
    cy.intercept('GET', '/api/jobs/*', {
      statusCode: 500,
      body: 'Server error'
    }).as('getJobError')

    cy.visit('/jobs/123')
    cy.wait('@getJobError')

    cy.get('[data-testid="error-message"]')
      .should('exist')
      .and('contain', 'Error loading job details')
  })

  it('shows loading state', () => {
    cy.intercept('GET', '/api/jobs/*', (req) => {
      req.delay(1000)
      req.reply({ fixture: 'job.json' })
    }).as('getJobDelayed')

    cy.visit('/jobs/123')
    cy.get('[data-testid="loading-skeleton"]').should('exist')
    cy.wait('@getJobDelayed')
    cy.get('[data-testid="loading-skeleton"]').should('not.exist')
  })
}) 