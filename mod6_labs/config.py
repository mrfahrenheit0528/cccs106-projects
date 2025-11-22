# config.py
"""Configuration management for the Weather App."""

import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """Application configuration."""
    
    # API Configuration
    API_KEY = os.getenv("OPENWEATHER_API_KEY")
    # --- NEW: AI API KEY ---
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    
    BASE_URL = os.getenv(
        "OPENWEATHER_BASE_URL", 
        "https://api.openweathermap.org/data/2.5/weather"
    )
    
    # App Configuration
    APP_TITLE = "Weather App"
    APP_WIDTH = 400
    APP_HEIGHT = 600
    
    # API Settings
    UNITS = "metric"  # metric, imperial, or standard
    TIMEOUT = 10  # seconds
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present."""
        if not cls.API_KEY:
            raise ValueError(
                "OPENWEATHER_API_KEY not found. "
                "Please create a .env file with your API key."
            )
        # We won't raise an error for Gemini key to allow fallback to hardcoded mode
        if not cls.GEMINI_API_KEY:
            print("WARNING: GEMINI_API_KEY not found. AI features will be disabled.")
        return True

# Validate configuration on import
Config.validate()