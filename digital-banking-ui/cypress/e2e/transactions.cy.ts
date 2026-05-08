// ============================================================================
// Transactions End-to-End Tests
// ============================================================================

describe('Transactions Management', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
  };

  beforeEach(() => {
    cy.login(testUser.email, testUser.password);
    cy.navigateToTransactions();
  });

  describe('Transactions List', () => {
    it('should display transactions list', () => {
      cy.get('.transactions-container').should('be.visible');
      cy.get('.transaction-item').should('have.length.greaterThan', 0);
    });

    it('should display transaction details', () => {
      cy.get('.transaction-item').first().within(() => {
        cy.get('.transaction-type').should('be.visible');
        cy.get('.transaction-amount').should('be.visible');
        cy.get('.transaction-date').should('be.visible');
        cy.get('.transaction-status').should('be.visible');
      });
    });

    it('should show debit transactions with red color', () => {
      cy.get('.transaction-item.debit').first().within(() => {
        cy.get('.transaction-amount').should('have.css', 'color').and('match', /rgb.*red|rgb\(229.*52|rgb\(231.*76/);
      });
    });

    it('should show credit transactions with green color', () => {
      cy.get('.transaction-item.credit').first().within(() => {
        cy.get('.transaction-amount').should('have.css', 'color').and('match', /rgb.*green|rgb\(39.*174|rgb\(26.*206/);
      });
    });
  });

  describe('Transaction Filtering', () => {
    it('should filter by transaction type', () => {
      cy.get('.filter-type').select('DEPOSIT');
      cy.get('.transaction-item').each(($item) => {
        cy.wrap($item).should('contain', 'Deposit');
      });
    });

    it('should filter by date range', () => {
      cy.get('.date-from-input').type('2026-01-01');
      cy.get('.date-to-input').type('2026-05-08');
      cy.get('.apply-filter-btn').click();
      cy.get('.transaction-item').should('have.length.greaterThan', 0);
    });

    it('should filter by amount range', () => {
      cy.get('.amount-min-input').type('1000');
      cy.get('.amount-max-input').type('10000');
      cy.get('.apply-filter-btn').click();
      cy.get('.transaction-item').should('have.length.greaterThan', 0);
    });

    it('should search transactions by description', () => {
      cy.get('.search-input').type('salary');
      cy.get('.transaction-item').should('contain', 'salary');
    });

    it('should show no results message when filter returns empty', () => {
      cy.get('.filter-type').select('DEPOSIT');
      cy.get('.amount-min-input').type('1000000');
      cy.get('.apply-filter-btn').click();
      cy.get('.no-results-message').should('be.visible');
    });
  });

  describe('Transaction Details', () => {
    it('should expand transaction on click', () => {
      cy.get('.transaction-item').first().click();
      cy.get('.transaction-details').should('be.visible');
    });

    it('should display transaction ID', () => {
      cy.get('.transaction-item').first().click();
      cy.get('.transaction-details').should('contain', 'Transaction ID');
    });

    it('should display timestamp', () => {
      cy.get('.transaction-item').first().click();
      cy.get('.transaction-details').should('contain', 'Date & Time');
    });

    it('should display transaction description', () => {
      cy.get('.transaction-item').first().click();
      cy.get('.transaction-details').should('contain', 'Description');
    });

    it('should display account details for transfers', () => {
      cy.get('.transaction-item').contains('Transfer').click();
      cy.get('.transaction-details').should('contain', 'From Account');
      cy.get('.transaction-details').should('contain', 'To Account');
    });

    it('should display reference number if available', () => {
      cy.get('.transaction-item').first().click();
      cy.get('.reference-number').should('be.visible');
    });
  });

  describe('Transaction Status', () => {
    it('should display transaction status badge', () => {
      cy.get('.transaction-item').within(() => {
        cy.get('.status-badge').should('be.visible');
      });
    });

    it('should show pending status with yellow color', () => {
      cy.get('.transaction-item').contains('Pending').within(() => {
        cy.get('.status-badge').should('have.class', 'status-pending');
      });
    });

    it('should show completed status with green color', () => {
      cy.get('.transaction-item').contains('Completed').within(() => {
        cy.get('.status-badge').should('have.class', 'status-completed');
      });
    });

    it('should show failed status with red color', () => {
      cy.get('.transaction-item').contains('Failed').within(() => {
        cy.get('.status-badge').should('have.class', 'status-failed');
      });
    });
  });

  describe('Transaction Download', () => {
    it('should display download button for completed transactions', () => {
      cy.get('.transaction-item').contains('Completed').click();
      cy.get('.download-receipt-btn').should('be.visible');
    });

    it('should download receipt on button click', () => {
      cy.get('.transaction-item').contains('Completed').click();
      cy.get('.download-receipt-btn').click();
      cy.readFile('cypress/downloads/receipt-*.pdf').should('exist');
    });

    it('should display print button', () => {
      cy.get('.transaction-item').first().click();
      cy.get('.print-btn').should('be.visible');
    });
  });

  describe('Transaction Pagination', () => {
    it('should display pagination controls', () => {
      cy.get('.pagination').should('be.visible');
    });

    it('should navigate to next page', () => {
      cy.get('.pagination-next').click();
      cy.get('.transaction-item').should('have.length.greaterThan', 0);
    });

    it('should navigate to previous page', () => {
      cy.get('.pagination-next').click();
      cy.get('.pagination-prev').click();
      cy.get('.transaction-item').should('have.length.greaterThan', 0);
    });

    it('should change items per page', () => {
      cy.get('.items-per-page-select').select('50');
      cy.get('.transaction-item').should('have.length.lessThan', 51);
    });
  });

  describe('Sorting', () => {
    it('should sort by date ascending', () => {
      cy.get('.sort-by-select').select('DATE_ASC');
      cy.get('.transaction-date').first().should('contain', '2026');
    });

    it('should sort by date descending', () => {
      cy.get('.sort-by-select').select('DATE_DESC');
      cy.get('.transaction-date').first().should('contain', '2026');
    });

    it('should sort by amount ascending', () => {
      cy.get('.sort-by-select').select('AMOUNT_ASC');
      cy.get('.transaction-item').first().should('be.visible');
    });

    it('should sort by amount descending', () => {
      cy.get('.sort-by-select').select('AMOUNT_DESC');
      cy.get('.transaction-item').first().should('be.visible');
    });
  });

  describe('Export Transactions', () => {
    it('should display export button', () => {
      cy.get('.export-btn').should('be.visible');
    });

    it('should export to CSV', () => {
      cy.get('.export-btn').click();
      cy.get('.export-csv-option').click();
      cy.readFile('cypress/downloads/transactions-*.csv').should('exist');
    });

    it('should export to PDF', () => {
      cy.get('.export-btn').click();
      cy.get('.export-pdf-option').click();
      cy.readFile('cypress/downloads/transactions-*.pdf').should('exist');
    });
  });

  describe('Responsive Transactions View', () => {
    it('should collapse details on mobile', () => {
      cy.viewport('iphone-x');
      cy.get('.transaction-item').first().click();
      cy.get('.transaction-details').should('not.be.visible');
    });

    it('should show full details on desktop', () => {
      cy.viewport(1280, 800);
      cy.get('.transaction-item').first().click();
      cy.get('.transaction-details').should('be.visible');
    });

    it('should stack filter controls vertically on mobile', () => {
      cy.viewport('iphone-x');
      cy.get('.filter-controls').should('have.css', 'flex-direction', 'column');
    });
  });

  describe('Accessibility - Transactions', () => {
    it('should have proper ARIA labels on transaction items', () => {
      cy.get('.transaction-item').first().should('have.attr', 'aria-label');
    });

    it('should have keyboard accessible transaction expansion', () => {
      cy.get('.transaction-item').first().focus();
      cy.focused().should('have.class', 'transaction-item');
      cy.get('.transaction-item').first().type('{enter}');
      cy.get('.transaction-details').should('be.visible');
    });

    it('should have proper heading hierarchy', () => {
      cy.get('h1').should('exist');
      cy.get('h2').should('exist');
    });
  });
});
