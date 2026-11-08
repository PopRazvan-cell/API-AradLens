from fastapi import APIRouter, Depends, HTTPException, Response, status

from app.api.deps import get_current_admin
from app.core.config import settings
from app.core.elevenlabs import ElevenLabsError, list_voices, synthesize_speech
from app.models.admin import Admin
from app.schemas.voice import SpeechRequest

router = APIRouter(prefix="/voice", tags=["voice"])


def _raise_http(exc: ElevenLabsError) -> None:
    code = exc.status_code
    if code not in (429, 503, 504):
        code = status.HTTP_502_BAD_GATEWAY
    raise HTTPException(status_code=code, detail=exc.detail)


@router.post(
    "/speech",
    response_class=Response,
    summary="Generează audio din text (ElevenLabs TTS)",
    responses={200: {"content": {"audio/mpeg": {}}, "description": "Audio MP3"}},
)
def speech(
    payload: SpeechRequest,
    _: Admin = Depends(get_current_admin),
) -> Response:
    try:
        audio = synthesize_speech(
            payload.text,
            voice_id=payload.voice_id,
            model_id=payload.model_id,
            language=payload.language,
        )
    except ElevenLabsError as exc:
        _raise_http(exc)

    return Response(content=audio, media_type="audio/mpeg")


@router.get("/voices", summary="Lista vocilor disponibile ElevenLabs")
def voices(_: Admin = Depends(get_current_admin)) -> dict:
    try:
        return list_voices()
    except ElevenLabsError as exc:
        _raise_http(exc)


@router.get("/status", summary="Starea configurării ElevenLabs")
def voice_status(_: Admin = Depends(get_current_admin)) -> dict:
    return {
        "configured": bool(settings.elevenlabs_api_key),
        "default_voice_id": settings.elevenlabs_voice_id,
        "voices": {
            "ro": settings.elevenlabs_voice_id_ro,
            "en": settings.elevenlabs_voice_id_en,
        },
        "model_id": settings.elevenlabs_model_id,
        "output_format": settings.elevenlabs_output_format,
    }
