"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from core import views


urlpatterns = [
    path('admin/', admin.site.urls),
    path('register/customer/',views.RegisterView.as_view(), name='customer-register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('api/preset/', views.PresetView.as_view(), name='preset'),
    path('api/daily/<str:date>/',views.FetchDailyDataView.as_view(), name='daily-entry-detail'),
    path('api/daily/<str:date>/add-smart-entry/', views.AddSmartEntryView.as_view(), name='add-smart-entry'),
    path('api/delete/foods/<int:entry_id>/', views.DeleteFoodEntryView.as_view(), name='delete-food-entry'),
    path('api/delete/exercises/<int:entry_id>/', views.DeleteExerciseEntryView.as_view(), name='delete-exercise-entry'),
    path("api/ai-calculate/", views.AICalculationView.as_view(), name="ai-calculate"),
    path("api/update/foods/<int:entry_id>/", views.UPDATEFOODAI.as_view(), name="update-food-entry"),
    path("api/update/exercises/<int:entry_id>/", views.UPDATEEXERCISEAI.as_view(), name="update-exercise-entry"),
    path("api/profile/", views.ProfileView.as_view(), name="profile"),
    path("api/weekly-summary/", views.WeeklySummaryView.as_view(), name="weekly-summary"),
    
    
]