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
          <div class="brand-icon">DB</div>
          <span class="brand-name">Digital Banking</span>
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
      background: #0f172a;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }

    .brand {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 20px 16px;
      border-bottom: 1px solid rgba(255,255,255,0.06);
    }
    .brand-icon {
      width: 34px;
      height: 34px;
      background: #2563eb;
      border-radius: 8px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 12px;
      font-weight: 800;
      color: #fff;
      letter-spacing: 0.05em;
      flex-shrink: 0;
    }
    .brand-name {
      font-size: 14px;
      font-weight: 600;
      color: #f1f5f9;
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
    .nav-link:hover { background: rgba(255,255,255,0.05); color: #e2e8f0; }
    .nav-link.active { background: rgba(37,99,235,0.2); color: #93c5fd; }
    .nav-link.active .nav-icon { color: #3b82f6; }

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
      color: #64748b;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }
    .logout-btn {
      width: 100%;
      padding: 8px;
      background: transparent;
      border: 1px solid rgba(255,255,255,0.1);
      border-radius: 6px;
      color: #94a3b8;
      font-size: 12px;
      cursor: pointer;
      transition: all 0.15s;
    }
    .logout-btn:hover { background: rgba(239,68,68,0.1); border-color: rgba(239,68,68,0.3); color: #f87171; }

    /* Main area */
    .main {
      display: flex;
      flex-direction: column;
      overflow: hidden;
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
