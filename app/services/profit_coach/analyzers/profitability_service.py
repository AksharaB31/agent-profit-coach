from typing import Dict

class ProfitabilityService:
    def calculate_expected_profit(self, flight_price: float, historical_profit_data: Dict[str, float], markup: float) -> float:
        """
        Calculates the expected profit by combining base fare commission potential with 
        historical profit margins and explicit markup overrides.
        """
        avg_commission = historical_profit_data.get("avg_commission", 0.0)
        historical_profit = historical_profit_data.get("avg_profit", 0.0)
        
        # Base commission estimation from flight price + historical fixed profit + explicit markup
        expected_profit = (flight_price * (avg_commission / 100)) + historical_profit + markup
        return expected_profit
