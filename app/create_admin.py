import sys

from sqlalchemy import select

from app.core.security import hash_password
from app.database import SessionLocal
from app.models.admin import Admin

VALID_ROLES = ("superadmin", "admin")


def main() -> int:
    if len(sys.argv) not in (4, 5):
        print(
            "Utilizare: python -m app.create_admin "
            "<username> <email> <parola> [superadmin|admin]"
        )
        return 1

    username, email, password = sys.argv[1], sys.argv[2], sys.argv[3]
    role = sys.argv[4] if len(sys.argv) == 5 else "superadmin"

    if len(password) < 8:
        print("Parola trebuie sa aiba minim 8 caractere.")
        return 1
    if role not in VALID_ROLES:
        print(f"Rol invalid. Alege unul din: {', '.join(VALID_ROLES)}")
        return 1

    with SessionLocal() as db:
        admin = db.scalar(select(Admin).where(Admin.username == username))
        if admin is None:
            admin = Admin(username=username, email=email, role=role, is_active=True)
            admin.password_hash = hash_password(password)
            db.add(admin)
            action = "creat"
        else:
            admin.email = email
            admin.role = role
            admin.is_active = True
            admin.password_hash = hash_password(password)
            action = "actualizat"

        db.commit()
        db.refresh(admin)
        print(
            f"Superadmin '{admin.username}' {action} "
            f"(id={admin.id}, role={admin.role}, active={admin.is_active})."
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
