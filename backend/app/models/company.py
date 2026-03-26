import uuid
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, ForeignKey, Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class CompanyType(str, enum.Enum):
    customer = "customer"
    general_contractor = "general_contractor"
    subcontractor = "subcontractor"
    designer = "designer"
    supervisor = "supervisor"
    operator = "operator"
    other = "other"


class UserRole(str, enum.Enum):
    admin = "admin"
    manager = "manager"
    editor = "editor"
    viewer = "viewer"


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    short_name: Mapped[str] = mapped_column(String(200), nullable=False)
    inn: Mapped[str | None] = mapped_column(String(12), nullable=True)
    kpp: Mapped[str | None] = mapped_column(String(9), nullable=True)
    company_type: Mapped[CompanyType] = mapped_column(
        SAEnum(CompanyType, name="company_type"), nullable=False, default=CompanyType.other
    )
    is_internal: Mapped[bool] = mapped_column(Boolean, default=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user_roles: Mapped[list["UserCompanyRole"]] = relationship(
        "UserCompanyRole", back_populates="company"
    )
    project_companies: Mapped[list["ProjectCompany"]] = relationship(
        "ProjectCompany", back_populates="company"
    )


class UserCompanyRole(Base):
    __tablename__ = "user_company_roles"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, index=True
    )
    role: Mapped[UserRole] = mapped_column(
        SAEnum(UserRole, name="user_role"), nullable=False, default=UserRole.viewer
    )
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    user: Mapped["User"] = relationship("User", back_populates="company_roles")
    company: Mapped["Company"] = relationship("Company", back_populates="user_roles")
