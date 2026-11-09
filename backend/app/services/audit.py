from __future__ import annotations

from sqlalchemy.orm import Session

from backend.app.models import AuditLog


def audit(session: Session, actor_id: str | None, action: str, entity: str, entity_id: str, **meta: object) -> None:
    session.add(AuditLog(actor_id=actor_id, action=action, entity=entity, entity_id=entity_id,
                         meta={k: str(v) for k, v in meta.items()}))
