import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { ApiService } from './api.service';
import { LoginComponent } from './login/login.component';
import { DashboardComponent } from './dashboard/dashboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, LoginComponent, DashboardComponent],
  template: `
    <div *ngIf="!isLoggedIn; else dashboard">
      <app-login (loginSuccess)="onLoginSuccess($event)"></app-login>
    </div>
    <ng-template #dashboard>
      <div class="header">
        <div class="container" style="display: flex; justify-content: space-between; align-items: center;">
          <h1>💳 Digital Banking</h1>
          <button class="btn btn-danger" (click)="logout()">Logout</button>
        </div>
      </div>
      <app-dashboard></app-dashboard>
    </ng-template>
  `,
  styles: [`
    .header {
      background: white;
      box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
  `]
})
export class AppComponent {
  isLoggedIn = false;

  constructor(private apiService: ApiService) {
    this.isLoggedIn = this.apiService.isLoggedIn();
  }

  onLoginSuccess(token: string) {
    this.isLoggedIn = true;
  }

  logout() {
    this.apiService.logout();
    this.isLoggedIn = false;
  }
}
