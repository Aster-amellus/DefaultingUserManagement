from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.deps import require_role, get_current_user
from app.models import User, RoleEnum
from app.schemas import UserCreate, UserOut
from app.security import get_password_hash


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        # idempotent: update password/role/full_name if provided
        if payload.full_name:
            existing.full_name = payload.full_name
        if payload.password:
            existing.hashed_password = get_password_hash(payload.password)
        if payload.role:
            existing.role = payload.role
        db.commit()
        db.refresh(existing)
        return existing
    new_user = User(email=payload.email, full_name=payload.full_name, role=(payload.role or RoleEnum.operator.value))
    new_user.hashed_password = get_password_hash(payload.password)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.get("/", response_model=List[UserOut], dependencies=[Depends(require_role(RoleEnum.admin))])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)):
    return user
