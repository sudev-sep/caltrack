# import requests
# import re
# from django.conf import settings
# from requests.auth import HTTPBasicAuth # <-- NEW IMPORT REQUIRED

# def get_fatsecret_token():
#     """
#     Exchanges your Consumer Key and Secret for a fresh OAuth 2.0 token.
#     This ensures your app never breaks due to an expired token!
#     """
#     url = "https://oauth.fatsecret.com/connect/token"
#     data = {
#         "grant_type": "client_credentials",
#         "scope": "basic"
#     }
    
#     # We grab the KEY and SECRET from your settings.py
#     auth = HTTPBasicAuth(
#         settings.FATSECRET_CONSUMER_KEY, 
#         settings.FATSECRET_CONSUMER_SECRET
#     )
    
#     response = requests.post(url, data=data, auth=auth)
    
#     if response.status_code == 200:
#         return response.json().get("access_token")
#     else:
#         print("Error fetching FatSecret token:", response.text)
#         return None

# def parse_fatsecret_description(description):
#     """Extracts macros from a FatSecret description string."""
#     macros = {'calories': 0, 'fat': 0.0, 'carbs': 0.0, 'protein': 0.0}
    
#     # Extract Calories
#     cal_match = re.search(r'Calories:\s*(\d+)kcal', description)
#     if cal_match:
#         macros['calories'] = int(cal_match.group(1))
        
#     # Extract Fat
#     fat_match = re.search(r'Fat:\s*([\d.]+)g', description)
#     if fat_match:
#         macros['fat'] = float(fat_match.group(1))
        
#     # Extract Carbs
#     carb_match = re.search(r'Carbs:\s*([\d.]+)g', description)
#     if carb_match:
#         macros['carbs'] = float(carb_match.group(1))
        
#     # Extract Protein
#     prot_match = re.search(r'Protein:\s*([\d.]+)g', description)
#     if prot_match:
#         macros['protein'] = float(prot_match.group(1))
        
#     return macros



# def search_food_fatsecret(query):
#     token = get_fatsecret_token()
#     if not token:
#         return None

#     search_url = 'https://platform.fatsecret.com/rest/server.api'
#     headers = {'Authorization': f'Bearer {token}'}
#     params = {
#         'method': 'foods.search',
#         'search_expression': query,
#         'format': 'json',
#         'max_results': 5  # <-- Changed from 1 to 5
#     }
    
#     response = requests.get(search_url, headers=headers, params=params)
#     data = response.json()

#     print("FATSECRET RAW DATA:", data)
    
#     try:
#         if not data.get('foods') or not data['foods'].get('food'):
#             return None

#         food_data = data['foods']['food']
        
#         # Ensure it's a list
#         if not isinstance(food_data, list):
#             food_list = [food_data]
#         else:
#             food_list = food_data
            
#         # 1. Default to the first result
#         best_match = food_list[0] 
        
#         # 2. Look for an EXACT name match to override the default
#         for food in food_list:
#             if food.get('food_name', '').strip().lower() == query.strip().lower():
#                 best_match = food
#                 break # Found exact match, stop looking
                
#         name = best_match.get('food_name')
#         description = best_match.get('food_description', '')
#         macros = parse_fatsecret_description(description)
        
#         return {
#             'name': name,
#             'calories': macros['calories'],
#             'protein': macros['protein'],
#             'carbs': macros['carbs'],
#             'fat': macros['fat']
#         }
#     except Exception as e:
#         print(f"Error parsing FatSecret data: {e}")
#         return None




import google.generativeai as genai
from django.conf import settings
import json

def analyze_entry_with_gemini(query):
    """
    Sends the user's natural language input to Gemini.
    Gemini figures out if it's food or exercise and calculates the macros/calories.
    Returns a clean Python dictionary.
    """
    try:
        # 1. Authenticate with your free API key from settings.py
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # 2. Use the fast flash model
        model = genai.GenerativeModel('gemini-2.5-flash')
        
        # 3. Give Gemini very strict instructions to only return JSON
        prompt = f"""
        Analyze this user input: "{query}"
        Is it a food they ate, or an exercise they did?
        Calculate the estimated nutritional macros or calories burned for an average adult.
        Respond strictly with ONLY a valid JSON object. Do not include formatting like ```json.
        
        If it's food, use exactly this format:
        {{"type": "food", "name": "Name of food", "calories": 200, "protein": 10.5, "carbs": 20.0, "fat": 5.0}}
        
        If it's exercise, use exactly this format:
        {{"type": "exercise", "name": "Name of exercise", "calories_burned": 300}}
        """
        
        print(f"Asking Gemini to analyze: '{query}'...")
        
        # 4. Send the prompt and get the response
        response = model.generate_content(prompt)
        reply = response.text.strip()
        
        # 5. Clean up in case Gemini accidentally adds markdown code blocks
        reply = reply.replace('```json', '').replace('```', '').strip()
        
        # 6. Convert the text string into a Python dictionary
        data = json.loads(reply)
        print("GEMINI RESULT:", data)
        
        return data
        
    except Exception as e:
        print(f"Gemini API Calculation failed: {e}")
        return None