import logging
from app.services.json_loader.itinerary_mapper import ItineraryMapper

logger = logging.getLogger(__name__)

class SearchResultsLoader:
    def __init__(self):
        self.mapper = ItineraryMapper()

    def load_oneway(self, json_data):
        options = []
        if not isinstance(json_data, list):
            return options

        for flight in json_data:
            try:
                legs = flight.get("legs", [])
                fares = flight.get("fares", [])
                
                if not legs or not fares:
                    continue
                    
                leg = legs[0]
                for fare in fares:
                    try:
                        mapped = self.mapper.map(flight, fare, leg)
                        options.append(mapped)
                    except Exception as e:
                        logger.warning(f"Error mapping one-way fare: {e}")
            except Exception as e:
                logger.warning(f"Error processing one-way flight: {e}")
                
        return options

    def load_roundtrip(self, json_data):
        options = []
        if not isinstance(json_data, list):
            return options

        for flight in json_data:
            try:
                legs = flight.get("legs", [])
                fares = flight.get("fares", [])
                
                if len(legs) < 2 or not fares:
                    continue
                    
                outbound = legs[0]
                inbound = legs[1]
                for fare in fares:
                    try:
                        mapped = self.mapper.map(flight, fare, outbound)
                        mapped["duration"] += inbound.get("duration_minutes", 0)
                        mapped["stops"] = max(mapped["stops"], inbound.get("stop_count", 0))
                        options.append(mapped)
                    except Exception as e:
                        logger.warning(f"Error mapping roundtrip fare: {e}")
            except Exception as e:
                logger.warning(f"Error processing roundtrip flight: {e}")
                
        return options
