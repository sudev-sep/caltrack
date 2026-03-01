import { Component, OnInit, ChangeDetectorRef } from '@angular/core';
import { CommonModule, formatDate } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { FormsModule } from '@angular/forms';
import { AuthService } from '../services/auth.service';
import { Router } from '@angular/router';

@Component({
  selector: 'app-home',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './home.component.html', 
  styleUrls: ['./home.component.css']
})
export class HomeComponent implements OnInit {
  
  private baseUrl = 'http://localhost:8000/api';

  selectedDate: Date = new Date();
  dates: Date[] = [];

  dailyEntry: any = null;
  totalProtein: number = 0;
  totalCarbs: number = 0;
  totalFat: number = 0;

  isLoading: boolean = false;
  isAdding: boolean = false;
  isSaving: boolean = false;

  smartQuery: string = '';

  showEditModal: boolean = false;
  editingType: 'food' | 'exercise' | null = null;
  editingItem: any = null;

  toastMessage:string='';
  toastType:'success' | 'error' | 'info' = 'info';
  showToast: boolean = false;
  toastTimeout:any;


  isMenuOpen: boolean = false;

  constructor(
    private http: HttpClient,
    private cd: ChangeDetectorRef,
    private authService: AuthService,
    private router: Router
  ) {}

  ngOnInit(): void {
    this.generateDateCarousel();
    this.fetchData();
  }

  
  displayToast(message: string, type: 'success' | 'error' | 'info' = 'info'): void {
    this.toastMessage = message;
    this.toastType = type;
    this.showToast = true;

    if (this.toastTimeout) {
      clearTimeout(this.toastTimeout);
    }

    this.toastTimeout = setTimeout(() => {
      this.showToast = false;
      this.cd.detectChanges();
    }, 3500);
    
    this.cd.detectChanges();
  }


  generateDateCarousel(): void {
    const today = new Date();
    this.dates = [];
    for (let i = -6; i <= 0; i++) {
      const d = new Date(today);
      d.setDate(today.getDate() + i);
      this.dates.push(d);
    }
  }


  selectDate(d: Date): void {
    this.selectedDate = d;
    this.fetchData();
  }

  
  fetchData(): void {
    const dateStr = formatDate(this.selectedDate, 'yyyy-MM-dd', 'en-US');

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
    this.totalProtein = 0;
    this.totalCarbs = 0;
    this.totalFat = 0;

    if (this.dailyEntry && this.dailyEntry.foods) {
      this.dailyEntry.foods.forEach((food: any) => {
        this.totalProtein += (food.protein || 0);
        this.totalCarbs += (food.carbs || 0);
        this.totalFat += (food.fat || 0);
      });
    }
  }

  // --- AI Add Logic ---

  addSmartEntry(): void {
    if (!this.smartQuery || this.smartQuery.trim() === '') return;

    this.isAdding = true;
    const dateStr = formatDate(this.selectedDate, 'yyyy-MM-dd', 'en-US');

    this.http.post(`${this.baseUrl}/daily/${dateStr}/add-smart-entry/`, {
      query: this.smartQuery
    }).subscribe({
      next: () => {
        this.smartQuery = ''; 
        this.isAdding = false;
        this.fetchData(); 
        this.displayToast('Entry added successfully!', 'success');
      },
      error: (err) => {
        this.isAdding = false;
        
        if (err.status === 429) {
            this.displayToast(err.error?.error || "The AI is cooling down. Please wait 40 seconds.", "error");
        } else {
            console.error('Smart Add Error:', err);
            this.displayToast('Failed to add entry. Try again.', 'error');
        }
        
        this.cd.detectChanges();
      }
    });
  }


  openEditModal(item: any, type: 'food' | 'exercise'): void {
    this.editingType = type;
    this.editingItem = { ...item }; 
    this.showEditModal = true;
  }

  closeEditModal(): void {
    this.showEditModal = false;
    this.editingItem = null;
    this.editingType = null;
  }


  deleteEditModal(): void {
    if (!this.editingItem || !this.editingType) return;
    this.isSaving = true;

    const endpoint = this.editingType === 'food' 
      ? `${this.baseUrl}/delete/foods/${this.editingItem.id}/` 
      : `${this.baseUrl}/delete/exercises/${this.editingItem.id}/`;
    this.http.delete(endpoint).subscribe({
      next: () => {
        this.isSaving = false;
        this.closeEditModal();
        this.fetchData();
      },
      error: (err) => {
        console.error('Delete Error:', err);  
        this.isSaving = false;
        this.cd.detectChanges();
      } 
    });
  }

 saveEdit(): void {
    if (!this.editingItem || !this.editingItem.name || !this.editingType) return;
    this.isSaving = true; 
    
    this.http.post(`${this.baseUrl}/ai-calculate/`, {
      query: this.editingItem.name,
      type: this.editingType 
    }).subscribe({
      next: (aiResult: any) => {
        
        if (this.editingType === 'food') {
            this.editingItem.calories = aiResult.calories || 0;
            this.editingItem.protein = aiResult.protein || 0;
            this.editingItem.carbs = aiResult.carbs || 0;
            this.editingItem.fat = aiResult.fat || 0;
        } else if (this.editingType === 'exercise') {
            this.editingItem.calories_burned = aiResult.calories_burned || 0;
        }

        const endpoint = this.editingType === 'food'
          ? `${this.baseUrl}/update/foods/${this.editingItem.id}/`
          : `${this.baseUrl}/update/exercises/${this.editingItem.id}/`;

        this.http.put(endpoint, this.editingItem).subscribe({
          next: () => {
            this.isSaving = false;      
            this.closeEditModal();
            this.fetchData();
            this.displayToast('Changes saved successfully!', 'success');
          },
          error: (err) => {
            console.error('Database Save Error:', err);   
            this.isSaving = false;
            this.displayToast("Failed to save to database. Check connection.", "error");
            this.cd.detectChanges(); 
          }
        });

      },
      error: (err) => {
        console.error('AI Calculation Error:', err);   
        this.isSaving = false;
        
        if (err.status === 429) {
            this.displayToast(err.error?.error || "The AI is cooling down. Please wait 40 seconds.", "error");
        } else {
            this.displayToast("Failed to calculate macros. Try again.", "error");
        }
        
        this.cd.detectChanges();
      }
    });
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


}