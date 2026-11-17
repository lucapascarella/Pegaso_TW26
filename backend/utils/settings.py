from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings, read from environment variables or from the .env file."""
    APP_NAME: str = "SensorHub API"
    DEBUG: bool = False

    # SQLite file in the backend folder; in production the path comes from the environment
    DATABASE_URL: str = "sqlite:///./sensorhub.db"

    # Authentication (the real SECRET_KEY must come from the environment)
    SECRET_KEY: str = "change-me"
    ACCESS_TOKEN_EXPIRE_MIN: int = 60
    ADMIN_EMAIL: str = "admin@altranodes.example"
    ADMIN_PASSWORD: str = "ChangeMe-2026!"

    # MQTT broker
    MQTT_HOST: str = "localhost"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = ""
    MQTT_PASSWORD: str = ""
    MQTT_TLS: bool = False
    MQTT_TOPIC_ROOT: str = "sensorhub"

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
