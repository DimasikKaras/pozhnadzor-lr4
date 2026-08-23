from sqlalchemy.orm import Session
from ..models import AuditLog

def add_audit_log(
    db: Session,
    *,
    user_id: int | None,
    action: str,
    entity: str,
    entity_id: int | None,
    ip_address: str | None,
    payload: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            entity_id=entity_id,
            ip_address=ip_address,
            payload=payload,
        )
    )
