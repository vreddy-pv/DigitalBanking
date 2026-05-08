// ============================================================================
// Accounts Management End-to-End Tests
// ============================================================================

describe('Accounts Management', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
  };

  beforeEach(() => {
    cy.login(testUser.email, testUser.password);
    cy.navigateToAccounts();
  });

  describe('Accounts List', () => {
    it('should display accounts list', () => {
      cy.get('.accounts-container').should('be.visible');
      cy.get('.account-card').should('have.length.greaterThan', 0);
    });

    it('should display account details on card', () => {
      cy.get('.account-card').first().within(() => {
        cy.get('.account-number').should('be.visible');
        cy.get('.account-type').should('be.visible');
        cy.get('.account-balance').should('be.visible');
      });
    });

    it('should display account balance with currency', () => {
      cy.get('.account-balance').first().should('contain', '₹');
    });

    it('should highlight primary account', () => {
      cy.get('.account-card.primary').should('be.visible');
    });
  });

  describe('Account Selection', () => {
    it('should select account on click', () => {
      cy.get('.account-card').first().click();
      cy.get('.account-card').first().should('have.class', 'selected');
    });

    it('should display account details in sidebar', () => {
      cy.get('.account-card').first().click();
      cy.get('.account-details-panel').should('be.visible');
      cy.get('.account-details-panel').should('contain', 'Account Details');
    });

    it('should show account holder information', () => {
      cy.get('.account-card').first().click();
      cy.get('.account-details-panel').within(() => {
        cy.get('.account-holder-name').should('be.visible');
        cy.get('.account-holder-email').should('be.visible');
      });
    });
  });

  describe('Account Actions', () => {
    it('should display action buttons', () => {
      cy.get('.account-card').first().click();
      cy.get('.action-button').should('have.length.greaterThan', 0);
    });

    it('should open deposit dialog', () => {
      cy.get('.account-card').first().click();
      cy.get('button[aria-label="Deposit"]').click();
      cy.get('.deposit-dialog').should('be.visible');
    });

    it('should open withdrawal dialog', () => {
      cy.get('.account-card').first().click();
      cy.get('button[aria-label="Withdraw"]').click();
      cy.get('.withdrawal-dialog').should('be.visible');
    });

    it('should open transfer dialog', () => {
      cy.get('.account-card').first().click();
      cy.get('button[aria-label="Transfer"]').click();
      cy.get('.transfer-dialog').should('be.visible');
    });
  });

  describe('Account Filtering', () => {
    it('should filter accounts by type', () => {
      cy.get('.filter-dropdown').select('SAVINGS');
      cy.get('.account-card').each(($card) => {
        cy.wrap($card).should('contain', 'Savings');
      });
    });

    it('should search accounts by name', () => {
      cy.get('.search-input').type('Primary');
      cy.get('.account-card').should('contain', 'Primary');
    });

    it('should show no results message', () => {
      cy.get('.search-input').type('NonExistent');
      cy.get('.no-results-message').should('be.visible');
    });
  });

  describe('Account Status', () => {
    it('should display account status badge', () => {
      cy.get('.account-card').within(() => {
        cy.get('.status-badge').should('be.visible');
      });
    });

    it('should show active status for valid accounts', () => {
      cy.get('.account-card').first().within(() => {
        cy.get('.status-badge').should('contain', 'Active');
      });
    });

    it('should disable actions for frozen accounts', () => {
      cy.get('.account-card').contains('Frozen').closest('.account-card').click();
      cy.get('button[aria-label="Deposit"]').should('be.disabled');
      cy.get('button[aria-label="Withdraw"]').should('be.disabled');
    });
  });

  describe('Account Details View', () => {
    it('should display recent transactions', () => {
      cy.get('.account-card').first().click();
      cy.get('.recent-transactions').should('be.visible');
      cy.get('.transaction-item').should('have.length.greaterThan', 0);
    });

    it('should display account statements link', () => {
      cy.get('.account-card').first().click();
      cy.get('a[href*="statements"]').should('be.visible');
    });

    it('should display account settings link', () => {
      cy.get('.account-card').first().click();
      cy.get('a[href*="account-settings"]').should('be.visible');
    });
  });

  describe('Responsive Accounts View', () => {
    it('should stack cards vertically on mobile', () => {
      cy.viewport('iphone-x');
      cy.get('.accounts-container').should('have.css', 'flex-direction', 'column');
    });

    it('should show grid layout on desktop', () => {
      cy.viewport(1280, 800);
      cy.get('.accounts-container').should('have.css', 'display', 'grid');
    });
  });

  describe('Accessibility - Accounts', () => {
    it('should have proper ARIA labels on account cards', () => {
      cy.get('.account-card').first().should('have.attr', 'aria-label');
    });

    it('should have keyboard accessible account selection', () => {
      cy.get('.account-card').first().focus();
      cy.focused().should('have.class', 'account-card');
      cy.get('.account-card').first().type('{enter}');
      cy.get('.account-details-panel').should('be.visible');
    });

    it('should have proper heading hierarchy in account details', () => {
      cy.get('.account-card').first().click();
      cy.get('.account-details-panel h2').should('exist');
      cy.get('.account-details-panel h3').should('exist');
    });
  });
});
