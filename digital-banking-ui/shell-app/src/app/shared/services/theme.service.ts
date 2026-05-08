import { Injectable } from '@angular/core';
import { BehaviorSubject } from 'rxjs';

export type ThemeMode = 'light' | 'dark';

interface VRGTTheme {
  // Primary colors
  '--vrgt-dark-purple': string;
  '--vrgt-medium-purple': string;
  '--vrgt-light-purple': string;
  '--vrgt-teal': string;
  '--vrgt-light-teal': string;
  '--vrgt-amber': string;
  '--vrgt-light-amber': string;
  '--vrgt-red': string;
  '--vrgt-light-red': string;
  '--vrgt-green': string;
  '--vrgt-light-green': string;

  // Neutral colors
  '--vrgt-white': string;
  '--vrgt-off-white': string;
  '--vrgt-light-gray': string;
  '--vrgt-medium-gray': string;
  '--vrgt-dark-gray': string;
  '--vrgt-black': string;

  // Text colors
  '--vrgt-text-primary': string;
  '--vrgt-text-secondary': string;
  '--vrgt-text-disabled': string;

  // Background colors
  '--vrgt-bg-primary': string;
  '--vrgt-bg-secondary': string;

  // Shadow
  '--vrgt-shadow': string;
}

@Injectable({
  providedIn: 'root',
})
export class ThemeService {
  private themeSubject = new BehaviorSubject<ThemeMode>('light');
  theme$ = this.themeSubject.asObservable();

  private vrgtTheme: VRGTTheme = {
    '--vrgt-dark-purple': '#26215C',
    '--vrgt-medium-purple': '#534AB7',
    '--vrgt-light-purple': '#E8E4F8',
    '--vrgt-teal': '#1D9E75',
    '--vrgt-light-teal': '#D5F0EB',
    '--vrgt-amber': '#EF9F27',
    '--vrgt-light-amber': '#FFF5E6',
    '--vrgt-red': '#E74C3C',
    '--vrgt-light-red': '#FADBD8',
    '--vrgt-green': '#27AE60',
    '--vrgt-light-green': '#D5F4E6',
    '--vrgt-white': '#FFFFFF',
    '--vrgt-off-white': '#F8F8F8',
    '--vrgt-light-gray': '#D3D1C7',
    '--vrgt-medium-gray': '#999999',
    '--vrgt-dark-gray': '#4A4A4A',
    '--vrgt-black': '#000000',
    '--vrgt-text-primary': '#26215C',
    '--vrgt-text-secondary': '#4A4A4A',
    '--vrgt-text-disabled': '#999999',
    '--vrgt-bg-primary': '#FFFFFF',
    '--vrgt-bg-secondary': '#F8F8F8',
    '--vrgt-shadow': '0 2px 8px rgba(38, 33, 92, 0.1)',
  };

  constructor() {
    this.loadThemeFromStorage();
  }

  applyVRGTTheme(): void {
    const root = document.documentElement;

    // Apply all VRGT colors
    Object.entries(this.vrgtTheme).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });

    // Apply typography
    this.applyTypography();

    // Apply spacing
    this.applySpacing();

    // Apply current theme mode
    this.applyThemeMode(this.themeSubject.value);
  }

  toggleTheme(): void {
    const newTheme = this.themeSubject.value === 'light' ? 'dark' : 'light';
    this.setTheme(newTheme);
  }

  setTheme(theme: ThemeMode): void {
    this.themeSubject.next(theme);
    localStorage.setItem('theme', theme);
    this.applyThemeMode(theme);
  }

  private applyThemeMode(theme: ThemeMode): void {
    const root = document.documentElement;

    if (theme === 'dark') {
      root.style.setProperty('--vrgt-bg-primary', '#1A1A1A');
      root.style.setProperty('--vrgt-bg-secondary', '#2D2D2D');
      root.style.setProperty('--vrgt-text-primary', '#FFFFFF');
      root.style.setProperty('--vrgt-text-secondary', '#D3D1C7');
    } else {
      root.style.setProperty('--vrgt-bg-primary', '#FFFFFF');
      root.style.setProperty('--vrgt-bg-secondary', '#F8F8F8');
      root.style.setProperty('--vrgt-text-primary', '#26215C');
      root.style.setProperty('--vrgt-text-secondary', '#4A4A4A');
    }

    document.body.classList.toggle('dark-theme', theme === 'dark');
  }

  private applyTypography(): void {
    const root = document.documentElement;

    // Typography scales
    const typography = {
      '--vrgt-font-h1': '32px',
      '--vrgt-font-h1-weight': '700',
      '--vrgt-font-h2': '28px',
      '--vrgt-font-h2-weight': '700',
      '--vrgt-font-h3': '24px',
      '--vrgt-font-h3-weight': '700',
      '--vrgt-font-h4': '20px',
      '--vrgt-font-h4-weight': '700',
      '--vrgt-font-h5': '18px',
      '--vrgt-font-h5-weight': '600',
      '--vrgt-font-body-lg': '18px',
      '--vrgt-font-body': '16px',
      '--vrgt-font-body-sm': '14px',
      '--vrgt-font-caption': '12px',
      '--vrgt-font-family': '"Segoe UI", "Roboto", "Oxygen", "Ubuntu", sans-serif',
      '--vrgt-font-family-mono': '"Courier New", monospace',
    };

    Object.entries(typography).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
  }

  private applySpacing(): void {
    const root = document.documentElement;

    const spacing = {
      '--vrgt-space-xs': '4px',
      '--vrgt-space-sm': '8px',
      '--vrgt-space-md': '12px',
      '--vrgt-space-lg': '16px',
      '--vrgt-space-xl': '24px',
      '--vrgt-space-2xl': '32px',
      '--vrgt-space-3xl': '48px',
    };

    Object.entries(spacing).forEach(([key, value]) => {
      root.style.setProperty(key, value);
    });
  }

  private loadThemeFromStorage(): void {
    const savedTheme = localStorage.getItem('theme') as ThemeMode | null;
    if (savedTheme) {
      this.themeSubject.next(savedTheme);
    }
  }
}
