import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.admin import Admin


def main() -> int:
    if len(sys.argv) != 3:
        print("Utilizare: python -m app.set_password <username_sau_email> <parola_noua>")
        return 1

    identifier, new_password = sys.argv[1], sys.argv[2]
    if len(new_password) < 8:
        print("Parola trebuie sa aiba minim 8 caractere.")
        return 1

    with SessionLocal() as db:
        admin = db.scalar(
            select(Admin).where(
                (Admin.username == identifier) | (Admin.email == identifier)
            )
        )
        if admin is None:
            print(f"Adminul '{identifier}' nu a fost gasit.")
            return 1

        admin.password_hash = hash_password(new_password)
        db.commit()
        print(f"Parola pentru '{admin.username}' a fost actualizata.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
