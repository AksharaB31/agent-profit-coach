import os

class Config:
    API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000")
    API_ENDPOINT = f"{API_BASE_URL}/api/v1/agent-profit-coach"
    API_TIMEOUT_SECONDS = 30
    
    # UI Configuration
    PAGE_TITLE = "Afinetrip | B2B Airline Engine"
    PAGE_ICON = "🌐"
    LAYOUT = "wide"
    
config = Config()
