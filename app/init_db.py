import os
import time

from sqlalchemy import inspect, select, text
from sqlalchemy.exc import OperationalError

from app.database import Base, SessionLocal, engine
from app.models import Admin, InviteCode, Location, LocationImage, Tour, TourLocation  # noqa: F401

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@aradlens.ro")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "Admin@123")

LOCATIONS_SEED = [
    {
        "name": "Turnul de Apă",
        "latitude": 46.1696614,
        "longitude": 21.3080284,
        "description": "Turnul de apă din Arad, monument industrial.",
    },
    {
        "name": "Palatul Cultural",
        "latitude": 46.1742213,
        "longitude": 21.3207016,
        "description": "Palatul Cultural din Arad, sediul Filarmonicii.",
    },
    {
        "name": "Primăria",
        "latitude": 46.1753711,
        "longitude": 21.3192954,
        "description": "Primăria Municipiului Arad, Bd. Revoluției 75.",
    },
    {
        "name": "Teatrul Slavici",
        "latitude": 46.1711220,
        "longitude": 21.3157873,
        "description": "Teatrul Clasic Ioan Slavici.",
    },
    {
        "name": "Catedrala Veche",
        "latitude": 46.1704803,
        "longitude": 21.3119299,
        "description": "Catedrala Nașterea Sfântului Ioan Botezătorul.",
    },
]


def wait_for_db(max_attempts: int = 30, delay: float = 2.0) -> None:
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect():
                return
        except OperationalError:
            print(f"[init_db] Baza de date nu e disponibila ({attempt}/{max_attempts})...")
            time.sleep(delay)
    raise RuntimeError("Baza de date nu a devenit disponibila la timp.")


def seed_admin() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(Admin).where(Admin.username == ADMIN_USERNAME))
        if existing is not None:
            print(f"[init_db] Admin '{ADMIN_USERNAME}' exista deja, se sare peste.")
            return

        admin = Admin(
            username=ADMIN_USERNAME,
            email=ADMIN_EMAIL,
            role="superadmin",
            is_active=True,
        )
        admin.set_password(ADMIN_PASSWORD)
        db.add(admin)
        db.commit()
        print(f"[init_db] Admin '{ADMIN_USERNAME}' a fost creat.")


def ensure_schema() -> None:
    inspector = inspect(engine)
    if "locations" not in inspector.get_table_names():
        return

    columns = {col["name"] for col in inspector.get_columns("locations")}
    if "image" not in columns:
        with engine.begin() as conn:
            conn.execute(
                text("ALTER TABLE locations ADD COLUMN image VARCHAR(500) NULL")
            )
        print("[init_db] Coloana 'image' a fost adaugata la tabela locations.")


def seed_locations() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(Location).limit(1))
        if existing is not None:
            print("[init_db] Locațiile există deja, se sare peste.")
            return

        db.add_all([Location(**data) for data in LOCATIONS_SEED])
        db.commit()
        print(f"[init_db] Au fost adăugate {len(LOCATIONS_SEED)} locații.")


def seed_tour() -> None:
    with SessionLocal() as db:
        existing = db.scalar(select(Tour).limit(1))
        if existing is not None:
            print("[init_db] Tururile există deja, se sare peste.")
            return

        location_ids = list(
            db.scalars(select(Location.id).order_by(Location.id))
        )
        if not location_ids:
            print("[init_db] Nu există locații pentru turul demonstrativ.")
            return

        tour = Tour(
            name="Turul Centrului",
            description="Traseu demonstrativ prin punctele de interes existente.",
        )
        tour.links = [
            TourLocation(location_id=location_id, position=position)
            for position, location_id in enumerate(location_ids, start=1)
        ]
        db.add(tour)
        db.commit()
        print(
            f"[init_db] Tur demonstrativ creat cu {len(location_ids)} locații: "
            f"{location_ids}."
        )


def main() -> None:
    wait_for_db()
    Base.metadata.create_all(bind=engine)
    ensure_schema()
    seed_admin()
    seed_locations()
    seed_tour()


if __name__ == "__main__":
    main()
