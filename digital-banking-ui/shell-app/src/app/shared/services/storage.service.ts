import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root',
})
export class StorageService {
  /**
   * Set a value in localStorage with type safety
   * @param key The storage key
   * @param value The value to store (will be serialized to JSON)
   */
  setItem<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      localStorage.setItem(key, serialized);
    } catch (error) {
      console.error(`Failed to set storage item '${key}':`, error);
    }
  }

  /**
   * Get a value from localStorage with type safety
   * @param key The storage key
   * @returns The deserialized value or null if not found
   */
  getItem<T>(key: string): T | null {
    try {
      const item = localStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error(`Failed to get storage item '${key}':`, error);
      return null;
    }
  }

  /**
   * Remove a value from localStorage
   * @param key The storage key
   */
  removeItem(key: string): void {
    try {
      localStorage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove storage item '${key}':`, error);
    }
  }

  /**
   * Clear all localStorage items
   */
  clear(): void {
    try {
      localStorage.clear();
    } catch (error) {
      console.error('Failed to clear storage:', error);
    }
  }

  /**
   * Check if a key exists in localStorage
   * @param key The storage key
   */
  hasItem(key: string): boolean {
    return localStorage.getItem(key) !== null;
  }

  /**
   * Get all keys in localStorage
   */
  keys(): string[] {
    const keys = [];
    for (let i = 0; i < localStorage.length; i++) {
      const key = localStorage.key(i);
      if (key) {
        keys.push(key);
      }
    }
    return keys;
  }

  /**
   * SessionStorage wrapper - Set a value
   */
  setSessionItem<T>(key: string, value: T): void {
    try {
      const serialized = JSON.stringify(value);
      sessionStorage.setItem(key, serialized);
    } catch (error) {
      console.error(`Failed to set session storage item '${key}':`, error);
    }
  }

  /**
   * SessionStorage wrapper - Get a value
   */
  getSessionItem<T>(key: string): T | null {
    try {
      const item = sessionStorage.getItem(key);
      return item ? JSON.parse(item) : null;
    } catch (error) {
      console.error(`Failed to get session storage item '${key}':`, error);
      return null;
    }
  }

  /**
   * SessionStorage wrapper - Remove a value
   */
  removeSessionItem(key: string): void {
    try {
      sessionStorage.removeItem(key);
    } catch (error) {
      console.error(`Failed to remove session storage item '${key}':`, error);
    }
  }

  /**
   * SessionStorage wrapper - Clear all
   */
  clearSession(): void {
    try {
      sessionStorage.clear();
    } catch (error) {
      console.error('Failed to clear session storage:', error);
    }
  }
}
