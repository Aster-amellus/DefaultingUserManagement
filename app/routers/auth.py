from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User, RoleEnum
from app.security import verify_password, get_password_hash, create_access_token
from app.schemas import Token
from app.core.config import settings
from app.audit import write_audit
from fastapi import Request

router = APIRouter(prefix="/auth", tags=["auth"])


def ensure_seed_users(db: Session):
    # Admin
    if not db.query(User).filter(User.email == settings.admin_default_email).first():
        db.add(User(
            email=settings.admin_default_email,
            full_name="Admin",
            hashed_password=get_password_hash(settings.admin_default_password),
            role=RoleEnum.admin.value,
        ))
    # Reviewer
    if not db.query(User).filter(User.email == settings.reviewer_default_email).first():
        db.add(User(
            email=settings.reviewer_default_email,
            full_name="Reviewer",
            hashed_password=get_password_hash(settings.reviewer_default_password),
            role=RoleEnum.reviewer.value,
        ))
    # Operator
    if not db.query(User).filter(User.email == settings.operator_default_email).first():
        db.add(User(
            email=settings.operator_default_email,
            full_name="Operator",
            hashed_password=get_password_hash(settings.operator_default_password),
            role=RoleEnum.operator.value,
        ))
    db.commit()


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db), request: Request = None):
    ensure_seed_users(db)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.email)
    # Audit login
    ip = request.client.host if request and request.client else None
    write_audit(db, user.id, "LOGIN", "User", str(user.id), None, ip)
    db.commit()
    return Token(access_token=token)
