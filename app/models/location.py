from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Double, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.location_image import LocationImage


class Location(Base):
    __tablename__ = "locations"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    latitude: Mapped[float] = mapped_column(Double, nullable=False)
    longitude: Mapped[float] = mapped_column(Double, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    image: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    images: Mapped[list["LocationImage"]] = relationship(
        back_populates="location",
        cascade="all, delete-orphan",
        order_by="LocationImage.id",
    )

    def __repr__(self) -> str:
        return f"<Location id={self.id} name={self.name!r}>"
