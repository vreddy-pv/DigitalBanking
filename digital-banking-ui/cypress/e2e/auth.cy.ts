// ============================================================================
// Authentication End-to-End Tests
// ============================================================================

describe('Authentication Flows', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
    fullName: 'Test User',
  };

  beforeEach(() => {
    cy.visit('/');
  });

  describe('Login Page', () => {
    it('should display login page with VRGT branding', () => {
      cy.visit('/login');
      cy.get('h1').should('contain', 'Digital Banking');
      cy.get('.login-container').should('be.visible');
      cy.get('input[formControlName="email"]').should('be.visible');
      cy.get('input[formControlName="password"]').should('be.visible');
      cy.get('button[type="submit"]').should('be.visible');
    });

    it('should display login form with all required fields', () => {
      cy.visit('/login');
      cy.get('input[formControlName="email"]').should('have.attr', 'placeholder');
      cy.get('input[formControlName="password"]').should('have.attr', 'placeholder');
      cy.get('input[formControlName="rememberMe"]').should('exist');
    });

    it('should validate email field', () => {
      cy.visit('/login');
      cy.get('input[formControlName="email"]').type('invalid-email');
      cy.get('button[type="submit"]').should('be.disabled');
      cy.get('.error-text').should('contain', 'valid email');
    });

    it('should validate password field', () => {
      cy.visit('/login');
      cy.get('input[formControlName="password"]').type('123');
      cy.get('button[type="submit"]').should('be.disabled');
      cy.get('.error-text').should('contain', 'at least 6 characters');
    });

    it('should toggle password visibility', () => {
      cy.visit('/login');
      const passwordInput = cy.get('input[formControlName="password"]');
      passwordInput.should('have.attr', 'type', 'password');

      cy.get('.password-toggle').click();
      passwordInput.should('have.attr', 'type', 'text');

      cy.get('.password-toggle').click();
      passwordInput.should('have.attr', 'type', 'password');
    });

    it('should display "Remember me" checkbox', () => {
      cy.visit('/login');
      cy.get('input[formControlName="rememberMe"]').should('exist');
      cy.get('label[for="rememberMe"]').should('contain', 'Remember me');
    });
  });

  describe('Login Functionality', () => {
    it('should successfully login with valid credentials', () => {
      cy.login(testUser.email, testUser.password);
      cy.url().should('include', '/app');
      cy.get('.sidebar').should('be.visible');
    });

    it('should display error message on failed login', () => {
      cy.visit('/login');
      cy.get('input[formControlName="email"]').type('wrong@example.com');
      cy.get('input[formControlName="password"]').type('wrongpassword');
      cy.get('button[type="submit"]').click();

      cy.get('.error-message').should('be.visible');
      cy.get('.error-message').should('contain', 'Login failed');
    });

    it('should display loading state while logging in', () => {
      cy.visit('/login');
      cy.get('input[formControlName="email"]').type(testUser.email);
      cy.get('input[formControlName="password"]').type(testUser.password);
      cy.get('button[type="submit"]').click();

      cy.get('.loading-spinner').should('be.visible');
    });

    it('should persist login token in localStorage', () => {
      cy.login(testUser.email, testUser.password);
      cy.window().then((win) => {
        const token = win.localStorage.getItem('auth_token');
        expect(token).to.exist;
      });
    });
  });

  describe('Logout Functionality', () => {
    it('should successfully logout', () => {
      cy.login(testUser.email, testUser.password);
      cy.logout();
      cy.url().should('include', '/login');
    });

    it('should clear authentication token on logout', () => {
      cy.login(testUser.email, testUser.password);
      cy.logout();
      cy.window().then((win) => {
        const token = win.localStorage.getItem('auth_token');
        expect(token).to.be.null;
      });
    });

    it('should redirect to login on unauthorized access', () => {
      cy.visit('/app/dashboard');
      cy.url().should('include', '/login');
    });
  });

  describe('Session Management', () => {
    it('should maintain session across page reload', () => {
      cy.login(testUser.email, testUser.password);
      cy.reload();
      cy.url().should('include', '/app');
      cy.get('.sidebar').should('be.visible');
    });

    it('should display user name in sidebar after login', () => {
      cy.login(testUser.email, testUser.password);
      cy.get('.user-name').should('contain', testUser.fullName);
    });

    it('should display user email in sidebar after login', () => {
      cy.login(testUser.email, testUser.password);
      cy.get('.user-email').should('contain', testUser.email);
    });
  });

  describe('Authentication Errors', () => {
    it('should handle network errors gracefully', () => {
      cy.visit('/login');
      cy.intercept('POST', '**/auth/login', { statusCode: 500 }).as('loginError');

      cy.get('input[formControlName="email"]').type(testUser.email);
      cy.get('input[formControlName="password"]').type(testUser.password);
      cy.get('button[type="submit"]').click();

      cy.wait('@loginError');
      cy.get('.error-message').should('be.visible');
    });

    it('should handle timeout errors', () => {
      cy.visit('/login');
      cy.intercept('POST', '**/auth/login', (req) => {
        req.destroy();
      }).as('loginTimeout');

      cy.get('input[formControlName="email"]').type(testUser.email);
      cy.get('input[formControlName="password"]').type(testUser.password);
      cy.get('button[type="submit"]').click();

      cy.wait('@loginTimeout', { timeout: 15000 }).then(() => {
        cy.get('.error-message').should('be.visible');
      });
    });
  });
});
