# Digital Banking UI Design System
## VRGT Theme - Angular Elements Frontend

**Application**: Digital Banking Platform  
**Design System**: VRGT (Vertex Realm Global Technologies)  
**Framework**: Angular with Web Components (Angular Elements)  
**Tagline**: "Secure Banking at the Peak of Digital Realm"

---

## Table of Contents
1. [Color System](#color-system)
2. [Typography](#typography)
3. [Component Library](#component-library)
4. [Page Layouts](#page-layouts)
5. [Design Patterns](#design-patterns)
6. [Angular Elements Implementation](#angular-elements-implementation)

---

## Color System

### VRGT Brand Colors

```css
:root {
  /* Primary Colors */
  --vrgt-dark-purple: #26215C;        /* Dark backgrounds, premium feel */
  --vrgt-medium-purple: #534AB7;      /* Primary buttons, CTAs */
  --vrgt-light-purple: #AFA9EC;       /* Borders, hover states */
  
  /* Secondary Colors */
  --vrgt-teal: #1D9E75;               /* Success, secondary actions */
  --vrgt-amber: #EF9F27;              /* Warnings, highlights */
  
  /* Neutral Colors */
  --vrgt-charcoal: #2C2C2A;           /* Body text (dark) */
  --vrgt-gray: #888780;               /* Secondary text */
  --vrgt-light-gray: #D3D1C7;         /* Borders, dividers */
  --vrgt-off-white: #F1EFE8;          /* Card backgrounds */
  --vrgt-very-light: #EEEDFE;         /* Subtle fills */
  --white: #FFFFFF;                   /* Pure white */
  
  /* Semantic Colors */
  --success: #1D9E75;
  --warning: #EF9F27;
  --error: #E74C3C;
  --info: #534AB7;
}
```

### Gradients

```css
/* Primary Gradient - Hero sections */
--gradient-primary: linear-gradient(90deg, #26215C 0%, #7F77DD 55%, #1D9E75 100%);

/* Hex Gradient - Logo/Premium elements */
--gradient-hex: linear-gradient(135deg, #26215C 0%, #3C3489 100%);

/* Teal Gradient - Success states */
--gradient-success: linear-gradient(135deg, #1D9E75 0%, #15A475 100%);

/* Purple Gradient - Interactive elements */
--gradient-interactive: linear-gradient(135deg, #534AB7 0%, #7F77DD 100%);
```

---

## Typography

### Font Family
```css
--font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", sans-serif;
--font-family-mono: "SF Mono", Monaco, "Cascadia Code", "Roboto Mono", Courier, monospace;
```

### Type Scale

| Level | Size | Weight | Usage | CSS Class |
|-------|------|--------|-------|-----------|
| **H1** | 32px | 700 | Page titles | `.h1`, `<h1>` |
| **H2** | 28px | 700 | Section titles | `.h2`, `<h2>` |
| **H3** | 24px | 700 | Card titles | `.h3`, `<h3>` |
| **H4** | 20px | 600 | Subsections | `.h4`, `<h4>` |
| **Body Large** | 18px | 400 | Main content | `.body-lg` |
| **Body** | 16px | 400 | Standard text | `.body`, `<p>` |
| **Body Small** | 14px | 400 | Secondary text | `.body-sm` |
| **Label** | 12px | 500 | Labels, badges | `.label` |
| **Caption** | 11px | 300 | Captions, hints | `.caption` |
| **Mono** | 14px | 400 | Code, amounts | `.mono` |

### Line Height & Spacing
```css
--line-height-tight: 1.2;     /* Headings */
--line-height-normal: 1.5;    /* Body text */
--line-height-relaxed: 1.8;   /* Descriptive text */
```

---

## Component Library

### Buttons

#### Primary Button
```css
.btn-primary {
  background-color: var(--vrgt-medium-purple);
  color: white;
  border-radius: 4px;
  padding: 10px 24px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-primary:hover {
  background: linear-gradient(135deg, #534AB7 0%, #7F77DD 100%);
  box-shadow: 0 4px 12px rgba(83, 74, 183, 0.3);
  transform: translateY(-2px);
}

.btn-primary:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(83, 74, 183, 0.2);
}

.btn-primary:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}
```

#### Secondary Button (Teal)
```css
.btn-secondary {
  background-color: var(--vrgt-teal);
  color: white;
  border-radius: 4px;
  padding: 10px 24px;
  border: none;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, #1D9E75 0%, #15A475 100%);
  box-shadow: 0 4px 12px rgba(29, 158, 117, 0.3);
}
```

#### Danger Button
```css
.btn-danger {
  background-color: #E74C3C;
  color: white;
  border-radius: 4px;
  padding: 10px 24px;
  border: none;
  font-weight: 600;
  cursor: pointer;
}

.btn-danger:hover {
  background-color: #C0392B;
  box-shadow: 0 4px 12px rgba(231, 76, 60, 0.3);
}
```

#### Text Button
```css
.btn-text {
  background: transparent;
  color: var(--vrgt-medium-purple);
  border: none;
  padding: 10px 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
}

.btn-text:hover {
  background-color: rgba(83, 74, 183, 0.08);
}
```

### Cards

```css
.card {
  background-color: white;
  border: 1px solid var(--vrgt-light-gray);
  border-radius: 8px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(38, 33, 92, 0.1);
  transition: all 0.3s ease;
}

.card:hover {
  box-shadow: 0 4px 16px rgba(38, 33, 92, 0.15);
  transform: translateY(-2px);
}

.card-dark {
  background: linear-gradient(135deg, #26215C 0%, #3C3489 100%);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.1);
}

.card-light {
  background-color: var(--vrgt-very-light);
  border: 1px solid var(--vrgt-light-purple);
}

.card-success {
  background: linear-gradient(135deg, rgba(29, 158, 117, 0.05) 0%, rgba(29, 158, 117, 0.02) 100%);
  border: 1px solid rgba(29, 158, 117, 0.2);
}

.card-warning {
  background: linear-gradient(135deg, rgba(239, 159, 39, 0.05) 0%, rgba(239, 159, 39, 0.02) 100%);
  border: 1px solid rgba(239, 159, 39, 0.2);
}
```

### Form Elements

```css
/* Input Fields */
.form-group {
  margin-bottom: 20px;
}

.form-label {
  display: block;
  font-size: 12px;
  font-weight: 500;
  color: var(--vrgt-charcoal);
  margin-bottom: 8px;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.form-input,
.form-select,
.form-textarea {
  width: 100%;
  padding: 12px 16px;
  border: 1px solid var(--vrgt-light-gray);
  border-radius: 4px;
  font-family: inherit;
  font-size: 14px;
  color: var(--vrgt-charcoal);
  transition: all 0.2s ease;
  background-color: white;
}

.form-input:focus,
.form-select:focus,
.form-textarea:focus {
  border-color: var(--vrgt-medium-purple);
  background-color: rgba(83, 74, 183, 0.02);
  box-shadow: 0 0 0 3px rgba(83, 74, 183, 0.1);
  outline: none;
}

.form-input:disabled,
.form-select:disabled {
  background-color: var(--vrgt-off-white);
  color: var(--vrgt-gray);
  cursor: not-allowed;
}

/* Input Error State */
.form-input.error,
.form-select.error {
  border-color: #E74C3C;
  background-color: rgba(231, 76, 60, 0.02);
}

.form-input.error:focus {
  box-shadow: 0 0 0 3px rgba(231, 76, 60, 0.1);
}

.form-error {
  font-size: 12px;
  color: #E74C3C;
  margin-top: 4px;
  font-weight: 500;
}

.form-hint {
  font-size: 12px;
  color: var(--vrgt-gray);
  margin-top: 4px;
}

/* Checkbox & Radio */
.form-checkbox,
.form-radio {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-checkbox input[type="checkbox"],
.form-radio input[type="radio"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--vrgt-medium-purple);
}
```

### Badges

```css
.badge {
  display: inline-block;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 11px;
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.badge-primary {
  background-color: rgba(83, 74, 183, 0.15);
  color: var(--vrgt-medium-purple);
}

.badge-success {
  background-color: rgba(29, 158, 117, 0.15);
  color: var(--vrgt-teal);
}

.badge-warning {
  background-color: rgba(239, 159, 39, 0.15);
  color: var(--vrgt-amber);
}

.badge-error {
  background-color: rgba(231, 76, 60, 0.15);
  color: #E74C3C;
}

.badge-dark {
  background-color: var(--vrgt-dark-purple);
  color: white;
}
```

### Alerts

```css
.alert {
  padding: 16px 20px;
  border-radius: 4px;
  margin-bottom: 16px;
  display: flex;
  gap: 12px;
  align-items: flex-start;
}

.alert-success {
  background-color: rgba(29, 158, 117, 0.1);
  border: 1px solid var(--vrgt-teal);
  color: #0B5D3D;
}

.alert-warning {
  background-color: rgba(239, 159, 39, 0.1);
  border: 1px solid var(--vrgt-amber);
  color: #B86F00;
}

.alert-error {
  background-color: rgba(231, 76, 60, 0.1);
  border: 1px solid #E74C3C;
  color: #A93226;
}

.alert-info {
  background-color: rgba(83, 74, 183, 0.1);
  border: 1px solid var(--vrgt-medium-purple);
  color: #2C1D4A;
}

.alert-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
}

.alert-message {
  flex: 1;
  font-size: 14px;
  line-height: 1.5;
}
```

### Modals

```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
  animation: fadeIn 0.2s ease;
}

.modal {
  background: white;
  border-radius: 8px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  max-width: 600px;
  width: 90%;
  max-height: 90vh;
  overflow-y: auto;
  animation: slideUp 0.3s ease;
}

.modal-header {
  padding: 24px;
  border-bottom: 1px solid var(--vrgt-light-gray);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-title {
  font-size: 20px;
  font-weight: 700;
  color: var(--vrgt-charcoal);
}

.modal-close {
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: var(--vrgt-gray);
  transition: color 0.2s ease;
}

.modal-close:hover {
  color: var(--vrgt-charcoal);
}

.modal-body {
  padding: 24px;
}

.modal-footer {
  padding: 24px;
  border-top: 1px solid var(--vrgt-light-gray);
  display: flex;
  gap: 12px;
  justify-content: flex-end;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}
```

---

## Page Layouts

### Layout Grid
```css
.page {
  display: grid;
  grid-template-columns: 1fr;
  min-height: 100vh;
  background-color: var(--vrgt-off-white);
}

.page-with-sidebar {
  grid-template-columns: 280px 1fr;
}

@media (max-width: 768px) {
  .page-with-sidebar {
    grid-template-columns: 1fr;
  }
}

.page-header {
  background: linear-gradient(135deg, #26215C 0%, #3C3489 100%);
  color: white;
  padding: 32px 40px;
}

.page-content {
  padding: 40px;
  overflow-y: auto;
}
```

### Spacing Scale
```css
--space-xs: 4px;
--space-sm: 8px;
--space-md: 16px;
--space-lg: 24px;
--space-xl: 32px;
--space-2xl: 48px;
--space-3xl: 64px;
```

---

## Design Patterns

### Transaction Card
```
┌─────────────────────────────────────────────┐
│  Transaction Type Icon    Amount             │
│  Description              +₹1,000.00         │
│  2:30 PM, Today          [Status Badge]     │
└─────────────────────────────────────────────┘
```

### Account Overview Card
```
┌──────────────────────────┐
│ SAVINGS ACCOUNT          │
│ ACC-002                  │
│                          │
│ Current Balance          │
│ ₹25,000.00              │
│                          │
│ Available    Pending     │
│ ₹25,000.00   ₹0.00     │
└──────────────────────────┘
```

### Form Layout Pattern
```
Section Title

Label
[Input Field]
Helper text

Label
[Select Field]

[Cancel Button] [Submit Button]
```

---

## Angular Elements Implementation

### Directory Structure
```
digital-banking-ui/
├── src/
│   ├── assets/
│   │   ├── styles/
│   │   │   ├── vrgt-theme.css
│   │   │   ├── variables.css
│   │   │   ├── components.css
│   │   │   └── utilities.css
│   │   └── icons/
│   │       └── (SVG icons)
│   │
│   ├── app/
│   │   ├── components/
│   │   │   ├── button/
│   │   │   ├── card/
│   │   │   ├── form-input/
│   │   │   ├── modal/
│   │   │   ├── navbar/
│   │   │   └── sidebar/
│   │   │
│   │   ├── layouts/
│   │   │   ├── dashboard-layout/
│   │   │   └── auth-layout/
│   │   │
│   │   ├── pages/
│   │   │   ├── login/
│   │   │   ├── register/
│   │   │   ├── dashboard/
│   │   │   ├── accounts/
│   │   │   ├── transactions/
│   │   │   ├── transfer/
│   │   │   ├── profile/
│   │   │   └── settings/
│   │   │
│   │   ├── services/
│   │   │   ├── api.service.ts
│   │   │   ├── auth.service.ts
│   │   │   └── notification.service.ts
│   │   │
│   │   └── app.module.ts
│   │
│   └── main.ts
│
├── angular.json
├── package.json
└── tsconfig.json
```

---

## Color Usage Guidelines

### Text
- **Primary headings**: `var(--vrgt-dark-purple)` or white on dark backgrounds
- **Body text**: `var(--vrgt-charcoal)`
- **Secondary text**: `var(--vrgt-gray)`
- **Links**: `var(--vrgt-medium-purple)` (underlined on hover)

### Backgrounds
- **Page background**: `var(--vrgt-off-white)`
- **Card background**: `white`
- **Dark sections**: `var(--vrgt-dark-purple)` with gradient
- **Input focus**: `rgba(83, 74, 183, 0.05)`

### Interactive Elements
- **Primary CTA**: `var(--vrgt-medium-purple)` gradient
- **Secondary CTA**: `var(--vrgt-teal)`
- **Danger actions**: `#E74C3C`
- **Success indicators**: `var(--vrgt-teal)`
- **Warning indicators**: `var(--vrgt-amber)`

### Borders & Dividers
- **Primary borders**: `var(--vrgt-light-gray)`
- **Secondary borders**: `var(--vrgt-light-purple)`
- **Focus borders**: `var(--vrgt-medium-purple)`

---

## Responsive Breakpoints

```css
/* Mobile First */
@media (min-width: 640px) { /* Tablets */ }
@media (min-width: 768px) { /* Small desktops */ }
@media (min-width: 1024px) { /* Desktops */ }
@media (min-width: 1280px) { /* Large screens */ }
```

---

## Accessibility Guidelines

- **Color contrast**: All text meets WCAG AA standards (4.5:1 for normal text)
- **Focus states**: Visible outline with `box-shadow` and border color change
- **Form labels**: Always associated with inputs via `for` attribute
- **Icons**: Include `aria-label` for icon-only buttons
- **Modals**: Use `role="dialog"` and manage focus
- **Loading states**: Include `aria-busy="true"` and `aria-label`

---

## Animation Principles

- **Duration**: 200-300ms for micro-interactions, 300-500ms for page transitions
- **Easing**: `ease` for most animations, `ease-out` for exits
- **Reduce motion**: Respect `prefers-reduced-motion` media query
- **Types**: Fade, slide, scale – subtle and professional

```css
@media (prefers-reduced-motion: reduce) {
  * {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Dark Mode Support (Future)

```css
@media (prefers-color-scheme: dark) {
  :root {
    --vrgt-off-white: #1a1a1a;
    --vrgt-very-light: #2d2d2d;
    --white: #0f0f0f;
    --vrgt-charcoal: #e0e0e0;
  }
}
```

---

## Summary

This design system provides a cohesive, professional banking interface using the VRGT brand identity. All components are built with:

✅ Consistent color palette  
✅ Clear typography hierarchy  
✅ Responsive design  
✅ Accessibility first  
✅ Angular Elements integration  
✅ Professional animations  
✅ Enterprise-grade quality  

Implementation starts with creating reusable Angular web components that wrap these styles and patterns.
