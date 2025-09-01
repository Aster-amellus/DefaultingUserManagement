from datetime import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import and_
from app.db.database import get_db
from app.deps import require_role
from app.models import AuditLog, RoleEnum, User


router = APIRouter(prefix="/audit-logs", tags=["audit"])  # Admin-only


@router.get("/")
def list_audit_logs(
    db: Session = Depends(get_db),
    _=Depends(require_role(RoleEnum.admin)),
    user_id: Optional[int] = None,
    action: Optional[str] = None,
    target_type: Optional[str] = None,
    start: Optional[datetime] = None,
    end: Optional[datetime] = None,
    limit: int = 100,
):
    cond = []
    if user_id is not None:
        cond.append(AuditLog.user_id == user_id)
    if action:
        cond.append(AuditLog.action == action)
    if target_type:
        cond.append(AuditLog.target_type == target_type)
    if start:
        cond.append(AuditLog.created_at >= start)
    if end:
        cond.append(AuditLog.created_at <= end)
    q = db.query(AuditLog)
    if cond:
        q = q.filter(and_(*cond))
    logs = q.order_by(AuditLog.created_at.desc()).limit(limit).all()
    # Enrich with actor name and friendly fields expected by frontend
    out = []
    for l in logs:
        actor = None
        if l.user_id:
            u = db.get(User, l.user_id)
            actor = u.full_name or u.email if u else None
        out.append({
            "id": l.id,
            "timestamp": l.created_at.isoformat() if l.created_at else None,
            "actor": actor,
            "action": l.action,
            "resource": f"{l.target_type}:{l.target_id}" if l.target_type else l.target_id,
            "ip": getattr(l, 'ip', None),
        })
    return {"items": out}
