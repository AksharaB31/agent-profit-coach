import logging
from app.services.json_loader.itinerary_mapper import ItineraryMapper

logger = logging.getLogger(__name__)

class RoundTripLoader:
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
                
                if len(legs) < 2 or not fares:
                    continue
                    
                outbound = legs[0]
                inbound = legs[1]
                # Just map the outbound leg for simplicity in roundtrip scoring or combine them
                for fare in fares:
                    try:
                        mapped = self.mapper.map(flight, fare, outbound)
                        # Add total duration
                        mapped["duration"] += inbound.get("duration_minutes", 0)
                        mapped["stops"] = max(mapped["stops"], inbound.get("stop_count", 0))
                        options.append(mapped)
                    except Exception as e:
                        logger.warning(f"Error mapping fare in RoundTripLoader: {e}")
            except Exception as e:
                logger.warning(f"Error processing flight in RoundTripLoader: {e}")
                
        return options