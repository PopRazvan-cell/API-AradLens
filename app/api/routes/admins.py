from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import (
    ensure_not_last_superadmin,
    get_current_admin,
    get_current_superadmin,
)
from app.database import get_db
from app.models.admin import Admin
from app.schemas.admin import AdminCreate, AdminOut, AdminSelfUpdate, AdminUpdate

router = APIRouter(prefix="/admins", tags=["admins"])


def _get_or_404(db: Session, admin_id: int) -> Admin:
    admin = db.get(Admin, admin_id)
    if admin is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adminul nu a fost gasit",
        )
    return admin


@router.get("", response_model=list[AdminOut], summary="Lista admini")
def list_admins(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> list[Admin]:
    return list(db.scalars(select(Admin).order_by(Admin.id)))


@router.get("/{admin_id}", response_model=AdminOut, summary="Detalii admin")
def get_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_admin),
) -> Admin:
    return _get_or_404(db, admin_id)


@router.post(
    "",
    response_model=AdminOut,
    status_code=status.HTTP_201_CREATED,
    summary="Creeaza admin",
)
def create_admin(
    payload: AdminCreate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_superadmin),
) -> Admin:
    duplicate = db.scalar(
        select(Admin).where(
            or_(Admin.username == payload.username, Admin.email == payload.email)
        )
    )
    if duplicate is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username sau email deja folosit",
        )

    admin = Admin(
        username=payload.username,
        email=payload.email,
        role=payload.role,
        is_active=payload.is_active,
    )
    admin.set_password(payload.password)
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@router.patch(
    "/me",
    response_model=AdminOut,
    summary="Actualizeaza propriul cont",
)
def update_own_admin(
    payload: AdminSelfUpdate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    if not current_admin.verify_password(payload.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parola veche este incorecta",
        )

    data = payload.model_dump(exclude_unset=True)

    new_username = data.get("username")
    new_email = data.get("email")

    if new_username or new_email:
        filters = []
        if new_username:
            filters.append(Admin.username == new_username)
        if new_email:
            filters.append(Admin.email == new_email)

        duplicate = db.scalar(
            select(Admin).where(
                or_(*filters),
                Admin.id != current_admin.id,
            )
        )
        if duplicate is not None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Username sau email deja folosit",
            )

    if new_username:
        current_admin.username = new_username
    if new_email:
        current_admin.email = new_email

    db.commit()
    db.refresh(current_admin)
    return current_admin


@router.put("/{admin_id}", response_model=AdminOut, summary="Actualizeaza admin")
def update_admin(
    admin_id: int,
    payload: AdminUpdate,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_superadmin),
) -> Admin:
    admin = _get_or_404(db, admin_id)
    data = payload.model_dump(exclude_unset=True)

    deactivating = data.get("is_active") is False and admin.is_active
    demoting = data.get("role") == "admin" and admin.role == "superadmin"
    if deactivating or demoting:
        ensure_not_last_superadmin(db, admin)

    if data.get("role") is not None:
        admin.role = data["role"]
    if data.get("is_active") is not None:
        admin.is_active = data["is_active"]

    db.commit()
    db.refresh(admin)
    return admin


@router.delete(
    "/{admin_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Sterge admin",
)
def delete_admin(
    admin_id: int,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_superadmin),
) -> None:
    if current_admin.id == admin_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nu iti poti sterge propriul cont",
        )

    admin = _get_or_404(db, admin_id)
    ensure_not_last_superadmin(db, admin)
    db.delete(admin)
    db.commit()
