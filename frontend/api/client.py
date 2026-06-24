import requests
import streamlit as st
from config import config
from typing import Dict, Any

@st.cache_data(ttl=300)
def fetch_itinerary_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the Agent Profit Coach FastAPI endpoint safely with timeouts and caching.
    """
    try:
        response = requests.post(
            config.API_ENDPOINT,
            json=payload,
            timeout=config.API_TIMEOUT_SECONDS,
            headers={
                "Content-Type": "application/json",
                "X-API-Key": config.API_KEY
            }
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.Timeout:
        st.error("API Request timed out. The server took too long to respond.")
        return {}
    except requests.exceptions.HTTPError as e:
        error_msg = f"API Error: {e.response.status_code}"
        try:
            detail = e.response.json().get("detail", "")
            error_msg += f" - {detail}"
        except:
            pass
        st.error(error_msg)
        return {}
    except requests.exceptions.ConnectionError:
        st.error(f"Failed to connect to API at {config.API_ENDPOINT}. Is the backend running? (uvicorn app.main:app --reload)")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred parsing JSON: {str(e)}")
        return {}
