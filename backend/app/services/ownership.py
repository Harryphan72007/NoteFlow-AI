from __future__ import annotations

from fastapi import HTTPException


def require_customer_access(record_customer_id: str | None, requested_customer_id: str | None) -> None:
    """Enforce the project's current customer-context ownership check.

    This is not a replacement for authentication. It prevents cross-customer
    access whenever the caller supplies a customer context.
    """
    if requested_customer_id is None:
        return
    if record_customer_id != requested_customer_id:
        raise HTTPException(status_code=403, detail="Access denied")
