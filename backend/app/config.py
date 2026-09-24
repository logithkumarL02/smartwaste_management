from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    supabase_url: str = Field(
        validation_alias="SUPABASE_URL"
    )

    supabase_service_role_key: str = Field(
        validation_alias="SUPABASE_SERVICE_ROLE_KEY"
    )

    model_path: str = Field(
        default="model/waste_classifier.keras",
        validation_alias="MODEL_PATH"
    )

    model_metadata_path: str = Field(
        default="model/metadata.json",
        validation_alias="MODEL_METADATA_PATH"
    )

    confidence_threshold: float = Field(
        default=0.80,
        validation_alias="CONFIDENCE_THRESHOLD"
    )

    uncertain_threshold: float = Field(
        default=0.50,
        validation_alias="UNCERTAIN_THRESHOLD"
    )

    max_alternatives: int = Field(
        default=3,
        validation_alias="MAX_ALTERNATIVES"
    )

    hardware_mode: str = Field(
        default="simulation",
        validation_alias="HARDWARE_MODE"
    )

    max_upload_size_mb: int = Field(
        default=10,
        validation_alias="MAX_UPLOAD_SIZE_MB"
    )

    allowed_mime_types: list = [
        "image/jpeg",
        "image/png",
        "image/webp",
        "image/bmp"
    ]

    cors_origins: list = Field(
        default=[
            "http://localhost:3000",
            "http://127.0.0.1:3000"
        ],
        validation_alias="CORS_ORIGINS"
    )

    store_images: bool = Field(
        default=False,
        validation_alias="STORE_IMAGES"
    )

    supabase_storage_bucket: str = Field(
        default="prediction-images",
        validation_alias="STORAGE_BUCKET"
    )


@lru_cache()
def get_settings() -> Settings:
    return Settings()