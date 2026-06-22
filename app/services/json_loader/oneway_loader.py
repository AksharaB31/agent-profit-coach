import logging
from app.services.json_loader.itinerary_mapper import ItineraryMapper

logger = logging.getLogger(__name__)

class OneWayLoader:
    def __init__(self):
        self.mapper = ItineraryMapper()

    def load(self, json_data):
        options = []
        if not isinstance(json_data, list):
            return options

        for flight in json_data:
            try:
                legs = flight.get("legs", [])
                fares = flight.get("fares", [])
                
                if not legs or not fares:
                    continue
                    
                leg = legs[0] # One way has one leg
                for fare in fares:
                    try:
                        mapped = self.mapper.map(flight, fare, leg)
                        options.append(mapped)
                    except Exception as e:
                        logger.warning(f"Error mapping fare in OneWayLoader: {e}")
            except Exception as e:
                logger.warning(f"Error processing flight in OneWayLoader: {e}")
                
        return options