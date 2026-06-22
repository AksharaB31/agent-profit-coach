class ConversionEngine:
    """Predicts likelihood of agent booking this option based on price competitiveness."""
    
    def calculate_probability(self, sell_price: float, min_price: float, max_price: float, db_probability: float = -1.0) -> float:
        # Use DB historical probability if sufficient data was found
        if db_probability >= 0.0:
            return round(db_probability, 2)
            
        if max_price == min_price:
            return 0.95
            
        # Fallback: Lower price = higher probability. 
        # Best price gets ~95% base probability. Worst price gets ~10%.
        ratio = (sell_price - min_price) / (max_price - min_price)
        prob = 0.95 - (ratio * 0.85)
        
        return round(max(0.01, min(0.99, prob)), 2)
