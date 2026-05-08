// ============================================================================
// API Integration End-to-End Tests
// ============================================================================

describe('API Integration', () => {
  const testUser = {
    email: 'test@example.com',
    password: 'TestPassword123!',
  };

  beforeEach(() => {
    cy.login(testUser.email, testUser.password);
  });

  describe('Auth API', () => {
    it('should authenticate with valid credentials', () => {
      cy.request('POST', 'http://api-gateway:8000/api/auth/login', {
        email: testUser.email,
        password: testUser.password,
      }).then((response) => {
        expect(response.status).to.equal(200);
        expect(response.body).to.have.property('token');
        expect(response.body).to.have.property('user');
        expect(response.body.user).to.have.property('email', testUser.email);
      });
    });

    it('should reject invalid credentials', () => {
      cy.request({
        method: 'POST',
        url: 'http://api-gateway:8000/api/auth/login',
        body: {
          email: 'invalid@example.com',
          password: 'wrongpassword',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.equal(401);
      });
    });

    it('should refresh token successfully', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'POST',
          url: 'http://api-gateway:8000/api/auth/refresh',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          expect(response.status).to.equal(200);
          expect(response.body).to.have.property('token');
        });
      });
    });

    it('should logout successfully', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'POST',
          url: 'http://api-gateway:8000/api/auth/logout',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          expect(response.status).to.equal(200);
        });
      });
    });
  });

  describe('Account API', () => {
    it('should retrieve user accounts', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          expect(response.status).to.equal(200);
          expect(response.body).to.be.an('array');
          expect(response.body.length).to.be.greaterThan(0);
          expect(response.body[0]).to.have.property('id');
          expect(response.body[0]).to.have.property('accountNumber');
          expect(response.body[0]).to.have.property('type');
          expect(response.body[0]).to.have.property('balance');
        });
      });
    });

    it('should retrieve account details', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          cy.request({
            method: 'GET',
            url: `http://api-gateway:8000/api/accounts/${accountId}`,
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }).then((accountResponse) => {
            expect(accountResponse.status).to.equal(200);
            expect(accountResponse.body).to.have.property('id', accountId);
          });
        });
      });
    });

    it('should retrieve account balance', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          cy.request({
            method: 'GET',
            url: `http://api-gateway:8000/api/accounts/${accountId}/balance`,
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }).then((balanceResponse) => {
            expect(balanceResponse.status).to.equal(200);
            expect(balanceResponse.body).to.have.property('currentBalance');
            expect(balanceResponse.body).to.have.property('availableBalance');
          });
        });
      });
    });
  });

  describe('Transaction API', () => {
    it('should retrieve transactions for account', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          cy.request({
            method: 'GET',
            url: `http://api-gateway:8000/api/accounts/${accountId}/transactions`,
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }).then((transactionResponse) => {
            expect(transactionResponse.status).to.equal(200);
            expect(transactionResponse.body).to.be.an('array');
            if (transactionResponse.body.length > 0) {
              expect(transactionResponse.body[0]).to.have.property('id');
              expect(transactionResponse.body[0]).to.have.property('type');
              expect(transactionResponse.body[0]).to.have.property('amount');
            }
          });
        });
      });
    });

    it('should retrieve transaction details', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          cy.request({
            method: 'GET',
            url: `http://api-gateway:8000/api/accounts/${accountId}/transactions?limit=1`,
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }).then((transactionResponse) => {
            if (transactionResponse.body.length > 0) {
              const transactionId = transactionResponse.body[0].id;
              cy.request({
                method: 'GET',
                url: `http://api-gateway:8000/api/transactions/${transactionId}`,
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              }).then((detailResponse) => {
                expect(detailResponse.status).to.equal(200);
                expect(detailResponse.body).to.have.property('id', transactionId);
              });
            }
          });
        });
      });
    });

    it('should create deposit transaction', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          cy.request({
            method: 'POST',
            url: 'http://api-gateway:8000/api/transactions/deposit',
            headers: {
              Authorization: `Bearer ${token}`,
            },
            body: {
              accountId: accountId,
              amount: 1000,
              description: 'Test deposit',
            },
          }).then((depositResponse) => {
            expect(depositResponse.status).to.equal(201);
            expect(depositResponse.body).to.have.property('id');
            expect(depositResponse.body).to.have.property('status');
          });
        });
      });
    });

    it('should create withdrawal transaction', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          cy.request({
            method: 'POST',
            url: 'http://api-gateway:8000/api/transactions/withdraw',
            headers: {
              Authorization: `Bearer ${token}`,
            },
            body: {
              accountId: accountId,
              amount: 500,
              description: 'Test withdrawal',
            },
          }).then((withdrawResponse) => {
            expect(withdrawResponse.status).to.equal(201);
            expect(withdrawResponse.body).to.have.property('id');
          });
        });
      });
    });

    it('should create transfer transaction', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          if (response.body.length >= 2) {
            const fromAccountId = response.body[0].id;
            const toAccountId = response.body[1].id;
            cy.request({
              method: 'POST',
              url: 'http://api-gateway:8000/api/transactions/transfer',
              headers: {
                Authorization: `Bearer ${token}`,
              },
              body: {
                fromAccountId: fromAccountId,
                toAccountId: toAccountId,
                amount: 1000,
                description: 'Test transfer',
              },
            }).then((transferResponse) => {
              expect(transferResponse.status).to.equal(201);
              expect(transferResponse.body).to.have.property('id');
            });
          }
        });
      });
    });
  });

  describe('API Error Handling', () => {
    it('should handle 401 unauthorized error', () => {
      cy.request({
        method: 'GET',
        url: 'http://api-gateway:8000/api/accounts',
        headers: {
          Authorization: 'Bearer invalid_token',
        },
        failOnStatusCode: false,
      }).then((response) => {
        expect(response.status).to.equal(401);
      });
    });

    it('should handle 403 forbidden error', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/admin/users',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          failOnStatusCode: false,
        }).then((response) => {
          expect(response.status).to.equal(403);
        });
      });
    });

    it('should handle 404 not found error', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts/nonexistent-id',
          headers: {
            Authorization: `Bearer ${token}`,
          },
          failOnStatusCode: false,
        }).then((response) => {
          expect(response.status).to.equal(404);
        });
      });
    });

    it('should handle validation errors', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          cy.request({
            method: 'POST',
            url: 'http://api-gateway:8000/api/transactions/deposit',
            headers: {
              Authorization: `Bearer ${token}`,
            },
            body: {
              accountId: accountId,
              amount: -100,
              description: 'Invalid amount',
            },
            failOnStatusCode: false,
          }).then((depositResponse) => {
            expect(depositResponse.status).to.equal(400);
          });
        });
      });
    });

    it('should handle server errors gracefully', () => {
      cy.intercept('GET', '**/api/accounts', {
        statusCode: 500,
        body: { error: 'Internal Server Error' },
      });
      cy.login(testUser.email, testUser.password);
      cy.navigateToAccounts();
      cy.get('.error-message').should('be.visible');
    });

    it('should handle network timeout', () => {
      cy.intercept('GET', '**/api/accounts', (req) => {
        req.destroy();
      });
      cy.login(testUser.email, testUser.password);
      cy.navigateToAccounts();
      cy.get('.error-message').should('contain', 'timeout');
    });
  });

  describe('API Health Checks', () => {
    it('should check API gateway health', () => {
      cy.request('GET', 'http://api-gateway:8000/health').then((response) => {
        expect(response.status).to.equal(200);
        expect(response.body).to.have.property('status');
      });
    });

    it('should check auth service health', () => {
      cy.request('GET', 'http://auth-service:8001/health').then((response) => {
        expect(response.status).to.equal(200);
      });
    });

    it('should check account service health', () => {
      cy.request('GET', 'http://account-service:8002/health').then((response) => {
        expect(response.status).to.equal(200);
      });
    });

    it('should check transaction service health', () => {
      cy.request('GET', 'http://transaction-service:8003/health').then((response) => {
        expect(response.status).to.equal(200);
      });
    });

    it('should check ledger service health', () => {
      cy.request('GET', 'http://ledger-service:8004/health').then((response) => {
        expect(response.status).to.equal(200);
      });
    });
  });

  describe('API Performance', () => {
    it('should retrieve accounts within acceptable time', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        const startTime = Date.now();
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const endTime = Date.now();
          const responseTime = endTime - startTime;
          expect(responseTime).to.be.lessThan(5000); // 5 seconds
        });
      });
    });

    it('should retrieve transactions within acceptable time', () => {
      cy.getAuthToken(testUser.email, testUser.password).then((token) => {
        cy.request({
          method: 'GET',
          url: 'http://api-gateway:8000/api/accounts',
          headers: {
            Authorization: `Bearer ${token}`,
          },
        }).then((response) => {
          const accountId = response.body[0].id;
          const startTime = Date.now();
          cy.request({
            method: 'GET',
            url: `http://api-gateway:8000/api/accounts/${accountId}/transactions`,
            headers: {
              Authorization: `Bearer ${token}`,
            },
          }).then(() => {
            const endTime = Date.now();
            const responseTime = endTime - startTime;
            expect(responseTime).to.be.lessThan(5000);
          });
        });
      });
    });
  });
});
