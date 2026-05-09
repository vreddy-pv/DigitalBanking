import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-dashboard',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="container">
      <div *ngIf="message" [class.alert]="true" [class.alert-success]="!error" [class.alert-danger]="error">
        {{ message }}
      </div>

      <!-- Accounts Section -->
      <div class="card">
        <h2>📊 Your Accounts</h2>
        <div *ngIf="accounts.length > 0; else noAccounts">
          <table>
            <thead>
              <tr>
                <th>Account Type</th>
                <th>Account Number</th>
                <th>Balance</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let account of accounts">
                <td>{{ account.accountType }}</td>
                <td>{{ account.accountNumber }}</td>
                <td class="text-right">₹ {{ account.balance | number:'1.2-2' }}</td>
                <td><span [class.text-success]="account.status === 'ACTIVE'">{{ account.status }}</span></td>
              </tr>
            </tbody>
          </table>
        </div>
        <ng-template #noAccounts>
          <p style="text-align: center; color: #666; padding: 20px;">No accounts found</p>
        </ng-template>
      </div>

      <!-- Transaction Section -->
      <div class="card">
        <h2>💰 Transaction Operations</h2>
        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
          <div>
            <h3>Deposit</h3>
            <div class="form-group">
              <label>Account ID</label>
              <input type="text" [(ngModel)]="depositAccountId" placeholder="Enter account ID">
            </div>
            <div class="form-group">
              <label>Amount</label>
              <input type="number" [(ngModel)]="depositAmount" placeholder="Enter amount">
            </div>
            <button class="btn btn-primary" (click)="submitDeposit()" [disabled]="loading">
              {{ loading ? 'Processing...' : 'Deposit' }}
            </button>
          </div>

          <div>
            <h3>Withdraw</h3>
            <div class="form-group">
              <label>Account ID</label>
              <input type="text" [(ngModel)]="withdrawAccountId" placeholder="Enter account ID">
            </div>
            <div class="form-group">
              <label>Amount</label>
              <input type="number" [(ngModel)]="withdrawAmount" placeholder="Enter amount">
            </div>
            <button class="btn btn-primary" (click)="submitWithdraw()" [disabled]="loading">
              {{ loading ? 'Processing...' : 'Withdraw' }}
            </button>
          </div>
        </div>
      </div>

      <!-- Transactions History -->
      <div class="card">
        <h2>📋 Transaction History</h2>
        <div *ngIf="transactions.length > 0; else noTransactions">
          <table>
            <thead>
              <tr>
                <th>Type</th>
                <th>Amount</th>
                <th>Account</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              <tr *ngFor="let transaction of transactions">
                <td>{{ transaction.type }}</td>
                <td [class.text-success]="transaction.type === 'DEPOSIT'" [class.text-danger]="transaction.type === 'WITHDRAWAL'">
                  ₹ {{ transaction.amount | number:'1.2-2' }}
                </td>
                <td>{{ transaction.accountId }}</td>
                <td>{{ transaction.status }}</td>
                <td>{{ transaction.createdAt | date:'short' }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <ng-template #noTransactions>
          <p style="text-align: center; color: #666; padding: 20px;">No transactions found</p>
        </ng-template>
      </div>
    </div>
  `,
  styles: [`
    .container {
      max-width: 1200px;
      margin: 0 auto;
      padding: 20px;
    }

    .card {
      background: white;
      border-radius: 8px;
      box-shadow: 0 2px 8px rgba(0,0,0,0.1);
      padding: 20px;
      margin-bottom: 20px;
    }

    h2 {
      margin-top: 0;
      color: #333;
      margin-bottom: 20px;
    }

    h3 {
      color: #333;
      font-size: 16px;
      margin-bottom: 15px;
    }

    .form-group {
      margin-bottom: 15px;
    }

    label {
      display: block;
      margin-bottom: 5px;
      font-weight: 500;
      color: #333;
      font-size: 14px;
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
      padding: 10px;
      background: #667eea;
      color: white;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-weight: 500;
    }

    .btn:hover:not(:disabled) {
      background: #5568d3;
    }

    .btn:disabled {
      opacity: 0.6;
      cursor: not-allowed;
    }

    table {
      width: 100%;
      border-collapse: collapse;
    }

    th, td {
      padding: 12px;
      text-align: left;
      border-bottom: 1px solid #ddd;
    }

    th {
      background: #f8f9fa;
      font-weight: 600;
      color: #333;
    }

    .text-right {
      text-align: right;
    }

    .text-danger {
      color: #dc3545;
    }

    .text-success {
      color: #28a745;
    }

    .alert {
      padding: 15px;
      border-radius: 4px;
      margin-bottom: 20px;
    }

    .alert-success {
      background: #d4edda;
      color: #155724;
      border: 1px solid #c3e6cb;
    }

    .alert-danger {
      background: #f8d7da;
      color: #721c24;
      border: 1px solid #f5c6cb;
    }
  `]
})
export class DashboardComponent implements OnInit {
  accounts: any[] = [];
  transactions: any[] = [];
  message = '';
  error = false;
  loading = false;

  depositAccountId = '';
  depositAmount: number | null = null;
  withdrawAccountId = '';
  withdrawAmount: number | null = null;

  constructor(private apiService: ApiService) {}

  ngOnInit() {
    this.loadAccounts();
    this.loadTransactions();
  }

  loadAccounts() {
    this.apiService.getAccounts().subscribe(
      (response: any) => {
        this.accounts = response.data || response;
      },
      (error: any) => {
        console.log('Accounts loading note: Make sure account creation is set up');
      }
    );
  }

  loadTransactions() {
    this.apiService.getTransactions().subscribe(
      (response: any) => {
        this.transactions = response.data || response;
      },
      (error: any) => {
        console.log('Transactions loading note: Waiting for transaction data');
      }
    );
  }

  submitDeposit() {
    if (!this.depositAccountId || !this.depositAmount) {
      this.message = 'Please fill all fields';
      this.error = true;
      return;
    }

    this.loading = true;
    this.apiService.deposit(this.depositAccountId, this.depositAmount).subscribe(
      (response: any) => {
        this.message = 'Deposit successful!';
        this.error = false;
        this.depositAccountId = '';
        this.depositAmount = null;
        this.loadTransactions();
        this.loading = false;
      },
      (error: any) => {
        this.message = error.error?.message || 'Deposit failed';
        this.error = true;
        this.loading = false;
      }
    );
  }

  submitWithdraw() {
    if (!this.withdrawAccountId || !this.withdrawAmount) {
      this.message = 'Please fill all fields';
      this.error = true;
      return;
    }

    this.loading = true;
    this.apiService.withdraw(this.withdrawAccountId, this.withdrawAmount).subscribe(
      (response: any) => {
        this.message = 'Withdrawal successful!';
        this.error = false;
        this.withdrawAccountId = '';
        this.withdrawAmount = null;
        this.loadTransactions();
        this.loading = false;
      },
      (error: any) => {
        this.message = error.error?.message || 'Withdrawal failed';
        this.error = true;
        this.loading = false;
      }
    );
  }
}
