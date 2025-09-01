from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import text
from sqlalchemy.orm import Session
from app.core.config import settings
from app.db.database import Base, engine
from app.routers import auth, users, customers, reasons, applications, notifications, stats
from app.routers import audit_logs
from app.audit import audit_middleware
from app.models import Reason


app = FastAPI(title=settings.app_name)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.middleware("http")(audit_middleware)


@app.on_event("startup")
def on_startup():
    # Run alembic migrations if available; fallback to metadata create_all for dev only
    try:
        import subprocess, os
        if os.path.exists("alembic"):
            subprocess.run(["alembic", "upgrade", "head"], check=True)
    except Exception:
        Base.metadata.create_all(bind=engine)
    # Seed default reasons if empty (idempotent)
    try:
        session = Session(bind=engine)
        if session.query(Reason).count() == 0:
            default_reasons = [
                ("DEFAULT", "6个月内，交易对手技术性或资金等原因，给当天结算带来头寸缺口2次以上", 1),
                ("DEFAULT", "6个月内因各种原因导致成交后撤单2次以上", 2),
                ("DEFAULT", "未能按合约规定支付或延期支付本金或其他义务（不含宽限期）", 3),
                ("DEFAULT", "关联违约触发集团成员违约", 4),
                ("DEFAULT", "发生消极债务置换或展期重组", 5),
                ("DEFAULT", "申请破产保护或法律接管", 6),
                ("DEFAULT", "在其他金融机构违约或外部评级为违约级别", 7),
            ]
            rebirth_reasons = [
                ("REBIRTH", "正常结算后解除", 1),
                ("REBIRTH", "在其他金融机构违约解除或外部评级非违约级别", 2),
                ("REBIRTH", "计提比例小于设置界限", 3),
                ("REBIRTH", "连续12个月内按时支付本金和利息", 4),
                ("REBIRTH", "偿付逾期款项且连续12个月按时支付，本息能力好转", 5),
                ("REBIRTH", "导致违约的关联集团内客户已重生，解除关联违约", 6),
            ]
            for t, desc, order in default_reasons + rebirth_reasons:
                session.add(Reason(type=t, description=desc, enabled=True, sort_order=order))
            session.commit()
    except Exception:
        pass
    # Mount static files for local storage
    if settings.storage_backend.lower() == "local":
        Path(settings.local_storage_dir).mkdir(parents=True, exist_ok=True)
        app.mount("/files", StaticFiles(directory=settings.local_storage_dir), name="files")


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(customers.router)
app.include_router(reasons.router)
app.include_router(applications.router)
app.include_router(notifications.router)
app.include_router(stats.router)
app.include_router(audit_logs.router)


@app.get("/health")
def health():
    return {"status": "ok"}
