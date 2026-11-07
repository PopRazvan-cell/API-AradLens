from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.admin import Admin
from app.models.location import Location
from app.models.tour import Tour, TourLocation
from app.schemas.tour import TourCreate, TourOut, TourUpdate

router = APIRouter(prefix="/tours", tags=["tours"])


def _tour_options():
    return (
        selectinload(Tour.links)
        .selectinload(TourLocation.location)
        .selectinload(Location.images)
    )


def _get_or_404(db: Session, tour_id: int) -> Tour:
    tour = db.get(Tour, tour_id, options=[_tour_options()])
    if tour is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Turul nu a fost gasit",
        )
    return tour


def _validate_location_ids(db: Session, location_ids: list[int]) -> None:
    unique_ids = list(dict.fromkeys(location_ids))
    found = set(
        db.scalars(select(Location.id).where(Location.id.in_(unique_ids)))
    )
    missing = [location_id for location_id in unique_ids if location_id not in found]
    if missing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Locatii inexistente: {missing}",
        )


def _build_links(location_ids: list[int]) -> list[TourLocation]:
    return [
        TourLocation(location_id=location_id, position=position)
        for position, location_id in enumerate(location_ids, start=1)
    ]


@router.post(
    "",
    response_model=TourOut,
    status_code=status.HTTP_201_CREATED,
    summary="Creeaza tur (lant de locatii)",
)
def create_tour(
    payload: TourCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Tour:
    _validate_location_ids(db, payload.location_ids)

    tour = Tour(name=payload.name, description=payload.description)
    tour.links = _build_links(payload.location_ids)
    db.add(tour)
    db.flush()
    tour_id = tour.id
    db.commit()

    return _get_or_404(db, tour_id)


@router.get("", response_model=list[TourOut], summary="Lista tururilor")
def list_tours(db: Session = Depends(get_db)) -> list[Tour]:
    return list(
        db.scalars(select(Tour).options(_tour_options()).order_by(Tour.id))
    )


@router.get("/{tour_id}", response_model=TourOut, summary="Detalii tur")
def get_tour(tour_id: int, db: Session = Depends(get_db)) -> Tour:
    return _get_or_404(db, tour_id)


@router.put("/{tour_id}", response_model=TourOut, summary="Actualizeaza tur")
def update_tour(
    tour_id: int,
    payload: TourUpdate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Tour:
    tour = _get_or_404(db, tour_id)
    data = payload.model_dump(exclude_unset=True)

    if "name" in data:
        tour.name = data["name"]
    if "description" in data:
        tour.description = data["description"]
    if "location_ids" in data:
        if not data["location_ids"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Turul trebuie sa contina cel putin o locatie",
            )
        _validate_location_ids(db, data["location_ids"])
        tour.links.clear()
        tour.links.extend(_build_links(data["location_ids"]))

    db.commit()
    return _get_or_404(db, tour_id)


@router.delete(
    "/{tour_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Sterge tur",
)
def delete_tour(
    tour_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Response:
    tour = _get_or_404(db, tour_id)
    db.delete(tour)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
