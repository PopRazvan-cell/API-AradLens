import secrets
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_superadmin
from app.database import get_db
from app.models.admin import Admin
from app.models.invite import InviteCode
from app.schemas.invite import InviteCreate, InviteOut

router = APIRouter(prefix="/invites", tags=["invites"])


def _get_or_404(db: Session, invite_id: int) -> InviteCode:
    invite = db.get(InviteCode, invite_id)
    if invite is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Codul nu a fost gasit",
        )
    return invite


@router.post(
    "",
    response_model=InviteOut,
    status_code=status.HTTP_201_CREATED,
    summary="Genereaza cod de invitație (admin/superadmin)",
)
def create_invite(
    payload: InviteCreate,
    db: Session = Depends(get_db),
    current_admin: Admin = Depends(get_current_superadmin),
) -> InviteCode:
    expires_at = None
    if payload.expires_in_minutes:
        expires_at = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(
            minutes=payload.expires_in_minutes
        )

    invite = InviteCode(
        code=secrets.token_urlsafe(24),
        role=payload.role,
        created_by_id=current_admin.id,
        expires_at=expires_at,
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)
    return invite


@router.get("", response_model=list[InviteOut], summary="Lista coduri de invitație")
def list_invites(
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_superadmin),
) -> list[InviteCode]:
    return list(db.scalars(select(InviteCode).order_by(InviteCode.id.desc())))


@router.delete(
    "/{invite_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Revoca cod de invitație",
)
def revoke_invite(
    invite_id: int,
    db: Session = Depends(get_db),
    _: Admin = Depends(get_current_superadmin),
) -> None:
    invite = _get_or_404(db, invite_id)
    invite.is_revoked = True
    db.commit()
