# config.py
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Gemini API Key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Amadeus API Credentials
AMADEUS_API_KEY = os.getenv("AMADEUS_API_KEY")
AMADEUS_API_SECRET = os.getenv("AMADEUS_API_SECRET")

# Basic validation
if not all([GEMINI_API_KEY, AMADEUS_API_KEY, AMADEUS_API_SECRET]):
    raise ValueError("One or more required API keys are missing from your .env file.")