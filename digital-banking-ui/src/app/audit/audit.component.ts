import { Component, OnInit } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from '../api.service';

@Component({
  selector: 'app-audit',
  standalone: true,
  imports: [CommonModule, FormsModule],
  template: `
    <div class="page-header">
      <h1>Audit Trail</h1>
      <p>Immutable append-only log of all system events</p>
    </div>

    <!-- Stats -->
    <div class="stats-row" *ngIf="stats">
      <div class="stat-card">
        <div class="label">Total Events</div>
        <div class="value">{{ stats.total_events || 0 }}</div>
      </div>
      <div class="stat-card" *ngFor="let e of statEventEntries">
        <div class="label">{{ e.key | titlecase }}</div>
        <div class="value">{{ e.value }}</div>
      </div>
    </div>

    <!-- Filters -->
    <div class="card">
      <div class="card-title" style="display:flex;justify-content:space-between;align-items:center">
        <span>Audit Events</span>
        <button class="btn btn-outline btn-sm" (click)="loadEvents()">Refresh</button>
      </div>

      <div style="display:flex;gap:12px;flex-wrap:wrap;margin-bottom:16px">
        <div class="form-group" style="margin-bottom:0;flex:1;min-width:160px">
          <label>Event Type</label>
          <select [(ngModel)]="filters.event_type">
            <option value="">All</option>
            <option value="TRANSACTION_CREATED">Transaction Created</option>
            <option value="USER_REGISTERED">User Registered</option>
            <option value="ACCOUNT_CREATED">Account Created</option>
            <option value="KYC_DOCUMENT_SUBMITTED">KYC Submitted</option>
            <option value="COMPLIANCE_ALERT_RAISED">Compliance Alert</option>
            <option value="ADMIN_ACTION">Admin Action</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0;flex:1;min-width:160px">
          <label>Resource Type</label>
          <select [(ngModel)]="filters.resource_type">
            <option value="">All</option>
            <option value="TRANSACTION">Transaction</option>
            <option value="ACCOUNT">Account</option>
            <option value="USER">User</option>
            <option value="CUSTOMER">Customer</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0;flex:1;min-width:160px">
          <label>Actor</label>
          <input type="text" [(ngModel)]="filters.actor" placeholder="e.g. user@bank.com">
        </div>
        <div class="form-group" style="margin-bottom:0;flex:1;min-width:160px">
          <label>Limit</label>
          <select [(ngModel)]="filters.limit">
            <option value="20">20</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
        <div style="display:flex;align-items:flex-end">
          <button class="btn btn-primary" (click)="loadEvents()">Apply</button>
        </div>
      </div>

      <div *ngIf="events.length; else noEvents" class="table-wrap">
        <table>
          <thead>
            <tr>
              <th>Event Type</th>
              <th>Actor</th>
              <th>Resource</th>
              <th>Action</th>
              <th>Service</th>
              <th>Timestamp</th>
              <th></th>
            </tr>
          </thead>
          <tbody>
            <tr *ngFor="let e of events">
              <td>
                <span class="badge"
                  [class.badge-primary]="e.event_type === 'TRANSACTION_CREATED'"
                  [class.badge-success]="e.event_type === 'USER_REGISTERED' || e.event_type === 'ACCOUNT_CREATED'"
                  [class.badge-warning]="e.event_type === 'KYC_DOCUMENT_SUBMITTED'"
                  [class.badge-danger]="e.event_type === 'COMPLIANCE_ALERT_RAISED'"
                  [class.badge-gray]="e.event_type === 'ADMIN_ACTION'">
                  {{ e.event_type }}
                </span>
              </td>
              <td class="text-muted" style="font-size:12px">{{ e.actor || '—' }}</td>
              <td>
                <div class="font-mono" style="font-size:11px">{{ e.resource_type }}</div>
                <div class="font-mono text-muted" style="font-size:10px">{{ e.resource_id | slice:0:16 }}…</div>
              </td>
              <td>{{ e.action || '—' }}</td>
              <td class="text-muted" style="font-size:12px">{{ e.source_service || '—' }}</td>
              <td class="text-muted">{{ e.created_at | date:'MMM d, y h:mm a' }}</td>
              <td>
                <button class="btn btn-outline btn-sm" (click)="selected = (selected?.id === e.id ? null : e)">
                  {{ selected?.id === e.id ? 'Hide' : 'Detail' }}
                </button>
              </td>
            </tr>
            <tr *ngIf="selected" class="detail-row-expanded">
              <td colspan="7">
                <div class="event-detail">
                  <div class="detail-grid">
                    <div><span class="detail-key">Event ID</span><span class="font-mono">{{ selected.id }}</span></div>
                    <div><span class="detail-key">Resource ID</span><span class="font-mono">{{ selected.resource_id }}</span></div>
                    <div><span class="detail-key">Description</span><span>{{ selected.description || '—' }}</span></div>
                    <div *ngIf="selected.metadata"><span class="detail-key">Metadata</span><pre class="inline-json">{{ selected.metadata | json }}</pre></div>
                  </div>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
      <ng-template #noEvents>
        <div class="empty-state">
          <div class="icon">◎</div>
          <div>No audit events found. Try adjusting filters.</div>
        </div>
      </ng-template>
    </div>

    <!-- Resource lookup -->
    <div class="card">
      <div class="card-title">Lookup Events by Resource</div>
      <div style="display:flex;gap:12px;align-items:flex-end;flex-wrap:wrap;max-width:600px">
        <div class="form-group" style="margin-bottom:0;flex:1;min-width:140px">
          <label>Resource Type</label>
          <select [(ngModel)]="lookupType">
            <option value="TRANSACTION">Transaction</option>
            <option value="ACCOUNT">Account</option>
            <option value="USER">User</option>
          </select>
        </div>
        <div class="form-group" style="margin-bottom:0;flex:2;min-width:200px">
          <label>Resource ID</label>
          <input type="text" [(ngModel)]="lookupId" placeholder="UUID">
        </div>
        <button class="btn btn-primary" (click)="loadByResource()" [disabled]="!lookupId">Lookup</button>
      </div>
      <div class="table-wrap" *ngIf="resourceEvents.length" style="margin-top:16px">
        <table>
          <thead>
            <tr><th>Event Type</th><th>Actor</th><th>Action</th><th>Timestamp</th></tr>
          </thead>
          <tbody>
            <tr *ngFor="let e of resourceEvents">
              <td><span class="badge badge-primary">{{ e.event_type }}</span></td>
              <td class="text-muted">{{ e.actor || '—' }}</td>
              <td>{{ e.action || '—' }}</td>
              <td class="text-muted">{{ e.created_at | date:'MMM d, y h:mm a' }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  `,
  styles: [`
    .font-bold { font-weight: 700; }
    .detail-row-expanded td { background: #f8fafc; padding: 0 !important; }
    .event-detail { padding: 16px; }
    .detail-grid { display: flex; flex-direction: column; gap: 8px; }
    .detail-grid > div { display: flex; gap: 12px; align-items: flex-start; font-size: 13px; }
    .detail-key { color: #64748b; width: 100px; flex-shrink: 0; font-size: 12px; }
    .inline-json {
      background: #f1f5f9;
      border: 1px solid #e2e8f0;
      border-radius: 4px;
      padding: 6px 8px;
      font-size: 10px;
      max-height: 120px;
      overflow: auto;
    }
  `]
})
export class AuditComponent implements OnInit {
  events: any[] = [];
  resourceEvents: any[] = [];
  stats: any = null;
  selected: any = null;
  lookupType = 'TRANSACTION';
  lookupId = '';

