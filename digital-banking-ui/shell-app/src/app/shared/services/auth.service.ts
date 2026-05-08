import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map, tap } from 'rxjs/operators';

export interface User {
  id: string;
  email: string;
  fullName: string;
  roles: string[];
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface AuthResponse {
  token: string;
  user: User;
  expiresIn: number;
}

@Injectable({
  providedIn: 'root',
})
export class AuthService {
  private apiUrl = 'http://localhost:8000/api/auth';

  private currentUserSubject = new BehaviorSubject<User | null>(this.getUserFromStorage());
  currentUser$ = this.currentUserSubject.asObservable();

  isAuthenticated$ = this.currentUserSubject.pipe(map((user) => !!user));

  constructor(private http: HttpClient) {
    // Load user from storage on service initialization
    this.loadUserFromStorage();
  }

  login(credentials: LoginCredentials): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/login`, credentials).pipe(
      tap((response) => {
        this.setToken(response.token);
        this.currentUserSubject.next(response.user);
        localStorage.setItem('user', JSON.stringify(response.user));
      }),
    );
  }

  logout(): void {
    this.http.post(`${this.apiUrl}/logout`, {}).subscribe(
      () => {
        this.clearAuth();
      },
      (error) => {
        // Clear auth even if logout fails
        this.clearAuth();
      },
    );
  }

  register(userData: any): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/register`, userData).pipe(
      tap((response) => {
        this.setToken(response.token);
        this.currentUserSubject.next(response.user);
        localStorage.setItem('user', JSON.stringify(response.user));
      }),
    );
  }

  refreshToken(): Observable<AuthResponse> {
    return this.http.post<AuthResponse>(`${this.apiUrl}/refresh`, {}).pipe(
      tap((response) => {
        this.setToken(response.token);
        this.currentUserSubject.next(response.user);
      }),
    );
  }

  getToken(): string | null {
    return localStorage.getItem('auth_token');
  }

  private setToken(token: string): void {
    localStorage.setItem('auth_token', token);
  }

  private clearAuth(): void {
    localStorage.removeItem('auth_token');
    localStorage.removeItem('user');
    this.currentUserSubject.next(null);
  }

  private getUserFromStorage(): User | null {
    const userStr = localStorage.getItem('user');
    return userStr ? JSON.parse(userStr) : null;
  }

  private loadUserFromStorage(): void {
    const user = this.getUserFromStorage();
    if (user) {
      this.currentUserSubject.next(user);
    }
  }
}
