import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { FormsModule, NgForm } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-register',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './register.component.html',
  styleUrls: ['./register.component.css']
})
export class RegisterComponent {

  formData = {
    name: '',
    last_name: '',
    username: '',
    email: '',
    password: '',
    confirm_password: ''
  };

  errorMessage = '';
  successMessage = '';
  isMenuOpen: boolean = false;

  constructor(
    private authService: AuthService,
    private router: Router
  ) {}

  register(form: NgForm) {
    // 1. FRONTEND CHECK: Did they miss fields or format things wrong in the HTML?
    if (form.invalid) {
      this.errorMessage = 'Please fill out all required fields correctly.';
      return;
    }

    // 2. FRONTEND CHECK: Do the passwords match?
    if (this.formData.password !== this.formData.confirm_password) {
      this.errorMessage = 'Passwords do not match';
      return;
    }

    // 3. SEND TO BACKEND
    this.authService.register(this.formData).subscribe({
      next: () => {
        this.successMessage = 'Registration successful';
        this.errorMessage = '';

        form.resetForm();

        this.router.navigate(['/login']);
      },
      error: (err) => {
        if (err.error && typeof err.error === 'object' && !err.error.message) {
           
           const errorData = err.error as Record<string, string[]>;
           const keys = Object.keys(errorData);
           
           if (keys.length > 0) {
              const firstErrorKey = keys; 
              const firstErrorMsg = errorData[firstErrorKey]; 
              
              this.errorMessage = `${firstErrorKey}: ${firstErrorMsg}`; 
           } else {
              this.errorMessage = 'Registration failed. Please check your details.';
           }

        } else {
           this.errorMessage = err.error?.message || 'Registration failed.';
        }
      }
    });
  }

  navigateAndClose(path: string): void {
    this.isMenuOpen = false; 
    this.router.navigate([path]); 
  }
}
