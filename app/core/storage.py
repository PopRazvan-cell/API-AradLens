import os
import uuid

from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".gif"}


def locations_image_dir() -> str:
    path = os.path.join(settings.media_dir, "locations")
    os.makedirs(path, exist_ok=True)
    return path


async def save_location_image(file: UploadFile) -> str:
    ext = os.path.splitext(file.filename or "")[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Extensie nepermisa. Acceptate: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
        )

    content = await file.read()
    if not content:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fisierul este gol",
        )

    max_bytes = settings.max_upload_mb * 1024 * 1024
    if len(content) > max_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"Fisier prea mare (max {settings.max_upload_mb} MB)",
        )

    filename = f"{uuid.uuid4().hex}{ext}"
    with open(os.path.join(locations_image_dir(), filename), "wb") as out:
        out.write(content)
    return f"/media/locations/{filename}"


def load_media_bytes(public_path: str | None) -> bytes | None:
    """Citeste continutul unui fisier media dupa calea publica (/media/...)."""
    if not public_path or not public_path.startswith("/media/"):
        return None
    full_path = os.path.join(settings.media_dir, public_path[len("/media/") :])
    try:
        with open(full_path, "rb") as src:
            return src.read()
    except OSError:
        return None


def delete_media_file(public_path: str | None) -> None:
    if not public_path or not public_path.startswith("/media/"):
        return
    full_path = os.path.join(settings.media_dir, public_path[len("/media/") :])
    try:
        os.remove(full_path)
    except OSError:
        pass
