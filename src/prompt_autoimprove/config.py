from functools import lru_cache
from typing import Literal

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ClassifierBackend = Literal["heuristic", "embeddings", "judge", "composite"]


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_DB_")

    dsn: str = "postgresql+asyncpg://pai:pai@localhost:5432/pai"
    echo: bool = False
    pool_size: int = 10
    auto_create: bool = False


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


class ScorerSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_SCORER_")

    semantic: bool = False
    embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2"
    device: str = "cpu"
    semantic_blend: float = 0.5


class APISettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PAI_API_")

    api_key: str = ""
    allow_dev_key: bool = False
    rate_limit_per_minute: int = 60
    grpc_enabled: bool = True
    grpc_port: int = 50051
    http_port: int = 8000
    cors_origins: str = "http://localhost:3000,http://127.0.0.1:3000"

    @property
    def cors_origin_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",") if origin.strip()]


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
    scorer: ScorerSettings = Field(default_factory=ScorerSettings)

    @model_validator(mode="after")
    def _resolve_api_key(self) -> "Settings":
        if self.api.api_key:
            return self
        if self.environment == "dev" or self.api.allow_dev_key:
            self.api.api_key = "dev-key"
            return self
        raise ValueError(
            "API key is required outside dev: set PAI_API__API_KEY "
            "or PAI_API__ALLOW_DEV_KEY=1 for local use"
        )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached `Settings` instance."""
    return Settings()
