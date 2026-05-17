import logging
from typing import Any

from studio.models import AuditLog

logger = logging.getLogger("studio.audit")


def audit(user, action: str, resource_type: str = "", resource_id: str = "", metadata: dict | None = None):
    meta = metadata or {}
    try:
        AuditLog.objects.create(
            user=user if user and user.is_authenticated else None,
            action=action,
            resource_type=resource_type[:64],
            resource_id=str(resource_id)[:64] if resource_id else "",
            metadata=meta,
        )
    except Exception:
        logger.exception("audit log failed action=%s", action)
    logger.info(
        "audit action=%s user=%s resource=%s:%s",
        action,
        getattr(user, "id", None),
        resource_type,
        resource_id,
    )
