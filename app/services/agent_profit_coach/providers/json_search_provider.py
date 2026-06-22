import json
import os
from typing import List, Dict, Any
from app.services.agent_profit_coach.providers.base_search_provider import BaseSearchProvider
from app.services.agent_profit_coach.core.exceptions import ProviderFailureException
from app.services.agent_profit_coach.core.logger import setup_logger

logger = setup_logger(__name__)

class JsonSearchProvider(BaseSearchProvider):
    """Provider that loads search results from local JSON files"""
    
    async def search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Dynamic extraction of the target JSON file based on params
        file_path = params.get("file_path")
        if not file_path:
            logger.error("JSON Search Provider requires 'file_path' in params")
            raise ProviderFailureException("Missing 'file_path' for JsonSearchProvider")
            
        if not os.path.exists(file_path):
            logger.error(f"JSON file not found: {file_path}")
            raise ProviderFailureException(f"Search file not found: {file_path}")
            
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            # If the json structure has a nested "flights" key, extract it
            if isinstance(data, dict) and "flights" in data:
                return data["flights"]
            elif isinstance(data, list):
                return data
            else:
                logger.warning(f"Unexpected JSON structure in {file_path}")
                return [data]
                
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON file {file_path}: {e}")
            raise ProviderFailureException(f"Invalid JSON format in {file_path}")
        except Exception as e:
            logger.error(f"Unexpected error reading {file_path}: {e}")
            raise ProviderFailureException(f"Failed to read search data: {e}")
