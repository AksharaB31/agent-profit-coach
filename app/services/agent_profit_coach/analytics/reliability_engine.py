from app.core.config import settings

class ReliabilityEngine:
    """
    Calculates dynamic supplier reliability based on DB historical counts.
    """
    def __init__(self):
        pass

    def calculate_booking_success_probability(self, successful_processes: int, total_processes: int) -> float:
        if total_processes == 0:
            return 0.0              
        prob = successful_processes / total_processes
        return max(0.0, min(prob, 1.0))

    def calculate_cancellation_risk(self, cancelled_bookings: int, total_bookings: int) -> float: 
        if total_bookings == 0:
            return 0.0
        risk = cancelled_bookings / total_bookings
        return max(0.0, min(risk, 1.0))

    def calculate_ticketing_success_rate(self, ticketed_processes: int, total_processes: int) -> float:
        if total_processes == 0:
            return 0.0
        return max(0.0, min(ticketed_processes / total_processes, 1.0))

    def calculate_refund_success_rate(self, refunded_processes: int, total_processes: int) -> float:
        # Assuming refund_processes is relative to total processes.
        # Often refunds are relative to total cancellations or total requests, but based on the provided formula it's a flat metric.
        # If total processes is 0, return 1.0 (no bad refund history) or 0.0. Let's use 0.0 for conservative scoring if no history.
        if total_processes == 0:
            return 0.0
        return max(0.0, min(refunded_processes / total_processes, 1.0))

    def calculate_supplier_reliability(
        self, 
        success_prob: float, 
        cancellation_risk: float, 
        ticketing_rate: float, 
        refund_rate: float, 
        health_status: str = "unknown"
    ) -> float:
            
        # Enterprise mathematical formula purely based on historical db ratios.
        # (ticketing_success_rate + (1 - cancellation_rate) + refund_success_rate) / 3

        score = (ticketing_rate + (1.0 - cancellation_risk) + refund_rate) / 3.0
        return max(0.0, min(score, 1.0))
