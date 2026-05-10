import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-compliance',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-header">
      <h1>Compliance</h1>
      <p>AML alerts, risk profiles, and compliance monitoring</p>
    </div>

    <!-- Stats -->
    <div class="stats-row" *ngIf="stats">
      <div class="stat-card">
        <div class="label">Total Alerts</div>
        <div class="value">{{ stats.total_alerts || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="label">Pending</div>
        <div class="value text-warning">{{ stats.pending_alerts || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="label">High Severity</div>
        <div class="value text-danger">{{ stats.high_severity || 0 }}</div>
      </div>
      <div class="stat-card">
        <div class="label">Cleared</div>
        <div class="value text-success">{{ stats.cleared_alerts || 0 }}</div>
      </div>
    </div>

    <div *ngIf="msg" class="alert" [class.alert-success]="!isError" [class.alert-danger]="isError">{{ msg }}</div>

    <!-- Filters -->
    <div class="card">
      <div class="card-title">AML Alerts</div>
      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">
        <div class="form-group" style="margin-bottom:0;flex:1;min-width:160px">
          <label>Severity</label>
          <select [(ngModel)]="filters.severity">
            <option value="">All</option>
            <option value="LOW">Low</option>
            <option value="MEDIUM">Medium</option>
            <option value="HIGH">High</option>
            <option value="CRITICAL">Critical</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0;flex:1;min-width:160px">
          <label>Status</label>
          <select [(ngModel)]="filters.status">
            <option value="">All</option>
            <option value="PENDING">Pending</option>
            <option value="REVIEWED">Reviewed</option>
            <option value="CLEARED">Cleared</option>
            <option value="ESCALATED">Escalated</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0;flex:2;min-width:200px">
          <label>Account ID (optional)</label>
          <input type="text" [(ngModel)]="filters.account_id" placeholder="Filter by account UUID">
        </div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn btn-primary" (click)="loadAlerts()">Apply Filters</button>
        </div>
      </div>

      <div *ngIf="alerts.length; else noAlerts" class="table-wrap">
        <table>
          <thead>
            <tr><th>Alert ID</th><th>Rule</th><th>Amount</th><th>Severity</th><th>Status</th><th>Date</th><th>Action</th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let a of alerts">
              <td class="font-mono" style="font-size:11px">{{ a.id }}</td>
              <td><span class="badge badge-info">{{ a.rule_name }}</span></td>
              <td class="font-bold">{{ a.amount | currency:'INR':'symbol':'1.0-0' }}</td>
              <td>
                <span class="badge"
                  [class.badge-danger]="a.severity === 'CRITICAL' || a.severity === 'HIGH'"
                  [class.badge-warning]="a.severity === 'MEDIUM'"
                  [class.badge-gray]="a.severity === 'LOW'">
                  {{ a.severity }}
                </span>
              </td>
              <td>
                <span class="badge"
                  [class.badge-warning]="a.status === 'PENDING'"
                  [class.badge-success]="a.status === 'CLEARED'"
                  [class.badge-info]="a.status === 'REVIEWED'"
                  [class.badge-danger]="a.status === 'ESCALATED'">
                  {{ a.status }}
                </span>
              </td>
              <td class="text-muted">{{ a.created_at | date:'MMM d, y' }}</td>
              <td>
                <button class="btn btn-outline btn-sm" (click)="openReview(a)" [disabled]="a.status !== 'PENDING'">
                  Review
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <ng-template #noAlerts>
        <div class="empty-state">
          <div class="icon">◆</div>
          <div>No compliance alerts found.</div>
        </div>
      </ng-template>
    </div>

    <!-- Review modal inline -->
    <div class="card" *ngIf="reviewAlert">
      <div class="card-title">Review Alert: {{ reviewAlert.rule_name }}</div>
      <div class="alert-detail">
        <div class="detail-row"><span>Alert ID</span><span class="font-mono">{{ reviewAlert.id }}</span></div>
        <div class="detail-row"><span>Account</span><span class="font-mono" style="font-size:11px">{{ reviewAlert.account_id }}</span></div>
        <div class="detail-row"><span>Amount</span><span class="font-bold">{{ reviewAlert.amount | currency:'INR':'symbol':'1.2-2' }}</span></div>
        <div class="detail-row"><span>Rule</span><span>{{ reviewAlert.rule_name }}</span></div>
        <div class="detail-row"><span>Transaction</span><span class="font-mono" style="font-size:11px">{{ reviewAlert.transaction_id }}</span></div>
      </div>
      <hr class="divider">
      <div style="max-width:440px">
        <div class="form-group">
          <label>Decision</label>
          <select [(ngModel)]="reviewForm.status">
            <option value="REVIEWED">Reviewed — Keep for records</option>
            <option value="CLEARED">Cleared — False positive</option>
            <option value="ESCALATED">Escalated — Requires action</option>
          </select>
        </div>
        <div class="form-group">
          <label>Reviewed By</label>
          <input type="text" [(ngModel)]="reviewForm.reviewedBy" placeholder="officer@bank.com">
        </div>
        <div class="form-group">
          <label>Notes</label>
          <textarea [(ngModel)]="reviewForm.notes" placeholder="Explain your decision…"></textarea>
        </div>
        <div style="display:flex;gap:8px">
          <button class="btn btn-primary" (click)="submitReview()" [disabled]="loading">
            {{ loading ? 'Submitting…' : 'Submit Review' }}
          </button>
          <button class="btn btn-outline" (click)="reviewAlert = null">Cancel</button>
        </div>
      </div>
    </div>

    <!-- Risk Profile section -->
    <div class="card">
      <div class="card-title">Customer Risk Profile</div>
      <div style="display:flex;gap:12px;align-items:flex-end;max-width:500px">
        <div class="form-group" style="flex:1;margin-bottom:0">
          <label>Account ID</label>
          <input type="text" [(ngModel)]="riskAccountId" placeholder="Account UUID">
        </div>
        <button class="btn btn-primary" (click)="loadRisk()" [disabled]="!riskAccountId">Check Risk</button>
      </div>
      <div class="risk-profile" *ngIf="riskProfile">
        <div class="risk-score-wrap">
          <div class="risk-score" [class.risk-low]="riskProfile.risk_level === 'LOW'" [class.risk-medium]="riskProfile.risk_level === 'MEDIUM'" [class.risk-high]="riskProfile.risk_level === 'HIGH' || riskProfile.risk_level === 'CRITICAL'">
            {{ riskProfile.risk_score || 0 }}
          </div>
          <div>
            <div class="risk-level">{{ riskProfile.risk_level }}</div>
            <div class="text-muted" style="font-size:12px">Risk score out of 100</div>
          </div>
        </div>
        <div class="risk-details" *ngIf="riskProfile.alert_counts">
          <div class="detail-row" *ngFor="let entry of riskAlertEntries">
            <span>{{ entry.key }}</span><span class="font-bold">{{ entry.value }}</span>
          </div>
        </div>
      </div>
    </div>
  `,
  styles: [`
    .font-bold { font-weight: 700; }
    .alert-detail { display: flex; flex-direction: column; gap: 0; }
    .detail-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #f1f5f9; font-size: 13px; }
    .detail-row:last-child { border-bottom: none; }
    .detail-row span:first-child { color: #64748b; width: 120px; flex-shrink: 0; }

    .risk-profile { margin-top: 20px; }
    .risk-score-wrap { display: flex; align-items: center; gap: 20px; margin-bottom: 16px; }
    .risk-score {
      width: 72px; height: 72px; border-radius: 50%;
      display: flex; align-items: center; justify-content: center;
      font-size: 24px; font-weight: 800; flex-shrink: 0;
    }
    .risk-low { background: #dcfce7; color: #16a34a; }
    .risk-medium { background: #fef3c7; color: #d97706; }
    .risk-high { background: #fee2e2; color: #dc2626; }
    .risk-level { font-size: 18px; font-weight: 700; }
    .risk-details { max-width: 300px; }
  `]
})
export class ComplianceComponent implements OnInit {
  alerts: any[] = [];
  stats: any = null;
  reviewAlert: any = null;
  riskProfile: any = null;
  riskAccountId = '';
  loading = false;
  msg = '';
  isError = false;

  filters = { severity: '', status: '', account_id: '' };
  reviewForm = { status: 'REVIEWED', reviewedBy: '', notes: '' };

  get riskAlertEntries() {
    if (!this.riskProfile?.alert_counts) return [];
    return Object.entries(this.riskProfile.alert_counts).map(([key, value]) => ({ key, value }));
  }

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.loadStats();
    this.loadAlerts();
    this.reviewForm.reviewedBy = this.api.getUserEmail() || '';
  }

  loadStats() {
    this.api.getComplianceStats().subscribe({
      next: (res: any) => { this.stats = res.data || res; },
      error: () => {}
    });
  }

  loadAlerts() {
    const params: Record<string, string> = {};
    if (this.filters.severity) params['severity'] = this.filters.severity;
    if (this.filters.status) params['status'] = this.filters.status;
    if (this.filters.account_id) params['account_id'] = this.filters.account_id;
    this.api.getAlerts(params).subscribe({
      next: (res: any) => { this.alerts = res.data || res || []; },
      error: () => {}
    });
  }

  openReview(alert: any) {
    this.reviewAlert = alert;
    this.reviewForm = { status: 'REVIEWED', reviewedBy: this.api.getUserEmail() || '', notes: '' };
  }

  submitReview() {
    if (!this.reviewAlert) return;
    this.loading = true;
    this.api.reviewAlert(this.reviewAlert.id, this.reviewForm.status, this.reviewForm.reviewedBy, this.reviewForm.notes).subscribe({
      next: () => {
        this.msg = `Alert marked as ${this.reviewForm.status}`;
        this.isError = false;
        this.reviewAlert = null;
        this.loading = false;
        this.loadAlerts();
        this.loadStats();
      },
      error: (e: any) => {
        this.msg = e.error?.message || 'Review failed';
        this.isError = true;
        this.loading = false;
      }
    });
  }

  loadRisk() {
    if (!this.riskAccountId) return;
    this.api.getRiskProfile(this.riskAccountId).subscribe({
      next: (res: any) => { this.riskProfile = res.data || res; },
      error: () => {}
    });
  }
}
