from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.location import LocationOut


class TourCreate(BaseModel):
    name: str = Field(min_length=1, max_length=150)
    description: str | None = None
    location_ids: list[int] = Field(
        min_length=1, description="Locatiile in ordinea traseului"
    )


class TourUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=150)
    description: str | None = None
    location_ids: list[int] | None = Field(
        default=None, description="Locatiile in ordinea traseului"
    )


class TourOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str | None = None
    created_at: datetime
    location_ids: list[int]
    locations: list[LocationOut]
