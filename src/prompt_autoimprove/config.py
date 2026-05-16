from functools import lru_cache
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

ClassifierBackend = Literal["heuristic", "embeddings", "judge", "composite"]


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


class ImproverSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_IMPROVER_")

    profile: str | None = None
    max_output_tokens: int = 1024


class ClassifierSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_CLASSIFIER_")

    backend: ClassifierBackend = "heuristic"
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    composite_lo: float = 0.30
    composite_hi: float = 0.55


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
    improver: ImproverSettings = Field(default_factory=ImproverSettings)
    classifier: ClassifierSettings = Field(default_factory=ClassifierSettings)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached `Settings` instance."""
    return Settings()
