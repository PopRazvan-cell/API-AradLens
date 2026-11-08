import json
import urllib.error
import urllib.request

from app.core.config import settings

ELEVENLABS_BASE_URL = "https://api.elevenlabs.io/v1"


class ElevenLabsError(Exception):
    def __init__(self, status_code: int, detail: str) -> None:
        self.status_code = status_code
        self.detail = detail
        super().__init__(detail)


def _api_key() -> str:
    if not settings.elevenlabs_api_key:
        raise ElevenLabsError(
            503,
            "ElevenLabs nu este configurat (setează ELEVENLABS_API_KEY)",
        )
    return settings.elevenlabs_api_key


def _request(
    url: str,
    *,
    method: str = "GET",
    payload: dict | None = None,
    accept: str = "application/json",
) -> bytes:
    data = json.dumps(payload).encode("utf-8") if payload is not None else None
    request = urllib.request.Request(url, data=data, method=method)
    request.add_header("xi-api-key", _api_key())
    request.add_header("Accept", accept)
    if data is not None:
        request.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(
            request, timeout=settings.elevenlabs_timeout_seconds
        ) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            parsed = json.loads(raw)
            detail = parsed.get("detail", parsed) if isinstance(parsed, dict) else parsed
            if isinstance(detail, dict):
                detail = detail.get("message") or json.dumps(detail)
        except json.JSONDecodeError:
            detail = raw
        raise ElevenLabsError(exc.code, str(detail or exc.reason)) from exc
    except urllib.error.URLError as exc:
        raise ElevenLabsError(502, f"ElevenLabs indisponibil: {exc.reason}") from exc
    except TimeoutError as exc:
        raise ElevenLabsError(504, "ElevenLabs a răspuns prea încet") from exc


def synthesize_speech(
    text: str,
    voice_id: str | None = None,
    model_id: str | None = None,
) -> bytes:
    voice = voice_id or settings.elevenlabs_voice_id
    model = model_id or settings.elevenlabs_model_id
    url = (
        f"{ELEVENLABS_BASE_URL}/text-to-speech/{voice}"
        f"?output_format={settings.elevenlabs_output_format}"
    )
    payload = {
        "text": text,
        "model_id": model,
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.75,
            "style": 0.0,
            "use_speaker_boost": True,
        },
    }
    return _request(url, method="POST", payload=payload, accept="audio/mpeg")


def list_voices() -> dict:
    raw = _request(f"{ELEVENLABS_BASE_URL}/voices")
    return json.loads(raw.decode("utf-8"))
