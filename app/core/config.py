import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    secret_key: str = os.getenv("SECRET_KEY", "schimba-aceasta-cheie-in-productie")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    media_dir: str = os.getenv("MEDIA_DIR", "/app/media")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "5"))


settings = Settings()
