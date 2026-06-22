class TimingEngine:
    """Scores convenience of departure time."""
    
    def calculate_score(self, departure_hour: int) -> float:
        # Best times: 8 AM to 6 PM (100)
        # Okay times: 6 AM to 8 AM, 6 PM to 10 PM (70)
        # Bad times: Red-eye 10 PM to 6 AM (40)
        
        if 8 <= departure_hour <= 18:
            return 100.0
        elif 6 <= departure_hour < 8 or 18 < departure_hour <= 22:
            return 70.0
        else:
            return 40.0
