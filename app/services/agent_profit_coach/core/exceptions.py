class AgentProfitCoachException(Exception):
    """Base exception for Agent Profit Coach"""
    pass

class MissingItineraryDataException(AgentProfitCoachException):
    """Raised when an itinerary is missing required enterprise data like supplier, scores, etc."""
    pass

class InvalidScoringException(AgentProfitCoachException):
    """Raised when scoring calculation fails or results in invalid values"""
    pass

class ProviderFailureException(AgentProfitCoachException):
    """Raised when a search provider fails to fetch or parse data"""
    pass
