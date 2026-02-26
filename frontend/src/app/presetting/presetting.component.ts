import { CommonModule, isPlatformBrowser } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClient } from '@angular/common/http';
import { Router } from '@angular/router';
import { AuthService } from '../services/auth.service';
import {  
  Component,
  OnInit,
  Inject,
  PLATFORM_ID
} from '@angular/core';

interface PresetResponse {
  daily_calorie_goal: number;
  message?: string;
}

@Component({
  selector: 'app-presetting',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './presetting.component.html',
})
export class PresettingComponent implements OnInit {

  gender: string = '';
  age: number | null = null;
  height: number | null = null;
  weight: number | null = null;
  goal: string = '';

  calorie_goal: number | null = null;
  loading = false;
  error: string | null = null;
  
  isMenuOpen: boolean = false;


  constructor(
    private http: HttpClient,
    private authService: AuthService,
    @Inject(PLATFORM_ID) private platformId: Object,private router: Router
  ) {}

  ngOnInit() {
    if (!isPlatformBrowser(this.platformId)) return;

    const token = localStorage.getItem('token');

    if (!token) {
      this.error = 'Not logged in';
      return;
    }

    this.http.get<any>('http://127.0.0.1:8000/api/preset/', {
      headers: {
        Authorization: `Token ${token}`
      }
    }).subscribe({
      next: (res) => {
        this.calorie_goal = res.daily_calorie_goal;
      },
      error: () => {
        this.calorie_goal = null;
      }
  });
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
  this.router.navigate(['/login']);
}


savePreset() {
  if (!isPlatformBrowser(this.platformId)) return;

  this.error = null;

  if (!this.gender || !this.age || !this.height || !this.weight || !this.goal) {
    this.error = 'Please fill all fields';
    return;
  }

  const token = localStorage.getItem('token');
  if (!token) {
    this.error = 'Not logged in';
    this.router.navigate(['/login']); 
    return;
  }

  this.loading = true;

  const payload = {
    gender: this.gender,
    age: this.age,
    height: this.height,
    weight: this.weight,
    goal: this.goal
  };
  

  this.http.post<PresetResponse>('http://127.0.0.1:8000/api/preset/', payload, {
    headers: { Authorization: `Token ${token}` }
  }).subscribe({
    next: (res) => {
      this.calorie_goal = res.daily_calorie_goal;
      this.loading = false;
      
      this.router.navigate(['/home']).then(() => {
         alert(`Goal set to ${this.calorie_goal} kcal!`); 
      });
    },
    error: (err) => {
      console.error(err); 
      this.error = err.error?.detail || 'An error occurred while saving.';
      this.loading = false;
    }
  });

}}