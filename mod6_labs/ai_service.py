# ai_service.py
"""Service for generating AI-based lifestyle content."""

import google.generativeai as genai
from config import Config
import json

class AIService:
    """Service to interact with Google Gemini API."""
    
    def __init__(self):
        self.api_key = Config.GEMINI_API_KEY
        self.model = None
        
        if self.api_key:
            genai.configure(api_key=self.api_key)
            # Updated model to match your curl command which is working
            self.model = genai.GenerativeModel('gemini-2.0-flash')

    async def generate_lifestyle_content(self, weather_desc, temp, city, time_of_day="day"):
        """
        Generate trivia and music based on weather and time using AI.
        Returns a dict with 'fact', 'music', and 'music_explanation'.
        """
        # Fallback content in case AI fails or key is missing
        fallback = {
            "fact": f"Did you know? Weather in {city} is quite unique today.",
            "music": "Here Comes The Sun - The Beatles",
            "music_explanation": "A classic for any day."
        }

        if not self.model:
            print("DEBUG: AI Model not initialized. Check API Key.")
            return fallback

        try:
            # UPDATED PROMPT AS REQUESTED
            prompt = (
                f"It is currently {time_of_day} in {city}. The weather is {weather_desc} and {temp} degrees Celsius. "
                "Give me a JSON response with three fields: "
                f"'fact' (a short and specific, scientific or historical trivia related to a {weather_desc} weather or to {city}), "
                "'music' (a song title and artist that strictly matches the vibe of this weather and time of day), "
                "and 'music_explanation' (a very short, 1-sentence explanation of why this song fits the current weather and time). "
                "Do not use markdown formatting."
            )
            print(f"DEBUG: AI Prompt: {time_of_day} | {city} | {weather_desc} | {temp}")
            
            # Generate content
            response = self.model.generate_content(prompt)
            text = response.text.strip()
            
            # Clean up potential markdown code blocks from response
            if text.startswith("```json"):
                text = text[7:-3]
            elif text.startswith("```"):
                text = text[3:-3]
            
            # Parse JSON
            data = json.loads(text)
            return data
            
        except Exception as e:
            print(f"DEBUG: AI Generation Error: {str(e)}")
            return fallback