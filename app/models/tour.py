from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.mysql import BIGINT
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.location import Location


class Tour(Base):
    __tablename__ = "tours"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    links: Mapped[list["TourLocation"]] = relationship(
        back_populates="tour",
        cascade="all, delete-orphan",
        order_by="TourLocation.position",
    )

    @property
    def location_ids(self) -> list[int]:
        return [link.location_id for link in self.links]

    @property
    def locations(self) -> list["Location"]:
        return [link.location for link in self.links]

    def __repr__(self) -> str:
        return f"<Tour id={self.id} name={self.name!r}>"


class TourLocation(Base):
    __tablename__ = "tour_locations"

    id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True), primary_key=True, autoincrement=True
    )
    tour_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("tours.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    location_id: Mapped[int] = mapped_column(
        BIGINT(unsigned=True),
        ForeignKey("locations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    position: Mapped[int] = mapped_column(Integer, nullable=False)

    tour: Mapped["Tour"] = relationship(back_populates="links")
    location: Mapped["Location"] = relationship()

    def __repr__(self) -> str:
        return (
            f"<TourLocation tour_id={self.tour_id} "
            f"location_id={self.location_id} position={self.position}>"
        )
