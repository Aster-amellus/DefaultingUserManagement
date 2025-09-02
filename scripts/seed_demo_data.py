"""
Seed demo data for the Contract Default Management system.

Usage:
  uv run python scripts/seed_demo_data.py
or
  python scripts/seed_demo_data.py

The script is idempotent: it will upsert by unique keys.
"""
from __future__ import annotations

import os
from datetime import datetime, timedelta
from random import Random

from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import SessionLocal, Base, engine
from app.models import (
    User, RoleEnum,
    Customer,
    Reason,
    Application, ApplicationStatus, ApplicationType,
    ApplicationAttachment,
)
from app.security import get_password_hash


rng = Random(42)


def ensure_schema():
    # In case alembic wasn't run, create tables for dev.
    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        pass


def ensure_seed_users(db: Session):
    def upsert(email: str, password: str, role: str, name: str):
        u = db.query(User).filter(User.email == email).first()
        if u:
            u.full_name = name
            u.role = role
            if password:
                u.hashed_password = get_password_hash(password)
            db.add(u)
        else:
            u = User(email=email, full_name=name, role=role, hashed_password=get_password_hash(password))
            db.add(u)

    upsert(settings.admin_default_email, settings.admin_default_password, RoleEnum.admin.value, "Admin")
    upsert(settings.reviewer_default_email, settings.reviewer_default_password, RoleEnum.reviewer.value, "Reviewer")
    upsert(settings.operator_default_email, settings.operator_default_password, RoleEnum.operator.value, "Operator")
    db.commit()


def ensure_reasons(db: Session):
    defaults = [
        ("DEFAULT", "6个月内技术性或资金原因导致头寸缺口2次以上", 1),
        ("DEFAULT", "6个月内成交后撤单2次以上", 2),
        ("DEFAULT", "未按合约规定支付或延期支付本金/义务（不含宽限期）", 3),
        ("DEFAULT", "关联违约触发集团成员违约", 4),
        ("DEFAULT", "发生消极债务置换或展期重组", 5),
        ("DEFAULT", "申请破产保护或法律接管", 6),
        ("DEFAULT", "在其他金融机构违约或外部评级为违约级别", 7),
    ]
    rebirths = [
        ("REBIRTH", "正常结算后解除", 1),
        ("REBIRTH", "在其他金融机构违约解除或外部评级非违约级别", 2),
        ("REBIRTH", "计提比例小于设置界限", 3),
        ("REBIRTH", "连续12个月内按时支付本金和利息", 4),
        ("REBIRTH", "偿付逾期款项且连续12个月按时支付，本息能力好转", 5),
        ("REBIRTH", "导致违约的关联集团已重生，解除关联违约", 6),
    ]
    for t, desc, order in defaults + rebirths:
        r = db.query(Reason).filter(Reason.type == t, Reason.description == desc).first()
        if r:
            r.enabled = True
            r.sort_order = order
            db.add(r)
        else:
            db.add(Reason(type=t, description=desc, enabled=True, sort_order=order))
    db.commit()


def upsert_customer(db: Session, name: str, industry: str, region: str, is_default: bool = False) -> Customer:
    c = db.query(Customer).filter(Customer.name == name).first()
    if c:
        c.industry = industry
        c.region = region
        c.is_default = is_default
        db.add(c)
        db.commit()
        db.refresh(c)
        return c
    c = Customer(name=name, industry=industry, region=region, is_default=is_default)
    db.add(c)
    db.commit()
    db.refresh(c)
    return c


def create_application(db: Session, creator: User, c: Customer, reason: Reason, a_type: str, severity: str, rating: str | None, remark: str | None, approve: bool, reviewed_by: User | None):
    app = Application(
        type=a_type,
        customer_id=c.id,
        latest_external_rating=rating,
        reason_id=reason.id,
        severity=severity,
        remark=remark,
        status=ApplicationStatus.pending.value,
        created_by=creator.id,
    )
    db.add(app)
    db.commit()
    db.refresh(app)

    # Optional dummy attachment
    if rng.random() < 0.7:
        att = ApplicationAttachment(application_id=app.id, filename="evidence.txt", url=f"/files/applications/{app.id}/evidence.txt")
        db.add(att)

    if approve and reviewed_by:
        app.status = ApplicationStatus.approved.value
        app.reviewed_by = reviewed_by.id
        app.reviewed_at = datetime.utcnow() - timedelta(days=rng.randint(0, 300))
        # Link customer default flag
        if a_type == ApplicationType.default.value:
            c.is_default = True
        else:
            c.is_default = False
        db.add(c)
        db.add(app)
    db.commit()


def main():
    ensure_schema()
    db: Session = SessionLocal()
    try:
        ensure_seed_users(db)
        ensure_reasons(db)

        # Prepare users
        admin = db.query(User).filter(User.email == settings.admin_default_email).first()
        reviewer = db.query(User).filter(User.email == settings.reviewer_default_email).first()
        operator = db.query(User).filter(User.email == settings.operator_default_email).first()

        # Create customers across industries and regions
        industries = ["制造", "能源", "科技", "金融", "交通"]
        regions = ["华东", "华南", "华北", "西南", "东北"]
        customers = []
        for i in range(15):
            name = f"客户{i+1:02d}"
            ind = industries[i % len(industries)]
            reg = regions[(i // len(industries)) % len(regions)]
            customers.append(upsert_customer(db, name, ind, reg, is_default=False))

        # Pick reasons
        default_reason = db.query(Reason).filter(Reason.type == ApplicationType.default.value).first()
        rebirth_reason = db.query(Reason).filter(Reason.type == ApplicationType.rebirth.value).first()

        # Submit a mix of DEFAULT and REBIRTH applications and approve some to generate stats
        for idx, c in enumerate(customers):
            if idx % 3 == 0:
                # DEFAULT from operator -> reviewed approved
                create_application(db, operator, c, default_reason, ApplicationType.default.value, "MEDIUM", "BBB", "现金流恶化", approve=True, reviewed_by=reviewer)
            elif idx % 3 == 1:
                # DEFAULT pending (to show pending list)
                create_application(db, operator, c, default_reason, ApplicationType.default.value, "HIGH", "BB", "多次撤单", approve=False, reviewed_by=None)
            else:
                # First mark customer as default via an approved DEFAULT if needed
                create_application(db, operator, c, default_reason, ApplicationType.default.value, "LOW", "A", "头寸缺口", approve=True, reviewed_by=reviewer)
                # Then REBIRTH to revert
                create_application(db, operator, c, rebirth_reason, ApplicationType.rebirth.value, "LOW", "A", "经营好转", approve=True, reviewed_by=reviewer)

        print("Demo data seeded successfully.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
