from datetime import datetime
from typing import Any


def mark_deleted(item: Any, user_id: int | None, reason: str = "solicitacao_administrativa") -> None:
    if hasattr(item, "deleted_at"):
        item.deleted_at = datetime.utcnow()
    if hasattr(item, "deleted_by"):
        item.deleted_by = user_id
    if hasattr(item, "deletion_reason"):
        item.deletion_reason = reason


def restore_deleted(item: Any) -> None:
    if hasattr(item, "deleted_at"):
        item.deleted_at = None
    if hasattr(item, "deleted_by"):
        item.deleted_by = None
    if hasattr(item, "deletion_reason"):
        item.deletion_reason = None
