import requests
import streamlit as st
from config import config
from typing import Dict, Any, Optional

@st.cache_data(ttl=300)
def fetch_itinerary_intelligence(payload: Dict[str, Any]) -> Dict[str, Any]:
    """
    Call the Agent Profit Coach FastAPI endpoint.
    Uses st.cache_data to avoid redundant API calls for the same payload.
    """
    try:
        response = requests.post(
            config.API_URL,
            json=payload,
            timeout=config.API_TIMEOUT_SECONDS,
            headers={"Content-Type": "application/json"}
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
        st.error(f"Failed to connect to API at {config.API_URL}. Is the backend running?")
        return {}
    except Exception as e:
        st.error(f"An unexpected error occurred: {str(e)}")
        return {}
