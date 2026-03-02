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

    if (this.formData.password !== this.formData.confirm_password) {
      this.errorMessage = 'Passwords do not match';
      return;
    }

    this.authService.register(this.formData).subscribe({
      next: () => {
        this.successMessage = 'Registration successful';
        this.errorMessage = '';

        form.resetForm();

        this.router.navigate(['/login']);
      },
      error: (err) => {
       if (err.error && typeof err.error === 'object' && !err.error.message) {
           const firstErrorKey = Object.keys(err.error); 
           const firstErrorMsg = err.error[firstErrorKey]; 
           this.errorMessage = `${firstErrorKey}: ${firstErrorMsg}`; 
        } else {
           this.errorMessage = err.error?.message || 'Registration failed. Please check your details.';
        }
      }
    });
      }
    });
  }



navigateAndClose(path: string): void {
    this.isMenuOpen = false; 
    this.router.navigate([path]); 
  }

}
