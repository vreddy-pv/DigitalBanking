import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private gatewayUrl = 'http://localhost:8000';
  private analyticsUrl = 'http://localhost:8007';
  private complianceUrl = 'http://localhost:8008';
  private auditUrl = 'http://localhost:8009';

  constructor(private http: HttpClient) {}

  setToken(token: string) { localStorage.setItem('authToken', token); }
  getToken(): string | null { return localStorage.getItem('authToken'); }
  setUserId(id: string) { localStorage.setItem('userId', id); }
  getUserId(): string | null { return localStorage.getItem('userId'); }
  setCustomerId(id: string) { localStorage.setItem('customerId', id); }
  getCustomerId(): string | null { return localStorage.getItem('customerId'); }
  setUserName(name: string) { localStorage.setItem('userName', name); }
  getUserName(): string | null { return localStorage.getItem('userName'); }
  setUserEmail(email: string) { localStorage.setItem('userEmail', email); }
  getUserEmail(): string | null { return localStorage.getItem('userEmail'); }

  isLoggedIn(): boolean { return !!this.getToken(); }

  logout() {
    ['authToken', 'userId', 'customerId', 'userName', 'userEmail'].forEach(k =>
      localStorage.removeItem(k)
    );
  }

  private headers(): HttpHeaders {
    const token = this.getToken();
    let h = new HttpHeaders({ 'Content-Type': 'application/json' });
    if (token) h = h.set('Authorization', `Bearer ${token}`);
    return h;
  }

  private reqId(): string {
    return `req-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
  }

  // Auth
  register(email: string, password: string, fullName: string): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/auth/register`, { email, password, fullName });
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/auth/login`, { email, password });
  }

  // Accounts
  getAccounts(): Observable<any> {
    return this.http.get(`${this.gatewayUrl}/api/v1/accounts`, { headers: this.headers() });
  }

  createAccount(data: any): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/accounts/register`, data, { headers: this.headers() });
  }

  // Transactions
  getTransactions(): Observable<any> {
    return this.http.get(`${this.gatewayUrl}/api/v1/transactions`, { headers: this.headers() });
  }

  deposit(toAccountId: string, amount: number, description = 'Deposit'): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/transactions/deposit`,
      { toAccountId, amount, requestId: this.reqId(), description },
      { headers: this.headers() });
  }

  withdraw(fromAccountId: string, amount: number, description = 'Withdrawal'): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/transactions/withdraw`,
      { fromAccountId, amount, requestId: this.reqId(), description },
      { headers: this.headers() });
  }

  transfer(fromAccountId: string, toAccountId: string, amount: number, description = 'Transfer'): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/transactions/transfer`,
      { fromAccountId, toAccountId, amount, requestId: this.reqId(), description },
      { headers: this.headers() });
  }

  // Customer / KYC
  submitKycDocument(customerId: string, documentType: string, documentReference: string): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/customers/${customerId}/kyc/documents`,
      { documentType, documentReference }, { headers: this.headers() });
  }

  getKycStatus(customerId: string): Observable<any> {
    return this.http.get(`${this.gatewayUrl}/api/v1/customers/${customerId}/kyc/status`, { headers: this.headers() });
  }

  getKycDocuments(customerId: string): Observable<any> {
    return this.http.get(`${this.gatewayUrl}/api/v1/customers/${customerId}/kyc/documents`, { headers: this.headers() });
  }

  addBeneficiary(customerId: string, beneficiaryAccountId: string, nickname: string): Observable<any> {
    return this.http.post(`${this.gatewayUrl}/api/v1/customers/${customerId}/beneficiaries`,
      { beneficiaryAccountId, nickname }, { headers: this.headers() });
  }

  getBeneficiaries(customerId: string): Observable<any> {
    return this.http.get(`${this.gatewayUrl}/api/v1/customers/${customerId}/beneficiaries`, { headers: this.headers() });
  }

  updatePreferences(customerId: string, prefs: any): Observable<any> {
    return this.http.put(`${this.gatewayUrl}/api/v1/customers/${customerId}/preferences`, prefs, { headers: this.headers() });
  }

  // Analytics (direct — CQRS read model)
  getStatement(accountId: string, page = 1, pageSize = 20): Observable<any> {
    return this.http.get(`${this.analyticsUrl}/api/v1/analytics/accounts/${accountId}/statement?page=${page}&page_size=${pageSize}`);
  }

  getSummary(accountId: string, month?: string): Observable<any> {
    const q = month ? `?month=${month}` : '';
    return this.http.get(`${this.analyticsUrl}/api/v1/analytics/accounts/${accountId}/summary${q}`);
  }

  getSpending(accountId: string): Observable<any> {
    return this.http.get(`${this.analyticsUrl}/api/v1/analytics/accounts/${accountId}/spending`);
  }

  getTrialBalance(): Observable<any> {
    return this.http.get(`${this.analyticsUrl}/api/v1/analytics/ledger/trial-balance`);
  }

  getPlatformSummary(): Observable<any> {
    return this.http.get(`${this.analyticsUrl}/api/v1/analytics/summary`);
  }

  // Compliance (direct)
  getAlerts(params?: Record<string, string>): Observable<any> {
    const q = params ? '?' + Object.entries(params).filter(([, v]) => v).map(([k, v]) => `${k}=${v}`).join('&') : '';
    return this.http.get(`${this.complianceUrl}/api/v1/compliance/alerts${q}`);
  }

  reviewAlert(alertId: string, status: string, reviewedBy: string, notes: string): Observable<any> {
    return this.http.put(`${this.complianceUrl}/api/v1/compliance/alerts/${alertId}/review`,
      { status, reviewed_by: reviewedBy, review_notes: notes });
  }

  getComplianceStats(): Observable<any> {
    return this.http.get(`${this.complianceUrl}/api/v1/compliance/stats`);
  }

  getRiskProfile(accountId: string): Observable<any> {
    return this.http.get(`${this.complianceUrl}/api/v1/compliance/customers/${accountId}/risk`);
  }

  // Audit (direct)
  getAuditEvents(params?: Record<string, string>): Observable<any> {
    const q = params ? '?' + Object.entries(params).filter(([, v]) => v).map(([k, v]) => `${k}=${v}`).join('&') : '';
    return this.http.get(`${this.auditUrl}/api/v1/audit/events${q}`);
  }

  getAuditStats(): Observable<any> {
    return this.http.get(`${this.auditUrl}/api/v1/audit/events/stats`);
  }

  getAuditForResource(type: string, id: string): Observable<any> {
    return this.http.get(`${this.auditUrl}/api/v1/audit/events/resource/${type}/${id}`);
  }
}
