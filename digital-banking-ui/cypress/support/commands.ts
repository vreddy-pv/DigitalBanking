// ============================================================================
// Custom Cypress Commands
// ============================================================================

/**
 * Login command - Navigate to login and authenticate
 */
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login');
  cy.get('input[formControlName="email"]').type(email);
  cy.get('input[formControlName="password"]').type(password);
  cy.get('button[type="submit"]').click();
  cy.url().should('include', '/app');
});

/**
 * Logout command
 */
Cypress.Commands.add('logout', () => {
  cy.get('.logout-btn').click();
  cy.url().should('include', '/login');
});

/**
 * Navigate to dashboard
 */
Cypress.Commands.add('navigateToDashboard', () => {
  cy.visit('/app/dashboard');
  cy.url().should('include', '/app/dashboard');
});

/**
 * Navigate to accounts section
 */
Cypress.Commands.add('navigateToAccounts', () => {
  cy.get('a[routerLink="/app/accounts"]').click();
  cy.url().should('include', '/app/accounts');
});

/**
 * Navigate to transactions section
 */
Cypress.Commands.add('navigateToTransactions', () => {
  cy.get('a[routerLink="/app/transactions"]').click();
  cy.url().should('include', '/app/transactions');
});

/**
 * Navigate to transfers section
 */
Cypress.Commands.add('navigateToTransfers', () => {
  cy.get('a[routerLink="/app/transfers"]').click();
  cy.url().should('include', '/app/transfers');
});

/**
 * Navigate to notifications section
 */
Cypress.Commands.add('navigateToNotifications', () => {
  cy.get('a[routerLink="/app/notifications"]').click();
  cy.url().should('include', '/app/notifications');
});

/**
 * Navigate to settings section
 */
Cypress.Commands.add('navigateToSettings', () => {
  cy.get('a[routerLink="/app/settings"]').click();
  cy.url().should('include', '/app/settings');
});

/**
 * Toggle theme (dark/light mode)
 */
Cypress.Commands.add('toggleTheme', () => {
  cy.get('.icon-btn').contains(/🌙|☀️/).click();
});

/**
 * Wait for page load
 */
Cypress.Commands.add('waitForPageLoad', () => {
  cy.get('.content').should('be.visible');
});

/**
 * Check if application is healthy
 */
Cypress.Commands.add('checkApplicationHealth', () => {
  cy.request('GET', 'http://api-gateway:8000/health').then((response) => {
    expect(response.status).to.equal(200);
  });
});

/**
 * Create test account
 */
Cypress.Commands.add('createTestAccount', (accountData: any) => {
  cy.request('POST', 'http://api-gateway:8000/api/accounts', accountData).then((response) => {
    expect(response.status).to.equal(201);
    return response.body;
  });
});

/**
 * Create test transaction
 */
Cypress.Commands.add('createTestTransaction', (transactionData: any) => {
  cy.request('POST', 'http://api-gateway:8000/api/transactions', transactionData).then((response) => {
    expect(response.status).to.equal(201);
    return response.body;
  });
});

/**
 * Get authentication token
 */
Cypress.Commands.add('getAuthToken', (email: string, password: string) => {
  cy.request('POST', 'http://api-gateway:8000/api/auth/login', {
    email,
    password,
  }).then((response) => {
    expect(response.status).to.equal(200);
    return response.body.token;
  });
});

/**
 * Set authentication header for API requests
 */
Cypress.Commands.add('setAuthHeader', (token: string) => {
  cy.request({
    method: 'GET',
    url: 'http://api-gateway:8000/api/accounts',
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
});

// ============================================================================
// Type Definitions for Custom Commands
// ============================================================================
declare global {
  namespace Cypress {
    interface Chainable {
      login(email: string, password: string): Chainable<void>;
      logout(): Chainable<void>;
      navigateToDashboard(): Chainable<void>;
      navigateToAccounts(): Chainable<void>;
      navigateToTransactions(): Chainable<void>;
      navigateToTransfers(): Chainable<void>;
      navigateToNotifications(): Chainable<void>;
      navigateToSettings(): Chainable<void>;
      toggleTheme(): Chainable<void>;
      waitForPageLoad(): Chainable<void>;
      checkApplicationHealth(): Chainable<void>;
      createTestAccount(accountData: any): Chainable<any>;
      createTestTransaction(transactionData: any): Chainable<any>;
      getAuthToken(email: string, password: string): Chainable<string>;
      setAuthHeader(token: string): Chainable<void>;
    }
  }
}

export {};
