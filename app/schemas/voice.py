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


class LocationVoiceOut(BaseModel):
    location_id: int = Field(description="ID-ul locației")
    file: str = Field(description="Calea publică a fișierului audio generat")
    media_type: str = Field(description="Tipul MIME al fișierului audio")
    size_bytes: int = Field(description="Dimensiunea fișierului în bytes")
