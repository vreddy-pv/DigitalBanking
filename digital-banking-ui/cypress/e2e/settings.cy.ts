// ============================================================================
// Settings End-to-End Tests
// ============================================================================

describe('Settings', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
    fullName: 'Test User',
  };

  beforeEach(() => {
    cy.login(testUser.email, testUser.password);
    cy.navigateToSettings();
  });

  describe('Settings Page', () => {
    it('should display settings page with header', () => {
      cy.get('h1').should('contain', 'Settings');
      cy.get('.settings-container').should('be.visible');
    });

    it('should display settings navigation menu', () => {
      cy.get('.settings-nav').should('be.visible');
      cy.get('.settings-nav-item').should('have.length.greaterThan', 0);
    });

    it('should display profile section', () => {
      cy.get('a[href="#profile"]').click();
      cy.get('.profile-section').should('be.visible');
    });

    it('should display security section', () => {
      cy.get('a[href="#security"]').click();
      cy.get('.security-section').should('be.visible');
    });

    it('should display notification section', () => {
      cy.get('a[href="#notifications"]').click();
      cy.get('.notification-section').should('be.visible');
    });

    it('should display preferences section', () => {
      cy.get('a[href="#preferences"]').click();
      cy.get('.preferences-section').should('be.visible');
    });
  });

  describe('Profile Settings', () => {
    beforeEach(() => {
      cy.get('a[href="#profile"]').click();
    });

    it('should display user name field', () => {
      cy.get('input[name="fullName"]').should('be.visible');
      cy.get('input[name="fullName"]').should('have.value', testUser.fullName);
    });

    it('should display email field (read-only)', () => {
      cy.get('input[name="email"]').should('be.visible');
      cy.get('input[name="email"]').should('be.disabled');
      cy.get('input[name="email"]').should('have.value', testUser.email);
    });

    it('should display phone number field', () => {
      cy.get('input[name="phoneNumber"]').should('be.visible');
    });

    it('should display date of birth field', () => {
      cy.get('input[name="dateOfBirth"]').should('be.visible');
    });

    it('should display address fields', () => {
      cy.get('input[name="address.line1"]').should('be.visible');
      cy.get('input[name="address.city"]').should('be.visible');
      cy.get('input[name="address.state"]').should('be.visible');
      cy.get('input[name="address.zipCode"]').should('be.visible');
    });

    it('should display profile picture upload', () => {
      cy.get('.profile-picture-upload').should('be.visible');
      cy.get('input[type="file"]').should('exist');
    });

    it('should update profile information', () => {
      cy.get('input[name="phoneNumber"]').clear().type('9876543210');
      cy.get('button.save-btn').click();
      cy.get('.success-message').should('contain', 'Profile updated successfully');
    });

    it('should validate required fields', () => {
      cy.get('input[name="fullName"]').clear();
      cy.get('button.save-btn').click();
      cy.get('.error-text').should('contain', 'required');
    });

    it('should validate phone number format', () => {
      cy.get('input[name="phoneNumber"]').type('abc');
      cy.get('button.save-btn').click();
      cy.get('.error-text').should('contain', 'valid phone number');
    });
  });

  describe('Security Settings', () => {
    beforeEach(() => {
      cy.get('a[href="#security"]').click();
    });

    it('should display password change section', () => {
      cy.get('.password-section').should('be.visible');
    });

    it('should require current password', () => {
      cy.get('input[name="currentPassword"]').should('be.visible');
    });

    it('should require new password', () => {
      cy.get('input[name="newPassword"]').should('be.visible');
    });

    it('should require password confirmation', () => {
      cy.get('input[name="confirmPassword"]').should('be.visible');
    });

    it('should validate password requirements', () => {
      cy.get('input[name="currentPassword"]').type('TestPassword123!');
      cy.get('input[name="newPassword"]').type('weak');
      cy.get('.error-text').should('contain', 'at least 8 characters');
    });

    it('should validate password match', () => {
      cy.get('input[name="currentPassword"]').type('TestPassword123!');
      cy.get('input[name="newPassword"]').type('NewPassword123!');
      cy.get('input[name="confirmPassword"]').type('DifferentPassword123!');
      cy.get('button.save-btn').click();
      cy.get('.error-text').should('contain', 'do not match');
    });

    it('should change password successfully', () => {
      cy.get('input[name="currentPassword"]').type('TestPassword123!');
      cy.get('input[name="newPassword"]').type('NewPassword123!');
      cy.get('input[name="confirmPassword"]').type('NewPassword123!');
      cy.get('button.save-btn').click();
      cy.get('.success-message').should('contain', 'Password changed successfully');
    });

    it('should display two-factor authentication option', () => {
      cy.get('.two-factor-section').should('be.visible');
      cy.get('.enable-2fa-btn').should('be.visible');
    });

    it('should display active sessions', () => {
      cy.get('.active-sessions').should('be.visible');
      cy.get('.session-item').should('have.length.greaterThan', 0);
    });

    it('should logout other sessions', () => {
      cy.get('.session-item').first().within(() => {
        cy.get('.logout-btn').click();
      });
      cy.get('.confirmation-dialog').should('be.visible');
      cy.get('.confirmation-dialog .confirm-btn').click();
      cy.get('.success-message').should('contain', 'Session ended');
    });

    it('should display login history', () => {
      cy.get('.login-history').should('be.visible');
      cy.get('.login-history-item').should('have.length.greaterThan', 0);
    });
  });

  describe('Notification Preferences', () => {
    beforeEach(() => {
      cy.get('a[href="#notifications"]').click();
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

    it('should configure notification types', () => {
      cy.get('input[name="transactionNotifications"]').check();
      cy.get('input[name="transactionNotifications"]').should('be.checked');
    });

    it('should configure quiet hours', () => {
      cy.get('input[name="quietHoursStart"]').type('22:00');
      cy.get('input[name="quietHoursEnd"]').type('08:00');
    });

    it('should save notification preferences', () => {
      cy.get('input[name="emailNotifications"]').check();
      cy.get('button.save-btn').click();
      cy.get('.success-message').should('contain', 'Preferences saved');
    });
  });

  describe('User Preferences', () => {
    beforeEach(() => {
      cy.get('a[href="#preferences"]').click();
    });

    it('should display theme preference', () => {
      cy.get('select[name="theme"]').should('be.visible');
    });

    it('should display language preference', () => {
      cy.get('select[name="language"]').should('be.visible');
    });

    it('should display currency preference', () => {
      cy.get('select[name="currency"]').should('be.visible');
    });

    it('should display date format preference', () => {
      cy.get('select[name="dateFormat"]').should('be.visible');
    });

    it('should change theme preference', () => {
      cy.get('select[name="theme"]').select('DARK');
      cy.get('button.save-btn').click();
      cy.get('.success-message').should('contain', 'Preferences updated');
    });

    it('should change language preference', () => {
      cy.get('select[name="language"]').select('SPANISH');
      cy.get('button.save-btn').click();
      cy.get('.success-message').should('contain', 'Preferences updated');
    });
  });

  describe('Account Preferences', () => {
    beforeEach(() => {
      cy.get('a[href="#account"]').click();
    });

    it('should display default account selection', () => {
      cy.get('select[name="defaultAccount"]').should('be.visible');
    });

    it('should display statement delivery preference', () => {
      cy.get('input[name="emailStatements"]').should('be.visible');
    });

    it('should update account preferences', () => {
      cy.get('input[name="emailStatements"]').check();
      cy.get('button.save-btn').click();
      cy.get('.success-message').should('contain', 'Preferences updated');
    });
  });

  describe('Linked Accounts', () => {
    beforeEach(() => {
      cy.get('a[href="#linked-accounts"]').click();
    });

    it('should display linked accounts list', () => {
      cy.get('.linked-accounts-list').should('be.visible');
    });

    it('should display add linked account button', () => {
      cy.get('.add-linked-account-btn').should('be.visible');
    });

    it('should remove linked account', () => {
      cy.get('.linked-account-item').first().within(() => {
        cy.get('.delete-btn').click();
      });
      cy.get('.confirmation-dialog').should('be.visible');
      cy.get('.confirmation-dialog .confirm-btn').click();
      cy.get('.success-message').should('contain', 'Account removed');
    });
  });

  describe('Privacy & Data', () => {
    beforeEach(() => {
      cy.get('a[href="#privacy"]').click();
    });

    it('should display download data button', () => {
      cy.get('.download-data-btn').should('be.visible');
    });

    it('should display delete account button', () => {
      cy.get('.delete-account-btn').should('be.visible');
    });

    it('should display privacy policy link', () => {
      cy.get('a[href*="privacy-policy"]').should('be.visible');
    });

    it('should display terms and conditions link', () => {
      cy.get('a[href*="terms"]').should('be.visible');
    });

    it('should require password confirmation for account deletion', () => {
      cy.get('.delete-account-btn').click();
      cy.get('.confirmation-dialog').should('be.visible');
      cy.get('input[name="password"]').should('be.visible');
    });
  });

  describe('Settings Responsiveness', () => {
    it('should be responsive on mobile', () => {
      cy.viewport('iphone-x');
      cy.get('.settings-container').should('be.visible');
      cy.get('.settings-nav').should('be.visible');
    });

    it('should be responsive on tablet', () => {
      cy.viewport('ipad-2');
      cy.get('.settings-container').should('be.visible');
    });
  });

  describe('Settings Accessibility', () => {
    it('should have proper form labels', () => {
      cy.get('a[href="#profile"]').click();
      cy.get('label[for="fullName"]').should('be.visible');
      cy.get('label[for="email"]').should('be.visible');
    });

    it('should have keyboard navigation in sidebar', () => {
      cy.get('.settings-nav-item').first().focus();
      cy.focused().should('have.class', 'settings-nav-item');
    });

    it('should have ARIA labels on form fields', () => {
      cy.get('a[href="#profile"]').click();
      cy.get('input[name="fullName"]').should('have.attr', 'aria-label');
    });
  });
});
