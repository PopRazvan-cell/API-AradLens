import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class Settings:
    secret_key: str = os.getenv("SECRET_KEY", "schimba-aceasta-cheie-in-productie")
    algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60")
    )
    media_dir: str = os.getenv("MEDIA_DIR", "/app/media")
    max_upload_mb: int = int(os.getenv("MAX_UPLOAD_MB", "5"))

    # Resetare parola
    frontend_url: str = os.getenv(
        "FRONTEND_URL", "https://admin.aradlens.binarysquad.club"
    ).rstrip("/")
    password_reset_expire_minutes: int = int(
        os.getenv("PASSWORD_RESET_EXPIRE_MINUTES", "30")
    )
    # Doar pentru test: returneaza linkul in raspunsul API.
    return_reset_link: bool = _env_bool("RETURN_RESET_LINK", False)

    # SMTP (optional - daca lipseste, linkul se scrie in log)
    smtp_host: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    smtp_port: int = int(os.getenv("SMTP_PORT", "587"))
    smtp_user: str = os.getenv("SMTP_USER", "")
    smtp_password: str = os.getenv("SMTP_PASSWORD", "")
    smtp_from: str = os.getenv("SMTP_FROM", "")
    smtp_use_tls: bool = _env_bool("SMTP_USE_TLS", True)
    smtp_use_ssl: bool = _env_bool("SMTP_USE_SSL", False)


settings = Settings()
