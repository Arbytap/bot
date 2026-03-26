import uuid
from pydantic import BaseModel, EmailStr


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenPayload(BaseModel):
    sub: str


class UserRegister(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    password: str


class UserOut(BaseModel):
    id: uuid.UUID
    email: str
    username: str
    full_name: str
    is_active: bool
    is_superuser: bool
    current_company_id: uuid.UUID | None

    model_config = {"from_attributes": True}


class SwitchCompany(BaseModel):
    company_id: uuid.UUID
