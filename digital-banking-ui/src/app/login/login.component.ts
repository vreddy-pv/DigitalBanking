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
          <svg class="brand-icon" width="52" height="52" viewBox="0 0 52 52" xmlns="http://www.w3.org/2000/svg">
            <defs>
              <linearGradient id="lHex" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#26215C"/>
                <stop offset="100%" stop-color="#3C3489"/>
              </linearGradient>
            </defs>
            <rect width="52" height="52" rx="14" fill="#26215C"/>
            <polygon points="26,5 47,17 47,35 26,47 5,35 5,17" fill="url(#lHex)" stroke="#534AB7" stroke-width="1"/>
            <ellipse cx="26" cy="30" rx="13" ry="5" fill="none" stroke="#5DCAA5" stroke-width="0.8"/>
            <ellipse cx="26" cy="30" rx="8" ry="3" fill="none" stroke="#9FE1CB" stroke-width="0.5"/>
            <polyline points="13,17 26,34 39,17" fill="none" stroke="white" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="26" cy="14" r="3.5" fill="#3C3489"/>
            <circle cx="26" cy="14" r="2.5" fill="#EF9F27"/>
            <circle cx="26" cy="14" r="1.2" fill="#FAC775"/>
          </svg>
          <div>
            <div class="brand-title">VRGT</div>
            <div class="brand-full">Vertex Realm Global Technologies</div>
            <div class="brand-sub">At the peak of every digital realm.</div>
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
      background: linear-gradient(135deg, #0d0b24 0%, #1a1646 50%, #0d0b24 100%);
      padding: 20px;
    }

    .card {
      background: #fff;
      border-radius: 18px;
      box-shadow: 0 24px 64px rgba(38, 33, 92, 0.45);
      padding: 36px 32px;
      width: 100%;
      max-width: 420px;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 14px;
      margin-bottom: 28px;
    }
    .brand-icon {
      flex-shrink: 0;
    }
    .brand-title {
      font-size: 22px;
      font-weight: 700;
      letter-spacing: 0.08em;
      background: linear-gradient(90deg, #26215C 0%, #7F77DD 55%, #1D9E75 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      background-clip: text;
      line-height: 1.1;
    }
    .brand-full {
      font-size: 10px;
      font-weight: 600;
      color: #534AB7;
      letter-spacing: 0.05em;
      text-transform: uppercase;
      margin-top: 2px;
    }
    .brand-sub { font-size: 11px; color: #888780; margin-top: 3px; font-style: italic; }

    .tabs {
      display: flex;
      background: #EEEDFE;
      border-radius: 10px;
      padding: 4px;
      margin-bottom: 22px;
    }
    .tab {
      flex: 1;
      padding: 8px;
      background: transparent;
      border: none;
      border-radius: 8px;
      font-size: 13px;
      font-weight: 500;
      color: #888780;
      cursor: pointer;
      transition: all 0.15s;
    }
    .tab.active {
      background: #fff;
      color: #534AB7;
      box-shadow: 0 2px 8px rgba(83, 74, 183, 0.14);
      font-weight: 600;
    }

    .alert {
      padding: 11px 13px;
      border-radius: 10px;
      font-size: 13px;
      margin-bottom: 14px;
    }
    .alert-success { background: #dcfce7; color: #15803d; border: 1px solid #bbf7d0; }
    .alert-danger { background: #fee2e2; color: #b91c1c; border: 1px solid #fecaca; }

    .form-group { margin-bottom: 14px; }
    label { display: block; font-size: 13px; font-weight: 600; color: #26215C; margin-bottom: 6px; }
    input {
      width: 100%;
      padding: 11px 13px;
      border: 1px solid #D3D1C7;
      border-radius: 10px;
      font-size: 14px;
      color: #2C2C2A;
      transition: border-color 0.15s, box-shadow 0.15s;
    }
    input:focus {
      outline: none;
      border-color: #534AB7;
      box-shadow: 0 0 0 3px rgba(83, 74, 183, 0.12);
    }

    .btn-submit {
      width: 100%;
      padding: 12px;
      background: linear-gradient(135deg, #534AB7, #1D9E75);
      color: #fff;
      border: none;
      border-radius: 999px;
      font-size: 14px;
      font-weight: 700;
      cursor: pointer;
      margin-top: 6px;
      transition: opacity 0.15s, transform 0.15s;
      letter-spacing: 0.03em;
    }
    .btn-submit:hover:not(:disabled) { opacity: 0.9; transform: translateY(-1px); }
    .btn-submit:disabled { opacity: 0.6; cursor: not-allowed; }

    .footer-note {
      text-align: center;
      font-size: 11px;
      color: #AFA9EC;
      margin-top: 20px;
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
