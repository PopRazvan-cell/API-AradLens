import os

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.core.elevenlabs import ElevenLabsError, synthesize_speech
from app.core.storage import (
    location_voice_path,
    save_location_voice,
    voice_audio_media_type,
)
from app.database import get_db
from app.models.admin import Admin
from app.models.location import Location
from app.schemas.voice import LocationVoiceOut

router = APIRouter(prefix="/voice", tags=["voice"])

MAX_TTS_CHARS = 5000


def _raise_http(exc: ElevenLabsError) -> None:
    code = exc.status_code
    if code not in (429, 503, 504):
        code = status.HTTP_502_BAD_GATEWAY
    raise HTTPException(status_code=code, detail=exc.detail)


@router.post(
    "/locations/{location_id}",
    response_model=LocationVoiceOut,
    status_code=status.HTTP_201_CREATED,
    summary="Generează fișierul audio al descrierii locației",
)
def generate_location_voice(
    location_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> LocationVoiceOut:
    location = db.get(Location, location_id)
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locația nu a fost găsită",
        )

    text = (location.description or "").strip()
    if not text:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Locația nu are descriere",
        )
    if len(text) > MAX_TTS_CHARS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                "Descrierea depășește limita ElevenLabs "
                f"({MAX_TTS_CHARS} caractere)"
            ),
        )

    try:
        audio = synthesize_speech(text, language="ro")
    except ElevenLabsError as exc:
        _raise_http(exc)

    public_path = save_location_voice(location_id, audio)
    return LocationVoiceOut(
        location_id=location_id,
        file=public_path,
        media_type=voice_audio_media_type(),
        size_bytes=len(audio),
    )


@router.get(
    "/locations/{location_id}",
    response_class=FileResponse,
    summary="Descarcă fișierul audio generat pentru locație",
    responses={
        200: {"content": {"audio/*": {}}, "description": "Fișier audio"},
        404: {"description": "Fișierul audio nu a fost generat"},
    },
)
def get_location_voice(location_id: int) -> FileResponse:
    path = location_voice_path(location_id)
    if not os.path.isfile(path):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fișierul audio nu a fost generat pentru această locație",
        )

    return FileResponse(path, media_type=voice_audio_media_type())

