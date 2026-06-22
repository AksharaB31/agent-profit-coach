class ItineraryFeatures:

    def build(self, itinerary):

        return {
            "duration": itinerary.get("duration", 0),
            "stops": itinerary.get("stops", 0),
            "baggage": itinerary.get("baggage", 20),
            "refundability": itinerary.get(
                "refundability",
                0.5
            )
        }