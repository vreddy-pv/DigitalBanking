import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

type TabKey = 'documents' | 'beneficiaries' | 'preferences';

@Component({
  selector: 'app-kyc',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-header">
      <h1>KYC & Profile</h1>
      <p>Manage identity documents, beneficiaries, and preferences</p>
    </div>

    <!-- Customer ID prompt -->
    <div class="card" *ngIf="!customerId">
      <div class="card-title">Customer ID Required</div>
      <div class="alert alert-warning">
        Customer ID is needed to access KYC features. It is displayed on the Accounts page after opening an account.
      </div>
      <div class="form-group" style="max-width:440px">
        <label>Enter your Customer ID</label>
        <input type="text" [(ngModel)]="manualId" placeholder="UUID from Accounts page">
      </div>
      <button class="btn btn-primary" (click)="setManualId()" [disabled]="!manualId">Continue</button>
    </div>

    <ng-container *ngIf="customerId">
      <div *ngIf="msg" class="alert" [class.alert-success]="!isError" [class.alert-danger]="isError">{{ msg }}</div>

      <!-- KYC Status -->
      <div class="card" *ngIf="kycStatus">
        <div class="card-title">KYC Status</div>
        <div class="kyc-status-row">
          <div class="kyc-stat">
            <div class="kyc-stat-label">Overall Status</div>
            <span class="badge badge-lg"
              [class.badge-success]="kycStatus.overallStatus === 'VERIFIED'"
              [class.badge-warning]="kycStatus.overallStatus === 'PENDING'"
              [class.badge-danger]="kycStatus.overallStatus === 'REJECTED'">
              {{ kycStatus.overallStatus || 'PENDING' }}
            </span>
          </div>
          <div class="kyc-stat">
            <div class="kyc-stat-label">Documents</div>
            <span class="kyc-stat-value">{{ kycStatus.documentCount || 0 }}</span>
          </div>
          <div class="kyc-stat">
            <div class="kyc-stat-label">Verified</div>
            <span class="kyc-stat-value text-success">{{ kycStatus.verifiedCount || 0 }}</span>
          </div>
          <div class="kyc-stat">
            <div class="kyc-stat-label">Pending</div>
            <span class="kyc-stat-value text-warning">{{ kycStatus.pendingCount || 0 }}</span>
          </div>
        </div>
      </div>

      <div class="tabs">
        <button class="tab-btn" [class.active]="tab === 'documents'" (click)="tab = 'documents'; loadDocs()">Documents</button>
        <button class="tab-btn" [class.active]="tab === 'beneficiaries'" (click)="tab = 'beneficiaries'; loadBeneficiaries()">Beneficiaries</button>
        <button class="tab-btn" [class.active]="tab === 'preferences'" (click)="tab = 'preferences'">Preferences</button>
      </div>

      <!-- Documents tab -->
      <ng-container *ngIf="tab === 'documents'">
        <div class="card">
          <div class="card-title">Submit KYC Document</div>
          <div style="max-width:440px">
            <div class="form-group">
              <label>Document Type</label>
              <select [(ngModel)]="docForm.documentType">
                <option value="PASSPORT">Passport</option>
                <option value="NATIONAL_ID">National ID</option>
                <option value="DRIVING_LICENSE">Driving License</option>
                <option value="PAN_CARD">PAN Card</option>
                <option value="UTILITY_BILL">Utility Bill</option>
              </select>
            </div>
            <div class="form-group">
              <label>Document Reference Number</label>
              <input type="text" [(ngModel)]="docForm.reference" placeholder="e.g. ABCDE1234F">
            </div>
            <button class="btn btn-primary" (click)="submitDoc()" [disabled]="loading">
              {{ loading ? 'Submitting…' : 'Submit Document' }}
            </button>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Submitted Documents</div>
          <div *ngIf="documents.length; else noDocs" class="table-wrap">
            <table>
              <thead>
                <tr><th>Type</th><th>Reference</th><th>Status</th><th>Submitted</th></tr>
              </thead>
              <tbody>
                <tr *ngFor="let d of documents">
                  <td><span class="badge badge-primary">{{ d.documentType }}</span></td>
                  <td class="font-mono">{{ d.documentReference }}</td>
                  <td>
                    <span class="badge" [class.badge-success]="d.status === 'VERIFIED'" [class.badge-warning]="d.status === 'PENDING'" [class.badge-danger]="d.status === 'REJECTED'">
                      {{ d.status }}
                    </span>
                  </td>
                  <td class="text-muted">{{ d.createdAt | date:'MMM d, y' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <ng-template #noDocs>
            <div class="empty-state">No documents submitted yet.</div>
          </ng-template>
        </div>
      </ng-container>

      <!-- Beneficiaries tab -->
      <ng-container *ngIf="tab === 'beneficiaries'">
        <div class="card">
          <div class="card-title">Add Beneficiary</div>
          <div style="max-width:440px">
            <div class="form-group">
              <label>Account ID</label>
              <input type="text" [(ngModel)]="benForm.accountId" placeholder="Beneficiary account UUID">
            </div>
            <div class="form-group">
              <label>Nickname</label>
              <input type="text" [(ngModel)]="benForm.nickname" placeholder="e.g. Friend, Parent">
            </div>
            <button class="btn btn-primary" (click)="addBeneficiary()" [disabled]="loading">
              {{ loading ? 'Adding…' : 'Add Beneficiary' }}
            </button>
          </div>
        </div>

        <div class="card">
          <div class="card-title">Beneficiaries</div>
          <div *ngIf="beneficiaries.length; else noBen" class="table-wrap">
            <table>
              <thead>
                <tr><th>Nickname</th><th>Account ID</th><th>Added</th></tr>
              </thead>
              <tbody>
                <tr *ngFor="let b of beneficiaries">
                  <td class="font-bold">{{ b.nickname }}</td>
                  <td class="font-mono" style="font-size:11px">{{ b.beneficiaryAccountId }}</td>
                  <td class="text-muted">{{ b.createdAt | date:'MMM d, y' }}</td>
                </tr>
              </tbody>
            </table>
          </div>
          <ng-template #noBen>
            <div class="empty-state">No beneficiaries added yet.</div>
          </ng-template>
        </div>
      </ng-container>

      <!-- Preferences tab -->
      <div class="card" *ngIf="tab === 'preferences'">
        <div class="card-title">Notification & Display Preferences</div>
        <div style="max-width:440px">
          <div class="pref-toggle">
            <div>
              <div class="pref-label">Email Notifications</div>
              <div class="pref-sub">Receive transaction alerts by email</div>
            </div>
            <label class="toggle">
              <input type="checkbox" [(ngModel)]="prefs.emailNotifications">
              <span class="slider"></span>
            </label>
          </div>
          <div class="pref-toggle">
            <div>
              <div class="pref-label">SMS Notifications</div>
              <div class="pref-sub">Receive OTP and alerts by SMS</div>
            </div>
            <label class="toggle">
              <input type="checkbox" [(ngModel)]="prefs.smsNotifications">
              <span class="slider"></span>
            </label>
          </div>
          <hr class="divider">
          <div class="form-group">
            <label>Preferred Currency</label>
            <select [(ngModel)]="prefs.currency">
              <option value="INR">INR — Indian Rupee</option>
              <option value="USD">USD — US Dollar</option>
              <option value="EUR">EUR — Euro</option>
            </select>
          </div>
          <div class="form-group">
            <label>Language</label>
            <select [(ngModel)]="prefs.language">
              <option value="en">English</option>
              <option value="hi">Hindi</option>
              <option value="ta">Tamil</option>
            </select>
          </div>
          <button class="btn btn-primary" (click)="savePreferences()" [disabled]="loading">
            {{ loading ? 'Saving…' : 'Save Preferences' }}
          </button>
        </div>
      </div>
    </ng-container>
  `,
  styles: [`
    .kyc-status-row { display: flex; gap: 24px; flex-wrap: wrap; }
    .kyc-stat { }
    .kyc-stat-label { font-size: 12px; color: #64748b; margin-bottom: 6px; }
    .kyc-stat-value { font-size: 22px; font-weight: 700; }
    .badge-lg { font-size: 13px; padding: 4px 12px; }
    .font-bold { font-weight: 700; }

    .pref-toggle { display: flex; justify-content: space-between; align-items: center; padding: 14px 0; border-bottom: 1px solid #f1f5f9; }
    .pref-label { font-size: 13px; font-weight: 500; }
    .pref-sub { font-size: 12px; color: #64748b; margin-top: 2px; }

    .toggle { position: relative; display: inline-block; width: 42px; height: 24px; flex-shrink: 0; }
    .toggle input { opacity: 0; width: 0; height: 0; }
    .slider {
      position: absolute; cursor: pointer; top: 0; left: 0; right: 0; bottom: 0;
      background: #cbd5e1; border-radius: 24px; transition: 0.2s;
    }
    .slider:before {
      content: ''; position: absolute; height: 18px; width: 18px; left: 3px; bottom: 3px;
      background: white; border-radius: 50%; transition: 0.2s;
    }
    input:checked + .slider { background: #2563eb; }
    input:checked + .slider:before { transform: translateX(18px); }
  `]
})
export class KycComponent implements OnInit {
  tab: TabKey = 'documents';
  customerId = '';
  manualId = '';
  documents: any[] = [];
  beneficiaries: any[] = [];
  kycStatus: any = null;
  loading = false;
  msg = '';
  isError = false;

  docForm = { documentType: 'PAN_CARD', reference: '' };
  benForm = { accountId: '', nickname: '' };
  prefs = { emailNotifications: true, smsNotifications: false, currency: 'INR', language: 'en' };

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.customerId = this.api.getCustomerId() || '';
    if (this.customerId) this.onCustomerIdReady();
  }

  setManualId() {
    if (this.manualId) {
      this.api.setCustomerId(this.manualId);
      this.customerId = this.manualId;
      this.onCustomerIdReady();
    }
  }

  onCustomerIdReady() {
    this.api.getKycStatus(this.customerId).subscribe({
      next: (res: any) => { this.kycStatus = res.data || res; },
      error: () => {}
    });
    this.loadDocs();
  }

  loadDocs() {
    if (!this.customerId) return;
    this.api.getKycDocuments(this.customerId).subscribe({
      next: (res: any) => { this.documents = res.data || res || []; },
      error: () => {}
    });
  }

  loadBeneficiaries() {
    if (!this.customerId) return;
    this.api.getBeneficiaries(this.customerId).subscribe({
      next: (res: any) => { this.beneficiaries = res.data || res || []; },
      error: () => {}
    });
  }

  submitDoc() {
    if (!this.docForm.reference) { this.setErr('Document reference is required'); return; }
    this.loading = true;
    this.api.submitKycDocument(this.customerId, this.docForm.documentType, this.docForm.reference).subscribe({
      next: () => { this.setOk('Document submitted!'); this.docForm.reference = ''; this.loadDocs(); },
      error: (e: any) => this.setErr(e.error?.message || 'Submission failed')
    });
  }

  addBeneficiary() {
    if (!this.benForm.accountId || !this.benForm.nickname) { this.setErr('All fields are required'); return; }
    this.loading = true;
    this.api.addBeneficiary(this.customerId, this.benForm.accountId, this.benForm.nickname).subscribe({
      next: () => { this.setOk('Beneficiary added!'); this.benForm = { accountId: '', nickname: '' }; this.loadBeneficiaries(); },
      error: (e: any) => this.setErr(e.error?.message || 'Failed to add beneficiary')
    });
  }

  savePreferences() {
    this.loading = true;
    this.api.updatePreferences(this.customerId, this.prefs).subscribe({
      next: () => this.setOk('Preferences saved!'),
      error: (e: any) => this.setErr(e.error?.message || 'Failed to save')
    });
  }

  private setOk(m: string) { this.msg = m; this.isError = false; this.loading = false; }
  private setErr(m: string) { this.msg = m; this.isError = true; this.loading = false; }
}
