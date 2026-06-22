from typing import Dict, Any
from app.services.agent_profit_coach.core.logger import setup_logger
from app.core.config import settings

logger = setup_logger(__name__)

class ProfitabilityEngine:
    """Engine responsible for calculating expected agent profit and profit score"""
    
    def calculate_profitability(
        self, 
        base_price: float, 
        historical_profit: float = 0.0, 
        markup: float = None,
        incentive: float = 0.0
    ) -> Dict[str, float]:
        """
        Dynamically calculates profitability strictly using agent data.
        Returns a dictionary containing sell_price, expected_agent_profit, profit_margin_percent, and profit_score.
        """
        try:
            if markup is None or markup < 0:
                markup = 0.0
                logger.debug("Markup missing or invalid, defaulting strictly to 0.0 (no fallback)")
            
            # Incentive engine logic: Expected Profit = Historical Profit + Active Markup + Supplier Incentive
            expected_agent_profit = historical_profit + markup + incentive
            
            # Recalculate sell_price backwards just for API stability (base + profit)
            sell_price = base_price + expected_agent_profit
            
            # Defensive calculation to avoid Division by Zero
            if sell_price > 0:
                profit_margin_percent = (expected_agent_profit / sell_price) * 100.0
            else:
                profit_margin_percent = 0.0
                
            # Score logic: normalized profitability score as profit-to-price ratio
            if expected_agent_profit > 0 and base_price > 0:
                profit_score = min(expected_agent_profit / base_price, 1.0)
            else:
                profit_score = 0.0
                
            logger.info(
                f"Calculated profitability: sell_price={sell_price:.2f}, "
                f"expected_agent_profit={expected_agent_profit:.2f}, "
                f"margin={profit_margin_percent:.2f}%"
            )
            
            return {
                "sell_price": round(sell_price, 2),
                "expected_agent_profit": round(expected_agent_profit, 2),
                "profit_margin_percent": round(profit_margin_percent, 2),
                "profit_score": round(profit_score, 2)
            }
            
        except Exception as e:
            logger.error(f"Error calculating profitability: {e}")
            # Enterprise-safe fallback
            return {
                "sell_price": base_price,
                "expected_agent_profit": 0.0,
                "profit_margin_percent": 0.0,
                "profit_score": 0.0
            }

    def analyze(self, itinerary: Dict[str, Any]) -> Dict[str, float]:
        """
        Extracts agent profit and calculates profit_score.
        Must ONLY use booking_fares.agent_profit or booking_adjusted_fares.agent_profit.
        """
        agent_profit = float(itinerary.get("agent_profit", 0.0))
        
        profit_score = float(itinerary.get("scores", {}).get("profit_score", 0.0))
        
        if profit_score == 0.0 and agent_profit > 0:
            profit_score = min(agent_profit / 100.0, 1.0) 
            
        logger.debug(f"Profitability analyzed: agent_profit={agent_profit}, profit_score={profit_score}")
        
        return {
            "expected_agent_profit": agent_profit,
            "profit_score": profit_score
        }
