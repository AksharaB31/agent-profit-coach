class JourneyScoringService:
    def score_duration(self, duration_minutes: int, min_duration: int, max_duration: int) -> float:
        if max_duration == min_duration or max_duration == 0:
            return 0.5
        return 1.0 - ((duration_minutes - min_duration) / (max_duration - min_duration))

    def score_convenience(self, stops: int) -> float:
        # Nonstop is 1.0, 1 stop is 0.7, 2 stops is 0.4, 3+ is 0.1
        if stops == 0: return 1.0
        elif stops == 1: return 0.7
        elif stops == 2: return 0.4
        else: return 0.1

    def score_timing(self, departure_hour: int) -> float:
        # Ideal hours 8 AM - 6 PM
        if 8 <= departure_hour <= 18:
            return 1.0
        # Acceptable hours 6 AM - 8 AM or 6 PM - 10 PM
        elif 6 <= departure_hour < 8 or 18 < departure_hour <= 22:
            return 0.7
        # Red-eye / midnight flights
        else:
            return 0.3
