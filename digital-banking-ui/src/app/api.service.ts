import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private apiUrl = 'http://localhost:8001';
  private token: string | null = null;

  constructor(private http: HttpClient) {
    this.token = localStorage.getItem('authToken');
  }

  setToken(token: string) {
    this.token = token;
    localStorage.setItem('authToken', token);
  }

  private getHeaders(): HttpHeaders {
    let headers = new HttpHeaders({ 'Content-Type': 'application/json' });
    if (this.token) {
      headers = headers.set('Authorization', `Bearer ${this.token}`);
    }
    return headers;
  }

  register(email: string, password: string, fullName: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/v1/auth/register`, {
      email,
      password,
      fullName
    });
  }

  login(email: string, password: string): Observable<any> {
    return this.http.post(`${this.apiUrl}/api/v1/auth/login`, { email, password });
  }

  getAccounts(): Observable<any> {
    return this.http.get(`http://localhost:8002/api/v1/accounts`, {
      headers: this.getHeaders()
    });
  }

  createAccount(accountType: string): Observable<any> {
    return this.http.post(`http://localhost:8002/api/v1/accounts`, { accountType }, {
      headers: this.getHeaders()
    });
  }

  getTransactions(): Observable<any> {
    return this.http.get(`http://localhost:8003/api/v1/transactions`, {
      headers: this.getHeaders()
    });
  }

  deposit(accountId: string, amount: number): Observable<any> {
    return this.http.post(`http://localhost:8003/api/v1/transactions/deposit`, {
      accountId,
      amount
    }, { headers: this.getHeaders() });
  }

  withdraw(accountId: string, amount: number): Observable<any> {
    return this.http.post(`http://localhost:8003/api/v1/transactions/withdraw`, {
      accountId,
      amount
    }, { headers: this.getHeaders() });
  }

  logout() {
    this.token = null;
    localStorage.removeItem('authToken');
  }

  isLoggedIn(): boolean {
    return !!this.token;
  }
}
