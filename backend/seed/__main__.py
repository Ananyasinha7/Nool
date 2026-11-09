"""python -m backend.seed  (idempotent: upserts by natural keys)."""
from __future__ import annotations

from backend.app.db import get_sessionmaker
from backend.seed.orders import seed_orders
from backend.seed.reference import seed_reference


def main() -> None:
    with get_sessionmaker()() as s:
        ids = seed_reference(s)
        n = seed_orders(s, ids)
        s.commit()
    print(f"Seed complete: reference data + {n} orders.")


if __name__ == "__main__":
    main()
