// ============================================================================
// Cypress E2E Support File
// ============================================================================

// Import commands and assertions
import './commands';

// Disable uncaught exception handling for development
Cypress.on('uncaught:exception', (err, runnable) => {
  // Return false to prevent Cypress from failing the test
  return false;
});

// Set viewport size
beforeEach(() => {
  cy.viewport(1280, 800);
});

// Global test timeout
Cypress.config('defaultCommandTimeout', 10000);
