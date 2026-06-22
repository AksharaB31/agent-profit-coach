from pydantic_settings import BaseSettings


class InfraSettings(BaseSettings):

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    TELEMETRY_ENABLED: bool = True

    class Config:
        env_file = ".env"


infra_settings = InfraSettings()