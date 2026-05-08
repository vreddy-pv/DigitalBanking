import { Component, OnInit } from '@angular/core';
import { Observable } from 'rxjs';
import { AuthService, User } from '../shared/services/auth.service';
import { ThemeService, ThemeMode } from '../shared/services/theme.service';
import { EventBusService, MFE_EVENTS } from '../shared/services/event-bus.service';

@Component({
  selector: 'app-layout',
  templateUrl: './layout.component.html',
  styleUrls: ['./layout.component.scss'],
})
export class LayoutComponent implements OnInit {
  currentUser$: Observable<User | null>;
  currentTheme$: Observable<ThemeMode>;
  isNotificationOpen = false;
  unreadNotificationCount = 0;

  navigationItems = [
    { label: 'Dashboard', route: '/app/dashboard', icon: 'home' },
    { label: 'Accounts', route: '/app/accounts', icon: 'account_balance' },
    {
      label: 'Transactions',
      route: '/app/transactions',
      icon: 'receipt_long',
    },
    {
      label: 'Money Transfer',
      route: '/app/transfers',
      icon: 'send',
    },
    { label: 'Notifications', route: '/app/notifications', icon: 'notifications' },
    { label: 'Settings', route: '/app/settings', icon: 'settings' },
  ];

  constructor(
    private authService: AuthService,
    private themeService: ThemeService,
    private eventBus: EventBusService,
  ) {
    this.currentUser$ = this.authService.currentUser$;
    this.currentTheme$ = this.themeService.theme$;
  }

  ngOnInit(): void {
    // Listen for notification events
    this.eventBus.on(MFE_EVENTS.NOTIFICATION_RECEIVED).subscribe((event) => {
      this.unreadNotificationCount++;
    });

    this.eventBus.on(MFE_EVENTS.NOTIFICATION_READ).subscribe(() => {
      if (this.unreadNotificationCount > 0) {
        this.unreadNotificationCount--;
      }
    });
  }

  toggleTheme(): void {
    this.themeService.toggleTheme();
  }

  toggleNotifications(): void {
    this.isNotificationOpen = !this.isNotificationOpen;
  }

  logout(): void {
    this.authService.logout();
  }
}
