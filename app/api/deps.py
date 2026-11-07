from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.core.security import decode_access_token
from app.database import get_db
from app.models.admin import Admin

bearer_scheme = HTTPBearer(auto_error=False)

_credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Token invalid sau expirat",
    headers={"WWW-Authenticate": "Bearer"},
)


def get_current_admin(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> Admin:
    if credentials is None or not credentials.credentials:
        raise _credentials_exception

    payload = decode_access_token(credentials.credentials)
    if not payload or not payload.get("sub"):
        raise _credentials_exception

    admin = db.get(Admin, int(payload["sub"]))
    if admin is None or not admin.is_active:
        raise _credentials_exception

    return admin


def get_current_superadmin(
    current_admin: Admin = Depends(get_current_admin),
) -> Admin:
    if current_admin.role != "superadmin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Necesita rol de superadmin",
        )
    return current_admin


def active_superadmin_count(db: Session) -> int:
    return db.scalar(
        select(func.count())
        .select_from(Admin)
        .where(Admin.role == "superadmin", Admin.is_active.is_(True))
    ) or 0


def ensure_not_last_superadmin(db: Session, admin: Admin) -> None:
    if admin.role == "superadmin" and admin.is_active and active_superadmin_count(db) <= 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Nu poti dezactiva sau sterge ultimul superadmin activ",
        )
