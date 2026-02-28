import { Component, OnInit } from '@angular/core';
import { CommonModule, formatDate } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { ChangeDetectorRef } from '@angular/core';
import { Router } from '@angular/router';
import { HttpHeaders } from '@angular/common/http';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-goalset',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './goalset.component.html',
  styleUrls: ['./goalset.component.css']
})
export class GoalsetComponent implements OnInit {
  profileData: any = null;
  isLoading: boolean = true;
  isMenuOpen: boolean = false;



  constructor(private http: HttpClient, private router: Router,private authService: AuthService,private cdr: ChangeDetectorRef
) {}

  ngOnInit(): void {
    this.fetchProfile();
    this.isLoading = false;
  
  }

  fetchProfile(): void {
    const token = localStorage.getItem('token'); 
    const headers = new HttpHeaders().set('Authorization', `Token ${token}`);

    this.http.get('https://caltrack-backend.vercel.app/api/profile/', { headers }).subscribe({
      next: (data) => {
        this.profileData = data;
        this.isLoading = false;
        this.cdr.detectChanges();
      },
      error: (err) => {
        console.error('Failed to load profile', err);
        this.isLoading = false;
        this.cdr.detectChanges();
      }
    });
  }

  goBack(): void {
    this.router.navigate(['/home']);
  }

  navigateAndClose(path: string): void {
    this.isMenuOpen = false; 
    this.router.navigate([path]); 
  }

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;

  }

  logout(): void {
    this.authService.logout();
  }


}