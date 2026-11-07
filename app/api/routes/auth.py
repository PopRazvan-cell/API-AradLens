from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.api.deps import ensure_not_last_superadmin, get_current_admin
from app.core.config import settings
from app.core.security import create_access_token
from app.database import get_db
from app.models.admin import Admin
from app.models.invite import InviteCode
from app.schemas.admin import AdminLogin, AdminOut, PasswordChange, Token
from app.schemas.invite import RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


def _authenticate(db: Session, identifier: str, password: str) -> Admin:
    stmt = select(Admin).where(
        or_(Admin.username == identifier, Admin.email == identifier)
    )
    admin = db.scalar(stmt)

    if admin is None or not admin.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credentiale invalide",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cont dezactivat",
        )

    admin.last_login_at = datetime.now(timezone.utc).replace(tzinfo=None)
    db.commit()
    db.refresh(admin)
    return admin


def _issue_token(admin: Admin) -> Token:
    token = create_access_token(
        subject=str(admin.id),
        extra_claims={"role": admin.role, "username": admin.username},
    )
    return Token(
        access_token=token,
        expires_in=settings.access_token_expire_minutes * 60,
    )


@router.post("/login", response_model=Token, summary="Login")
def login(payload: AdminLogin, db: Session = Depends(get_db)) -> Token:
    admin = _authenticate(db, payload.username, payload.password)
    return _issue_token(admin)


@router.post(
    "/register",
    response_model=AdminOut,
    status_code=status.HTTP_201_CREATED,
    summary="Inregistrare cu cod de invitație",
)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> Admin:
    invite = db.scalar(select(InviteCode).where(InviteCode.code == payload.code))
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cod de invitație invalid",
        )
    if invite.is_revoked:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cod de invitație revocat",
        )
    if invite.used_at is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cod de invitație deja folosit",
        )
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    if invite.expires_at is not None and invite.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cod de invitație expirat",
        )

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
        role=invite.role,
        is_active=True,
    )
    admin.set_password(payload.password)
    db.add(admin)
    db.flush()

    invite.used_at = now
    invite.used_by_id = admin.id

    db.commit()
    db.refresh(admin)
    return admin


@router.get("/me", response_model=AdminOut, summary="Admin autentificat")
def read_me(current_admin: Admin = Depends(get_current_admin)) -> Admin:
    return current_admin


@router.post(
    "/deactivate",
    summary="Dezactiveaza propriul cont (soft)",
)
def deactivate_self(
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> dict[str, str]:
    ensure_not_last_superadmin(db, current_admin)
    current_admin.is_active = False
    db.commit()
    return {"detail": "Contul a fost dezactivat"}


@router.post("/change-password", response_model=AdminOut, summary="Schimba parola adminului autentificat")
def change_password(
    payload: PasswordChange,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    if not current_admin.verify_password(payload.old_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parola actuala este incorecta",
        )
    if payload.old_password == payload.new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Parola noua trebuie sa difere de cea actuala",
        )

    current_admin.set_password(payload.new_password)
    db.commit()
    db.refresh(current_admin)
    return current_admin
