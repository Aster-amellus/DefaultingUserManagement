from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.deps import require_role, get_current_user
from app.models import Customer, RoleEnum
from app.schemas import CustomerCreate, CustomerUpdate, CustomerOut


router = APIRouter(prefix="/customers", tags=["customers"])


@router.post("/", response_model=CustomerOut, dependencies=[Depends(require_role(RoleEnum.admin, RoleEnum.operator))])
def create_customer(payload: CustomerCreate, db: Session = Depends(get_db)):
    exists = db.query(Customer).filter(Customer.name == payload.name).first()
    if exists:
        # idempotent: update basic fields if provided and return
        if payload.industry is not None:
            exists.industry = payload.industry
        if payload.region is not None:
            exists.region = payload.region
        db.commit()
        db.refresh(exists)
        return exists
    c = Customer(name=payload.name, industry=payload.industry, region=payload.region)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.get("/", response_model=List[CustomerOut])
def list_customers(db: Session = Depends(get_db), user=Depends(get_current_user)):
    return db.query(Customer).all()


@router.get("/{customer_id}", response_model=CustomerOut)
def get_customer(customer_id: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    return c


@router.patch("/{customer_id}", response_model=CustomerOut, dependencies=[Depends(require_role(RoleEnum.admin, RoleEnum.operator))])
def update_customer(customer_id: int, payload: CustomerUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    data = payload.model_dump(exclude_none=True)
    # Only Admin can rename customer name to avoid collisions
    if "name" in data and user.role != RoleEnum.admin.value:
        del data["name"]
    # if renaming, ensure uniqueness
    if "name" in data:
        exists = db.query(Customer).filter(Customer.name == data["name"], Customer.id != customer_id).first()
        if exists:
            raise HTTPException(status_code=400, detail="Customer name already exists")
    for k, v in data.items():
        setattr(c, k, v)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


@router.delete("/{customer_id}", dependencies=[Depends(require_role(RoleEnum.admin))])
def delete_customer(customer_id: int, db: Session = Depends(get_db)):
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404, detail="Not found")
    db.delete(c)
    db.commit()
    return {"ok": True}
