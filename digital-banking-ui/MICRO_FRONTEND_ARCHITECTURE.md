# Digital Banking Micro Frontend Architecture

## Overview

This is a **Micro Frontend (MFE) architecture** using Angular with Module Federation (Webpack 5). Each banking service has its own independent frontend that can be developed, deployed, and scaled independently.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        SHELL APPLICATION (Port 4200)             │
│                   (Host / Container Application)                 │
│                                                                   │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  Navigation  │  │   Auth/User  │  │   Layout    │          │
│  │   Sidebar    │  │   Context    │  │   Header    │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │                    ROUTER OUTLET                            │ │
│  │                  (Routes to MFEs)                           │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │  Micro Frontend Component (Loaded Dynamically)      │ │ │
│  │  │  (Account-MFE, Transaction-MFE, etc.)               │ │ │
│  │  └──────────────────────────────────────────────────────┘ │ │
│  └────────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘

                              │
                ┌─────────────┼─────────────┐
                │             │             │
            ┌───▼────┐    ┌───▼────┐    ┌──▼────┐
            │ Account │    │Transaction  │Transfer│
            │  MFE    │    │   MFE       │  MFE  │
            │ (4201)  │    │  (4202)     │(4203) │
            └────┬────┘    └────┬────┘    └──┬───┘
                 │             │             │
            ┌────▼────┐    ┌────▼────┐   ┌──▼────┐
            │Notification │Settings │
            │  MFE (4204) │MFE(4205)│
            └─────────────┴─────────┘
```

---

## Services Structure

### 1. **Shell Application** (Port 4200)
**Type**: Host/Container Application
**Responsibility**:
- Main entry point for users
- Authentication and user context management
- Navigation and sidebar
- Routes requests to appropriate micro frontends
- Shared services (auth, theme, global state)

**Key Files**:
- `shell-app/src/app/app.component.ts` - Main layout with router outlet
- `shell-app/src/app/shared/` - Shared authentication, theme, services
- `shell-app/webpack.config.js` - Module Federation host config
- `shell-app/src/app/app-routing.module.ts` - Routes to MFEs

### 2. **Account Micro Frontend** (Port 4201)
**Type**: Standalone Module
**Responsibility**:
- Account management (create, view, update)
- Account balance display
- Account status
- Account details and history

**Routes**:
- `/accounts` - List accounts
- `/accounts/:id` - Account details
- `/accounts/create` - Create new account

**Key Components**:
- AccountListComponent
- AccountDetailsComponent
- AccountCardComponent
- BalanceDisplayComponent

### 3. **Transaction Micro Frontend** (Port 4202)
**Type**: Standalone Module
**Responsibility**:
- Transaction history
- Transaction filtering and search
- Transaction export
- Transaction details

**Routes**:
- `/transactions` - List transactions
- `/transactions/:id` - Transaction details
- `/transactions/export` - Export transactions

**Key Components**:
- TransactionListComponent
- TransactionDetailsComponent
- TransactionFilterComponent
- TransactionExportComponent

### 4. **Transfer Micro Frontend** (Port 4203)
**Type**: Standalone Module
**Responsibility**:
- Money transfer flow
- Transfer validation
- Recipient management
- Transfer confirmation and tracking

**Routes**:
- `/transfers` - Transfers list/history
- `/transfers/new` - Create new transfer
- `/transfers/:id` - Transfer details

**Key Components**:
- TransferFormComponent
- RecipientSelectComponent
- TransferConfirmationComponent
- TransferHistoryComponent

### 5. **Notification Micro Frontend** (Port 4204)
**Type**: Standalone Module
**Responsibility**:
- Notification center
- Notification preferences
- Notification history
- Notification delivery status

**Routes**:
- `/notifications` - Notification center
- `/notifications/preferences` - Notification settings
- `/notifications/history` - Notification history

**Key Components**:
- NotificationCenterComponent
- NotificationItemComponent
- NotificationPreferencesComponent
- NotificationHistoryComponent

### 6. **Settings Micro Frontend** (Port 4205)
**Type**: Standalone Module
**Responsibility**:
- User profile management
- Security settings (password, 2FA)
- Preferences (theme, language, notifications)
- Account closure

**Routes**:
- `/settings` - Settings overview
- `/settings/profile` - Profile management
- `/settings/security` - Security settings
- `/settings/preferences` - User preferences

**Key Components**:
- SettingsOverviewComponent
- ProfileFormComponent
- SecuritySettingsComponent
- PreferencesFormComponent

---

## Module Federation Configuration

### Host (Shell App) webpack.config.js
```javascript
const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'shell',
  filename: 'remoteEntry.js',
  
  remotes: {
    account: 'http://localhost:4201/remoteEntry.js',
    transaction: 'http://localhost:4202/remoteEntry.js',
    transfer: 'http://localhost:4203/remoteEntry.js',
    notification: 'http://localhost:4204/remoteEntry.js',
    settings: 'http://localhost:4205/remoteEntry.js',
  },
  
  shared: shareAll({
    singleton: true,
    strictVersion: false,
    requiredVersion: 'auto',
  }),
});
```

### Remote (MFE) webpack.config.js Example
```javascript
const { shareAll, withModuleFederationPlugin } = require('@angular-architects/module-federation/webpack');

