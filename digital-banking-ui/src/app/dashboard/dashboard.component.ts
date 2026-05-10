import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { RouterLink } from '@angular/router';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, RouterLink],
  template: `
    <div class="page-header">
      <h1>Dashboard</h1>
      <p>Welcome back, {{ userName }}</p>
    </div>

    <!-- Stats row -->
    <div class="stats-row">
      <div class="stat-card">
        <div class="label">Total Accounts</div>
        <div class="value">{{ accounts.length }}</div>
        <div class="sub">Active accounts</div>
      </div>
      <div class="stat-card">
        <div class="label">Total Balance</div>
        <div class="value">{{ totalBalance | currency:'INR':'symbol':'1.0-0' }}</div>
        <div class="sub">Across all accounts</div>
      </div>
      <div class="stat-card">
        <div class="label">Recent Transactions</div>
        <div class="value">{{ transactions.length }}</div>
        <div class="sub">Last loaded</div>
      </div>
      <div class="stat-card" *ngIf="platformStats">
        <div class="label">Platform Transactions</div>
        <div class="value">{{ platformStats.total_transactions || 0 }}</div>
        <div class="sub">All time</div>
      </div>
    </div>

    <div class="two-col">
      <!-- Accounts summary -->
      <div class="card">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>Your Accounts</span>
          <a routerLink="/accounts" class="btn btn-outline btn-sm">Manage</a>
        </div>
        <div *ngIf="accounts.length; else noAccounts">
          <div class="account-item" *ngFor="let a of accounts">
            <div class="account-info">
              <div class="account-type">{{ a.accountType }}</div>
              <div class="account-num font-mono">{{ a.accountNumber }}</div>
            </div>
            <div class="account-right">
              <div class="account-balance">{{ a.balance | currency:'INR':'symbol':'1.2-2' }}</div>
              <span class="badge" [class.badge-success]="a.status === 'ACTIVE'" [class.badge-gray]="a.status !== 'ACTIVE'">
                {{ a.status }}
              </span>
            </div>
          </div>
        </div>
        <ng-template #noAccounts>
          <div class="empty-state">
            <div>No accounts found.</div>
            <a routerLink="/accounts" class="btn btn-primary btn-sm mt-16">Open an Account</a>
          </div>
        </ng-template>
      </div>

      <!-- Recent transactions -->
      <div class="card">
        <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
          <span>Recent Transactions</span>
          <a routerLink="/transactions" class="btn btn-outline btn-sm">All</a>
        </div>
        <div *ngIf="recentTxns.length; else noTxns">
          <div class="txn-item" *ngFor="let t of recentTxns">
            <div class="txn-type-badge" [class.deposit]="t.type === 'DEPOSIT'" [class.withdrawal]="t.type === 'WITHDRAWAL'" [class.transfer]="t.type === 'TRANSFER'">
              {{ t.type?.charAt(0) || '?' }}
            </div>
            <div class="txn-info">
              <div class="txn-type">{{ t.type }}</div>
              <div class="txn-date text-muted">{{ t.createdAt | date:'MMM d, h:mm a' }}</div>
            </div>
            <div class="txn-amount" [class.text-success]="t.type === 'DEPOSIT'" [class.text-danger]="t.type !== 'DEPOSIT'">
              {{ t.type === 'DEPOSIT' ? '+' : '-' }}{{ t.amount | currency:'INR':'symbol':'1.2-2' }}
            </div>
          </div>
        </div>
        <ng-template #noTxns>
          <div class="empty-state">No recent transactions.</div>
        </ng-template>
      </div>
    </div>

    <!-- Quick actions -->
    <div class="card">
      <div class="card-title">Quick Actions</div>
      <div class="quick-actions">
        <a routerLink="/transactions" class="action-btn">
          <div class="action-icon deposit-icon">+</div>
          <span>Deposit</span>
        </a>
        <a routerLink="/transactions" class="action-btn">
          <div class="action-icon withdraw-icon">-</div>
          <span>Withdraw</span>
        </a>
        <a routerLink="/transactions" class="action-btn">
          <div class="action-icon transfer-icon">⇄</div>
          <span>Transfer</span>
        </a>
        <a routerLink="/kyc" class="action-btn">
          <div class="action-icon kyc-icon">◉</div>
          <span>KYC</span>
        </a>
        <a routerLink="/analytics" class="action-btn">
          <div class="action-icon analytics-icon">◫</div>
          <span>Analytics</span>
        </a>
        <a routerLink="/compliance" class="action-btn">
          <div class="action-icon compliance-icon">◆</div>
          <span>Compliance</span>
        </a>
      </div>
    </div>
  `,
  styles: [`
    .two-col { display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }

    .account-item {
      display: flex;
      justify-content: space-between;
      align-items: center;
      padding: 12px 0;
      border-bottom: 1px solid #f1f5f9;
    }
    .account-item:last-child { border-bottom: none; }
    .account-type { font-weight: 600; font-size: 13px; }
    .account-num { font-size: 12px; color: #64748b; margin-top: 2px; }
    .account-right { text-align: right; }
    .account-balance { font-weight: 700; font-size: 15px; margin-bottom: 4px; }

    .txn-item {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid #f1f5f9;
    }
    .txn-item:last-child { border-bottom: none; }
    .txn-type-badge {
      width: 34px;
      height: 34px;
      border-radius: 50%;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 13px;
      font-weight: 700;
      flex-shrink: 0;
    }
    .txn-type-badge.deposit { background: #dcfce7; color: #16a34a; }
    .txn-type-badge.withdrawal { background: #fee2e2; color: #dc2626; }
    .txn-type-badge.transfer { background: #dbeafe; color: #2563eb; }
    .txn-info { flex: 1; }
    .txn-type { font-size: 13px; font-weight: 500; }
    .txn-date { font-size: 11px; margin-top: 2px; }
    .txn-amount { font-weight: 600; font-size: 13px; }

    .quick-actions { display: grid; grid-template-columns: repeat(6, 1fr); gap: 12px; }
    .action-btn {
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 8px;
      padding: 16px 8px;
      background: #f8fafc;
      border-radius: 10px;
      text-decoration: none;
      color: #1e293b;
      font-size: 12px;
      font-weight: 500;
      transition: all 0.15s;
      cursor: pointer;
    }
    .action-btn:hover { background: #f1f5f9; transform: translateY(-1px); }
    .action-icon {
      width: 40px;
      height: 40px;
      border-radius: 10px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-size: 18px;
      font-weight: 700;
    }
    .deposit-icon { background: #dcfce7; color: #16a34a; }
    .withdraw-icon { background: #fee2e2; color: #dc2626; }
    .transfer-icon { background: #dbeafe; color: #2563eb; }
    .kyc-icon { background: #fef3c7; color: #d97706; }
    .analytics-icon { background: #cffafe; color: #0891b2; }
    .compliance-icon { background: #ede9fe; color: #7c3aed; }

    @media (max-width: 900px) {
      .two-col { grid-template-columns: 1fr; }
      .quick-actions { grid-template-columns: repeat(3, 1fr); }
    }
  `]
})
export class DashboardComponent implements OnInit {
  accounts: any[] = [];
  transactions: any[] = [];
  platformStats: any = null;

  get userName() { return this.api.getUserName() || 'there'; }
  get totalBalance() { return this.accounts.reduce((s, a) => s + (a.balance || 0), 0); }
  get recentTxns() { return this.transactions.slice(0, 5); }

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getAccounts().subscribe({
      next: (res: any) => { this.accounts = res.data || res || []; },
      error: () => {}
    });
    this.api.getTransactions().subscribe({
      next: (res: any) => { this.transactions = res.data || res || []; },
      error: () => {}
    });
    this.api.getPlatformSummary().subscribe({
      next: (res: any) => { this.platformStats = res; },
      error: () => {}
    });
  }
}
