from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_admin
from app.database import get_db
from app.models.admin import Admin
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryOut, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


def _get_or_404(db: Session, category_id: int) -> Category:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria nu a fost găsită",
        )
    return category


@router.get("", response_model=list[CategoryOut], summary="Lista categoriilor")
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)))


@router.get("/{category_id}", response_model=CategoryOut, summary="Detalii categorie")
def get_category(category_id: int, db: Session = Depends(get_db)) -> Category:
    return _get_or_404(db, category_id)


@router.post(
    "",
    response_model=CategoryOut,
    status_code=status.HTTP_201_CREATED,
    summary="Adauga categorie",
)
def create_category(
    payload: CategoryCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Category:
    duplicate = db.scalar(select(Category).where(Category.name == payload.name))
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Categoria există deja",
        )

    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.put(
    "/{category_id}",
    response_model=CategoryOut,
    summary="Redenumeste categorie",
)
def update_category(
    category_id: int,
    payload: CategoryUpdate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Category:
    category = _get_or_404(db, category_id)

    duplicate = db.scalar(
        select(Category).where(
            Category.name == payload.name,
            Category.id != category_id,
        )
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Categoria există deja",
        )

    category.name = payload.name
    db.commit()
    db.refresh(category)
    return category


@router.delete(
    "/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    response_class=Response,
    summary="Sterge categorie",
)
def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Response:
    category = _get_or_404(db, category_id)
    db.delete(category)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)
