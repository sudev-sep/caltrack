from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_date
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import Customer, DailyEntry, ExerciseItem, FoodItem
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



class FetchDailyDataView(APIView):
    def get(self, request, date):
        customer = request.user.customer_profile
        entry, created = DailyEntry.objects.get_or_create(
            customer=customer, 
            date=date
        )
        serializer = DailyEntrySerializer(entry)
        print(f"Fetched data for {customer.user.username} on {date}: {serializer.data}")
        return Response(serializer.data, status=status.HTTP_200_OK)





from .utils import analyze_entry_with_gemini
class AddSmartEntryView(APIView):
    def post(self, request, date):
        query = request.data.get('query')
        if not query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            ai_result = analyze_entry_with_gemini(query)
            print(f"--- AI RAW RESULT: {ai_result} ---")
        
            if not ai_result:
                return Response({"error": "AI could not understand the input"}, status=status.HTTP_400_BAD_REQUEST)
                
        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "Quota exceeded" in error_message:
                return Response({
                    "error": "The AI is cooling down. Please wait about 40 seconds and try again."
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            return Response({
                "error": "AI calculation failed due to an unexpected error."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        
        customer = request.user.customer_profile
        entry, _ = DailyEntry.objects.get_or_create(customer=customer, date=date)
        
        if ai_result.get('type') == 'food':
            FoodItem.objects.create(
                daily_entry=entry,
                name=ai_result.get('name', 'Unknown Food'),
                calories=ai_result.get('calories', 0),
                protein=ai_result.get('protein', 0),
                carbs=ai_result.get('carbs', 0),
                fat=ai_result.get('fat', 0)
            )
            
        elif ai_result.get('type') == 'exercise':
            burned = ai_result.get('calories_burned', 0)
            
            ExerciseItem.objects.create(
                daily_entry=entry,
                name=ai_result.get('name', 'Workout'),
                calories_burned=burned
            )
            entry.calories_burned = sum(e.calories_burned for e in entry.exercises.all())
            entry.save()

        else:
            return Response({"error": "AI returned an unrecognized type"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = DailyEntrySerializer(entry)
        return Response(serializer.data, status=status.HTTP_200_OK)



class UPDATEEXERCISEAI(APIView):
    def put(self, request, entry_id):
        exercise = get_object_or_404(ExerciseItem, id=entry_id)
        exercise.name = request.data.get('name', exercise.name)
        exercise.calories_burned = request.data.get('calories_burned', exercise.calories_burned)
        exercise.save()
        
        daily_entry = exercise.daily_entry
        daily_entry.calories_burned = sum(e.calories_burned for e in daily_entry.exercises.all())
        daily_entry.save()
        
        return Response({"message": "Exercise entry updated"}, status=status.HTTP_200_OK)
    

class UPDATEFOODAI(APIView):
    def put(self,request,entry_id):
        food=get_object_or_404(FoodItem, id=entry_id)
        food.name=request.data.get('name', food.name)
        food.calories=request.data.get('calories', food.calories)
        food.protein=request.data.get('protein', food.protein)
        food.carbs=request.data.get('carbs', food.carbs)
        food.fat=request.data.get('fat', food.fat)
        food.save()

        daily_entry = food.daily_entry
        daily_entry.calories_consumed = sum(f.calories for f in daily_entry.foods.all())
        daily_entry.save()

        return Response({"message": "Food entry updated"}, status=status.HTTP_200_OK)
    

class DeleteFoodEntryView(APIView):
    def delete(self, request, entry_id):
        food = get_object_or_404(FoodItem, id=entry_id)
        food.delete()

        daily_entry = food.daily_entry
        daily_entry.calories_consumed = sum(f.calories for f in daily_entry.foods.all())
        daily_entry.save()
        return Response({"message": "Food entry deleted"}, status=status.HTTP_200_OK)
    
class DeleteExerciseEntryView(APIView):
    def delete(self, request, entry_id):
        exercise = get_object_or_404(ExerciseItem, id=entry_id)
        daily_entry = exercise.daily_entry
        exercise.delete()
        
        daily_entry.calories_burned = sum(e.calories_burned for e in daily_entry.exercises.all())
        daily_entry.save()
        
        return Response({"message": "Exercise entry deleted"}, status=status.HTTP_200_OK)
    


class AICalculationView(APIView):
    def post(self, request):
        query = request.data.get('query')
        item_type = request.data.get('type') 
        
        if not query:
            return Response({"error": "No query provided"}, status=status.HTTP_400_BAD_REQUEST)
            
        try:
            ai_result = analyze_entry_with_gemini(query)
            
            if not ai_result:
                return Response({"error": "AI could not process the input"}, status=status.HTTP_400_BAD_REQUEST)
                
            return Response(ai_result, status=status.HTTP_200_OK)
            
        except Exception as e:
            error_message = str(e)
            if "429" in error_message or "Quota exceeded" in error_message:
                return Response({
                    "error": "The AI is cooling down. Please wait about 40 seconds and try again."
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            return Response({
                "error": "AI service is currently unavailable."
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user.customer_profile
        
        print(f"Fetching profile for {customer.user.username}...")
        print(f"Profile data: {customer.__dict__}")
        
        return Response({
            "username": request.user.username,
            "email": request.user.email,
            "customer_id": customer.customer_id,
            "gender": customer.gender,
            "age": customer.age,
            "height": customer.height,
            "weight": customer.weight,
            "calorie_goal": customer.calorie_goal,
            "joined_at": customer.joined_at.strftime('%B %Y') if customer.joined_at else "Recently"
        }, status=status.HTTP_200_OK)
    


class WeeklySummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        customer = request.user.customer_profile
        today = timezone.now().date()
        seven_days_ago = today - timezone.timedelta(days=6)

        entries = DailyEntry.objects.filter(
            customer=customer,
            date__range=[seven_days_ago, today]
        ).order_by('date')

        summary = []
        for entry in entries:
            summary.append({
                "date": entry.date.strftime('%Y-%m-%d'),
                "total_calories": entry.calories_consumed,
                "calorie_goal": customer.calorie_goal,
                "goal_met": entry.calories_consumed <= customer.calorie_goal
            })

        return Response(summary, status=status.HTTP_200_OK)