  filters = { event_type: '', resource_type: '', actor: '', limit: '20' };

  get statEventEntries() {
    if (!this.stats?.events_by_type) return [];
    return Object.entries(this.stats.events_by_type).map(([key, value]) => ({
      key: key.replace(/_/g, ' ').toLowerCase(),
      value
    })).slice(0, 4);
  }

  constructor(private api: ApiService) {}

  ngOnInit() {
    this.api.getAuditStats().subscribe({
      next: (res: any) => { this.stats = res.data || res; },
      error: () => {}
    });
    this.loadEvents();
  }

  loadEvents() {
    const params: Record<string, string> = {};
    if (this.filters.event_type) params['event_type'] = this.filters.event_type;
    if (this.filters.resource_type) params['resource_type'] = this.filters.resource_type;
    if (this.filters.actor) params['actor'] = this.filters.actor;
    if (this.filters.limit) params['limit'] = this.filters.limit;
    this.api.getAuditEvents(params).subscribe({
      next: (res: any) => { this.events = res.data || res || []; },
      error: () => {}
    });
  }

  loadByResource() {
    if (!this.lookupId) return;
    this.api.getAuditForResource(this.lookupType, this.lookupId).subscribe({
      next: (res: any) => { this.resourceEvents = res.data || res || []; },
      error: () => {}
    });
  }
}
