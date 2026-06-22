from typing import Dict, Any
from app.core.config import settings
from app.services.agent_profit_coach.providers.base_search_provider import BaseSearchProvider
from app.services.agent_profit_coach.providers.json_search_provider import JsonSearchProvider
from app.services.agent_profit_coach.providers.supplier_api_provider import SupplierApiProvider
from app.services.agent_profit_coach.core.logger import setup_logger

logger = setup_logger(__name__)

def get_search_provider() -> BaseSearchProvider:
    """
    Factory function to return the correct provider based on configuration.
    """
    env = settings.ENVIRONMENT.lower()
    
    if env in ["development", "testing", "local"]:
        logger.info("Using JsonSearchProvider for development environment")
        return JsonSearchProvider()
    elif env == "production":
        logger.info("Using SupplierApiProvider for production environment")
        return SupplierApiProvider()
    else:
        logger.warning(f"Unknown environment {env}, defaulting to JsonSearchProvider")
        return JsonSearchProvider()
