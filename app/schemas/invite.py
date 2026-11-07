from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.admin import AdminRole


class InviteCreate(BaseModel):
    role: AdminRole = "admin"
    expires_in_minutes: int | None = Field(
        default=None, gt=0, description="Optional: codul expira dupa N minute"
    )


class InviteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    code: str
    role: str
    expires_at: datetime | None = None
    used_at: datetime | None = None
    is_revoked: bool
    created_at: datetime


class RegisterRequest(BaseModel):
    code: str
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)
