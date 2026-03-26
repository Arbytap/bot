import uuid
from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, Text, Enum as SAEnum, Integer, BigInteger
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class DocType(str, enum.Enum):
    project_doc = "project_doc"       # ПД (Проектная документация)
    working_doc = "working_doc"       # РД (Рабочая документация)
    as_built = "as_built"             # ИД (Исполнительная документация)
    contract = "contract"             # Договор
    order = "order"                   # Приказ
    report = "report"                 # Отчёт
    other = "other"


class DocStatus(str, enum.Enum):
    draft = "draft"
    on_approval = "on_approval"
    approved = "approved"
    archived = "archived"


class ProjectDocument(Base):
    __tablename__ = "project_documents"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    doc_type: Mapped[DocType] = mapped_column(
        SAEnum(DocType, name="doc_type"),
        nullable=False,
        default=DocType.other,
        index=True,
    )
    code: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[DocStatus] = mapped_column(
        SAEnum(DocStatus, name="doc_status"),
        nullable=False,
        default=DocStatus.draft,
        index=True,
    )
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    # Optional link to a letter/chain this document originated from
    linked_letter_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("letters.id", ondelete="SET NULL"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="documents")
    owner_company: Mapped["Company"] = relationship("Company", foreign_keys=[owner_company_id])
    linked_letter: Mapped["Letter | None"] = relationship("Letter")
    files: Mapped[list["ProjectDocumentFile"]] = relationship(
        "ProjectDocumentFile", back_populates="document", cascade="all, delete-orphan"
    )


class ProjectDocumentFile(Base):
    __tablename__ = "project_document_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    document_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("project_documents.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(200), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False, default="1.0")
    uploaded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    document: Mapped["ProjectDocument"] = relationship("ProjectDocument", back_populates="files")
    uploaded_by: Mapped["User | None"] = relationship("User")
