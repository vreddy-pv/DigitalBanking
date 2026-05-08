// ============================================================================
// Navigation and Layout End-to-End Tests
// ============================================================================

describe('Navigation and Layout', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
  };

  beforeEach(() => {
    cy.login(testUser.email, testUser.password);
  });

  describe('Sidebar Navigation', () => {
    it('should display all navigation items', () => {
      const navItems = [
        'Dashboard',
        'Accounts',
        'Transactions',
        'Money Transfer',
        'Notifications',
        'Settings',
      ];

      navItems.forEach((item) => {
        cy.get('.sidebar-nav').should('contain', item);
      });
    });

    it('should highlight active navigation item', () => {
      cy.navigateToDashboard();
      cy.get('a[routerLink="/app/dashboard"]').should('have.class', 'active');
    });

    it('should navigate to Accounts section', () => {
      cy.navigateToAccounts();
      cy.url().should('include', '/app/accounts');
      cy.get('a[routerLink="/app/accounts"]').should('have.class', 'active');
    });

    it('should navigate to Transactions section', () => {
      cy.navigateToTransactions();
      cy.url().should('include', '/app/transactions');
      cy.get('a[routerLink="/app/transactions"]').should('have.class', 'active');
    });

    it('should navigate to Transfers section', () => {
      cy.navigateToTransfers();
      cy.url().should('include', '/app/transfers');
      cy.get('a[routerLink="/app/transfers"]').should('have.class', 'active');
    });

    it('should navigate to Notifications section', () => {
      cy.navigateToNotifications();
      cy.url().should('include', '/app/notifications');
      cy.get('a[routerLink="/app/notifications"]').should('have.class', 'active');
    });

    it('should navigate to Settings section', () => {
      cy.navigateToSettings();
      cy.url().should('include', '/app/settings');
      cy.get('a[routerLink="/app/settings"]').should('have.class', 'active');
    });
  });

  describe('Header Elements', () => {
    it('should display theme toggle button', () => {
      cy.get('.icon-btn').contains(/🌙|☀️/).should('be.visible');
    });

    it('should display notification bell icon', () => {
      cy.get('.notification-btn').should('be.visible');
    });

    it('should display user menu button', () => {
      cy.get('.user-btn').should('be.visible');
    });

    it('should display "Digital Banking Platform" title', () => {
      cy.get('.header-left h2').should('contain', 'Digital Banking Platform');
    });
  });

  describe('Sidebar User Info', () => {
    it('should display user avatar with first letter', () => {
      cy.get('.user-avatar').should('be.visible');
    });

    it('should display user name in sidebar footer', () => {
      cy.get('.user-name').should('exist');
    });

    it('should display user email in sidebar footer', () => {
      cy.get('.user-email').should('exist');
    });

    it('should display logout button', () => {
      cy.get('.logout-btn').should('contain', 'Logout');
    });
  });

  describe('Theme Toggle', () => {
    it('should toggle between light and dark themes', () => {
      cy.get('html').should('not.have.class', 'dark-theme');

      cy.toggleTheme();
      cy.get('html').should('have.class', 'dark-theme');

      cy.toggleTheme();
      cy.get('html').should('not.have.class', 'dark-theme');
    });

    it('should persist theme selection', () => {
      cy.toggleTheme();
      cy.reload();
      cy.get('html').should('have.class', 'dark-theme');
    });

    it('should update colors on theme toggle', () => {
      cy.get('.sidebar').should('have.css', 'background').and('include', 'rgb');
      cy.toggleTheme();
      cy.get('.sidebar').should('have.css', 'background').and('include', 'rgb');
    });
  });

  describe('Responsive Layout', () => {
    it('should be responsive on tablet size', () => {
      cy.viewport('ipad-2');
      cy.get('.sidebar').should('be.visible');
      cy.get('.main-content').should('be.visible');
    });

    it('should be responsive on mobile size', () => {
      cy.viewport('iphone-x');
      cy.get('.sidebar').should('be.visible');
      cy.get('.main-content').should('be.visible');
    });

    it('should be responsive on desktop size', () => {
      cy.viewport(1280, 800);
      cy.get('.sidebar').should('be.visible');
      cy.get('.main-content').should('be.visible');
    });
  });

  describe('Micro Frontend Loading', () => {
    it('should load Account MFE when navigating to Accounts', () => {
      cy.navigateToAccounts();
      cy.url().should('include', '/app/accounts');
      cy.get('.content').should('be.visible');
    });

    it('should load Transaction MFE when navigating to Transactions', () => {
      cy.navigateToTransactions();
      cy.url().should('include', '/app/transactions');
      cy.get('.content').should('be.visible');
    });

    it('should load Transfer MFE when navigating to Transfers', () => {
      cy.navigateToTransfers();
      cy.url().should('include', '/app/transfers');
      cy.get('.content').should('be.visible');
    });

    it('should load Notification MFE when navigating to Notifications', () => {
      cy.navigateToNotifications();
      cy.url().should('include', '/app/notifications');
      cy.get('.content').should('be.visible');
    });

    it('should load Settings MFE when navigating to Settings', () => {
      cy.navigateToSettings();
      cy.url().should('include', '/app/settings');
      cy.get('.content').should('be.visible');
    });
  });

  describe('Navigation Performance', () => {
    it('should navigate between MFEs without full page reload', () => {
      cy.navigateToAccounts();
      cy.window().then((win) => {
        const initialReloads = win.performance.navigation.type;
        cy.navigateToTransactions();
        expect(win.performance.navigation.type).to.equal(initialReloads);
      });
    });

    it('should load MFE content within acceptable time', () => {
      cy.navigateToAccounts();
      cy.get('.content').should('be.visible', { timeout: 5000 });
    });
  });

  describe('Navigation State Persistence', () => {
    it('should maintain navigation state after page reload', () => {
      cy.navigateToAccounts();
      cy.reload();
      cy.url().should('include', '/app/accounts');
      cy.get('a[routerLink="/app/accounts"]').should('have.class', 'active');
    });

    it('should maintain user session across navigation', () => {
      cy.navigateToAccounts();
      cy.navigateToTransactions();
      cy.navigateToSettings();
      cy.get('.user-name').should('exist');
    });
  });

  describe('Accessibility', () => {
    it('should have proper heading hierarchy', () => {
      cy.get('h1').should('exist');
      cy.get('h2').should('exist');
    });

    it('should have keyboard accessible navigation', () => {
      cy.get('a[routerLink="/app/accounts"]').focus();
      cy.focused().should('have.attr', 'routerLink', '/app/accounts');
      cy.focused().should('have.attr', 'tabindex');
    });

    it('should have proper ARIA labels', () => {
      cy.get('button.logout-btn').should('be.visible');
      cy.get('button.logout-btn').should('have.attr', 'class');
    });
  });
});
