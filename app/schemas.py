from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    password: Optional[str] = None
    role: Optional[str] = None


class UserOut(BaseModel):
    id: int
    email: EmailStr
    full_name: Optional[str]
    role: str
    is_active: bool

    class Config:
        from_attributes = True


class CustomerCreate(BaseModel):
    name: str
    industry: Optional[str] = None
    region: Optional[str] = None


class CustomerUpdate(BaseModel):
    name: Optional[str] = None
    industry: Optional[str] = None
    region: Optional[str] = None
    is_default: Optional[bool] = None


class CustomerOut(BaseModel):
    id: int
    name: str
    industry: Optional[str]
    region: Optional[str]
    is_default: bool

    class Config:
        from_attributes = True


class ReasonCreate(BaseModel):
    type: str
    description: str
    enabled: bool = True
    sort_order: int = 0


class ReasonOut(BaseModel):
    id: int
    type: str
    description: str
    enabled: bool
    sort_order: int

    class Config:
        from_attributes = True


class ApplicationCreate(BaseModel):
    type: str
    customer_id: int
    latest_external_rating: Optional[str] = None
    reason_id: int
    severity: Optional[str] = None
    remark: Optional[str] = None


class ApplicationOut(BaseModel):
    id: int
    type: str
    customer_id: int
    latest_external_rating: Optional[str]
    reason_id: int
    severity: Optional[str]
    remark: Optional[str]
    status: str
    created_by: int
    reviewed_by: Optional[int]
    created_at: datetime
    reviewed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ReviewAction(BaseModel):
    decision: str  # APPROVED or REJECTED
    remark: Optional[str] = None


class ApplicationUpdate(BaseModel):
    type: Optional[str] = None
    customer_id: Optional[int] = None
    latest_external_rating: Optional[str] = None
    reason_id: Optional[int] = None
    severity: Optional[str] = None
    remark: Optional[str] = None


class NotificationOut(BaseModel):
    id: int
    content: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApplicationAttachmentOut(BaseModel):
    id: int
    filename: str
    url: str
    uploaded_at: datetime

    class Config:
        from_attributes = True


class ApplicationDetailOut(BaseModel):
    id: int
    type: str
    status: str
    severity: Optional[str]
    latest_external_rating: Optional[str]
    remark: Optional[str]
    created_at: datetime
    reviewed_at: Optional[datetime]
    customer_id: int
    customer_name: str
    reason_id: int
    reason_description: str
    created_by: int
    created_by_name: Optional[str]
    reviewed_by: Optional[int]
    reviewed_by_name: Optional[str]

