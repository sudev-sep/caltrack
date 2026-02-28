import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-weekreport',
  standalone: true, 
  imports: [CommonModule], 
  templateUrl: './weekreport.component.html',
  styleUrl: './weekreport.component.css',
})
export class WeekreportComponent implements OnInit {

  private baseUrl = 'https://caltrack-backend.vercel.app';

  dailyEntry: any = null;
  isLoading: boolean = false; 

  isMenuOpen: boolean = false;

  weeklyEntries: any[] = []; 
  goalsMetCount: number = 0;
  averageCalories: number = 0; 
  chartData: any[] = [];

  constructor(
    private http: HttpClient,
    private cd: ChangeDetectorRef,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.fetchData(); 
    this.fetchWeeklyData(); 
  }

  fetchData(): void {
    const dateStr = new Date().toISOString().split('T')[0];
    this.isLoading = true;
    this.dailyEntry = null; 
    
    this.http.get(`${this.baseUrl}/daily/${dateStr}/`).subscribe({
      next: (data) => {
        this.dailyEntry = data;
        this.calculateMacros();
        
        this.isLoading = false;
        this.cd.detectChanges(); 
      },
      error: (error) => {
        console.error('API Error:', error);
        this.dailyEntry = null;
        this.isLoading = false;
        this.cd.detectChanges(); 
      }
    });
  }

  calculateMacros(): void {
    if (this.dailyEntry) {
      console.log('Calculating macros for:', this.dailyEntry);
    }
  }

  logout(): void {
    this.authService.logout();
  } 

  toggleMenu(): void {
    this.isMenuOpen = !this.isMenuOpen;
  }

  navigateAndClose(path: string): void {
    this.isMenuOpen = false; 
    this.router.navigate([path]); 
  }

  // --- WEEKLY DATA LOGIC ---
  fetchWeeklyData(): void {
    this.isLoading = true;
    
    this.http.get<any[]>(`${this.baseUrl}/weekly-summary/`).subscribe({
      next: (data) => {
        this.weeklyEntries = data;
        
        // 1. Calculate Goals Met Count
        this.goalsMetCount = this.weeklyEntries.filter(
          day => day.total_calories <= day.calorie_goal
        ).length;

        // 2. Calculate Average Calories
        if (this.weeklyEntries.length > 0) {
          const total = this.weeklyEntries.reduce((sum, day) => sum + (day.total_calories || 0), 0);
          this.averageCalories = Math.round(total / this.weeklyEntries.length);
        }

        // 3. Process the data for the CSS chart
        this.processChartData();
        
        this.isLoading = false;
        this.cd.detectChanges(); 
      },
      error: (error) => {
        console.error('API Error:', error);
        this.isLoading = false;
        this.cd.detectChanges(); 
      }
    });
  } 
  processChartData(): void {
    const maxScale = Math.max(
      ...this.weeklyEntries.map(day => day.total_calories || 0), 
      2000 
    );

    this.chartData = this.weeklyEntries.map(day => {
      let height = ((day.total_calories || 0) / maxScale) * 100;
      
      if (height === 0 || !day.total_calories) height = 5; 

      return {
        ...day, 
        heightPercentage: height,
        isOverGoal: day.total_calories > day.calorie_goal
      };
    });
  }
}