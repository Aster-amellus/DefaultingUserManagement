from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from app.models import AuditLog
from app.db.database import SessionLocal


def write_audit(db: Session, user_id: Optional[int], action: str, target_type: str, target_id: Optional[str], details: Optional[str] = None):
    log = AuditLog(user_id=user_id, action=action, target_type=target_type, target_id=target_id, details=details)
    db.add(log)


async def audit_middleware(request: Request, call_next):
    response = await call_next(request)
    # Simple coverage: log POST/PATCH/DELETE requests path
    if request.method in {"POST", "PATCH", "DELETE"}:
        try:
            user_id = None
            # Attempt to read user from state (set by auth dep) — optional
            if hasattr(request.state, "user_id"):
                user_id = request.state.user_id
        except Exception:
            user_id = None
        db: Session = SessionLocal()
        try:
            log = AuditLog(user_id=user_id, action=request.method, target_type="HTTP", target_id=str(request.url.path))
            db.add(log)
            db.commit()
        finally:
            db.close()
    return response
