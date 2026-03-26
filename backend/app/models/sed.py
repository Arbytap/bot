import uuid
from datetime import datetime, date
from sqlalchemy import (
    String, DateTime, Date, ForeignKey, Text,
    Enum as SAEnum, Integer, BigInteger
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship
import enum

from app.database import Base


class ChainDirection(str, enum.Enum):
    incoming = "incoming"
    outgoing = "outgoing"
    mixed = "mixed"


class LetterType(str, enum.Enum):
    incoming = "incoming"
    outgoing = "outgoing"
    internal = "internal"


class LetterStatus(str, enum.Enum):
    received = "received"
    in_work = "in_work"
    done = "done"
    sent = "sent"
    archived = "archived"


class Chain(Base):
    __tablename__ = "chains"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    direction: Mapped[ChainDirection] = mapped_column(
        SAEnum(ChainDirection, name="chain_direction"),
        nullable=False,
        default=ChainDirection.mixed,
    )
    main_company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    project: Mapped["Project"] = relationship("Project", back_populates="chains")
    main_company: Mapped["Company | None"] = relationship("Company", foreign_keys=[main_company_id])
    letters: Mapped[list["Letter"]] = relationship(
        "Letter", back_populates="chain", cascade="all, delete-orphan"
    )


class Letter(Base):
    __tablename__ = "letters"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    chain_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("chains.id", ondelete="CASCADE"), nullable=False, index=True
    )
    project_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True
    )
    owner_company_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="RESTRICT"), nullable=False, index=True
    )
    letter_type: Mapped[LetterType] = mapped_column(
        SAEnum(LetterType, name="letter_type"),
        nullable=False,
        index=True,
    )
    letter_date: Mapped[date | None] = mapped_column(Date, nullable=True, index=True)
    number: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    org_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    from_company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    to_company_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("companies.id", ondelete="SET NULL"), nullable=True, index=True
    )
    subject: Mapped[str | None] = mapped_column(String(500), nullable=True)
    body: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[LetterStatus] = mapped_column(
        SAEnum(LetterStatus, name="letter_status"),
        nullable=False,
        default=LetterStatus.received,
        index=True,
    )
    reply_to_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("letters.id", ondelete="SET NULL"), nullable=True, index=True
    )
    resolution: Mapped[str | None] = mapped_column(Text, nullable=True)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )

    # Relationships
    chain: Mapped["Chain"] = relationship("Chain", back_populates="letters")
    project: Mapped["Project"] = relationship("Project")
    owner_company: Mapped["Company"] = relationship("Company", foreign_keys=[owner_company_id])
    from_company: Mapped["Company | None"] = relationship("Company", foreign_keys=[from_company_id])
    to_company: Mapped["Company | None"] = relationship("Company", foreign_keys=[to_company_id])
    reply_to: Mapped["Letter | None"] = relationship(
        "Letter", remote_side="Letter.id", foreign_keys=[reply_to_id]
    )
    replies: Mapped[list["Letter"]] = relationship(
        "Letter", foreign_keys=[reply_to_id], back_populates="reply_to",
        overlaps="reply_to",
    )
    files: Mapped[list["LetterFile"]] = relationship(
        "LetterFile", back_populates="letter", cascade="all, delete-orphan"
    )


class LetterFile(Base):
    __tablename__ = "letter_files"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4
    )
    letter_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("letters.id", ondelete="CASCADE"), nullable=False, index=True
    )
    filename: Mapped[str] = mapped_column(String(500), nullable=False)
    original_name: Mapped[str] = mapped_column(String(500), nullable=False)
    content_type: Mapped[str] = mapped_column(String(200), nullable=False)
    size: Mapped[int] = mapped_column(BigInteger, nullable=False)
    storage_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    uploaded_by_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"), nullable=True
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    # Relationships
    letter: Mapped["Letter"] = relationship("Letter", back_populates="files")
    uploaded_by: Mapped["User | None"] = relationship("User")
