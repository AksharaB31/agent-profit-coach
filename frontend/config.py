import os
from dotenv import load_dotenv

# Load from the root directory where .env is stored
root_dir = os.path.dirname(os.path.dirname(__file__))
load_dotenv(os.path.join(root_dir, ".env"))

class Config:
    API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
    API_ENDPOINT = f"{API_BASE_URL}/api/v1/agent-profit-coach"
    API_TIMEOUT_SECONDS = 30
    API_KEY = os.getenv("API_KEY", "change-me-to-a-secure-api-key")
    
    # UI Configuration
    PAGE_TITLE = "Afinetrip | B2B Airline Engine"
    PAGE_ICON = "🌐"
    LAYOUT = "wide"
    
config = Config()
