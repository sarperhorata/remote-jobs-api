describe('User Authentication E2E Tests', () => {
  beforeEach(() => {
    cy.visit('/');
  });

  describe('Login Flow', () => {
    it('should display login modal when login button is clicked', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="auth-modal"]').should('be.visible');
      cy.get('[data-testid="login-form"]').should('be.visible');
    });

    it('should show validation errors for empty fields', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="login-submit"]').click();
      
      cy.get('[data-testid="email-error"]').should('be.visible');
      cy.get('[data-testid="password-error"]').should('be.visible');
    });

    it('should show validation error for invalid email', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="email-input"]').type('invalid-email');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-submit"]').click();
      
      cy.get('[data-testid="email-error"]').should('be.visible');
    });

    it('should successfully login with valid credentials', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="password-input"]').type('password123');
      cy.get('[data-testid="login-submit"]').click();
      
      // Should redirect to dashboard or show success
      cy.get('[data-testid="user-menu"]').should('be.visible');
      cy.get('[data-testid="auth-modal"]').should('not.exist');
    });

    it('should show error message for invalid credentials', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="email-input"]').type('wrong@example.com');
      cy.get('[data-testid="password-input"]').type('wrongpassword');
      cy.get('[data-testid="login-submit"]').click();
      
      cy.get('[data-testid="login-error"]').should('be.visible');
    });
  });

  describe('Registration Flow', () => {
    it('should switch to registration form', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="register-tab"]').click();
      cy.get('[data-testid="register-form"]').should('be.visible');
    });

    it('should validate registration form fields', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="register-tab"]').click();
      cy.get('[data-testid="register-submit"]').click();
      
      cy.get('[data-testid="name-error"]').should('be.visible');
      cy.get('[data-testid="email-error"]').should('be.visible');
      cy.get('[data-testid="password-error"]').should('be.visible');
    });

    it('should validate password strength', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="register-tab"]').click();
      cy.get('[data-testid="password-input"]').type('weak');
      
      cy.get('[data-testid="password-strength"]').should('contain', 'Weak');
    });

    it('should successfully register new user', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="register-tab"]').click();
      
      cy.get('[data-testid="name-input"]').type('Test User');
      cy.get('[data-testid="email-input"]').type('newuser@example.com');
      cy.get('[data-testid="password-input"]').type('StrongPassword123!');
      cy.get('[data-testid="register-submit"]').click();
      
      // Should show success message or redirect
      cy.get('[data-testid="registration-success"]').should('be.visible');
    });
  });

  describe('Password Reset Flow', () => {
    it('should show forgot password form', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="forgot-password"]').click();
      cy.get('[data-testid="forgot-password-form"]').should('be.visible');
    });

    it('should send password reset email', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="forgot-password"]').click();
      cy.get('[data-testid="email-input"]').type('test@example.com');
      cy.get('[data-testid="reset-submit"]').click();
      
      cy.get('[data-testid="reset-success"]').should('be.visible');
    });
  });

  describe('Social Login', () => {
    it('should show social login options', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="google-login"]').should('be.visible');
      cy.get('[data-testid="linkedin-login"]').should('be.visible');
    });

    it('should redirect to Google OAuth', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('[data-testid="google-login"]').click();
      
      // Should redirect to Google OAuth
      cy.url().should('include', 'accounts.google.com');
    });
  });

  describe('Logout Flow', () => {
    beforeEach(() => {
      // Login first
      cy.login('test@example.com', 'password123');
    });

    it('should logout successfully', () => {
      cy.get('[data-testid="user-menu"]').click();
      cy.get('[data-testid="logout-button"]').click();
      
      cy.get('[data-testid="login-button"]').should('be.visible');
      cy.get('[data-testid="user-menu"]').should('not.exist');
    });
  });

  describe('Protected Routes', () => {
    it('should redirect to login when accessing protected route', () => {
      cy.visit('/profile');
      cy.url().should('include', '/login');
    });

    it('should access protected route after login', () => {
      cy.login('test@example.com', 'password123');
      cy.visit('/profile');
      cy.get('[data-testid="profile-page"]').should('be.visible');
    });
  });
});