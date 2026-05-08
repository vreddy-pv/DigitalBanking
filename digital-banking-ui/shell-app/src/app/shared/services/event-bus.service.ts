import { Injectable } from '@angular/core';
import { Subject, Observable, filter } from 'rxjs';

export interface MFEEvent {
  type: string;
  payload?: any;
  timestamp?: number;
}

@Injectable({
  providedIn: 'root',
})
export class EventBusService {
  private eventBus$ = new Subject<MFEEvent>();

  /**
   * Emit an event to all subscribers
   * @param event The event to emit
   */
  emit(event: MFEEvent): void {
    this.eventBus$.next({
      ...event,
      timestamp: Date.now(),
    });
  }

  /**
   * Subscribe to events of a specific type
   * @param eventType The type of event to listen for
   * @returns Observable of events matching the type
   */
  on(eventType: string): Observable<MFEEvent> {
    return this.eventBus$.pipe(
      filter((event) => event.type === eventType),
    );
  }

  /**
   * Subscribe to all events (for debugging/logging)
   * @returns Observable of all events
   */
  onAll(): Observable<MFEEvent> {
    return this.eventBus$.asObservable();
  }

  /**
   * Subscribe to multiple event types
   * @param eventTypes Array of event types to listen for
   * @returns Observable of events matching any of the types
   */
  onMultiple(eventTypes: string[]): Observable<MFEEvent> {
    return this.eventBus$.pipe(
      filter((event) => eventTypes.includes(event.type)),
    );
  }
}

/**
 * Common Event Types Emitted Across MFEs
 */
export const MFE_EVENTS = {
  // Transaction Events
  TRANSACTION_CREATED: 'transaction.created',
  TRANSACTION_DELETED: 'transaction.deleted',
  TRANSACTION_UPDATED: 'transaction.updated',

  // Account Events
  ACCOUNT_CREATED: 'account.created',
  ACCOUNT_UPDATED: 'account.updated',
  ACCOUNT_DELETED: 'account.deleted',
  BALANCE_CHANGED: 'balance.changed',

  // Transfer Events
  TRANSFER_INITIATED: 'transfer.initiated',
  TRANSFER_COMPLETED: 'transfer.completed',
  TRANSFER_FAILED: 'transfer.failed',

  // Notification Events
  NOTIFICATION_RECEIVED: 'notification.received',
  NOTIFICATION_READ: 'notification.read',

  // Auth Events
  USER_LOGGED_IN: 'user.logged_in',
  USER_LOGGED_OUT: 'user.logged_out',
  SESSION_EXPIRED: 'session.expired',

  // Global UI Events
  THEME_CHANGED: 'theme.changed',
  LOADING_STARTED: 'loading.started',
  LOADING_FINISHED: 'loading.finished',
  ERROR_OCCURRED: 'error.occurred',
};
