import uuid
from datetime import datetime, date
from pydantic import BaseModel
from app.models.project import ProjectStatus, ProjectCompanyRole
from app.schemas.company import CompanyOut


class ProjectCreate(BaseModel):
    code: str
    name: str
    description: str | None = None
    status: ProjectStatus = ProjectStatus.planned
    start_date: date | None = None
    end_date: date | None = None
    owner_company_id: uuid.UUID


class ProjectUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    status: ProjectStatus | None = None
    start_date: date | None = None
    end_date: date | None = None


class ProjectCompanyAdd(BaseModel):
    company_id: uuid.UUID
    role: ProjectCompanyRole = ProjectCompanyRole.other


class ProjectCompanyOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    company_id: uuid.UUID
    role: ProjectCompanyRole
    company: CompanyOut

    model_config = {"from_attributes": True}


class ProjectOut(BaseModel):
    id: uuid.UUID
    code: str
    name: str
    description: str | None
    status: ProjectStatus
    start_date: date | None
    end_date: date | None
    owner_company_id: uuid.UUID
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class ProjectDetail(ProjectOut):
    owner_company: CompanyOut
    project_companies: list[ProjectCompanyOut]

    model_config = {"from_attributes": True}


class ProjectSummary(BaseModel):
    project_id: uuid.UUID
    letters_count: int
    incoming_count: int
    outgoing_count: int
    documents_count: int
    approval_tasks_count: int
    chains_count: int
