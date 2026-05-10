import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

type TabKey = 'deposit' | 'withdraw' | 'transfer' | 'history';

@Component({
  selector: 'app-transactions',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-header">
      <h1>Transactions</h1>
      <p>Deposit, withdraw, transfer funds and view your history</p>
    </div>

    <div *ngIf="msg" class="alert" [class.alert-success]="!isError" [class.alert-danger]="isError">{{ msg }}</div>

    <div class="tabs">
      <button class="tab-btn" [class.active]="tab === 'deposit'" (click)="tab = 'deposit'; clearMsg()">Deposit</button>
      <button class="tab-btn" [class.active]="tab === 'withdraw'" (click)="tab = 'withdraw'; clearMsg()">Withdraw</button>
      <button class="tab-btn" [class.active]="tab === 'transfer'" (click)="tab = 'transfer'; clearMsg()">Transfer</button>
      <button class="tab-btn" [class.active]="tab === 'history'" (click)="tab = 'history'; loadTxns()">History</button>
    </div>

    <!-- Deposit -->
    <div class="card" *ngIf="tab === 'deposit'">
      <div class="card-title">Deposit Funds</div>
      <div style="max-width:440px">
        <div class="form-group">
          <label>Destination Account</label>
          <select [(ngModel)]="deposit.accountId" *ngIf="accounts.length; else noAccSel">
            <option value="">-- Select account --</option>
            <option *ngFor="let a of accounts" [value]="a.id">{{ a.accountType }} — {{ a.accountNumber }} ({{ a.balance | currency:'INR':'symbol':'1.0-0' }})</option>
          </select>
          <ng-template #noAccSel>
            <input type="text" [(ngModel)]="deposit.accountId" placeholder="Enter Account ID (UUID)">
          </ng-template>
        </div>
        <div class="form-group">
          <label>Amount (INR)</label>
          <input type="number" [(ngModel)]="deposit.amount" placeholder="0.00" min="1">
        </div>
        <div class="form-group">
          <label>Description (optional)</label>
          <input type="text" [(ngModel)]="deposit.description" placeholder="e.g. Salary credit">
        </div>
        <button class="btn btn-success" (click)="doDeposit()" [disabled]="loading">
          {{ loading ? 'Processing…' : 'Deposit Funds' }}
        </button>
      </div>
    </div>

    <!-- Withdraw -->
    <div class="card" *ngIf="tab === 'withdraw'">
      <div class="card-title">Withdraw Funds</div>
      <div style="max-width:440px">
        <div class="form-group">
          <label>Source Account</label>
          <select [(ngModel)]="withdraw.accountId" *ngIf="accounts.length; else noAccSel2">
            <option value="">-- Select account --</option>
            <option *ngFor="let a of accounts" [value]="a.id">{{ a.accountType }} — {{ a.accountNumber }} ({{ a.balance | currency:'INR':'symbol':'1.0-0' }})</option>
          </select>
          <ng-template #noAccSel2>
            <input type="text" [(ngModel)]="withdraw.accountId" placeholder="Enter Account ID (UUID)">
          </ng-template>
        </div>
        <div class="form-group">
          <label>Amount (INR)</label>
          <input type="number" [(ngModel)]="withdraw.amount" placeholder="0.00" min="1">
        </div>
        <div class="form-group">
          <label>Description (optional)</label>
          <input type="text" [(ngModel)]="withdraw.description" placeholder="e.g. ATM withdrawal">
        </div>
        <button class="btn btn-danger" (click)="doWithdraw()" [disabled]="loading">
          {{ loading ? 'Processing…' : 'Withdraw Funds' }}
        </button>
      </div>
    </div>

    <!-- Transfer -->
    <div class="card" *ngIf="tab === 'transfer'">
      <div class="card-title">Transfer Funds</div>
      <div style="max-width:440px">
        <div class="form-group">
          <label>From Account</label>
          <select [(ngModel)]="transfer.fromId" *ngIf="accounts.length; else noAccSel3">
            <option value="">-- Select account --</option>
            <option *ngFor="let a of accounts" [value]="a.id">{{ a.accountType }} — {{ a.accountNumber }} ({{ a.balance | currency:'INR':'symbol':'1.0-0' }})</option>
          </select>
          <ng-template #noAccSel3>
            <input type="text" [(ngModel)]="transfer.fromId" placeholder="From Account ID">
          </ng-template>
        </div>
        <div class="form-group">
          <label>To Account ID</label>
          <input type="text" [(ngModel)]="transfer.toId" placeholder="Recipient account UUID">
          <div class="field-hint">Enter the destination account's UUID</div>
        </div>
        <div class="form-group">
          <label>Amount (INR)</label>
          <input type="number" [(ngModel)]="transfer.amount" placeholder="0.00" min="1">
        </div>
        <div class="form-group">
          <label>Description (optional)</label>
          <input type="text" [(ngModel)]="transfer.description" placeholder="e.g. Rent payment">
        </div>
        <button class="btn btn-primary" (click)="doTransfer()" [disabled]="loading">
          {{ loading ? 'Processing…' : 'Transfer Funds' }}
        </button>
      </div>
    </div>

    <!-- History -->
    <div class="card" *ngIf="tab === 'history'">
      <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
        <span>Transaction History</span>
        <button class="btn btn-outline btn-sm" (click)="loadTxns()">Refresh</button>
      </div>
      <div *ngIf="transactions.length; else noTxns" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Amount</th>
              <th>Account</th>
              <th>Description</th>
              <th>Status</th>
              <th>Date</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let t of transactions">
              <td>
                <span class="badge"
                  [class.badge-success]="t.type === 'DEPOSIT'"
                  [class.badge-danger]="t.type === 'WITHDRAWAL'"
                  [class.badge-primary]="t.type === 'TRANSFER'">
                  {{ t.type }}
                </span>
              </td>
              <td class="font-bold" [class.text-success]="t.type === 'DEPOSIT'" [class.text-danger]="t.type === 'WITHDRAWAL'">
                {{ t.amount | currency:'INR':'symbol':'1.2-2' }}
              </td>
              <td class="font-mono" style="font-size:11px">{{ t.fromAccountId || t.toAccountId || t.accountId || '—' }}</td>
              <td class="text-muted">{{ t.description || '—' }}</td>
              <td>
                <span class="badge" [class.badge-success]="t.status === 'COMPLETED'" [class.badge-warning]="t.status === 'PENDING'" [class.badge-danger]="t.status === 'FAILED'">
                  {{ t.status }}
                </span>
              </td>
              <td class="text-muted">{{ t.createdAt | date:'MMM d, y h:mm a' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <ng-template #noTxns>
        <div class="empty-state">
          <div class="icon">⇄</div>
          <div>No transactions found.</div>
        </div>
      </ng-template>
    </div>
  `,
  styles: [`
    .font-bold { font-weight: 700; }
    .field-hint { font-size: 11px; color: #94a3b8; margin-top: 4px; }
  `]
})
export class TransactionsComponent implements OnInit {
  tab: TabKey = 'deposit';
  accounts: any[] = [];
  transactions: any[] = [];
  loading = false;
  msg = '';
  isError = false;

  deposit = { accountId: '', amount: null as number | null, description: 'Deposit' };
  withdraw = { accountId: '', amount: null as number | null, description: 'Withdrawal' };
  transfer = { fromId: '', toId: '', amount: null as number | null, description: 'Transfer' };

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getAccounts().subscribe({
      next: (res: any) => { this.accounts = res.data || res || []; },
      error: () => {}
    });
    this.loadTxns();
  }

  clearMsg() { this.msg = ''; }

  loadTxns() {
    this.api.getTransactions().subscribe({
      next: (res: any) => { this.transactions = res.data || res || []; },
      error: () => {}
    });
  }

  doDeposit() {
    if (!this.deposit.accountId || !this.deposit.amount) { this.setErr('Account and amount are required'); return; }
    this.loading = true;
    this.api.deposit(this.deposit.accountId, this.deposit.amount, this.deposit.description).subscribe({
      next: () => { this.setOk('Deposit successful!'); this.deposit = { accountId: '', amount: null, description: 'Deposit' }; this.loadTxns(); },
      error: (e: any) => this.setErr(e.error?.message || 'Deposit failed')
    });
  }

  doWithdraw() {
    if (!this.withdraw.accountId || !this.withdraw.amount) { this.setErr('Account and amount are required'); return; }
    this.loading = true;
    this.api.withdraw(this.withdraw.accountId, this.withdraw.amount, this.withdraw.description).subscribe({
      next: () => { this.setOk('Withdrawal successful!'); this.withdraw = { accountId: '', amount: null, description: 'Withdrawal' }; this.loadTxns(); },
      error: (e: any) => this.setErr(e.error?.message || 'Withdrawal failed')
    });
  }

  doTransfer() {
    if (!this.transfer.fromId || !this.transfer.toId || !this.transfer.amount) { this.setErr('All fields are required'); return; }
    this.loading = true;
    this.api.transfer(this.transfer.fromId, this.transfer.toId, this.transfer.amount, this.transfer.description).subscribe({
      next: () => { this.setOk('Transfer successful!'); this.transfer = { fromId: '', toId: '', amount: null, description: 'Transfer' }; this.loadTxns(); },
      error: (e: any) => this.setErr(e.error?.message || 'Transfer failed')
    });
  }

  private setOk(m: string) { this.msg = m; this.isError = false; this.loading = false; }
  private setErr(m: string) { this.msg = m; this.isError = true; this.loading = false; }
}
