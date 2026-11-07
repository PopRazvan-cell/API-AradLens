import mimetypes

from fastapi import APIRouter, Depends, File, HTTPException, Response, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.api.deps import get_current_admin
from app.core.storage import delete_media_file, load_media_bytes, save_location_image
from app.database import get_db
from app.models.admin import Admin
from app.models.location import Location
from app.models.location_image import LocationImage
from app.schemas.location import (
    LocationCreate,
    LocationImageOut,
    LocationOut,
    LocationUpdate,
)

router = APIRouter(prefix="/locations", tags=["locations"])


def _get_or_404(db: Session, location_id: int) -> Location:
    location = db.get(Location, location_id, options=[selectinload(Location.images)])
    if location is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Locația nu a fost găsită",
        )
    return location


@router.get(
    "",
    response_model=list[LocationOut],
    summary="Lista locațiilor (nume + coordonate)",
)
def list_locations(db: Session = Depends(get_db)) -> list[Location]:
    return list(
        db.scalars(
            select(Location)
            .options(selectinload(Location.images))
            .order_by(Location.name)
        )
    )


@router.get("/{location_id}", response_model=LocationOut, summary="Detalii locație")
def get_location(location_id: int, db: Session = Depends(get_db)) -> Location:
    return _get_or_404(db, location_id)


@router.post(
    "",
    response_model=LocationOut,
    status_code=status.HTTP_201_CREATED,
    summary="Adauga locație",
)
def create_location(
    payload: LocationCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Location:
    location = Location(**payload.model_dump())
    db.add(location)
    db.commit()
    db.refresh(location)
    return location


@router.get(
    "/images/{image_id}",
    summary="Descarca o poza dupa id-ul ei",
    response_class=Response,
    responses={
        200: {
            "content": {"image/*": {}},
            "description": "Fisierul imagine",
        }
    },
)
def get_location_image(image_id: int, db: Session = Depends(get_db)) -> Response:
    image = db.get(LocationImage, image_id)
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poza nu a fost găsită",
        )

    content = load_media_bytes(image.image)
    if content is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Fisierul pozei nu a fost găsit",
        )

    media_type = mimetypes.guess_type(image.image)[0] or "application/octet-stream"
    return Response(content=content, media_type=media_type)


@router.post(
    "/{location_id}/images",
    response_model=LocationImageOut,
    status_code=status.HTTP_201_CREATED,
    summary="Adauga o poza in galeria locației (upload fisier)",
)
async def add_location_image(
    location_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> LocationImage:
    _get_or_404(db, location_id)
    image = LocationImage(
        location_id=location_id,
        image=await save_location_image(file),
    )
    db.add(image)
    db.commit()
    db.refresh(image)
    return image


@router.delete(
    "/{location_id}/images/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Sterge o poza din galeria locației",
)
def delete_location_image(
    location_id: int,
    image_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Response:
    _get_or_404(db, location_id)

    image = db.scalar(
        select(LocationImage).where(
            LocationImage.id == image_id,
            LocationImage.location_id == location_id,
        )
    )
    if image is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Poza nu a fost găsită",
        )

    delete_media_file(image.image)
    db.delete(image)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.patch(
    "/{location_id}",
    response_model=LocationOut,
    summary="Actualizeaza locație",
)
def update_location(
    location_id: int,
    payload: LocationUpdate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Location:
    location = _get_or_404(db, location_id)
    data = payload.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(location, field, value)
    db.commit()
    db.refresh(location)
    return location
