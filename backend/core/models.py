from django.db import models
from datetime import date
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


# ---------------- USER ---------------- #

class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_verified = models.BooleanField(default=False)

    USERNAME_FIELD = 'username'


UserModel = get_user_model()


# ---------------- CUSTOMER ---------------- #

class Customer(models.Model):
    user = models.OneToOneField(
        UserModel,
        on_delete=models.CASCADE,
        related_name='customer_profile'
    )

    customer_id = models.CharField(max_length=20, unique=True, editable=False)

    gender = models.CharField(max_length=10, null=True, blank=True)
    date_of_birth = models.DateField(null=True, blank=True)

    age = models.IntegerField(null=True, blank=True)
    height = models.FloatField(null=True, blank=True)  
    weight = models.FloatField(null=True, blank=True) 

    calorie_goal = models.IntegerField(null=True, blank=True)

    joined_at = models.DateTimeField(auto_now_add=True)

    @property
    def age_from_dob(self):
        if self.date_of_birth:
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day)
                < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None

    def calculate_calorie_goal(self):
        if not all([self.height, self.weight, self.age, self.gender]):
            return None

        if self.gender == 'male':
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age + 5
        else:
            bmr = 10 * self.weight + 6.25 * self.height - 5 * self.age - 161

        return round(bmr)

    def save(self, *args, **kwargs):
        if not self.customer_id:
            last = Customer.objects.order_by('-id').first()
            next_id = 1 if not last else last.id + 1
            self.customer_id = f"CALCUST{next_id:04d}"

        if self.date_of_birth:
            self.age = self.age_from_dob

        if self.height and self.weight and not self.calorie_goal:
            self.calorie_goal = self.calculate_calorie_goal()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} ({self.customer_id})"


# ---------------- DAILY ENTRY ---------------- #

class DailyEntry(models.Model):
    customer = models.ForeignKey(
        Customer,
        on_delete=models.CASCADE,
        related_name="daily_entries"
    )

    date = models.DateField()

    calories_consumed = models.IntegerField(default=0)
    calories_burned = models.IntegerField(default=0)

    calorie_goal = models.IntegerField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('customer', 'date')
        ordering = ['-date']

    def save(self, *args, **kwargs):
        if not self.calorie_goal:
            self.calorie_goal = self.customer.calorie_goal or 100
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.customer.user.username} - {self.date}"


        


# ---------------- FOOD ITEM ---------------- #

class FoodItem(models.Model):
    daily_entry = models.ForeignKey(
        DailyEntry, on_delete=models.CASCADE, related_name="foods"
    )
    name = models.CharField(max_length=255)
    calories = models.IntegerField()
    protein = models.FloatField(default=0)
    carbs = models.FloatField(default=0)
    fat = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Auto-update the daily entry calories when a food is saved
        total_cals = sum(item.calories for item in self.daily_entry.foods.all())
        self.daily_entry.calories_consumed = total_cals
        self.daily_entry.save()

    def delete(self, *args, **kwargs):
        entry = self.daily_entry
        super().delete(*args, **kwargs)
        # Auto-update the daily entry calories when a food is deleted
        total_cals = sum(item.calories for item in entry.foods.all())
        entry.calories_consumed = total_cals
        entry.save()

    def __str__(self):
        return self.name


class ExerciseItem(models.Model):
    daily_entry = models.ForeignKey(DailyEntry, related_name='exercises', on_delete=models.CASCADE)
    name = models.CharField(max_length=255) # e.g., "Ran 3 miles"
    calories_burned = models.IntegerField()