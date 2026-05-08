import { Injectable } from '@angular/core';
import {
  HttpRequest,
  HttpHandler,
  HttpEvent,
  HttpInterceptor,
  HttpErrorResponse,
} from '@angular/common/http';
import { Observable, throwError } from 'rxjs';
import { catchError, switchMap } from 'rxjs/operators';
import { AuthService } from '../services/auth.service';

@Injectable()
export class AuthInterceptor implements HttpInterceptor {
  constructor(private authService: AuthService) {}

  intercept(
    request: HttpRequest<any>,
    next: HttpHandler,
  ): Observable<HttpEvent<any>> {
    // Skip adding token for auth endpoints
    if (request.url.includes('/api/auth/login') || request.url.includes('/api/auth/register')) {
      return next.handle(request);
    }

    // Get token and add to request
    const token = this.authService.getToken();
    if (token) {
      request = this.addTokenToRequest(request, token);
    }

    return next.handle(request).pipe(
      catchError((error: HttpErrorResponse) => {
        if (error.status === 401) {
          // Token expired, try to refresh
          return this.handle401Error(request, next);
        }
        return throwError(() => error);
      }),
    );
  }

  private addTokenToRequest(
    request: HttpRequest<any>,
    token: string,
  ): HttpRequest<any> {
    return request.clone({
      setHeaders: {
        Authorization: `Bearer ${token}`,
      },
    });
  }

  private handle401Error(
    request: HttpRequest<any>,
    next: HttpHandler,
  ): Observable<HttpEvent<any>> {
    return this.authService.refreshToken().pipe(
      switchMap((response) => {
        const newRequest = this.addTokenToRequest(request, response.token);
        return next.handle(newRequest);
      }),
      catchError((error) => {
        // Refresh failed, redirect to login
        this.authService.logout();
        return throwError(() => error);
      }),
    );
  }
}
