from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, case
from sqlalchemy.orm import Session
from typing import List
from app.db.database import get_db
from app.deps import get_current_user
from app.models import Application, ApplicationType, Customer


router = APIRouter(prefix="/stats", tags=["stats"])


@router.get("/industry")
def by_industry(year: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    q = (
        db.query(
            Customer.industry,
            func.sum(case((Application.type == ApplicationType.default.value, 1), else_=0)).label("defaults"),
            func.sum(case((Application.type == ApplicationType.rebirth.value, 1), else_=0)).label("rebirths"),
        )
        .join(Application, Application.customer_id == Customer.id)
        .filter(Application.reviewed_at >= start, Application.reviewed_at < end, Application.status == "APPROVED")
        .group_by(Customer.industry)
    )
    return [
        {"industry": ind or "N/A", "default_count": int(defs or 0), "rebirth_count": int(rebs or 0)}
        for ind, defs, rebs in q.all()
    ]


@router.get("/region")
def by_region(year: int, db: Session = Depends(get_db), user=Depends(get_current_user)):
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    q = (
        db.query(
            Customer.region,
            func.sum(case((Application.type == ApplicationType.default.value, 1), else_=0)).label("defaults"),
            func.sum(case((Application.type == ApplicationType.rebirth.value, 1), else_=0)).label("rebirths"),
        )
        .join(Application, Application.customer_id == Customer.id)
        .filter(Application.reviewed_at >= start, Application.reviewed_at < end, Application.status == "APPROVED")
        .group_by(Customer.region)
    )
    return [
        {"region": reg or "N/A", "default_count": int(defs or 0), "rebirth_count": int(rebs or 0)}
        for reg, defs, rebs in q.all()
    ]
