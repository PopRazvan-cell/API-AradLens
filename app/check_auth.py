import sys
from urllib.parse import urlsplit, urlunsplit

from sqlalchemy import select

from app.core.security import verify_password
from app.database import DATABASE_URL, SessionLocal
from app.models.admin import Admin


def _masked_url(url: str) -> str:
    parts = urlsplit(url)
    if parts.password:
        netloc = f"{parts.username}:***@{parts.hostname}"
        if parts.port:
            netloc += f":{parts.port}"
        return urlunsplit(parts._replace(netloc=netloc))
    return url


def main() -> int:
    print(f"DB: {_masked_url(DATABASE_URL)}")

    with SessionLocal() as db:
        admins = list(db.scalars(select(Admin).order_by(Admin.id)))
        print(f"Admini gasiti: {len(admins)}")
        for a in admins:
            h = a.password_hash or ""
            print(
                f"  id={a.id} user={a.username!r} email={a.email!r} "
                f"role={a.role} active={a.is_active} "
                f"hash_prefix={h[:4]!r} hash_len={len(h)}"
            )

        if len(sys.argv) == 3:
            identifier, password = sys.argv[1], sys.argv[2]
            admin = db.scalar(
                select(Admin).where(
                    (Admin.username == identifier) | (Admin.email == identifier)
                )
            )
            if admin is None:
                print(f"Admin '{identifier}' NU exista in baza de date.")
            else:
                result = verify_password(password, admin.password_hash)
                print(f"verify_password('{identifier}', ...) -> {result}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
