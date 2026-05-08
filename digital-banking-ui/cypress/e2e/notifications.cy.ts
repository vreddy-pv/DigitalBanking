// ============================================================================
// Notifications End-to-End Tests
// ============================================================================

describe('Notifications', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
  };

  beforeEach(() => {
    cy.login(testUser.email, testUser.password);
  });

  describe('Notification Bell', () => {
    it('should display notification bell in header', () => {
      cy.get('.notification-btn').should('be.visible');
    });

    it('should show notification count badge', () => {
      cy.get('.notification-badge').should('be.visible');
      cy.get('.notification-badge').should('contain.text', /\d+/);
    });

    it('should update badge count on new notification', () => {
      cy.get('.notification-badge').invoke('text').then((initialCount) => {
        // Simulate event that creates notification
        cy.window().then((win) => {
          const event = new CustomEvent('newNotification');
          win.dispatchEvent(event);
        });
        cy.get('.notification-badge').invoke('text').should('not.equal', initialCount);
      });
    });

    it('should open notification panel on click', () => {
      cy.get('.notification-btn').click();
      cy.get('.notification-panel').should('be.visible');
    });

    it('should close notification panel on click outside', () => {
      cy.get('.notification-btn').click();
      cy.get('.notification-panel').should('be.visible');
      cy.get('body').click(0, 0);
      cy.get('.notification-panel').should('not.be.visible');
    });
  });

  describe('Notification Panel', () => {
    beforeEach(() => {
      cy.get('.notification-btn').click();
    });

    it('should display notification list', () => {
      cy.get('.notification-list').should('be.visible');
      cy.get('.notification-item').should('have.length.greaterThan', 0);
    });

    it('should display notification details', () => {
      cy.get('.notification-item').first().within(() => {
        cy.get('.notification-title').should('be.visible');
        cy.get('.notification-message').should('be.visible');
        cy.get('.notification-time').should('be.visible');
      });
    });

    it('should show unread notifications with highlight', () => {
      cy.get('.notification-item.unread').should('have.length.greaterThan', 0);
    });

    it('should mark notification as read on click', () => {
      cy.get('.notification-item.unread').first().click();
      cy.get('.notification-item.unread').first().should('not.have.class', 'unread');
    });

    it('should show notification type icon', () => {
      cy.get('.notification-item').first().within(() => {
        cy.get('.notification-icon').should('be.visible');
      });
    });

    it('should display all notification types', () => {
      cy.get('.notification-item').should('have.length.greaterThan', 0);
      // Check for different notification types
      cy.get('.notification-item[data-type="TRANSACTION"]').should('exist');
      cy.get('.notification-item[data-type="ALERT"]').should('exist');
    });
  });

  describe('Notification Actions', () => {
    beforeEach(() => {
      cy.get('.notification-btn').click();
    });

    it('should display mark as read button', () => {
      cy.get('.notification-item.unread').first().within(() => {
        cy.get('.mark-read-btn').should('be.visible');
      });
    });

    it('should display delete button', () => {
      cy.get('.notification-item').first().within(() => {
        cy.get('.delete-notification-btn').should('be.visible');
      });
    });

    it('should delete notification on button click', () => {
      const initialCount = cy.get('.notification-item').then((items) => items.length);
      cy.get('.notification-item').first().within(() => {
        cy.get('.delete-notification-btn').click();
      });
      cy.get('.notification-item').then((items) => {
        expect(items.length).to.be.lessThan(parseInt(initialCount));
      });
    });

    it('should mark all as read', () => {
      cy.get('.mark-all-read-btn').click();
      cy.get('.notification-item.unread').should('have.length', 0);
    });

    it('should clear all notifications', () => {
      cy.get('.clear-all-btn').click();
      cy.get('.confirmation-dialog').should('be.visible');
      cy.get('.confirmation-dialog .confirm-btn').click();
      cy.get('.notification-item').should('have.length', 0);
    });
  });

  describe('Notification Filtering', () => {
    beforeEach(() => {
      cy.navigateToNotifications();
    });

    it('should display notification page with filters', () => {
      cy.get('h1').should('contain', 'Notifications');
      cy.get('.filter-tabs').should('be.visible');
    });

    it('should filter by All', () => {
      cy.get('.filter-tab[data-filter="ALL"]').click();
      cy.get('.notification-item').should('have.length.greaterThan', 0);
    });

    it('should filter by Unread', () => {
      cy.get('.filter-tab[data-filter="UNREAD"]').click();
      cy.get('.notification-item').each(($item) => {
        cy.wrap($item).should('have.class', 'unread');
      });
    });

    it('should filter by Transaction', () => {
      cy.get('.filter-tab[data-filter="TRANSACTION"]').click();
      cy.get('.notification-item').each(($item) => {
        cy.wrap($item).should('have.attr', 'data-type', 'TRANSACTION');
      });
    });

    it('should filter by Alert', () => {
      cy.get('.filter-tab[data-filter="ALERT"]').click();
      cy.get('.notification-item').each(($item) => {
        cy.wrap($item).should('have.attr', 'data-type', 'ALERT');
      });
    });

    it('should search notifications', () => {
      cy.get('.search-input').type('transfer');
      cy.get('.notification-item').should('contain', 'transfer');
    });
  });

  describe('Notification Details', () => {
    beforeEach(() => {
      cy.navigateToNotifications();
    });

    it('should expand notification to show full details', () => {
      cy.get('.notification-item').first().click();
      cy.get('.notification-details').should('be.visible');
    });

    it('should show notification content', () => {
      cy.get('.notification-item').first().click();
      cy.get('.notification-details').should('contain', 'Content');
    });

    it('should show transaction reference for transaction notifications', () => {
      cy.get('.notification-item[data-type="TRANSACTION"]').first().click();
      cy.get('.notification-details').should('contain', 'Transaction ID');
    });

    it('should show action links', () => {
      cy.get('.notification-item').first().click();
      cy.get('.notification-action-link').should('be.visible');
    });

    it('should navigate to related section on action link click', () => {
      cy.get('.notification-item[data-type="TRANSACTION"]').first().click();
      cy.get('.notification-action-link').click();
      cy.url().should('include', '/app/transactions');
    });
  });

  describe('Notification Settings', () => {
    beforeEach(() => {
      cy.navigateToSettings();
      cy.get('a[href="#notifications"]').click();
    });

    it('should display notification preferences', () => {
      cy.get('.notification-preferences').should('be.visible');
    });

    it('should toggle email notifications', () => {
      cy.get('input[name="emailNotifications"]').check();
      cy.get('input[name="emailNotifications"]').should('be.checked');
    });

    it('should toggle SMS notifications', () => {
      cy.get('input[name="smsNotifications"]').check();
      cy.get('input[name="smsNotifications"]').should('be.checked');
    });

    it('should toggle push notifications', () => {
      cy.get('input[name="pushNotifications"]').check();
      cy.get('input[name="pushNotifications"]').should('be.checked');
    });

    it('should configure notification frequency', () => {
      cy.get('select[name="notificationFrequency"]').select('IMMEDIATE');
      cy.get('select[name="notificationFrequency"]').should('have.value', 'IMMEDIATE');
    });

    it('should configure notification types', () => {
      cy.get('input[name="notifyTransactions"]').check();
      cy.get('input[name="notifyTransactions"]').should('be.checked');
    });

    it('should save notification settings', () => {
      cy.get('input[name="emailNotifications"]').check();
      cy.get('button.save-btn').click();
      cy.get('.success-message').should('contain', 'Settings saved');
    });
  });

  describe('Notification Types', () => {
    beforeEach(() => {
      cy.navigateToNotifications();
    });

    it('should display transaction notifications', () => {
      cy.get('.notification-item[data-type="TRANSACTION"]').should('have.length.greaterThan', 0);
    });

    it('should display alert notifications', () => {
      cy.get('.notification-item[data-type="ALERT"]').should('have.length.greaterThan', 0);
    });

    it('should display system notifications', () => {
      cy.get('.notification-item[data-type="SYSTEM"]').should('have.length.greaterThan', 0);
    });

    it('should display promotional notifications', () => {
      cy.get('.notification-item[data-type="PROMOTIONAL"]').should('have.length.greaterThan', 0);
    });
  });

  describe('Notification Pagination', () => {
    beforeEach(() => {
      cy.navigateToNotifications();
    });

    it('should display pagination if many notifications', () => {
      cy.get('.pagination').should('be.visible');
    });

    it('should navigate between pages', () => {
      cy.get('.pagination-next').click();
      cy.get('.notification-item').should('have.length.greaterThan', 0);
    });

    it('should change items per page', () => {
      cy.get('.items-per-page-select').select('25');
      cy.get('.notification-item').should('have.length.lessThan', 26);
    });
  });

  describe('Notification Accessibility', () => {
    beforeEach(() => {
      cy.navigateToNotifications();
    });

    it('should have proper heading structure', () => {
      cy.get('h1').should('exist');
      cy.get('h2').should('exist');
    });

    it('should have keyboard accessible notification items', () => {
      cy.get('.notification-item').first().focus();
      cy.focused().should('have.class', 'notification-item');
    });

    it('should have ARIA live region for new notifications', () => {
      cy.get('[aria-live="polite"]').should('exist');
    });

    it('should announce notification count to screen readers', () => {
      cy.get('.notification-badge').should('have.attr', 'aria-label');
    });
  });
});
