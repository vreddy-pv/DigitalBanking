import { Component, EventEmitter, Output } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="login-container">
      <div class="login-card">
        <h1>💳 Digital Banking</h1>

        <div *ngIf="error" class="alert alert-danger">{{ error }}</div>

        <div class="tabs">
          <button [class.active]="isLogin" (click)="toggleMode()">Login</button>
          <button [class.active]="!isLogin" (click)="toggleMode()">Register</button>
        </div>

        <form (ngSubmit)="isLogin ? submitLogin() : submitRegister()">
          <div class="form-group">
            <label>Email</label>
            <input type="email" [(ngModel)]="email" name="email" required>
          </div>

          <div class="form-group">
            <label>Password</label>
            <input type="password" [(ngModel)]="password" name="password" required>
          </div>

          <div class="form-group" *ngIf="!isLogin">
            <label>Full Name</label>
            <input type="text" [(ngModel)]="fullName" name="fullName">
          </div>

          <button type="submit" class="btn btn-primary" [disabled]="loading">
            {{ loading ? 'Please wait...' : (isLogin ? 'Login' : 'Register') }}
          </button>
        </form>
      </div>
    </div>
  `,
  styles: [`
    .login-container {
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }

    .login-card {
      background: white;
      padding: 40px;
      border-radius: 8px;
      box-shadow: 0 10px 25px rgba(0,0,0,0.2);
      width: 100%;
      max-width: 400px;
    }

    h1 {
      text-align: center;
      color: #333;
      margin-bottom: 30px;
      font-size: 24px;
    }

    .tabs {
      display: flex;
      gap: 10px;
      margin-bottom: 20px;
    }

    .tabs button {
      flex: 1;
      padding: 10px;
      border: 2px solid #ddd;
      background: white;
      cursor: pointer;
      border-radius: 4px;
      font-weight: 500;
    }

    .tabs button.active {
      background: #667eea;
      color: white;
      border-color: #667eea;
    }

    .form-group {
      margin-bottom: 15px;
    }

    label {
      display: block;
      margin-bottom: 5px;
      font-weight: 500;
      color: #333;
    }

    input {
      width: 100%;
      padding: 10px;
      border: 1px solid #ddd;
      border-radius: 4px;
      font-size: 14px;
    }

    input:focus {
      outline: none;
      border-color: #667eea;
    }

    .btn {
      width: 100%;
      padding: 12px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 4px;
      font-size: 14px;
      font-weight: 500;
      cursor: pointer;
      margin-top: 10px;
    }

    .btn:hover:not(:disabled) {
      background: #5568d3;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    .alert {
      padding: 12px;
      border-radius: 4px;
      margin-bottom: 15px;
      background: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }
  `]
})
export class LoginComponent {
  @Output() loginSuccess = new EventEmitter<string>();

  email = '';
  password = '';
  fullName = '';
  isLogin = true;
  error = '';
  loading = false;

  constructor(private apiService: ApiService) {}

  toggleMode() {
    this.isLogin = !this.isLogin;
    this.error = '';
  }

  submitLogin() {
    this.loading = true;
    this.error = '';

    this.apiService.login(this.email, this.password).subscribe(
      (response: any) => {
        const token = response.data?.accessToken || response.accessToken;
        if (token) {
          this.apiService.setToken(token);
          this.loginSuccess.emit(token);
        } else {
          this.error = 'Login failed: No token received';
        }
        this.loading = false;
      },
      (error: any) => {
        this.error = error.error?.message || 'Login failed. Please try again.';
        this.loading = false;
      }
    );
  }

  submitRegister() {
    this.loading = true;
    this.error = '';

    this.apiService.register(this.email, this.password, this.fullName).subscribe(
      (response: any) => {
        this.error = '';
        this.isLogin = true;
        this.password = '';
        this.loading = false;
      },
      (error: any) => {
        this.error = error.error?.message || 'Registration failed. Please try again.';
        this.loading = false;
      }
    );
  }
}
