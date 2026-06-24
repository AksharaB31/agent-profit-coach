from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    PROJECT_NAME: str = "Agent Profit Coach API"
    VERSION: str = "1.0.0"

    ENVIRONMENT: str = "development"

    HOST: str = "0.0.0.0"
    PORT: int = 8000 

    DATABASE_URL: str

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    SECRET_KEY: str
    API_KEY: str

    # ML MODELS
    PROFIT_MODEL_PATH: str = (
        "app/ml/models/ml_profit_model_oneway_v1.pkl"
    )

    ROUNDTRIP_PROFIT_MODEL_PATH: str = (
        "app/ml/models/ml_profit_model_roundtrip_v1.pkl"
    )

    CONVERSION_MODEL_PATH: str = (
        "app/ml/models/conversion_model.pkl"
    )

    # PROFIT COACH SCORING WEIGHTS
    PROFIT_WEIGHT: float = 0.40
    RELIABILITY_WEIGHT: float = 0.25
    PRICE_WEIGHT: float = 0.15
    CONVENIENCE_WEIGHT: float = 0.10
    CONVERSION_WEIGHT: float = 0.10
    ML_PROFIT_WEIGHT: float = 0.50

    # ENTERPRISE ENGINE CONFIGURATION
    MIN_BOOKING_THRESHOLD: int = 5
    DEFAULT_RELIABILITY_SCORE: float = 0.80
    DEFAULT_BOOKING_SUCCESS_PROBABILITY: float = 0.85
    DEFAULT_CANCELLATION_RISK: float = 0.10
    DEFAULT_MARKUP_PERCENTAGE: float = 0.08
    MINIMUM_PROFIT_MARGIN: float = 2.0

    ENGINE_VERSION: str = "enterprise_v2"

    LOG_LEVEL: str = "INFO"

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )


settings = Settings()