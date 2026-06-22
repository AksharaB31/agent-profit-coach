class PriceScoringService:
    def score(self, price: float, min_price: float, max_price: float) -> float:
        """
        Scores price by normalizing against the minimum and maximum prices in the cohort.
        Lower prices get higher scores.
        """
        if max_price == min_price or max_price == 0:
            return 0.5
        
        # Max score for cheapest, min score for most expensive
        return 1.0 - ((price - min_price) / (max_price - min_price))
