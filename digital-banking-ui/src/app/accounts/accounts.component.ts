import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-accounts',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-header">
      <h1>Accounts</h1>
      <p>Manage your bank accounts</p>
    </div>

    <div *ngIf="msg" class="alert" [class.alert-success]="!isError" [class.alert-danger]="isError">{{ msg }}</div>

    <!-- Accounts list -->
    <div class="card">
      <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
        <span>Your Accounts</span>
        <button class="btn btn-primary btn-sm" (click)="showCreate = !showCreate">
          {{ showCreate ? 'Cancel' : '+ Open Account' }}
        </button>
      </div>

      <div *ngIf="accounts.length; else noAccounts" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Type</th>
              <th>Account Number</th>
              <th>Account ID</th>
              <th>Balance</th>
              <th>Status</th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let a of accounts">
              <td><span class="badge badge-primary">{{ a.accountType }}</span></td>
              <td class="font-mono">{{ a.accountNumber }}</td>
              <td>
                <span class="font-mono text-muted" style="font-size:11px">{{ a.id }}</span>
                <button class="copy-btn" (click)="copy(a.id)" title="Copy Account ID">&#x2398;</button>
              </td>
              <td class="font-bold">{{ a.balance | currency:'INR':'symbol':'1.2-2' }}</td>
              <td>
                <span class="badge" [class.badge-success]="a.status === 'ACTIVE'" [class.badge-danger]="a.status === 'SUSPENDED'" [class.badge-gray]="a.status !== 'ACTIVE' && a.status !== 'SUSPENDED'">
                  {{ a.status }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <ng-template #noAccounts>
        <div class="empty-state">
          <div class="icon">◈</div>
          <div>No accounts yet. Open your first account below.</div>
        </div>
      </ng-template>
    </div>

    <!-- Customer ID info -->
    <div class="card" *ngIf="customerId">
      <div class="card-title">Customer Profile</div>
      <div class="info-row">
        <span class="info-label">Customer ID</span>
        <span class="font-mono">{{ customerId }}</span>
        <button class="copy-btn" (click)="copy(customerId)">&#x2398;</button>
      </div>
      <div class="info-row">
        <span class="info-label">User ID</span>
        <span class="font-mono text-muted" style="font-size:12px">{{ userId || '—' }}</span>
      </div>
      <p class="text-muted" style="font-size:12px;margin-top:8px">
        Use the Customer ID for KYC document submission and beneficiary management.
      </p>
    </div>

    <!-- Create account form -->
    <div class="card" *ngIf="showCreate">
      <div class="card-title">Open New Account</div>
      <div class="alert alert-info" style="margin-bottom:16px;font-size:12px">
        This will create a full customer profile linked to your user ID. All fields are required by the bank's KYC policy.
      </div>
      <div class="form-grid">
        <div class="form-group">
          <label>Account Type</label>
          <select [(ngModel)]="form.accountType">
            <option value="SAVINGS">Savings</option>
            <option value="CURRENT">Current</option>
          </select>
        </div>
        <div class="form-group">
          <label>Full Name</label>
          <input type="text" [(ngModel)]="form.name" placeholder="As per PAN card">
        </div>
        <div class="form-group">
          <label>Email</label>
          <input type="email" [(ngModel)]="form.email" placeholder="your@email.com">
        </div>
        <div class="form-group">
          <label>Phone</label>
          <input type="text" [(ngModel)]="form.phone" placeholder="10-digit mobile number">
        </div>
        <div class="form-group">
          <label>Date of Birth</label>
          <input type="date" [(ngModel)]="form.dob">
        </div>
        <div class="form-group">
          <label>PAN Number</label>
          <input type="text" [(ngModel)]="form.pan" placeholder="ABCDE1234F">
        </div>
        <div class="form-group">
          <label>Aadhaar Number</label>
          <input type="text" [(ngModel)]="form.aadhar" placeholder="12-digit Aadhaar">
        </div>
        <div class="form-group">
          <label>Address</label>
          <input type="text" [(ngModel)]="form.address" placeholder="House / Street">
        </div>
        <div class="form-group">
          <label>City</label>
          <input type="text" [(ngModel)]="form.city" placeholder="City">
        </div>
        <div class="form-group">
          <label>State</label>
          <input type="text" [(ngModel)]="form.state" placeholder="State">
        </div>
        <div class="form-group">
          <label>ZIP Code</label>
          <input type="text" [(ngModel)]="form.zipCode" placeholder="6-digit PIN">
        </div>
      </div>
      <button class="btn btn-primary" (click)="createAccount()" [disabled]="loading">
        {{ loading ? 'Opening account…' : 'Open Account' }}
      </button>
    </div>
  `,
  styles: [`
    .info-row {
      display: flex;
      align-items: center;
      gap: 10px;
      padding: 8px 0;
      border-bottom: 1px solid #f1f5f9;
    }
    .info-row:last-of-type { border-bottom: none; }
    .info-label { font-size: 12px; font-weight: 500; color: #64748b; width: 100px; flex-shrink: 0; }
    .font-bold { font-weight: 700; }
    .copy-btn {
      background: none;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 1px 6px;
      cursor: pointer;
      font-size: 13px;
      color: #64748b;
      transition: all 0.15s;
    }
    .copy-btn:hover { background: #f1f5f9; color: #2563eb; }
  `]
})
export class AccountsComponent implements OnInit {
  accounts: any[] = [];
  showCreate = false;
  loading = false;
  msg = '';
  isError = false;

  form = {
    accountType: 'SAVINGS',
    name: '',
    email: '',
    phone: '',
    dob: '',
    pan: '',
    aadhar: '',
    address: '',
    city: '',
    state: '',
    zipCode: ''
  };

  get customerId() { return this.api.getCustomerId(); }
  get userId() { return this.api.getUserId(); }

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.load();
    // Pre-fill email from session
    this.form.email = this.api.getUserEmail() || '';
    this.form.name = this.api.getUserName() || '';
  }

  load() {
    this.api.getAccounts().subscribe({
      next: (res: any) => { this.accounts = res.data || res || []; },
      error: () => {}
    });
  }

  createAccount() {
    const userId = this.api.getUserId();
    if (!userId) {
      this.msg = 'User ID not found. Please log out and log in again.';
      this.isError = true;
      return;
    }
    this.loading = true;
    this.msg = '';
    const payload = { ...this.form, userId };
    this.api.createAccount(payload).subscribe({
      next: (res: any) => {
        const customerId = res.data?.id || res.id;
        if (customerId) this.api.setCustomerId(customerId);
        this.msg = 'Account opened successfully!';
        this.isError = false;
        this.showCreate = false;
        this.loading = false;
        this.load();
      },
      error: (err: any) => {
        this.msg = err.error?.message || 'Failed to open account';
        this.isError = true;
        this.loading = false;
      }
    });
  }

  copy(text: string) {
    navigator.clipboard.writeText(text).catch(() => {});
  }
}
