import os
import google.generativeai as genai
from dotenv import load_dotenv
from typing import Dict, Any
import json
import re

load_dotenv()

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY must be set in environment variables")

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')


def classify_intent(question: str) -> str:
    """
    Use Gemini to classify user question into one of the predefined intents.
    Returns: intent category as string
    """
    prompt = f"""Classify the following user question into EXACTLY ONE category.
Return ONLY the category name, nothing else.

Categories:
- crop_recommendation: Questions about which crops to grow, farming suggestions
- nutrition_recommendation: Questions about diet, food for health conditions, nutrition plans
- explanation: Questions asking "why", "how", or details about a specific crop or food
- general: General greetings, unclear questions, or off-topic queries

Question: "{question}"

Category:"""

    try:
        response = model.generate_content(prompt)
        intent = response.text.strip().lower()
        
        # Validate intent
        valid_intents = ['crop_recommendation', 'nutrition_recommendation', 'explanation', 'general']
        if intent not in valid_intents:
            # Default to general if invalid
            return 'general'
        
        return intent
    except Exception as e:
        print(f"Intent classification error: {e}")
        return 'general'


def extract_parameters(question: str, context: Dict[str, Any], intent: str) -> Dict[str, Any]:
    """
    Extract relevant parameters from question and context based on intent.
    Uses defaults where necessary.
    """
    params = {}
    
    if intent == 'crop_recommendation':
        # Extract from context with fallbacks
        climate = context.get('climate', {})
        params = {
            'temperature': climate.get('temperature', 25.0),
            'humidity': climate.get('humidity', 60.0),
            'moisture': context.get('moisture', 45.0),
            'soil_type': context.get('soil_type', 'loamy'),
            'nitrogen': context.get('nitrogen', 50.0),
            'phosphorous': context.get('phosphorous', 40.0),
            'potassium': context.get('potassium', 45.0),
            'limit': 3
        }
        
    elif intent == 'nutrition_recommendation':
        # Extract user profile
        params = {
            'age': context.get('age', 30),
            'bmi': context.get('bmi', 21.5),
            'condition': context.get('condition', 'general'),
            'diet': context.get('diet', 'vegetarian'),
            'limit': 4
        }
        
        # Try to extract condition from question using Gemini
        if 'condition' not in context:
            condition = extract_health_condition(question)
            if condition:
                params['condition'] = condition
                
    elif intent == 'explanation':
        # Try to extract crop or food name from question
        params = {
            'subject': extract_subject(question),
            'context': context
        }
    
    return params


def extract_health_condition(question: str) -> str:
    """Use Gemini to extract health condition from question."""
    prompt = f"""Extract the health condition or deficiency mentioned in this question.
Return ONLY the condition name (like "anemia", "diabetes", "iron deficiency", etc.).
If no specific condition is mentioned, return "general".

Question: "{question}"

Condition:"""
    
    try:
        response = model.generate_content(prompt)
        condition = response.text.strip().lower()
        return condition if condition else "general"
    except:
        return "general"


def extract_subject(question: str) -> str:
    """Extract the main subject (crop or food name) from question."""
    prompt = f"""Extract the main crop or food item being asked about.
Return ONLY the name, nothing else.
If no specific item is mentioned, return "none".

Question: "{question}"

Item:"""
    
    try:
        response = model.generate_content(prompt)
        subject = response.text.strip()
        return subject if subject.lower() != "none" else None
    except:
        return None


def format_response(structured_data: Dict[str, Any], intent: str, question: str) -> str:
    """
    Use Gemini to convert structured backend output into friendly, conversational language.
    """
    prompt = f"""Convert the following recommendation data into a friendly, conversational response.

Original Question: "{question}"
Intent: {intent}

Data:
{json.dumps(structured_data, indent=2)}

Instructions:
- Be concise and friendly
- Address the user's question directly
- Use simple language
- Do not add facts not in the data
- Keep response under 150 words
- For crop recommendations, mention 2-3 top crops
- For nutrition plans, mention 2-3 key foods
- Sound helpful and supportive

Response:"""
    
    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print(f"Response formatting error: {e}")
        # Fallback to simple formatting
        return format_fallback_response(structured_data, intent)


def format_fallback_response(data: Dict[str, Any], intent: str) -> str:
    """Simple fallback formatting if Gemini fails."""
    if intent == 'crop_recommendation' and 'recommendations' in data:
        crops = [r['crop'] for r in data['recommendations'][:3]]
        return f"Based on your conditions, I recommend growing: {', '.join(crops)}. These crops are well-suited to your region."
    
    elif intent == 'nutrition_recommendation' and 'recommendations' in data:
        foods = [r['food'] for r in data['recommendations'][:3]]
        return f"For your health needs, I suggest including: {', '.join(foods)} in your diet."
    
    elif intent == 'explanation' and 'details' in data:
        return str(data.get('details', 'No details available.'))
    
    return "I've processed your request. Please check the detailed data for more information."


def handle_ai_question(question: str, context: Dict[str, Any]) -> Dict[str, Any]:
    """
    Main handler for AI questions.
    
    Flow:
    1. Classify intent using Gemini
    2. Route to existing backend logic
    3. Format response using Gemini
    4. Return friendly answer
    """
    
    # Step 1: Classify intent
    intent = classify_intent(question)
    
    # Step 2: Extract parameters
    params = extract_parameters(question, context, intent)
    
    # Step 3: Route to existing logic (imported from other modules)
    structured_output = {}
    
    if intent == 'crop_recommendation':
        from logic.crop_logic import recommend_crop
        structured_output = recommend_crop(params)
        
    elif intent == 'nutrition_recommendation':
        from logic.nutrition_logic import nutrition_plan
        structured_output = nutrition_plan(params)
        
    elif intent == 'explanation':
        subject = params.get('subject')
        if subject:
            # Try crop details first
            try:
                from logic.crop_logic import get_crop_details
                crop_params = {
                    'crop_name': subject,
                    'temperature': context.get('climate', {}).get('temperature', 25),
                    'humidity': context.get('climate', {}).get('humidity', 60),
                    'moisture': 45,
                    'soil_type': 'loamy',
                    'nitrogen': 50,
                    'phosphorous': 40,
                    'potassium': 45
                }
                structured_output = get_crop_details(crop_params)
            except:
                # Try food details
                try:
                    from logic.nutrition_logic import get_food_details
                    food_params = {
                        'food_name': subject,
                        'age': context.get('age', 30),
                        'bmi': context.get('bmi', 21.5),
                        'condition': context.get('condition', 'general'),
                        'diet': context.get('diet', 'vegetarian')
                    }
                    structured_output = get_food_details(food_params)
                except:
                    structured_output = {'details': f'No detailed information available for {subject}'}
        else:
            structured_output = {'details': 'Please specify what you would like to know more about.'}
    
    elif intent == 'general':
        structured_output = {
            'message': 'Hello! I can help you with crop recommendations, nutrition advice, or explain details about crops and foods. What would you like to know?'
        }
    
    # Step 4: Format response using Gemini
    friendly_answer = format_response(structured_output, intent, question)
    
    # Step 5: Return final response
    return {
        'answer': friendly_answer,
        'source': 'nutrigrow-ai',
        'intent': intent,
        'raw_data': structured_output  # Optional: include for debugging
    }