from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseSearchProvider(ABC):
    """Abstract base class for all search providers"""

    @abstractmethod
    async def search(self, params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Execute a search and return a list of flight itineraries.
        
        Args:
            params: Dictionary containing search parameters (e.g., origin, destination, date)
            
        Returns:
            List of dictionary objects representing itineraries
        """
        pass
