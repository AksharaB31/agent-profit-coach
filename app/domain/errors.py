class AgentProfitCoachException(Exception):
    pass


class SupplierNotFoundException(AgentProfitCoachException):
    def __init__(self, supplier: str):
        self.message = f"Supplier '{supplier}' not found"
        super().__init__(self.message)


class PredictionException(AgentProfitCoachException):
    def __init__(self, message="Prediction failed"):
        self.message = message
        super().__init__(self.message)


class ModelNotLoadedException(AgentProfitCoachException):
    def __init__(self, model_name: str):
        self.message = f"Model '{model_name}' could not be loaded"
        super().__init__(self.message)