import uuid
from datetime import datetime, date
from pydantic import BaseModel
from app.models.sed import ChainDirection, LetterType, LetterStatus
from app.schemas.company import CompanyOut


class ChainCreate(BaseModel):
    project_id: uuid.UUID
    subject: str
    direction: ChainDirection = ChainDirection.mixed
    main_company_id: uuid.UUID | None = None


class ChainUpdate(BaseModel):
    subject: str | None = None
    direction: ChainDirection | None = None
    main_company_id: uuid.UUID | None = None


class ChainOut(BaseModel):
    id: uuid.UUID
    project_id: uuid.UUID
    subject: str
    direction: ChainDirection
    main_company_id: uuid.UUID | None
    created_at: datetime
    letters_count: int = 0

    model_config = {"from_attributes": True}


class LetterCreate(BaseModel):
    chain_id: uuid.UUID
    project_id: uuid.UUID
    letter_type: LetterType
    letter_date: date | None = None
    number: str | None = None
    org_number: str | None = None
    from_company_id: uuid.UUID | None = None
    to_company_id: uuid.UUID | None = None
    subject: str | None = None
    body: str | None = None
    status: LetterStatus = LetterStatus.received
    reply_to_id: uuid.UUID | None = None
    resolution: str | None = None
    note: str | None = None


class LetterUpdate(BaseModel):
    letter_date: date | None = None
    number: str | None = None
    org_number: str | None = None
    from_company_id: uuid.UUID | None = None
    to_company_id: uuid.UUID | None = None
    subject: str | None = None
    body: str | None = None
    status: LetterStatus | None = None
    reply_to_id: uuid.UUID | None = None
    resolution: str | None = None
    note: str | None = None


class LetterFileOut(BaseModel):
    id: uuid.UUID
    letter_id: uuid.UUID
    filename: str
    original_name: str
    content_type: str
    size: int
    uploaded_at: datetime

    model_config = {"from_attributes": True}


class LetterOut(BaseModel):
    id: uuid.UUID
    chain_id: uuid.UUID
    project_id: uuid.UUID
    owner_company_id: uuid.UUID
    letter_type: LetterType
    letter_date: date | None
    number: str | None
    org_number: str | None
    from_company_id: uuid.UUID | None
    to_company_id: uuid.UUID | None
    subject: str | None
    body: str | None
    status: LetterStatus
    reply_to_id: uuid.UUID | None
    resolution: str | None
    note: str | None
    created_at: datetime
    updated_at: datetime
    files_count: int = 0
    has_replies: bool = False

    model_config = {"from_attributes": True}


class LetterDetail(LetterOut):
    owner_company: CompanyOut
    from_company: CompanyOut | None
    to_company: CompanyOut | None
    files: list[LetterFileOut]

    model_config = {"from_attributes": True}


class LetterThread(BaseModel):
    letter: LetterDetail
    reply_to: LetterOut | None
    replies: list[LetterOut]
    chain_letters: list[LetterOut]
