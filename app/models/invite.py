from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class InviteCode(Base):
    __tablename__ = "invite_codes"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    code: Mapped[str] = mapped_column(
        String(64), unique=True, nullable=False, index=True
    )
    role: Mapped[str] = mapped_column(
        Enum("superadmin", "admin", name="invite_role"),
        nullable=False,
        default="admin",
        server_default="admin",
    )
    created_by_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    used_by_id: Mapped[int | None] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("admins.id", ondelete="SET NULL"),
        nullable=True,
    )
    expires_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    is_revoked: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default="0"
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    def __repr__(self) -> str:
        return f"<InviteCode id={self.id} role={self.role!r} used={self.used_at is not None}>"
