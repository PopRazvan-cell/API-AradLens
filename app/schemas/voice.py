from pydantic import BaseModel, Field


class SpeechRequest(BaseModel):
    text: str = Field(
        min_length=1,
        max_length=5000,
        description="Textul care va fi citit (max 5000 caractere)",
    )
    voice_id: str | None = Field(
        default=None, description="Opțional; suprascrie ELEVENLABS_VOICE_ID"
    )
    model_id: str | None = Field(
        default=None, description="Opțional; suprascrie ELEVENLABS_MODEL_ID"
    )
