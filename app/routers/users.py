from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.deps import require_role
from app.models import User, RoleEnum
from app.schemas import UserCreate, UserOut
from app.security import get_password_hash


router = APIRouter(prefix="/users", tags=["users"])


@router.post("/", response_model=UserOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_user(payload: UserCreate, db: Session = Depends(get_db)):
    user = User(email=payload.email, full_name=payload.full_name, role=(payload.role or RoleEnum.operator.value))
    user.hashed_password = get_password_hash(payload.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/", response_model=List[UserOut], dependencies=[Depends(require_role(RoleEnum.admin))])
def list_users(db: Session = Depends(get_db)):
    return db.query(User).all()
