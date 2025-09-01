from typing import Optional
from fastapi import Request
from sqlalchemy.orm import Session
from app.models import AuditLog, User
from app.db.database import SessionLocal
from app.security import decode_token


CN_ACTIONS = {
    "POST": "新增",
    "PATCH": "修改",
    "PUT": "修改",
    "DELETE": "删除",
    "GET": "查询",
    "LOGIN": "登录",
    "CREATE": "新增",
    "REVIEW": "审核",
    "UPLOAD": "上传附件",
}


def write_audit(db: Session, user_id: Optional[int], action: str, target_type: str, target_id: Optional[str], details: Optional[str] = None, ip: Optional[str] = None):
    label = CN_ACTIONS.get(action.upper(), action)
    log = AuditLog(user_id=user_id, action=label, target_type=target_type, target_id=target_id, details=details, ip=ip)
    db.add(log)


def _extract_user_id_from_request(request: Request, db: Session) -> Optional[int]:
    # Try from Authorization header
    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if auth and auth.lower().startswith("bearer "):
        token = auth.split(" ", 1)[1]
        email = decode_token(token)
        if email:
            u = db.query(User).filter(User.email == email).first()
            return u.id if u else None
    # Fallback: custom state
    if hasattr(request.state, "user_id"):
        return getattr(request.state, "user_id")
    return None


async def audit_middleware(request: Request, call_next):
    response = await call_next(request)
    if request.method in {"POST", "PATCH", "DELETE"}:
        db: Session = SessionLocal()
        try:
            user_id = _extract_user_id_from_request(request, db)
            ip = request.client.host if request.client else None
            path = str(request.url.path)
            write_audit(db, user_id, request.method, "HTTP", path, None, ip)
            db.commit()
        finally:
            db.close()
    return response
