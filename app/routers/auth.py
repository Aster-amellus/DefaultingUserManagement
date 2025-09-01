from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models import User, RoleEnum
from app.security import verify_password, get_password_hash, create_access_token
from app.schemas import Token
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])


def ensure_admin(db: Session):
    admin = db.query(User).filter(User.email == settings.admin_default_email).first()
    if not admin:
        admin = User(
            email=settings.admin_default_email,
            full_name="Admin",
            hashed_password=get_password_hash(settings.admin_default_password),
            role=RoleEnum.admin.value,
        )
        db.add(admin)
        db.commit()


@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    ensure_admin(db)
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
    token = create_access_token(user.email)
    return Token(access_token=token)
