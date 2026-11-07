from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

AdminRole = Literal["superadmin", "admin"]


class AdminLogin(BaseModel):
    username: str = Field(description="Username sau email")
    password: str


class AdminCreate(BaseModel):
    username: str = Field(min_length=3, max_length=50)
    email: str = Field(max_length=255)
    password: str = Field(min_length=8)
    role: AdminRole = "admin"
    is_active: bool = True


class AdminUpdate(BaseModel):
    role: AdminRole | None = None
    is_active: bool | None = None


class AdminSelfUpdate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=50)
    email: str | None = Field(default=None, max_length=255)
    old_password: str


class AdminOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    username: str
    email: str
    role: str
    is_active: bool
    last_login_at: datetime | None = None


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8, description="Minim 8 caractere")


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int
