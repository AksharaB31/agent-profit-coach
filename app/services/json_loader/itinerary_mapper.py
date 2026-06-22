from datetime import datetime
import re


class ItineraryMapper:

    def map(self, flight, fare, leg):

        # -------------------------
        # BAGGAGE
        # -------------------------

        baggage_str = fare.get("checkin_baggage")

        # HANDLE NONE
        if baggage_str is None:
            baggage_str = "0"

        # ENSURE STRING
        baggage_str = str(baggage_str)

        baggage_weight = 0

        match = re.search(r'(\d+)', baggage_str)

        if match:
            baggage_weight = int(match.group(1))

        # -------------------------
        # MEALS
        # -------------------------

        amenities = fare.get("amenities", {})

        meal_text = str(
            amenities.get("meal", "")
        )

        meal_included = (
            1.0
            if "included" in meal_text.lower()
            else 0.0
        )

        # -------------------------
        # REFUNDABILITY
        # -------------------------

        is_refundable = fare.get(
            "is_refundable",
            False
        )

        refundability = (
            1.0 if is_refundable else 0.0
        )

        # -------------------------
        # TIMING SCORE
        # -------------------------

        dep_time_str = leg.get(
            "departure_time",
            ""
        )

        timing_score = 0.5

        departure_hour = 12

        if dep_time_str:

            try:

                dt = datetime.fromisoformat(
                    dep_time_str.replace(
                        "Z",
                        "+00:00"
                    )
                )

                departure_hour = dt.hour

                # BEST HOURS
                if 8 <= dt.hour <= 18:
                    timing_score = 0.9

                # GOOD HOURS
                elif 6 <= dt.hour <= 22:
                    timing_score = 0.7

            except Exception:
                pass

        # -------------------------
        # SEGMENTS & ROUTE
        # -------------------------

        segments = leg.get("segments", [])

        flight_number = "Unknown"
        origin = leg.get("origin_code")
        destination = leg.get("destination_code")

        if segments:
            flight_number = segments[0].get(
                "flight_number",
                "Unknown"
            )
            if not origin:
                origin = segments[0].get("origin_code", "Unknown")
            if not destination:
                destination = segments[-1].get("destination_code", "Unknown")

        # -------------------------
        # PRICE
        # -------------------------

        price_data = fare.get("price", {})

        if isinstance(price_data, dict):

            price = price_data.get(
                "buy_price",
                0.0
            )

        else:

            price = price_data or 0.0

        # -------------------------
        # RETURN
        # -------------------------

        return {

            "origin": origin,

            "destination": destination,

            "supplier": flight.get(
                "source",
                "Unknown"
            ),

            "airline": flight.get(
                "airline_name",
                "Unknown"
            ),

            "flight_number": flight_number,

            "price": float(price),

            "duration": leg.get(
                "duration_minutes",
                0
            ),

            "stops": leg.get(
                "stop_count",
                0
            ),

            "baggage": baggage_weight,

            "refundability": refundability,

            "meals": meal_included,

            "timing_score": timing_score,

            "departure_hour": departure_hour,

            "refundable": is_refundable
        }

