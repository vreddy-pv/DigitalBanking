import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { Router } from '@angular/router';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-login',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page">
      <div class="card">
        <div class="brand">
          <div class="brand-icon">DB</div>
          <div>
            <div class="brand-title">Digital Banking</div>
            <div class="brand-sub">Secure. Modern. Reliable.</div>
          </div>
        </div>

        <div class="tabs">
          <button class="tab" [class.active]="mode === 'login'" (click)="mode = 'login'; clearMsg()">Sign In</button>
          <button class="tab" [class.active]="mode === 'register'" (click)="mode = 'register'; clearMsg()">Create Account</button>
        </div>

        <div *ngIf="msg" class="alert" [class.alert-success]="!isError" [class.alert-danger]="isError">
          {{ msg }}
        </div>

        <form (ngSubmit)="submit()" #f="ngForm">
          <div *ngIf="mode === 'register'" class="form-group">
            <label>Full Name</label>
            <input type="text" [(ngModel)]="fullName" name="fullName" placeholder="Jane Doe" required>
          </div>
          <div class="form-group">
            <label>Email Address</label>
            <input type="email" [(ngModel)]="email" name="email" placeholder="you@example.com" required>
          </div>
          <div class="form-group">
            <label>Password</label>
            <input type="password" [(ngModel)]="password" name="password" placeholder="••••••••" required>
          </div>
          <button type="submit" class="btn-submit" [disabled]="loading">
            {{ loading ? 'Please wait…' : (mode === 'login' ? 'Sign In' : 'Create Account') }}
          </button>
        </form>

        <p class="footer-note">
          Protected by 256-bit TLS encryption
        </p>
      </div>
    </div>
  `,
  styles: [`
    .page {
      min-height: 100vh;
      display: flex;
      align-items: center;
      justify-content: center;
      background: linear-gradient(135deg, #0f172a 0%, #1e3a5f 50%, #0f172a 100%);
      padding: 20px;
    }

    .card {
      background: #fff;
      border-radius: 14px;
      box-shadow: 0 20px 60px rgba(0,0,0,0.3);
      padding: 36px 32px;
      width: 100%;
      max-width: 400px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 28px;
    }
    .brand-icon {
      width: 44px;
      height: 44px;
      background: #2563eb;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 14px;
      font-weight: 800;
      color: #fff;
      letter-spacing: 0.05em;
      flex-shrink: 0;
    }
    .brand-title { font-size: 18px; font-weight: 700; color: #1e293b; }
    .brand-sub { font-size: 12px; color: #64748b; margin-top: 2px; }

    .tabs {
      display: flex;
      background: #f1f5f9;
      border-radius: 8px;
      padding: 4px;
      margin-bottom: 22px;
    }
    .tab {
      flex: 1;
      padding: 8px;
      background: transparent;
      border: none;
      border-radius: 6px;
      font-size: 13px;
      font-weight: 500;
      color: #64748b;
      cursor: pointer;
      transition: all 0.15s;
    }
    .tab.active {
      background: #fff;
      color: #2563eb;
      box-shadow: 0 1px 3px rgba(0,0,0,0.1);
    }

    .alert {
      padding: 11px 13px;
      border-radius: 6px;
      font-size: 13px;
      margin-bottom: 14px;
    }
    .alert-success { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .alert-danger { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

    .form-group { margin-bottom: 14px; }
    label { display: block; font-size: 13px; font-weight: 500; color: #374151; margin-bottom: 5px; }
    input {
      width: 100%;
      padding: 10px 12px;
      border: 1px solid #d1d5db;
      border-radius: 7px;
      font-size: 14px;
      color: #1e293b;
      transition: border-color 0.15s, box-shadow 0.15s;
    }
    input:focus {
      outline: none;
      border-color: #2563eb;
      box-shadow: 0 0 0 3px rgba(37,99,235,0.1);
    }

    .btn-submit {
      width: 100%;
      padding: 11px;
      background: #2563eb;
      color: #fff;
      border: none;
      border-radius: 7px;
      font-size: 14px;
      font-weight: 600;
      cursor: pointer;
      margin-top: 4px;
      transition: background 0.15s, opacity 0.15s;
    }
    .btn-submit:hover:not(:disabled) { background: #1d4ed8; }
    .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

    .footer-note {
      text-align: center;
      font-size: 11px;
      color: #94a3b8;
      margin-top: 18px;
    }
  `]
})
export class LoginComponent {
  mode: 'login' | 'register' = 'login';
  email = '';
  password = '';
  fullName = '';
  msg = '';
  isError = false;
  loading = false;

  constructor(private api: ApiService, private router: Router) {
    if (this.api.isLoggedIn()) this.router.navigate(['/dashboard']);
  }

  clearMsg() { this.msg = ''; }

  submit() {
    this.loading = true;
    this.msg = '';
    if (this.mode === 'login') {
      this.api.login(this.email, this.password).subscribe({
        next: (res: any) => {
          const token = res.data?.accessToken || res.accessToken;
          const userId = res.data?.userId || res.userId || res.data?.id || res.id;
          const name = res.data?.fullName || res.fullName || res.data?.name || res.name || this.email;
          if (token) {
            this.api.setToken(token);
            if (userId) this.api.setUserId(userId);
            this.api.setUserEmail(this.email);
            this.api.setUserName(name);
            this.router.navigate(['/dashboard']);
          } else {
            this.msg = 'Login failed: no token received';
            this.isError = true;
          }
          this.loading = false;
        },
        error: (err: any) => {
          this.msg = err.error?.message || 'Invalid email or password';
          this.isError = true;
          this.loading = false;
        }
      });
    } else {
      this.api.register(this.email, this.password, this.fullName).subscribe({
        next: () => {
          this.msg = 'Account created! You can now sign in.';
          this.isError = false;
          this.mode = 'login';
          this.password = '';
          this.loading = false;
        },
        error: (err: any) => {
          this.msg = err.error?.message || 'Registration failed';
          this.isError = true;
          this.loading = false;
        }
      });
    }
  }
}
