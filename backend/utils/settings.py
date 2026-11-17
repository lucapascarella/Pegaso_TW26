from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables or from the .env file."""
    APP_NAME: str = "SensorHub API"
    DEBUG: bool = False

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
