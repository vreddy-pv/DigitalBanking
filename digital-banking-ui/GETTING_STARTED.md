# Getting Started - Digital Banking Micro Frontend

## Quick Start (5 Minutes)

### Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Git

### Step 1: Install Dependencies

```bash
# Shell App
cd shell-app
npm install

# Account MFE
cd ../account-mfe
npm install

# Transaction MFE
cd ../transaction-mfe
npm install

# Transfer MFE
cd ../transfer-mfe
npm install

# Notification MFE
cd ../notification-mfe
npm install

# Settings MFE
cd ../settings-mfe
npm install
```

### Step 2: Start All Services

Open 6 terminals and run:

**Terminal 1 - Shell App (Main Application)**
```bash
cd shell-app
npm start
```
Runs on: http://localhost:4200

**Terminal 2 - Account MFE**
```bash
cd account-mfe
npm start
```
Runs on: http://localhost:4201

**Terminal 3 - Transaction MFE**
```bash
cd transaction-mfe
npm start
```
Runs on: http://localhost:4202

**Terminal 4 - Transfer MFE**
```bash
cd transfer-mfe
npm start
```
Runs on: http://localhost:4203

**Terminal 5 - Notification MFE**
```bash
cd notification-mfe
npm start
```
Runs on: http://localhost:4204

**Terminal 6 - Settings MFE**
```bash
cd settings-mfe
npm start
```
Runs on: http://localhost:4205

### Step 3: Access Application

1. Open browser: http://localhost:4200
2. You should see the login page with VRGT purple gradient background
3. Default credentials (to be configured with backend):
   - Email: `demo@example.com`
   - Password: `password123`

---

## Architecture Overview

### Shell Application (Main Container)
- **Port**: 4200
- **Role**: Host application, handles routing and authentication
- **Contains**: Login page, main layout, navigation sidebar
- **Loads**: All 5 micro frontends dynamically

### Micro Frontends (Independent Modules)
Each MFE is a completely independent Angular application:

| MFE | Port | Features |
|-----|------|----------|
| Account | 4201 | Account management, balance display, account details |
| Transaction | 4202 | Transaction history, search, export, filtering |
| Transfer | 4203 | Money transfer flows, recipient management |
| Notification | 4204 | Notification center, preferences, history |
| Settings | 4205 | User profile, security settings, preferences |

---

## Project Structure

```
digital-banking-ui/
├── shell-app/              ← Main application (Port 4200)
├── account-mfe/            ← Account module (Port 4201)
├── transaction-mfe/        ← Transaction module (Port 4202)
├── transfer-mfe/           ← Transfer module (Port 4203)
├── notification-mfe/       ← Notification module (Port 4204)
├── settings-mfe/           ← Settings module (Port 4205)
├── shared-components/      ← Shared UI components library (to create)
├── MICRO_FRONTEND_ARCHITECTURE.md
├── IMPLEMENTATION_GUIDE.md
├── GETTING_STARTED.md      (This file)
└── docker-compose.yml      (For containerized deployment)
```

---

## Key Concepts

### 1. Module Federation
- Each MFE is a **separate** Angular application
- Shell App **loads** MFEs dynamically at runtime
- Shared dependencies (Angular, RxJS) are **cached**
- Each MFE can be deployed independently

### 2. Shared Services (From Shell App)
All MFEs have access to:

**AuthService**
- User login/logout
- JWT token management
- User context

**ThemeService**
- VRGT color system
- Light/dark theme toggle
- Typography and spacing scales

**EventBusService**
- Pub/Sub for MFE communication
- No direct MFE-to-MFE coupling

**StorageService**
- Safe localStorage access
- Serialized JSON storage

### 3. Communication Between MFEs
MFEs don't communicate directly. Instead:

```
Account MFE → EventBusService → Transaction MFE
     (emit transaction.created)     (listen)
```

