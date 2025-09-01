from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.deps import require_role, get_current_user
from app.models import User, RoleEnum
from app.schemas import UserCreate, UserUpdate, UserOut
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


@router.get("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def get_user(user_id: int, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    return u


@router.patch("/{user_id}", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def update_user(user_id: int, payload: UserUpdate, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    if payload.full_name is not None:
        u.full_name = payload.full_name
    if payload.password:
        u.hashed_password = get_password_hash(payload.password)
    if payload.role:
        u.role = payload.role
    db.add(u)
    db.commit()
    db.refresh(u)
    return u


@router.delete("/{user_id}", dependencies=[Depends(require_role(RoleEnum.admin))])
def delete_user(user_id: int, db: Session = Depends(get_db)):
    u = db.get(User, user_id)
    if not u:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(u)
    db.commit()
    return {"ok": True}


 
