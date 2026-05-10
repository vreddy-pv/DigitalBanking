import { Routes } from '@angular/router';
import { authGuard } from './auth.guard';
import { LoginComponent } from './login/login.component';
import { ShellComponent } from './shell/shell.component';
import { DashboardComponent } from './dashboard/dashboard.component';
import { AccountsComponent } from './accounts/accounts.component';
import { TransactionsComponent } from './transactions/transactions.component';
import { KycComponent } from './kyc/kyc.component';
import { AnalyticsComponent } from './analytics/analytics.component';
import { ComplianceComponent } from './compliance/compliance.component';
import { AuditComponent } from './audit/audit.component';

export const routes: Routes = [
  { path: 'login', component: LoginComponent },
  {
    path: '',
    component: ShellComponent,
    canActivate: [authGuard],
    children: [
      { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
      { path: 'dashboard', component: DashboardComponent },
      { path: 'accounts', component: AccountsComponent },
      { path: 'transactions', component: TransactionsComponent },
      { path: 'kyc', component: KycComponent },
      { path: 'analytics', component: AnalyticsComponent },
      { path: 'compliance', component: ComplianceComponent },
      { path: 'audit', component: AuditComponent },
    ]
  },
  { path: '**', redirectTo: '' }
];
