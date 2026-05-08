// ============================================================================
// Money Transfers End-to-End Tests
// ============================================================================

describe('Money Transfers', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
  };

  const transferData = {
    fromAccount: 'SA001234',
    toAccount: 'SA009999',
    amount: 5000,
    description: 'Test transfer',
  };

  beforeEach(() => {
    cy.login(testUser.email, testUser.password);
    cy.navigateToTransfers();
  });

  describe('Transfer Page', () => {
    it('should display transfer page with header', () => {
      cy.get('h1').should('contain', 'Money Transfer');
      cy.get('.transfer-container').should('be.visible');
    });

    it('should display quick transfer options', () => {
      cy.get('.quick-transfer-options').should('be.visible');
      cy.get('.quick-transfer-option').should('have.length.greaterThan', 0);
    });

    it('should display beneficiary list', () => {
      cy.get('.beneficiary-list').should('be.visible');
      cy.get('.beneficiary-item').should('have.length.greaterThan', 0);
    });

    it('should display new transfer form', () => {
      cy.get('.transfer-form').should('be.visible');
    });
  });

  describe('Transfer Form Validation', () => {
    it('should have from account dropdown', () => {
      cy.get('select[formControlName="fromAccount"]').should('be.visible');
      cy.get('select[formControlName="fromAccount"]').should('not.be.disabled');
    });

    it('should have to account field', () => {
      cy.get('input[formControlName="toAccount"]').should('be.visible');
    });

    it('should have amount field', () => {
      cy.get('input[formControlName="amount"]').should('be.visible');
      cy.get('input[formControlName="amount"]').should('have.attr', 'type', 'number');
    });

    it('should have description field', () => {
      cy.get('textarea[formControlName="description"]').should('be.visible');
    });

    it('should validate required fields', () => {
      cy.get('button[type="submit"]').should('be.disabled');
    });

    it('should validate amount greater than zero', () => {
      cy.get('input[formControlName="amount"]').type('0');
      cy.get('.error-text').should('contain', 'greater than 0');
    });

    it('should validate sufficient balance', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type('1000000');
      cy.get('.balance-check').should('contain', 'Insufficient balance');
    });

    it('should validate different from and to accounts', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.fromAccount);
      cy.get('.error-text').should('contain', 'cannot be the same');
    });
  });

  describe('Transfer Execution', () => {
    it('should successfully complete transfer', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('textarea[formControlName="description"]').type(transferData.description);
      cy.get('button[type="submit"]').click();

      cy.get('.success-message').should('be.visible');
      cy.get('.success-message').should('contain', 'Transfer completed successfully');
    });

    it('should display transfer confirmation dialog', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('textarea[formControlName="description"]').type(transferData.description);
      cy.get('button[type="submit"]').click();

      cy.get('.confirmation-dialog').should('be.visible');
      cy.get('.confirmation-dialog').should('contain', 'Confirm Transfer');
      cy.get('.confirmation-dialog').should('contain', transferData.amount);
    });

    it('should allow user to cancel transfer', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('button[type="submit"]').click();

      cy.get('.confirmation-dialog .cancel-btn').click();
      cy.get('.confirmation-dialog').should('not.be.visible');
      cy.get('.transfer-form').should('be.visible');
    });

    it('should confirm transfer on confirmation dialog', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('button[type="submit"]').click();

      cy.get('.confirmation-dialog .confirm-btn').click();
      cy.get('.success-message').should('be.visible');
    });

    it('should show loading state during transfer', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('button[type="submit"]').click();

      cy.get('.confirmation-dialog .confirm-btn').click();
      cy.get('.loading-spinner').should('be.visible');
    });

    it('should display transfer reference number', () => {
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('button[type="submit"]').click();

      cy.get('.confirmation-dialog .confirm-btn').click();
      cy.get('.success-message').should('contain', 'Reference Number');
    });
  });

  describe('Beneficiary Management', () => {
    it('should display add beneficiary button', () => {
      cy.get('.add-beneficiary-btn').should('be.visible');
    });

    it('should open add beneficiary dialog', () => {
      cy.get('.add-beneficiary-btn').click();
      cy.get('.add-beneficiary-dialog').should('be.visible');
    });

    it('should save new beneficiary', () => {
      cy.get('.add-beneficiary-btn').click();
      cy.get('input[placeholder="Beneficiary Account"]').type('SA005555');
      cy.get('input[placeholder="Beneficiary Name"]').type('John Doe');
      cy.get('button[type="submit"]').click();

      cy.get('.success-message').should('contain', 'Beneficiary added');
    });

    it('should display saved beneficiaries', () => {
      cy.get('.beneficiary-item').should('have.length.greaterThan', 0);
    });

    it('should use saved beneficiary for quick transfer', () => {
      cy.get('.beneficiary-item').first().click();
      cy.get('.quick-transfer-form').should('be.visible');
      cy.get('input[formControlName="toAccount"]').should('have.value', '@todo');
    });

    it('should delete beneficiary', () => {
      cy.get('.beneficiary-item').first().within(() => {
        cy.get('.delete-btn').click();
      });
      cy.get('.confirmation-dialog').should('be.visible');
      cy.get('.confirmation-dialog .confirm-btn').click();
      cy.get('.success-message').should('contain', 'Beneficiary deleted');
    });
  });

  describe('Scheduled Transfers', () => {
    it('should display schedule option', () => {
      cy.get('.schedule-transfer-option').should('be.visible');
    });

    it('should open scheduled transfer form', () => {
      cy.get('.schedule-transfer-option').click();
      cy.get('.scheduled-transfer-form').should('be.visible');
    });

    it('should select transfer frequency', () => {
      cy.get('.schedule-transfer-option').click();
      cy.get('select[formControlName="frequency"]').should('be.visible');
      cy.get('select[formControlName="frequency"]').select('MONTHLY');
    });

    it('should select transfer date', () => {
      cy.get('.schedule-transfer-option').click();
      cy.get('input[formControlName="startDate"]').should('be.visible');
      cy.get('input[formControlName="startDate"]').type('2026-06-08');
    });

    it('should set end date for recurring transfers', () => {
      cy.get('.schedule-transfer-option').click();
      cy.get('select[formControlName="frequency"]').select('MONTHLY');
      cy.get('input[formControlName="endDate"]').should('be.visible');
    });

    it('should schedule transfer successfully', () => {
      cy.get('.schedule-transfer-option').click();
      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('select[formControlName="frequency"]').select('MONTHLY');
      cy.get('input[formControlName="startDate"]').type('2026-06-08');
      cy.get('button[type="submit"]').click();

      cy.get('.success-message').should('contain', 'Scheduled successfully');
    });
  });

  describe('Transfer History', () => {
    it('should display transfer history tab', () => {
      cy.get('.history-tab').should('be.visible');
    });

    it('should show recent transfers in history', () => {
      cy.get('.history-tab').click();
      cy.get('.transfer-history-item').should('have.length.greaterThan', 0);
    });

    it('should display transfer details in history', () => {
      cy.get('.history-tab').click();
      cy.get('.transfer-history-item').first().within(() => {
        cy.get('.to-account').should('be.visible');
        cy.get('.amount').should('be.visible');
        cy.get('.date').should('be.visible');
        cy.get('.status').should('be.visible');
      });
    });

    it('should filter history by date range', () => {
      cy.get('.history-tab').click();
      cy.get('.date-from-input').type('2026-01-01');
      cy.get('.date-to-input').type('2026-05-08');
      cy.get('.apply-filter-btn').click();
      cy.get('.transfer-history-item').should('have.length.greaterThan', 0);
    });
  });

  describe('Transfer Error Handling', () => {
    it('should display error on failed transfer', () => {
      cy.intercept('POST', '**/api/transfers', { statusCode: 400, body: { error: 'Transfer failed' } }).as('failedTransfer');

      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('button[type="submit"]').click();
      cy.get('.confirmation-dialog .confirm-btn').click();

      cy.wait('@failedTransfer');
      cy.get('.error-message').should('be.visible');
    });

    it('should handle network timeout', () => {
      cy.intercept('POST', '**/api/transfers', (req) => {
        req.destroy();
      }).as('transferTimeout');

      cy.get('select[formControlName="fromAccount"]').select(transferData.fromAccount);
      cy.get('input[formControlName="toAccount"]').type(transferData.toAccount);
      cy.get('input[formControlName="amount"]').type(transferData.amount.toString());
      cy.get('button[type="submit"]').click();
      cy.get('.confirmation-dialog .confirm-btn').click();

      cy.get('.error-message').should('contain', 'Request timeout');
    });
  });

  describe('Responsive Transfers', () => {
    it('should be responsive on mobile', () => {
      cy.viewport('iphone-x');
      cy.get('.transfer-container').should('be.visible');
      cy.get('.transfer-form').should('be.visible');
    });

    it('should be responsive on tablet', () => {
      cy.viewport('ipad-2');
      cy.get('.transfer-container').should('be.visible');
    });
  });

  describe('Accessibility - Transfers', () => {
    it('should have proper form labels', () => {
      cy.get('label[for="fromAccount"]').should('be.visible');
      cy.get('label[for="toAccount"]').should('be.visible');
      cy.get('label[for="amount"]').should('be.visible');
    });

    it('should have keyboard accessible form', () => {
      cy.get('select[formControlName="fromAccount"]').focus();
      cy.focused().should('have.name', 'fromAccount');
      cy.get('select[formControlName="fromAccount"]').type('{tab}');
      cy.focused().should('have.name', 'toAccount');
    });

    it('should have proper ARIA labels', () => {
      cy.get('button[type="submit"]').should('have.attr', 'aria-label');
    });
  });
});
