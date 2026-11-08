import hashlib
import logging
import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select, update
from sqlalchemy.orm import Session

from app.api.deps import (
    ensure_not_last_superadmin,
    get_current_admin,
    get_current_superadmin,
)
from app.core.config import settings
from app.core.email import send_password_reset_email
from app.core.security import create_access_token
from app.database import get_db
from app.models.admin import Admin
from app.models.invite import InviteCode
from app.models.password_reset_token import PasswordResetToken
from app.schemas.admin import (
    AdminLogin,
    AdminOut,
    ForgotPasswordRequest,
    ForgotPasswordResponse,
    PasswordChange,
    PasswordResetLinkOut,
    PasswordResetRequestOut,
    ResetPasswordRequest,
    Token,
)
from app.schemas.invite import RegisterRequest

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["auth"])


def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _password_reset_link(token: str) -> str:
    return f"{settings.frontend_url}/reset-password?token={token}"


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
    "/forgot-password",
    response_model=ForgotPasswordResponse,
    summary="Cere un link de resetare a parolei",
)
def forgot_password(
    payload: ForgotPasswordRequest,
    db: Session = Depends(get_db),
) -> ForgotPasswordResponse:
    generic_detail = (
        "Daca emailul exista, vei primi un link de resetare a parolei."
    )

    admin = db.scalar(select(Admin).where(Admin.email == payload.email))
    if admin is None or not admin.is_active:
        return ForgotPasswordResponse(detail=generic_detail)

    now = datetime.now(timezone.utc).replace(tzinfo=None)

    # Invalideaza tokenurile anterioare nefolosite.
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.admin_id == admin.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )

    raw_token = secrets.token_urlsafe(32)
    db.add(
        PasswordResetToken(
            admin_id=admin.id,
            token_hash=_hash_token(raw_token),
            expires_at=now
            + timedelta(minutes=settings.password_reset_expire_minutes),
        )
    )
    db.commit()

    reset_link = _password_reset_link(raw_token)
    sent = send_password_reset_email(admin.email, reset_link)
    if not sent:
        logger.warning(
            "Link de resetare parola pentru %s: %s", admin.email, reset_link
        )

    return ForgotPasswordResponse(
        detail=generic_detail,
        reset_link=reset_link if settings.return_reset_link else None,
    )


@router.post(
    "/reset-password",
    summary="Reseteaza parola folosind tokenul din link",
)
def reset_password(
    payload: ResetPasswordRequest,
    db: Session = Depends(get_db),
) -> dict[str, str]:
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    token = db.scalar(
        select(PasswordResetToken).where(
            PasswordResetToken.token_hash == _hash_token(payload.token)
        )
    )
    if token is None or token.used_at is not None or token.expires_at < now:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link de resetare invalid sau expirat",
        )

    admin = db.get(Admin, token.admin_id)
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Link de resetare invalid sau expirat",
        )

    admin.set_password(payload.new_password)
    token.used_at = now
    db.commit()

    return {"detail": "Parola a fost resetata cu succes"}


@router.get(
    "/password-reset-requests",
    response_model=list[PasswordResetRequestOut],
    summary="Cereri de resetare parola (superadmin)",
)
def list_password_reset_requests(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_superadmin),
) -> list[PasswordResetRequestOut]:
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    rows = db.execute(
        select(PasswordResetToken, Admin)
        .join(Admin, Admin.id == PasswordResetToken.admin_id)
        .where(
            PasswordResetToken.used_at.is_(None),
            Admin.is_active.is_(True),
        )
        .order_by(PasswordResetToken.id.desc())
    ).all()

    seen: set[int] = set()
    requests: list[PasswordResetRequestOut] = []
    for token, admin in rows:
        if admin.id in seen:
            continue
        seen.add(admin.id)
        requests.append(
            PasswordResetRequestOut(
                admin_id=admin.id,
                username=admin.username,
                email=admin.email,
                requested_at=token.created_at,
                expires_at=token.expires_at,
                expired=token.expires_at < now,
            )
        )
    return requests


@router.post(
    "/password-reset-requests/{admin_id}",
    response_model=PasswordResetLinkOut,
    summary="Genereaza un link de resetare pentru un admin (superadmin)",
)
def generate_password_reset_link(
    admin_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_superadmin),
) -> PasswordResetLinkOut:
    admin = db.get(Admin, admin_id)
    if admin is None or not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Adminul nu a fost gasit",
        )

    now = datetime.now(timezone.utc).replace(tzinfo=None)
    db.execute(
        update(PasswordResetToken)
        .where(
            PasswordResetToken.admin_id == admin.id,
            PasswordResetToken.used_at.is_(None),
        )
        .values(used_at=now)
    )

    raw_token = secrets.token_urlsafe(32)
    token = PasswordResetToken(
        admin_id=admin.id,
        token_hash=_hash_token(raw_token),
        expires_at=now + timedelta(minutes=settings.password_reset_expire_minutes),
    )
    db.add(token)
    db.commit()
    db.refresh(token)

    return PasswordResetLinkOut(
        admin_id=admin.id,
        username=admin.username,
        email=admin.email,
        token=raw_token,
        reset_link=_password_reset_link(raw_token),
        expires_at=token.expires_at,
    )


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
