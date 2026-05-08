import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';
import { LoginComponent } from './login/login.component';
import { LayoutComponent } from './layout/layout.component';
import { AuthGuard } from './shared/guards/auth.guard';

const routes: Routes = [
  {
    path: '',
    redirectTo: 'app/dashboard',
    pathMatch: 'full',
  },
  {
    path: 'login',
    component: LoginComponent,
  },
  {
    path: 'app',
    component: LayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: 'dashboard',
        loadChildren: () =>
          import('shared-components/dashboard').then(
            (m) => m.DashboardModule,
          ),
      },
      {
        path: 'accounts',
        loadChildren: () =>
          import('account/Module').then((m) => m.AccountModule),
      },
      {
        path: 'transactions',
        loadChildren: () =>
          import('transaction/Module').then((m) => m.TransactionModule),
      },
      {
        path: 'transfers',
        loadChildren: () =>
          import('transfer/Module').then((m) => m.TransferModule),
      },
      {
        path: 'notifications',
        loadChildren: () =>
          import('notification/Module').then((m) => m.NotificationModule),
      },
      {
        path: 'settings',
        loadChildren: () =>
          import('settings/Module').then((m) => m.SettingsModule),
      },
    ],
  },
  {
    path: '**',
    redirectTo: 'app/dashboard',
  },
];

@NgModule({
  imports: [RouterModule.forRoot(routes, { useHash: true })],
  exports: [RouterModule],
})
export class AppRoutingModule {}
