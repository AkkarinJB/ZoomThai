import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    API_KEY = os.getenv("API_KEY")
    CONFIDENCE_THRESHOLD = 0.80

settings = Settings()