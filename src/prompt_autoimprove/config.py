from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_DB_")

    dsn: str = "postgresql+asyncpg://pai:pai@localhost:5432/pai"
    echo: bool = False
    pool_size: int = 10


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_KAFKA_")

    bootstrap_servers: str = "localhost:9092"
    client_id: str = "prompt-autoimprove"
    enabled: bool = False


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_API_")

    api_key: str = "dev-key"
    rate_limit_per_minute: int = 60
    grpc_port: int = 50051
    http_port: int = 8000


class Settings(BaseSettings):
    """Top-level settings aggregator."""

    model_config = SettingsConfigDict(
        env_prefix="PAI_",
        env_nested_delimiter="__",
        env_file=".env",
        extra="ignore",
    )

    environment: str = "dev"
    log_level: str = "INFO"
    profiles_dir: str = "src/prompt_autoimprove/registry/profiles"

    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
    kafka: KafkaSettings = Field(default_factory=KafkaSettings)
    api: APISettings = Field(default_factory=APISettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached `Settings` instance."""
    return Settings()
