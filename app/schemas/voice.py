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
