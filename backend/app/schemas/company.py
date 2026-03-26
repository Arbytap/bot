import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.company import CompanyType, UserRole


class CompanyCreate(BaseModel):
    name: str
    short_name: str
    inn: str | None = None
    kpp: str | None = None
    company_type: CompanyType = CompanyType.other
    is_internal: bool = False


class CompanyUpdate(BaseModel):
    name: str | None = None
    short_name: str | None = None
    inn: str | None = None
    kpp: str | None = None
    company_type: CompanyType | None = None
    is_internal: bool | None = None


class CompanyOut(BaseModel):
    id: uuid.UUID
    name: str
    short_name: str
    inn: str | None
    kpp: str | None
    company_type: CompanyType
    is_internal: bool
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class UserCompanyRoleCreate(BaseModel):
    user_id: uuid.UUID
    company_id: uuid.UUID
    role: UserRole = UserRole.viewer


class UserCompanyRoleOut(BaseModel):
    id: uuid.UUID
    user_id: uuid.UUID
    company_id: uuid.UUID
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}
