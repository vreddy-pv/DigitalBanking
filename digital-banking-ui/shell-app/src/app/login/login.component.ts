import { Component, OnInit } from '@angular/core';
import { FormBuilder, FormGroup, Validators } from '@angular/forms';
import { Router, ActivatedRoute } from '@angular/router';
import { AuthService } from '../shared/services/auth.service';
import { ThemeService } from '../shared/services/theme.service';
import { Observable } from 'rxjs';

@Component({
  selector: 'app-login',
  templateUrl: './login.component.html',
  styleUrls: ['./login.component.scss'],
})
export class LoginComponent implements OnInit {
  loginForm!: FormGroup;
  isLoading = false;
  errorMessage = '';
  showPassword = false;
  currentTheme$!: Observable<any>;

  constructor(
    private formBuilder: FormBuilder,
    private authService: AuthService,
    private themeService: ThemeService,
    private router: Router,
    private route: ActivatedRoute,
  ) {
    this.currentTheme$ = this.themeService.theme$;
  }

  ngOnInit(): void {
    this.initializeForm();
    this.themeService.applyVRGTTheme();
  }

  private initializeForm(): void {
    this.loginForm = this.formBuilder.group({
      email: ['', [Validators.required, Validators.email]],
      password: ['', [Validators.required, Validators.minLength(6)]],
      rememberMe: [false],
    });
  }

  onSubmit(): void {
    if (this.loginForm.invalid) {
      return;
    }

    this.isLoading = true;
    this.errorMessage = '';

    this.authService.login(this.loginForm.value).subscribe({
      next: () => {
        const returnUrl = this.route.snapshot.queryParams['returnUrl'] || '/app/dashboard';
        this.router.navigate([returnUrl]);
      },
      error: (error) => {
        this.isLoading = false;
        this.errorMessage = error.error?.message || 'Login failed. Please try again.';
      },
    });
  }

  togglePasswordVisibility(): void {
    this.showPassword = !this.showPassword;
  }

  get email() {
    return this.loginForm.get('email');
  }

  get password() {
    return this.loginForm.get('password');
  }
}
