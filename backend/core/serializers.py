from rest_framework import serializers
from .models import Customer, User,DailyEntry,FoodItem,ExerciseItem


class CustomerSerializer(serializers.ModelSerializer):
    name = serializers.CharField(write_only=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "last_name",
            "email",
            "password",
        ]

    def create(self, validated_data):
        name = validated_data.pop("name")
        password = validated_data.pop("password")

        user = User(**validated_data)
        user.first_name = name
        user.set_password(password)
        user.save()

        Customer.objects.create(
            user=user
           
        )

        return user


from rest_framework import serializers
from .models import DailyEntry, FoodItem

class FoodItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodItem
        fields = ['id', 'name', 'calories', 'protein', 'carbs', 'fat']


class ExerciseItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExerciseItem
        fields = ['id', 'name', 'calories_burned']

class DailyEntrySerializer(serializers.ModelSerializer):
    foods = FoodItemSerializer(many=True, read_only=True)
    exercises = ExerciseItemSerializer(many=True, read_only=True) 

    class Meta:
        model = DailyEntry
        fields = ['id', 'date', 'calorie_goal', 'calories_consumed', 'calories_burned', 'foods', 'exercises']