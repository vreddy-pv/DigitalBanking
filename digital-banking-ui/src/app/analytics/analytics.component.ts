import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

type TabKey = 'statement' | 'summary' | 'spending' | 'trial-balance' | 'platform';

@Component({
  selector: 'app-analytics',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-header">
      <h1>Analytics</h1>
      <p>Transaction statements, spending breakdowns, and ledger reports</p>
    </div>

    <div class="tabs">
      <button class="tab-btn" [class.active]="tab === 'statement'" (click)="tab = 'statement'">Statement</button>
      <button class="tab-btn" [class.active]="tab === 'summary'" (click)="tab = 'summary'">Monthly Summary</button>
      <button class="tab-btn" [class.active]="tab === 'spending'" (click)="tab = 'spending'">Spending</button>
      <button class="tab-btn" [class.active]="tab === 'trial-balance'" (click)="tab = 'trial-balance'; loadTrialBalance()">Trial Balance</button>
      <button class="tab-btn" [class.active]="tab === 'platform'" (click)="tab = 'platform'; loadPlatform()">Platform</button>
    </div>

    <!-- Account selector (for account-specific tabs) -->
    <div class="card" *ngIf="tab !== 'trial-balance' && tab !== 'platform'">
      <div style="display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap">
        <div class="form-group" style="flex:1;min-width:200px;margin-bottom:0">
          <label>Account</label>
          <select [(ngModel)]="selectedAccountId" *ngIf="accounts.length; else noAccSel">
            <option value="">-- Select account --</option>
            <option *ngFor="let a of accounts" [value]="a.id">{{ a.accountType }} — {{ a.accountNumber }}</option>
          </select>
          <ng-template #noAccSel>
            <input type="text" [(ngModel)]="selectedAccountId" placeholder="Account UUID">
          </ng-template>
        </div>
        <div class="form-group" style="margin-bottom:0" *ngIf="tab === 'summary'">
          <label>Month</label>
          <input type="month" [(ngModel)]="selectedMonth" style="width:160px">
        </div>
        <button class="btn btn-primary" (click)="loadActive()" [disabled]="!selectedAccountId || loading">
          {{ loading ? 'Loading…' : 'Load Data' }}
        </button>
      </div>
    </div>

    <!-- Statement tab -->
    <div class="card" *ngIf="tab === 'statement'">
      <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
        <span>Transaction Statement</span>
        <div style="display:flex;gap:8px">
          <button class="btn btn-outline btn-sm" (click)="statPage > 1 && (statPage = statPage - 1); loadStatement()" [disabled]="statPage <= 1">Prev</button>
          <span style="font-size:13px;padding:6px 10px">Page {{ statPage }}</span>
          <button class="btn btn-outline btn-sm" (click)="statPage = statPage + 1; loadStatement()">Next</button>
        </div>
      </div>
      <div *ngIf="statement.length; else noData" class="table-wrap">
        <table>
          <thead>
            <tr><th>Type</th><th>Amount</th><th>Description</th><th>Status</th><th>Date</th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let t of statement">
              <td><span class="badge" [class.badge-success]="t.type === 'DEPOSIT'" [class.badge-danger]="t.type === 'WITHDRAWAL'" [class.badge-primary]="t.type === 'TRANSFER'">{{ t.type }}</span></td>
              <td class="font-bold" [class.text-success]="t.type === 'DEPOSIT'" [class.text-danger]="t.type !== 'DEPOSIT'">
                {{ t.amount | currency:'INR':'symbol':'1.2-2' }}
              </td>
              <td class="text-muted">{{ t.description || '—' }}</td>
              <td><span class="badge badge-gray">{{ t.status }}</span></td>
              <td class="text-muted">{{ t.createdAt | date:'MMM d, y h:mm a' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <ng-template #noData><div class="empty-state">Select an account and click Load Data.</div></ng-template>
    </div>

    <!-- Monthly Summary tab -->
    <div class="card" *ngIf="tab === 'summary'">
      <div class="card-title">Monthly Summary</div>
      <div *ngIf="monthlySummary; else noData2">
        <div class="stats-row">
          <div class="stat-card">
            <div class="label">Total Credits</div>
            <div class="value text-success">{{ monthlySummary.total_credits | currency:'INR':'symbol':'1.0-0' }}</div>
          </div>
          <div class="stat-card">
            <div class="label">Total Debits</div>
            <div class="value text-danger">{{ monthlySummary.total_debits | currency:'INR':'symbol':'1.0-0' }}</div>
          </div>
          <div class="stat-card">
            <div class="label">Net Flow</div>
            <div class="value" [class.text-success]="monthlySummary.net_flow >= 0" [class.text-danger]="monthlySummary.net_flow < 0">
              {{ monthlySummary.net_flow | currency:'INR':'symbol':'1.0-0' }}
            </div>
          </div>
          <div class="stat-card">
            <div class="label">Transactions</div>
            <div class="value">{{ monthlySummary.transaction_count || 0 }}</div>
          </div>
        </div>
      </div>
      <ng-template #noData2><div class="empty-state">Select an account and month, then click Load Data.</div></ng-template>
    </div>

    <!-- Spending tab -->
    <div class="card" *ngIf="tab === 'spending'">
      <div class="card-title">Spending Breakdown</div>
      <div *ngIf="spending; else noData3">
        <div *ngFor="let item of spendingItems" class="spending-row">
          <div class="spending-label">{{ item.type }}</div>
          <div class="spending-bar-wrap">
            <div class="spending-bar" [style.width.%]="item.pct"></div>
          </div>
          <div class="spending-amount">{{ item.amount | currency:'INR':'symbol':'1.0-0' }}</div>
          <div class="spending-pct text-muted">{{ item.pct | number:'1.0-0' }}%</div>
        </div>
      </div>
      <ng-template #noData3><div class="empty-state">Select an account and click Load Data.</div></ng-template>
    </div>

    <!-- Trial Balance tab -->
    <div class="card" *ngIf="tab === 'trial-balance'">
      <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
        <span>Ledger Trial Balance</span>
        <button class="btn btn-outline btn-sm" (click)="loadTrialBalance()">Refresh</button>
      </div>
      <div *ngIf="trialBalance.length; else noTB" class="table-wrap">
        <table>
          <thead>
            <tr><th>Account Code</th><th>Account Name</th><th>Debit</th><th>Credit</th><th>Balance</th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let row of trialBalance">
              <td class="font-mono">{{ row.account_code || row.accountCode }}</td>
              <td>{{ row.account_name || row.accountName }}</td>
              <td class="text-right">{{ (row.total_debits || row.totalDebits || 0) | currency:'INR':'symbol':'1.2-2' }}</td>
              <td class="text-right">{{ (row.total_credits || row.totalCredits || 0) | currency:'INR':'symbol':'1.2-2' }}</td>
              <td class="text-right font-bold">{{ (row.balance || 0) | currency:'INR':'symbol':'1.2-2' }}</td>
            </tr>
          </tbody>
          <tfoot>
            <tr class="totals-row">
              <td colspan="2" class="font-bold">TOTALS</td>
              <td class="text-right font-bold">{{ totalDebits | currency:'INR':'symbol':'1.2-2' }}</td>
              <td class="text-right font-bold">{{ totalCredits | currency:'INR':'symbol':'1.2-2' }}</td>
              <td></td>
            </tr>
          </tfoot>
        </table>
      </div>
      <ng-template #noTB><div class="empty-state">No ledger entries found.</div></ng-template>
    </div>

    <!-- Platform tab -->
    <div class="card" *ngIf="tab === 'platform'">
      <div class="card-title">Platform Statistics</div>
      <div *ngIf="platformStats; else noPlatform">
        <div class="stats-row">
          <div class="stat-card" *ngFor="let s of platformStatItems">
            <div class="label">{{ s.label }}</div>
            <div class="value">{{ s.value }}</div>
          </div>
        </div>
        <pre class="raw-json" *ngIf="showRaw">{{ platformStats | json }}</pre>
        <button class="btn btn-outline btn-sm mt-16" (click)="showRaw = !showRaw">{{ showRaw ? 'Hide' : 'Show' }} Raw JSON</button>
      </div>
      <ng-template #noPlatform><div class="empty-state">No platform data available.</div></ng-template>
    </div>
  `,
  styles: [`
    .font-bold { font-weight: 700; }

    .spending-row {
      display: flex;
      align-items: center;
      gap: 12px;
      padding: 10px 0;
      border-bottom: 1px solid #f1f5f9;
    }
    .spending-label { width: 120px; font-size: 13px; font-weight: 500; flex-shrink: 0; }
    .spending-bar-wrap { flex: 1; height: 8px; background: #f1f5f9; border-radius: 4px; overflow: hidden; }
    .spending-bar { height: 100%; background: #2563eb; border-radius: 4px; transition: width 0.5s; }
    .spending-amount { width: 100px; text-align: right; font-weight: 600; font-size: 13px; }
    .spending-pct { width: 44px; text-align: right; font-size: 12px; }

    tfoot td { padding: 10px 12px; font-size: 13px; border-top: 2px solid #e2e8f0; background: #f8fafc; }

    .raw-json {
      background: #f8fafc;
      border: 1px solid #e2e8f0;
      border-radius: 6px;
      padding: 12px;
      font-size: 11px;
      overflow-x: auto;
      margin-top: 12px;
    }
  `]
})
export class AnalyticsComponent implements OnInit {
  tab: TabKey = 'statement';
  accounts: any[] = [];
  selectedAccountId = '';
  selectedMonth = new Date().toISOString().slice(0, 7);
  statPage = 1;
  loading = false;
  showRaw = false;

  statement: any[] = [];
  monthlySummary: any = null;
  spending: any = null;
  trialBalance: any[] = [];
  platformStats: any = null;

  get spendingItems(): any[] {
    if (!this.spending) return [];
    const entries = Object.entries(this.spending) as [string, number][];
    const total = entries.reduce((s, [, v]) => s + v, 0);
    return entries.map(([type, amount]) => ({ type, amount, pct: total ? (amount / total * 100) : 0 }))
      .sort((a, b) => b.amount - a.amount);
  }

  get totalDebits(): number {
    return this.trialBalance.reduce((s, r) => s + (r.total_debits || r.totalDebits || 0), 0);
  }
  get totalCredits(): number {
    return this.trialBalance.reduce((s, r) => s + (r.total_credits || r.totalCredits || 0), 0);
  }

  get platformStatItems(): { label: string; value: string }[] {
    if (!this.platformStats) return [];
    return Object.entries(this.platformStats).map(([k, v]) => ({
      label: k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase()),
      value: String(v)
    }));
  }

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getAccounts().subscribe({
      next: (res: any) => { this.accounts = res.data || res || []; },
      error: () => {}
    });
  }

  loadActive() {
    if (this.tab === 'statement') this.loadStatement();
    else if (this.tab === 'summary') this.loadSummary();
    else if (this.tab === 'spending') this.loadSpending();
  }

  loadStatement() {
    if (!this.selectedAccountId) return;
    this.loading = true;
    this.api.getStatement(this.selectedAccountId, this.statPage).subscribe({
      next: (res: any) => { this.statement = res.data || res || []; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  loadSummary() {
    if (!this.selectedAccountId) return;
    this.loading = true;
    this.api.getSummary(this.selectedAccountId, this.selectedMonth).subscribe({
      next: (res: any) => { this.monthlySummary = res.data || res; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  loadSpending() {
    if (!this.selectedAccountId) return;
    this.loading = true;
    this.api.getSpending(this.selectedAccountId).subscribe({
      next: (res: any) => { this.spending = res.data || res; this.loading = false; },
      error: () => { this.loading = false; }
    });
  }

  loadTrialBalance() {
    this.api.getTrialBalance().subscribe({
      next: (res: any) => { this.trialBalance = res.data || res || []; },
      error: () => {}
    });
  }

  loadPlatform() {
    this.api.getPlatformSummary().subscribe({
      next: (res: any) => { this.platformStats = res.data || res; },
      error: () => {}
    });
  }
}
