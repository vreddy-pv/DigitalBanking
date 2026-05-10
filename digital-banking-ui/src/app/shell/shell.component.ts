import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterOutlet, RouterLink, RouterLinkActive, Router } from '@angular/router';
import { ApiService } from '../api.service';

interface NavItem {
  label: string;
  path: string;
  icon: string;
}

@Component({
  selector: 'app-shell',
  standalone: true,
  imports: [CommonModule, RouterOutlet, RouterLink, RouterLinkActive],
  template: `
    <div class="shell">
      <aside class="sidebar">
        <div class="brand">
          <svg width="34" height="34" viewBox="0 0 34 34" xmlns="http://www.w3.org/2000/svg" style="flex-shrink:0">
            <defs>
              <linearGradient id="sHex" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#26215C"/>
                <stop offset="100%" stop-color="#3C3489"/>
              </linearGradient>
            </defs>
            <rect width="34" height="34" rx="10" fill="#3C3489"/>
            <polygon points="17,3 30,10 30,24 17,31 4,24 4,10" fill="url(#sHex)" stroke="#534AB7" stroke-width="0.7"/>
            <ellipse cx="17" cy="19" rx="8.5" ry="3" fill="none" stroke="#5DCAA5" stroke-width="0.7"/>
            <ellipse cx="17" cy="19" rx="5" ry="2" fill="none" stroke="#9FE1CB" stroke-width="0.5"/>
            <polyline points="8,11 17,22 26,11" fill="none" stroke="white" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <circle cx="17" cy="9" r="2.4" fill="#3C3489"/>
            <circle cx="17" cy="9" r="1.7" fill="#EF9F27"/>
            <circle cx="17" cy="9" r="0.9" fill="#FAC775"/>
          </svg>
          <div class="brand-text">
            <span class="brand-name">VRGT</span>
            <span class="brand-sub">Digital Banking</span>
          </div>
        </div>

        <nav class="nav">
          <a
            *ngFor="let item of navItems"
            [routerLink]="item.path"
            routerLinkActive="active"
            class="nav-link"
          >
            <span class="nav-icon">{{ item.icon }}</span>
            <span>{{ item.label }}</span>
          </a>
        </nav>

        <div class="sidebar-footer">
          <div class="user-info">
            <div class="user-avatar">{{ initials }}</div>
            <div class="user-details">
              <div class="user-name">{{ userName }}</div>
              <div class="user-email">{{ userEmail }}</div>
            </div>
          </div>
          <button class="logout-btn" (click)="logout()">Sign out</button>
        </div>
      </aside>

      <div class="main">
        <header class="topbar">
          <div class="topbar-left">
            <div class="breadcrumb">{{ currentLabel }}</div>
          </div>
          <div class="topbar-right">
            <span class="env-badge">Development</span>
          </div>
        </header>
        <main class="content">
          <router-outlet></router-outlet>
        </main>
      </div>
    </div>
  `,
  styles: [`
    .shell {
      display: grid;
      grid-template-columns: 240px 1fr;
      height: 100vh;
      overflow: hidden;
    }

    /* Sidebar */
    .sidebar {
      background: linear-gradient(180deg, #1f204f 0%, #171b3f 100%);
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 18px 16px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .brand-text {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .brand-name {
      font-size: 16px;
      font-weight: 700;
      color: #f8f8ff;
      letter-spacing: 0.12em;
      white-space: nowrap;
      line-height: 1.1;
    }
    .brand-sub {
      font-size: 10px;
      font-weight: 500;
      color: #5DCAA5;
      letter-spacing: 0.06em;
      text-transform: uppercase;
      margin-top: 2px;
      white-space: nowrap;
    }

    .nav {
      flex: 1;
      padding: 12px 8px;
      display: flex;
      flex-direction: column;
      gap: 2px;
      overflow-y: auto;
    }

    .nav-link {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 9px 10px;
      border-radius: 7px;
      color: #94a3b8;
      text-decoration: none;
      font-size: 13px;
      font-weight: 500;
      transition: all 0.15s;
    }
    .nav-link:hover { background: rgba(83, 74, 183, 0.18); color: #f8f8ff; }
    .nav-link.active { background: rgba(83, 74, 183, 0.3); color: #fff; }
    .nav-link.active .nav-icon { color: #1d9e75; }

    .nav-icon {
      width: 20px;
      text-align: center;
      font-size: 15px;
      flex-shrink: 0;
    }

    .sidebar-footer {
      padding: 12px 8px;
      border-top: 1px solid rgba(255,255,255,0.06);
    }
    .user-info {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 10px;
      margin-bottom: 6px;
    }
    .user-avatar {
      width: 32px;
      height: 32px;
      background: #334155;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 600;
      color: #94a3b8;
      flex-shrink: 0;
    }
    .user-details { overflow: hidden; }
    .user-name {
      font-size: 13px;
      font-weight: 500;
      color: #e2e8f0;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .user-email {
      font-size: 11px;
      color: #94a3b8;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .logout-btn {
      width: 100%;
      padding: 10px 12px;
      border-radius: 10px;
      background: linear-gradient(135deg, #534ab7, #1d9e75);
      color: #fff;
      border: none;
      font-weight: 700;
      cursor: pointer;
      transition: background 0.2s ease;
    }
    .logout-btn:hover {
      background: linear-gradient(135deg, #3e349f, #17795f);
    }

    /* Main area */
    .main {
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    .topbar {
      background: #ffffff;
      border-bottom: 1px solid rgba(83, 74, 183, 0.08);
      padding: 0 24px;
      height: 64px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
      box-shadow: 0 1px 0 rgba(83, 74, 183, 0.05);
    }
    .breadcrumb {
      font-size: 15px;
      font-weight: 600;
      color: var(--vrgt-dark-purple, #1e293b);
    }
    .env-badge {
      font-size: 11px;
      font-weight: 700;
      background: #eff6ff;
      color: #2563eb;
      padding: 4px 12px;
      border-radius: 999px;
      border: 1px solid rgba(37, 99, 235, 0.18);
    }

    .content {
      flex: 1;
      overflow-y: auto;
      background: linear-gradient(180deg, #f7f6ff 0%, #f5f5ff 100%);
      padding: 28px;
    }

    .topbar {
      background: #fff;
      border-bottom: 1px solid #e2e8f0;
      padding: 0 24px;
      height: 56px;
      display: flex;
      align-items: center;
      justify-content: space-between;
      flex-shrink: 0;
    }
    .breadcrumb {
      font-size: 15px;
      font-weight: 600;
      color: #1e293b;
    }
    .env-badge {
      font-size: 11px;
      font-weight: 500;
      background: #fef3c7;
      color: #92400e;
      padding: 3px 10px;
      border-radius: 99px;
      border: 1px solid #fde68a;
    }

    .content {
      flex: 1;
      overflow-y: auto;
      background: #f1f5f9;
      padding: 24px;
    }
  `]
})
export class ShellComponent {
  navItems: NavItem[] = [
    { label: 'Dashboard', path: '/dashboard', icon: '▣' },
    { label: 'Accounts', path: '/accounts', icon: '◈' },
    { label: 'Transactions', path: '/transactions', icon: '⇄' },
    { label: 'KYC & Profile', path: '/kyc', icon: '◉' },
    { label: 'Analytics', path: '/analytics', icon: '◫' },
    { label: 'Compliance', path: '/compliance', icon: '◆' },
    { label: 'Audit Trail', path: '/audit', icon: '◎' },
  ];

  get userName(): string { return this.api.getUserName() || 'User'; }
  get userEmail(): string { return this.api.getUserEmail() || ''; }
  get initials(): string {
    return (this.api.getUserName() || 'U').split(' ').map(w => w[0]).join('').toUpperCase().slice(0, 2);
  }
  get currentLabel(): string {
    const path = window.location.pathname.replace('/', '');
    const item = this.navItems.find(n => n.path === '/' + path);
    return item?.label || 'Dashboard';
  }

  constructor(private api: ApiService, private router: Router) {}

  logout() {
    this.api.logout();
    this.router.navigate(['/login']);
  }
}
