from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from sqlalchemy import text
from app.core.config import settings
from app.db.database import Base, engine
from app.routers import auth, users, customers, reasons, applications, notifications, stats
from app.routers import audit_logs
from app.audit import audit_middleware


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
