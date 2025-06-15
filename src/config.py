import os
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API Configuration
WEATHER_API_KEY = os.getenv('WEATHER_API_KEY')
WEATHER_API_BASE_URL = os.getenv('WEATHER_API_BASE_URL', 'http://api.weatherapi.com/v1')

def validate_config():
    """Validate that all required configuration is present"""
    if not WEATHER_API_KEY:
        raise ValueError(
            "WEATHER_API_KEY environment variable is not set. "
            "Please create a .env file with your API key or set it in your environment."
        )
    logging.info("✅ Configuration validated successfully")