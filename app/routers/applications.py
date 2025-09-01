from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.database import get_db
from app.deps import get_current_user, require_role
from app.models import (
    Application,
    ApplicationStatus,
    ApplicationType,
    ApplicationAttachment,
    Customer,
    Reason,
    RoleEnum,
    Notification,
)
from app.schemas import ApplicationCreate, ApplicationOut, ReviewAction
from app.audit import write_audit
from app.storage import Storage


router = APIRouter(prefix="/applications", tags=["applications"])


def _validate_business_rules(db: Session, payload: ApplicationCreate):
    customer = db.get(Customer, payload.customer_id)
    if not customer:
        raise HTTPException(status_code=400, detail="Customer not found")
    reason = db.get(Reason, payload.reason_id)
    if not reason or not reason.enabled:
        raise HTTPException(status_code=400, detail="Invalid reason")
    if payload.type == ApplicationType.default.value:
        if customer.is_default:
            raise HTTPException(status_code=400, detail="Customer already default")
    elif payload.type == ApplicationType.rebirth.value:
        if not customer.is_default:
            raise HTTPException(status_code=400, detail="Customer is not default")
    else:
        raise HTTPException(status_code=400, detail="Invalid application type")


@router.post("/", response_model=ApplicationOut, dependencies=[Depends(require_role(RoleEnum.operator, RoleEnum.admin))])
def create_application(
    payload: ApplicationCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
):
    _validate_business_rules(db, payload)
    app = Application(
        type=payload.type,
        customer_id=payload.customer_id,
        latest_external_rating=payload.latest_external_rating,
        reason_id=payload.reason_id,
        severity=payload.severity,
        remark=payload.remark,
        status=ApplicationStatus.pending.value,
        created_by=user.id,
    )
    db.add(app)
    write_audit(db, user.id, "CREATE", "Application", None, f"type={payload.type}")
    db.commit()
    db.refresh(app)
    return app


@router.get("/", response_model=List[ApplicationOut])
def list_applications(
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
    customer_name: Optional[str] = None,
    status: Optional[str] = None,
):
    q = db.query(Application)
    if customer_name:
        q = q.join(Customer).filter(Customer.name.ilike(f"%{customer_name}%"))
    if status:
        q = q.filter(Application.status == status)
    return q.order_by(Application.created_at.desc()).all()


@router.post("/{app_id}/attachments")
def upload_attachment(app_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), user=Depends(get_current_user)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Application not found")
    content = file.file.read()
    key = f"applications/{app_id}/{file.filename}"
    storage = Storage()
    url = storage.save(key, content, file.content_type)
    att = ApplicationAttachment(application_id=app_id, filename=file.filename, url=url)
    db.add(att)
    write_audit(db, user.id, "UPLOAD", "ApplicationAttachment", str(app_id), file.filename)
    db.commit()
    return {"ok": True}


@router.get("/{app_id}/attachments/presign")
def get_presigned_attachment(app_id: int, filename: str, db: Session = Depends(get_db), user=Depends(get_current_user)):
    # return a presigned url (only for s3 backend); for local storage, return direct path
    key = f"applications/{app_id}/{filename}"
    storage = Storage()
    url = storage.get_presigned_url(key)
    if url:
        return {"url": url}
    return {"url": f"/files/{key}"}


@router.post("/{app_id}/review", response_model=ApplicationOut, dependencies=[Depends(require_role(RoleEnum.reviewer, RoleEnum.admin))])
def review_application(app_id: int, payload: ReviewAction, db: Session = Depends(get_db), reviewer=Depends(get_current_user)):
    app = db.get(Application, app_id)
    if not app:
        raise HTTPException(status_code=404, detail="Not found")
    if app.status != ApplicationStatus.pending.value:
        raise HTTPException(status_code=400, detail="Not pending")

    if payload.decision not in (ApplicationStatus.approved.value, ApplicationStatus.rejected.value):
        raise HTTPException(status_code=400, detail="Invalid decision")

    # Transition and side effects in one transaction
    app.status = payload.decision
    app.reviewed_by = reviewer.id
    app.reviewed_at = datetime.utcnow()
    db.add(app)

    customer = db.get(Customer, app.customer_id)
    if payload.decision == ApplicationStatus.approved.value:
        if app.type == ApplicationType.default.value:
            customer.is_default = True
        elif app.type == ApplicationType.rebirth.value:
            customer.is_default = False
        db.add(customer)

    # Notify applicant
    n = Notification(user_id=app.created_by, content=f"Application #{app.id} {payload.decision}")
    db.add(n)

    write_audit(db, reviewer.id, "REVIEW", "Application", str(app.id), payload.decision)
    db.commit()
    db.refresh(app)
    return app
