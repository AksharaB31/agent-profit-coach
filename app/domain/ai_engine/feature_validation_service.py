import logging
from typing import List

logger = logging.getLogger(__name__)

class DataLeakageException(Exception):
    pass

class FeatureValidationService:
    """Validates ML training features to prevent data leakage (post-booking info)."""
    
    # List of substrings/keywords that suggest future or post-booking data
    LEAKAGE_BLACKLIST = [
        "current_booking_status",
        "booked_outcome",
        "transaction_result",
        "post_booking",
        "ticket_issued",
        "payment_status",
        "actual_profit"
    ]

    @classmethod
    def validate_features(cls, features: List[str]) -> bool:
        """
        Scans feature column names against a strict blacklist.
        Raises DataLeakageException if leakage is detected.
        """
        for feature in features:
            feature_lower = feature.lower()
            for bad_word in cls.LEAKAGE_BLACKLIST:
                if bad_word in feature_lower:
                    msg = f"DATA LEAKAGE DETECTED: Feature '{feature}' contains prohibited post-booking keyword '{bad_word}'."
                    logger.error(msg)
                    raise DataLeakageException(msg)
                    
        return True