### 4. VRGT Design System
All components use VRGT brand colors:
- **Dark Purple** (#26215C) - Primary
- **Medium Purple** (#534AB7) - Interactive
- **Teal** (#1D9E75) - Success
- **Amber** (#EF9F27) - Highlights
- **Red** (#E74C3C) - Errors

---

## Common Tasks

### View Shell App Layout

Shell App contains:
- **Sidebar** - Navigation menu
  - Dashboard
  - Accounts
  - Transactions
  - Money Transfer
  - Notifications
  - Settings

- **Header** - Top bar with:
  - Theme toggle (light/dark)
  - Notification bell with count
  - User menu

- **Main Content** - Router outlet for MFE content

### Add a New Feature to Account MFE

```bash
# Navigate to Account MFE
cd account-mfe

# Generate new component
ng generate component account/account-settings

# Component automatically uses shared services
```

### Listen to Events from Other MFEs

```typescript
// In any MFE component
import { EventBusService } from 'shell-app/shared/services';

export class MyComponent {
  constructor(private eventBus: EventBusService) {
    // Listen for transaction created event
    this.eventBus.on('transaction.created').subscribe(event => {
      console.log('Transaction:', event.payload);
      // Refresh data, update UI, etc.
    });
  }
}
```

### Emit Events to Other MFEs

```typescript
// After creating a transaction
this.eventBus.emit({
  type: 'transaction.created',
  payload: {
    transactionId: '123',
    amount: 1000,
    type: 'TRANSFER'
  }
});
```

### Toggle Theme (Dark Mode)

```typescript
import { ThemeService } from 'shell-app/shared/services';

export class MyComponent {
  constructor(private themeService: ThemeService) {}

  toggleTheme(): void {
    this.themeService.toggleTheme();
    // Theme automatically updates app-wide
  }
}
```

---

## Troubleshooting

### MFE Not Loading
**Problem**: Remote MFE shows as undefined
**Solution**:
1. Verify MFE is running on correct port (4201-4205)
2. Check webpack.config.js has correct remote URL
3. Clear browser cache and reload

### Module Not Found Error
**Problem**: `Cannot find module 'account/Module'`
**Solution**:
1. Ensure MFE webpack.config.js has `exposes`
2. Verify MFE module exists at `src/app/[mfe-name]/[mfe-name].module.ts`
3. MFE must export the module in exposes config

### Authentication Not Working
**Problem**: Can't login or token not persisting
**Solution**:
1. Check AuthService localStorage keys
2. Verify backend API is running on port 8000
3. Check API endpoints in auth.service.ts

### Style Issues
**Problem**: VRGT colors not applying
**Solution**:
1. Verify ThemeService.applyVRGTTheme() is called in AppComponent.ngOnInit()
2. Check CSS variables in theme.service.ts
3. Clear browser cache

### Port Already in Use
**Problem**: `Address already in use :4200`
**Solution**:
```bash
# Kill process on port 4200
# On Windows:
netstat -ano | findstr :4200
taskkill /PID [PID] /F

# On Mac/Linux:
lsof -ti:4200 | xargs kill -9
```

---

## VRGT Design Colors Reference

### Brand Colors
```css
--vrgt-dark-purple: #26215C;      /* Primary brand color */
--vrgt-medium-purple: #534AB7;    /* Interactive elements */
--vrgt-light-purple: #E8E4F8;     /* Backgrounds */
--vrgt-teal: #1D9E75;             /* Success/positive */
--vrgt-amber: #EF9F27;            /* Highlights/warnings */
--vrgt-red: #E74C3C;              /* Errors/danger */
--vrgt-green: #27AE60;            /* Additional positive */
```

### Neutral Colors
```css
--vrgt-white: #FFFFFF;
--vrgt-off-white: #F8F8F8;
--vrgt-light-gray: #D3D1C7;
--vrgt-medium-gray: #999999;
--vrgt-dark-gray: #4A4A4A;
--vrgt-black: #000000;
```

---

## Testing the App

### Manual Testing Flow
1. **Login Screen**
   - ✓ Page loads with gradient background
   - ✓ Email field accepts email format
   - ✓ Password field shows/hides with eye icon
   - ✓ Form validation works
   - ✓ Login button disables when form invalid

2. **Dashboard**
   - ✓ Sidebar shows navigation items
   - ✓ Header displays theme toggle
   - ✓ Notification bell shows
   - ✓ User menu displays name
   - ✓ Active nav item highlights (amber border)

3. **Theme Toggle**
   - ✓ Click theme button in header
   - ✓ Colors change to dark theme
   - ✓ Click again to switch back to light
   - ✓ Theme persists on page reload

4. **Navigation**
   - ✓ Click Accounts → Account MFE loads
   - ✓ Click Transactions → Transaction MFE loads
   - ✓ Click Transfers → Transfer MFE loads
   - ✓ Click Notifications → Notification MFE loads
   - ✓ Click Settings → Settings MFE loads

5. **Logout**
   - ✓ Click Logout button
   - ✓ Redirected to login page
   - ✓ User data cleared from localStorage

---

## Building for Production

### Build All MFEs

```bash
# Shell App
cd shell-app && npm run build:prod

# Account MFE
cd account-mfe && npm run build:prod

# Build all others similarly
cd transaction-mfe && npm run build:prod
cd transfer-mfe && npm run build:prod
cd notification-mfe && npm run build:prod
cd settings-mfe && npm run build:prod
```

### Docker Compose Build

```bash
# Build all images
docker-compose build

# Start services
docker-compose up -d

# Stop services
docker-compose down
```

---

## Environment Configuration

Each MFE can have its own `.env` file:

```env
API_GATEWAY_URL=http://localhost:8000
ACCOUNT_SERVICE_URL=http://localhost:8002
TRANSACTION_SERVICE_URL=http://localhost:8003
NOTIFICATION_SERVICE_URL=http://localhost:8006
ENABLE_MOCK_DATA=true
DEBUG_MODE=false
```

---

## Next Steps

1. **Complete Account MFE**
   - [ ] List accounts with balance
   - [ ] Account details page
   - [ ] Create new account form
   - [ ] Account edit functionality

2. **Complete Transaction MFE**
   - [ ] Transaction list with filtering
   - [ ] Transaction details modal
   - [ ] Export functionality
   - [ ] Date range filtering

3. **Complete Transfer MFE**
   - [ ] Multi-step transfer form
   - [ ] Recipient management
   - [ ] Transfer confirmation
   - [ ] Status tracking

4. **Complete Notification MFE**
   - [ ] Notification list
   - [ ] Mark as read
   - [ ] Notification preferences
   - [ ] Push notification integration

5. **Complete Settings MFE**
   - [ ] Profile management
   - [ ] Password change
   - [ ] 2FA setup
   - [ ] Theme/language preferences

6. **Backend Integration**
   - [ ] Connect to Account Service (Port 8002)
   - [ ] Connect to Transaction Service (Port 8003)
   - [ ] Connect to Notification Service (Port 8006)
   - [ ] Connect to other backend services

7. **Testing & QA**
   - [ ] Unit tests for each component
   - [ ] Integration tests between MFEs
   - [ ] E2E tests with Cypress
   - [ ] Accessibility audit (WCAG AA)

8. **Deployment**
   - [ ] Docker Compose setup verified
   - [ ] Kubernetes YAML files created
   - [ ] CI/CD pipeline configured
   - [ ] Production environment ready

---

## Support & Help

### Documentation Files
- `MICRO_FRONTEND_ARCHITECTURE.md` - Detailed architecture
- `IMPLEMENTATION_GUIDE.md` - Step-by-step implementation
- `GETTING_STARTED.md` - This file

### Key Files to Study
- `shell-app/src/app/shared/services/` - Shared services
- `shell-app/src/app/layout/layout.component.ts` - Main layout
- `shell-app/webpack.config.js` - Module Federation config
- `shell-app/src/app/app-routing.module.ts` - Routing setup

### Resources
- [Angular Documentation](https://angular.io)
- [Module Federation](https://webpack.js.org/concepts/module-federation/)
- [VRGT Design System](../DIGITAL_BANKING_UI_DESIGN.md)

---

## Status at a Glance

✅ **Completed**
- Shell App framework
- Shared authentication services
- VRGT design system applied
- Module Federation configuration
- Login page with styling
- Layout component with navigation
- Event bus for MFE communication
- Dark/light theme support

⏳ **In Progress**
- Account MFE components
- Transaction MFE components
- Transfer MFE components
- Notification MFE components
- Settings MFE components

📋 **To Do**
- Shared component library
- Backend API integration
- Comprehensive testing
- Docker deployment

---

**Ready to start development!** 🚀

Next: Open 6 terminals and run `npm start` in each MFE directory, then navigate to http://localhost:4200
