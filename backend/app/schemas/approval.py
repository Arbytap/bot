import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.approval import ApprovalStatus
from app.schemas.auth import UserOut


class ApprovalRouteCreate(BaseModel):
    project_id: uuid.UUID | None = None
    name: str
    description: str | None = None


class ApprovalStepCreate(BaseModel):
    order_num: int
    name: str
    assignee_id: uuid.UUID | None = None
    company_id: uuid.UUID | None = None
    deadline_days: int | None = None


class ApprovalStartRequest(BaseModel):
    project_id: uuid.UUID
    route_id: uuid.UUID | None = None
    letter_id: uuid.UUID | None = None
    document_id: uuid.UUID | None = None
    title: str
    assignee_id: uuid.UUID | None = None
    deadline: datetime | None = None
    comment: str | None = None


class ApprovalTaskUpdate(BaseModel):
    status: ApprovalStatus | None = None
    comment: str | None = None
    assignee_id: uuid.UUID | None = None


class ApprovalTaskOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    route_id: uuid.UUID | None
    letter_id: uuid.UUID | None
    document_id: uuid.UUID | None
    title: str
    status: ApprovalStatus
    current_step: int
    assignee_id: uuid.UUID | None
    created_by_id: uuid.UUID | None
    comment: str | None
    deadline: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
