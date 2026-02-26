import json
import google.generativeai as genai
from django.conf import settings

def analyze_entry_with_gemini(query):
    """
    Sends the user's natural language input to Gemini.
    Gemini figures out if it's food or exercise and calculates the macros/calories.
    Returns a clean Python dictionary.
    """
    try:
        genai.configure(api_key=settings.GEMINI_API_KEY)
        
        # 1. Use the fast flash model
        model = genai.GenerativeModel('gemini-2.5-flash-lite')
        
        # 2. Give Gemini very strict instructions to only return JSON
        prompt = f"""
        You are a strict, highly accurate expert nutritionist and fitness database. 
        Analyze the user's input and calculate the exact calories and macros.
        
        STRICT GUIDELINES:
        - Use standard, realistic portion sizes.
        - For Indian cuisine, use standard NIN estimates (e.g., 1 cup cooked rice is ~130 kcal).
        - IF THE USER ENTERS MULTIPLE FOODS: You MUST combine them into a single meal. Sum up all the calories, protein, carbs, and fat into ONE total. 
        - Make the "name" a short summary (e.g., "Rice, Peas Curry & Thoran").
        - NEVER return a JSON array/list. ALWAYS return exactly ONE JSON object.
        
        User Input: "{query}"
        
        Respond ONLY with a valid JSON object. Do not include markdown formatting.
        Format for food: {{"type": "food", "name": "...", "calories": 0, "protein": 0, "carbs": 0, "fat": 0}}
        Format for exercise: {{"type": "exercise", "name": "...", "calories_burned": 0}}
        """
        
        print(f"Asking Gemini to analyze: '{query}'...")

        # 3. Apply the strict temperature setting
        generation_config = genai.types.GenerationConfig(
            temperature=0.1,
        )

        # 4. Generate the response
        response = model.generate_content(
            prompt,
            generation_config=generation_config
        )
        
        # 5. Clean up the text just in case the AI wraps it in markdown
        response_text = response.text.strip().replace('```json', '').replace('```', '')
        
        return json.loads(response_text)
        
    except Exception as e:
        print(f"Gemini API Error: {e}")
        raise e