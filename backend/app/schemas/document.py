import uuid
from datetime import datetime
from pydantic import BaseModel
from app.models.document import DocType, DocStatus
from app.schemas.company import CompanyOut


class DocumentCreate(BaseModel):
    project_id: uuid.UUID
    doc_type: DocType = DocType.other
    code: str | None = None
    name: str
    description: str | None = None
    version: str = "1.0"
    linked_letter_id: uuid.UUID | None = None


class DocumentUpdate(BaseModel):
    doc_type: DocType | None = None
    code: str | None = None
    name: str | None = None
    description: str | None = None
    status: DocStatus | None = None
    version: str | None = None
    linked_letter_id: uuid.UUID | None = None


class DocumentFileOut(BaseModel):
    id: uuid.UUID
    document_id: uuid.UUID
    filename: str
    original_name: str
    content_type: str
    size: int
    version: str
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class DocumentOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    owner_company_id: uuid.UUID
    doc_type: DocType
    code: str | None
    name: str
    description: str | None
    status: DocStatus
    version: str
    linked_letter_id: uuid.UUID | None
    created_at: datetime
    updated_at: datetime
    files_count: int = 0

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentOut):
    owner_company: CompanyOut
    files: list[DocumentFileOut]

    model_config = {"from_attributes": True}
