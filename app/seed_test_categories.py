from sqlalchemy import select

from app.database import SessionLocal
from app.models.category import Category

TEST_CATEGORIES = [
    "Parcuri",
    "Clădiri istorice",
    "Muzee",
    "Biserici",
    "Monumente",
    "Piețe",
    "Poduri",
    "Statui",
    "Turnuri",
    "Galerii de artă",
    "Cafenele",
    "Restaurante",
]


def main() -> None:
    with SessionLocal() as db:
        existing = set(db.scalars(select(Category.name)))
        added = 0
        for name in TEST_CATEGORIES:
            if name in existing:
                continue
            db.add(Category(name=name))
            added += 1
        db.commit()
        print(f"[seed_test_categories] Categorii noi adăugate: {added}")


if __name__ == "__main__":
    main()
