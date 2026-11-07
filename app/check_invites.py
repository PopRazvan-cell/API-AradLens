from datetime import datetime, timezone

from sqlalchemy import select

from app.database import SessionLocal
from app.models.invite import InviteCode


def main() -> int:
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    print(f"now (UTC, naive) = {now.isoformat()}")

    with SessionLocal() as db:
        invites = list(db.scalars(select(InviteCode).order_by(InviteCode.id.desc())))
        print(f"Coduri gasite: {len(invites)}")
        for inv in invites:
            expired = (
                inv.expires_at is not None and inv.expires_at < now
            )
            print(
                f"  id={inv.id} role={inv.role} revoked={inv.is_revoked} "
                f"used_at={inv.used_at} expires_at={inv.expires_at} "
                f"-> expired={expired}"
            )
            print(f"     code={inv.code}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
