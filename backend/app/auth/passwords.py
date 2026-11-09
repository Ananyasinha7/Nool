"""bcrypt hashing (cost 10-12, Doc3 section 12)."""
from __future__ import annotations

import bcrypt

_COST = 10
# A real hash to compare against when the username is unknown, so response time
# does not reveal which usernames exist.
_DUMMY = bcrypt.hashpw(b"not-a-real-password", bcrypt.gensalt(rounds=_COST)).decode()


def hash_password(secret: str) -> str:
    return bcrypt.hashpw(secret.encode(), bcrypt.gensalt(rounds=_COST)).decode()


def verify_password(secret: str, hashed: str | None) -> bool:
    target = hashed or _DUMMY
    try:
        ok = bcrypt.checkpw(secret.encode(), target.encode())
    except ValueError:
        return False
    return ok and hashed is not None
