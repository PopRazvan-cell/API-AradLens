from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class LocationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    latitude: float
    longitude: float
    description: str | None = None
    images: list[int] = Field(default_factory=list)

    @field_validator("images", mode="before")
    @classmethod
    def _image_ids(cls, value: object) -> list[int]:
        if value is None:
            return []
        return [item if isinstance(item, int) else item.id for item in value]  # type: ignore[union-attr]


class LocationCreate(BaseModel):
    name: str = Field(min_length=2, max_length=150)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    description: str | None = None
    image: str | None = Field(default=None, max_length=500)


class LocationUpdate(BaseModel):
    name: str | None = Field(default=None, max_length=150)
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)
    description: str | None = None
    image: str | None = Field(default=None, max_length=500)


class LocationImageOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    location_id: int
    image: str
    created_at: datetime

