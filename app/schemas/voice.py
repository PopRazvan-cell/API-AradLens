from typing import Literal

from pydantic import BaseModel, Field


class SpeechRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=5000,
        description="Textul care va fi citit (max 5000 caractere)",
    )
    language: Literal["ro", "en"] | None = Field(
        default="ro",
        description="Limba vocii: ro (implicit) sau en",
    )
    voice_id: str | None = Field(
        default=None, description="Opțional; suprascrie vocea pentru limbă"
    )
    model_id: str | None = Field(
        default=None, description="Opțional; suprascrie ELEVENLABS_MODEL_ID"
    )


class LocationVoiceFileOut(BaseModel):
    file: str = Field(description="Calea publică a fișierului audio generat")
    size_bytes: int = Field(description="Dimensiunea fișierului în bytes")


class LocationVoiceOut(BaseModel):
    location_id: int = Field(description="ID-ul locației")
    media_type: str = Field(description="Tipul MIME al fișierelor audio")
    files: dict[str, LocationVoiceFileOut] = Field(
        description="Fișierele audio generate, cheie = limba (ro/en)"
    )
