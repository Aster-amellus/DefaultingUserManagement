from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func, case, text
from sqlalchemy.orm import Session
from typing import List, Dict, Tuple
from app.db.database import get_db
from app.deps import get_current_user
from app.models import Application, ApplicationType, Customer


router = APIRouter(prefix="/stats", tags=["stats"])


def _monthly_trends(db: Session, group_col, year: int) -> Tuple[Dict[str, List[int]], Dict[str, List[int]]]:
    start = datetime(year, 1, 1)
    end = datetime(year + 1, 1, 1)
    # DB-agnostic month extraction
    dialect = db.bind.dialect.name if db.bind is not None else "sqlite"
    if dialect == "sqlite":
        month_expr = func.strftime("%m", Application.reviewed_at)
    else:
        # assumes postgres
        month_expr = func.to_char(Application.reviewed_at, text("'MM'"))
    rows = (
        db.query(
            group_col.label("g"),
            month_expr.label("m"),
            func.sum(case((Application.type == ApplicationType.default.value, 1), else_=0)).label("cnt_d"),
            func.sum(case((Application.type == ApplicationType.rebirth.value, 1), else_=0)).label("cnt_r"),
        )
        .join(Customer, Application.customer_id == Customer.id)
        .filter(Application.reviewed_at >= start, Application.reviewed_at < end, Application.status == "APPROVED")
        .group_by("g", "m")
        .all()
    )
    d: Dict[str, List[int]] = {}
    r: Dict[str, List[int]] = {}
    for g, m, cnt_d, cnt_r in rows:
        gk = g or "N/A"
        if gk not in d:
            d[gk] = [0] * 12
            r[gk] = [0] * 12
        mi = int(m) - 1 if m and m.isdigit() else 0
        d[gk][mi] += int(cnt_d or 0)
        r[gk][mi] += int(cnt_r or 0)
    return d, r


@router.get("/industry")
def by_industry(year: int, detailed: bool = False, db: Session = Depends(get_db), user=Depends(get_current_user)):
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
    rows = q.all()
    base = [
        {"industry": ind or "N/A", "default_count": int(defs or 0), "rebirth_count": int(rebs or 0)}
        for ind, defs, rebs in rows
    ]
    if not detailed:
        return base
    total_defaults = sum(x[1] or 0 for x in rows)
    total_rebirths = sum(x[2] or 0 for x in rows)
    d_trend, r_trend = _monthly_trends(db, Customer.industry, year)
    enhanced = []
    for item in base:
        ind = item["industry"]
        dc = item["default_count"]
        rc = item["rebirth_count"]
        enhanced.append({
            **item,
            "default_share": (dc / total_defaults) if total_defaults else 0.0,
            "rebirth_share": (rc / total_rebirths) if total_rebirths else 0.0,
            "default_trend": d_trend.get(ind, [0]*12),
            "rebirth_trend": r_trend.get(ind, [0]*12),
        })
    return enhanced


@router.get("/region")
def by_region(year: int, detailed: bool = False, db: Session = Depends(get_db), user=Depends(get_current_user)):
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
    rows = q.all()
    base = [
        {"region": reg or "N/A", "default_count": int(defs or 0), "rebirth_count": int(rebs or 0)}
        for reg, defs, rebs in rows
    ]
    if not detailed:
        return base
    total_defaults = sum(x[1] or 0 for x in rows)
    total_rebirths = sum(x[2] or 0 for x in rows)
    d_trend, r_trend = _monthly_trends(db, Customer.region, year)
    enhanced = []
    for item in base:
        reg = item["region"]
        dc = item["default_count"]
        rc = item["rebirth_count"]
        enhanced.append({
            **item,
            "default_share": (dc / total_defaults) if total_defaults else 0.0,
            "rebirth_share": (rc / total_rebirths) if total_rebirths else 0.0,
            "default_trend": d_trend.get(reg, [0]*12),
            "rebirth_trend": r_trend.get(reg, [0]*12),
        })
    return enhanced
