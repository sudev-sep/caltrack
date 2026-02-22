from django.shortcuts import get_object_or_404
from django.utils.dateparse import parse_date
from django.utils import timezone
from django.contrib.auth import authenticate

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework import status
from rest_framework.authtoken.models import Token

from datetime import date, datetime
import logging
import re

from .models import Customer, DailyEntry, FoodItem, ExerciseItem
from .serializers import CustomerSerializer, DailyEntrySerializer



class RegisterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = CustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Registered"}, status=201)

        return Response(serializer.errors, status=400)



class LoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")

        user = authenticate(username=username, password=password)
        if not user:
            return Response(
                {"message": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        token, _ = Token.objects.get_or_create(user=user)

        return Response({
            "message": "Login successful",
            "token": token.key,
            "username": user.username
        })



class PresetView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user.customer_profile
        return Response({"daily_calorie_goal": customer.calorie_goal})

    def post(self, request):
        customer = request.user.customer_profile

        gender = request.data.get("gender")
        age = int(request.data.get("age"))
        height = float(request.data.get("height"))
        weight = float(request.data.get("weight"))
        goal = request.data.get("goal")

        if gender == "male":
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        elif gender == "female":
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        else:
            return Response({"error": "Invalid gender"}, status=400)

        if goal == "lose":
            calories = bmr - 500
        elif goal == "gain":
            calories = bmr + 500
        else:
            calories = bmr

        calories = max(int(calories), 1200)

        customer.gender = gender
        customer.age = age
        customer.height = height
        customer.weight = weight
        customer.calorie_goal = calories
        customer.save()

        return Response({
            "message": "Preset saved",
            "daily_calorie_goal": calories
        })


# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import DailyEntry, FoodItem
from .serializers import DailyEntrySerializer
# from .utils import search_food_fatsecret

class FetchDailyDataView(APIView):
    def get(self, request, date):
        # Format expected: YYYY-MM-DD
        customer = request.user.customer_profile
        entry, created = DailyEntry.objects.get_or_create(
            customer=customer, 
            date=date
        )
        serializer = DailyEntrySerializer(entry)
        print(f"Fetched data for {customer.user.username} on {date}: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)


# class AddFoodFromSearchView(APIView):
#     def post(self, request, date):
#         query = request.data.get('query')
#         customer = request.user.customer_profile
        
#         entry, _ = DailyEntry.objects.get_or_create(customer=customer, date=date)
        
#         # This now returns our clean, parsed dictionary
#         fs_data = search_food_fatsecret(query)
        
#         if not fs_data:
#             return Response({"error": "Food not found in database"}, status=status.HTTP_404_NOT_FOUND)
        
#         # Create the Food Item using the exact parsed numbers
#         FoodItem.objects.create(
#             daily_entry=entry,
#             name=fs_data['name'],
#             calories=fs_data['calories'],
#             protein=fs_data['protein'],
#             carbs=fs_data['carbs'],
#             fat=fs_data['fat']
#         )
        
#         serializer = DailyEntrySerializer(entry)
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


from .utils import analyze_entry_with_gemini
class AddSmartEntryView(APIView):
    def post(self, request, date):
        query = request.data.get('query')
        if not query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 1. Ask Gemini to analyze the text
        ai_result = analyze_entry_with_gemini(query)
        
        if not ai_result:
            return Response({"error": "AI could not understand the input"}, status=status.HTTP_400_BAD_REQUEST)
            
        # 2. Get the daily entry
        customer = request.user.customer_profile
        entry, _ = DailyEntry.objects.get_or_create(customer=customer, date=date)
        
        # 3. Handle Food
        if ai_result.get('type') == 'food':
            FoodItem.objects.create(
                daily_entry=entry,
                name=ai_result.get('name', 'Unknown Food'),
                calories=ai_result.get('calories', 0),
                protein=ai_result.get('protein', 0),
                carbs=ai_result.get('carbs', 0),
                fat=ai_result.get('fat', 0)
            )
            
        # 4. Handle Exercise
        elif ai_result.get('type') == 'exercise':
            burned = ai_result.get('calories_burned', 0)
            
            # Create the list item so we remember what they did
            ExerciseItem.objects.create(
                daily_entry=entry,
                name=ai_result.get('name', 'Workout'),
                calories_burned=burned
            )
            
            # Keep the daily total math working
            entry.calories_burned += burned
            entry.save()
            
        # 5. Return updated data to Angular (MUST be outside the if/elif blocks!)
        serializer = DailyEntrySerializer(entry)
        return Response(serializer.data, status=status.HTTP_200_OK)