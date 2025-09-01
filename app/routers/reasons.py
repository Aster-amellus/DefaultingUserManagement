from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.deps import require_role, get_current_user
from app.models import Reason, RoleEnum
from app.schemas import ReasonCreate, ReasonOut


router = APIRouter(prefix="/reasons", tags=["reasons"])


@router.post("/", response_model=ReasonOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def create_reason(payload: ReasonCreate, db: Session = Depends(get_db)):
    r = Reason(type=payload.type, description=payload.description, enabled=payload.enabled, sort_order=payload.sort_order)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.get("/", response_model=List[ReasonOut])
def list_reasons(db: Session = Depends(get_db), user=Depends(get_current_user), type: Optional[str] = None):
    q = db.query(Reason)
    if type:
        q = q.filter(Reason.type == type)
    return q.order_by(Reason.sort_order).all()


@router.patch("/{rid}", response_model=ReasonOut, dependencies=[Depends(require_role(RoleEnum.admin))])
def update_reason(rid: int, payload: ReasonCreate, db: Session = Depends(get_db)):
    r = db.get(Reason, rid)
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    for k, v in payload.model_dump().items():
        setattr(r, k, v)
    db.add(r)
    db.commit()
    db.refresh(r)
    return r


@router.delete("/{rid}", dependencies=[Depends(require_role(RoleEnum.admin))])
def delete_reason(rid: int, db: Session = Depends(get_db)):
    r = db.get(Reason, rid)
    if not r:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(r)
    db.commit()
    return {"ok": True}