module.exports = withModuleFederationPlugin({
  name: 'account',
  filename: 'remoteEntry.js',
  exposes: {
    './Module': './src/app/account/account.module.ts',
  },
  
  shared: shareAll({
    singleton: true,
    strictVersion: false,
    requiredVersion: 'auto',
  }),
});
```

---

## Routing Architecture

### Shell App Routes
```typescript
const routes: Routes = [
  { path: '', redirectTo: 'dashboard', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  
  {
    path: 'app',
    component: LayoutComponent,
    canActivate: [AuthGuard],
    children: [
      {
        path: 'dashboard',
        loadChildren: () => import('dashboard/Module').then(m => m.DashboardModule),
      },
      {
        path: 'accounts',
        loadChildren: () => import('account/Module').then(m => m.AccountModule),
      },
      {
        path: 'transactions',
        loadChildren: () => import('transaction/Module').then(m => m.TransactionModule),
      },
      {
        path: 'transfers',
        loadChildren: () => import('transfer/Module').then(m => m.TransferModule),
      },
      {
        path: 'notifications',
        loadChildren: () => import('notification/Module').then(m => m.NotificationModule),
      },
      {
        path: 'settings',
        loadChildren: () => import('settings/Module').then(m => m.SettingsModule),
      },
    ],
  },
];
```

---

## Shared State & Communication

### 1. Shared Authentication Service
**Location**: Shell app
**Responsibility**: User login, token management, user context

```typescript
// Shared service in shell app
@Injectable({ providedIn: 'root' })
export class AuthService {
  currentUser$ = new BehaviorSubject<User | null>(null);
  isAuthenticated$ = this.currentUser$.pipe(map(user => !!user));
  
  login(credentials: LoginCredentials): Observable<User> { }
  logout(): void { }
  refreshToken(): Observable<string> { }
}
```

### 2. Shared Theme Service
**Location**: Shell app
**Responsibility**: VRGT theme colors, typography, dark mode

```typescript
@Injectable({ providedIn: 'root' })
export class ThemeService {
  theme$ = new BehaviorSubject<'light' | 'dark'>('light');
  
  toggleTheme(): void { }
  applyVRGTTheme(): void { }
}
```

### 3. Shared Storage Service
**Location**: Shell app
**Responsibility**: Access to localStorage, sessionStorage with type safety

```typescript
@Injectable({ providedIn: 'root' })
export class StorageService {
  setItem<T>(key: string, value: T): void { }
  getItem<T>(key: string): T | null { }
  removeItem(key: string): void { }
}
```

### 4. Event Bus (RxJS Subject)
**Location**: Shell app
**Pattern**: Publish-Subscribe for MFE communication

```typescript
@Injectable({ providedIn: 'root' })
export class EventBusService {
  private eventBus$ = new Subject<MFEEvent>();
  
  emit(event: MFEEvent): void { }
  on(eventType: string): Observable<MFEEvent> { }
}
```

---

## Communication Between MFEs

### Pattern 1: Through Shell App (Recommended)
```typescript
// In Account MFE - Listen to transaction updates
constructor(private eventBus: EventBusService) {
  this.eventBus.on('transaction.created').subscribe(event => {
    this.loadAccounts(); // Refresh accounts
  });
}

// In Transaction MFE - Emit event after transaction
this.eventBus.emit({
  type: 'transaction.created',
  payload: { transactionId, amount, toAccountId }
});
```

### Pattern 2: API-Based Communication
```typescript
// Each MFE communicates with its respective backend service
// No direct MFE-to-MFE communication
// All state changes go through backend

export class AccountMFEService {
  getAccounts(): Observable<Account[]> {
    return this.http.get('/api/accounts');
  }
}
```

---

## Shared Components Library

Create a separate `shared-components` library for VRGT design system components:

```
shared-components/
├── src/
│  ├── lib/
│  │  ├── button/
│  │  ├── card/
│  │  ├── form/
│  │  ├── badge/
│  │  ├── alert/
│  │  └── modal/
│  ├── styles/
│  │  └── vrgt-theme.scss (VRGT color variables)
│  └── index.ts
└── package.json
```

Each MFE imports and uses shared components:
```typescript
import { VRGTButtonComponent, VRGTCardComponent } from 'shared-components';
```

---

## Development Workflow

### Start All Services Locally
```bash
# Terminal 1: Start Shell App
cd shell-app && npm start

# Terminal 2: Account MFE
cd account-mfe && npm start

# Terminal 3: Transaction MFE
cd transaction-mfe && npm start

# Terminal 4: Transfer MFE
cd transfer-mfe && npm start

# Terminal 5: Notification MFE
cd notification-mfe && npm start

# Terminal 6: Settings MFE
cd settings-mfe && npm start
```

### Docker Compose for Development
```yaml
version: '3.8'

services:
  shell:
    build:
      context: ./shell-app
      dockerfile: Dockerfile.dev
    ports:
      - "4200:4200"
    environment:
      - ACCOUNT_MFE_URL=http://localhost:4201
      - TRANSACTION_MFE_URL=http://localhost:4202
      - TRANSFER_MFE_URL=http://localhost:4203
      - NOTIFICATION_MFE_URL=http://localhost:4204
      - SETTINGS_MFE_URL=http://localhost:4205

  account-mfe:
    build: ./account-mfe
    ports:
      - "4201:4200"

  transaction-mfe:
    build: ./transaction-mfe
    ports:
      - "4202:4200"

  transfer-mfe:
    build: ./transfer-mfe
    ports:
      - "4203:4200"

  notification-mfe:
    build: ./notification-mfe
    ports:
      - "4204:4200"

  settings-mfe:
    build: ./settings-mfe
    ports:
      - "4205:4200"

networks:
  banking-network:
    driver: bridge
```

---

## Benefits of This Architecture

1. **Independent Deployment**: Each MFE can be deployed separately
2. **Team Autonomy**: Teams own their complete service (backend + frontend)
3. **Technology Flexibility**: Each MFE can use different versions of Angular/dependencies
4. **Scalability**: Scale individual MFEs based on demand
5. **Faster Development**: Parallel development across teams
6. **Easy Testing**: Each MFE has isolated tests
7. **Code Reusability**: Shared component library and services

---

## Performance Optimization

### Lazy Loading
- Each MFE is lazy-loaded via dynamic imports
- Only loaded when user navigates to that route

### Code Sharing
- Core Angular, RxJS, and utilities are shared between MFEs
- Reduces bundle size significantly

### Caching Strategy
- Shell app caches remote module bundles
- Service workers for offline support

---

## Security Considerations

1. **Authentication**: Centralized in Shell App
2. **CORS**: Configure CORS headers for MFE communication
3. **API Access**: Each MFE accesses only its own backend service
4. **Token Management**: Shell app manages JWT tokens, passes to MFEs
5. **CSP Headers**: Configure Content Security Policy

---

## Testing Strategy

### Unit Tests
- Each MFE has isolated unit tests
- Mock backend services

### Integration Tests
- Test MFE within Shell app
- Mock remote modules

### E2E Tests
- Cypress/Playwright tests across entire application
- Test user flows crossing multiple MFEs

---

## Future Enhancements

1. **Shared Analytics**: Central analytics tracking across MFEs
2. **Feature Flags**: Enable/disable MFEs based on configuration
3. **Performance Monitoring**: Track bundle sizes and load times
4. **A/B Testing**: Run experiments on individual MFEs
5. **Advanced Caching**: Service Worker with cache strategies
6. **Internationalization**: Centralized i18n in Shell app

---

## File Structure

```
digital-banking-ui/
├── shell-app/
│  ├── src/
│  │  ├── app/
│  │  │  ├── app.component.ts
│  │  │  ├── layout/
│  │  │  ├── shared/
│  │  │  │  ├── services/
│  │  │  │  │  ├── auth.service.ts
│  │  │  │  │  ├── theme.service.ts
│  │  │  │  │  ├── event-bus.service.ts
│  │  │  │  │  └── storage.service.ts
│  │  │  │  └── guards/
│  │  │  └── app-routing.module.ts
│  │  └── main.ts
│  ├── webpack.config.js
│  ├── Dockerfile
│  └── package.json
│
├── account-mfe/
│  ├── src/
│  │  ├── app/
│  │  │  ├── account/
│  │  │  │  ├── account.module.ts
│  │  │  │  ├── account-list/
│  │  │  │  ├── account-details/
│  │  │  │  └── account.service.ts
│  │  └── main.ts
│  ├── webpack.config.js
│  ├── Dockerfile
│  └── package.json
│
├── transaction-mfe/
├── transfer-mfe/
├── notification-mfe/
├── settings-mfe/
│
├── shared-components/
│  ├── src/lib/
│  │  ├── button/
│  │  ├── card/
│  │  ├── form/
│  │  └── styles/vrgt-theme.scss
│  └── package.json
│
├── docker-compose.yml
├── docker-compose.prod.yml
└── MICRO_FRONTEND_ARCHITECTURE.md
```

---

## Summary

This micro frontend architecture provides:
- ✅ Independent, scalable frontend services
- ✅ Aligned with backend microservices
- ✅ VRGT design system consistency
- ✅ Team autonomy and parallel development
- ✅ Production-ready with Docker support
- ✅ Comprehensive testing capabilities

**Status**: Ready for implementation
